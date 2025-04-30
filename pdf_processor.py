import os
import re
import math
import logging
from collections import Counter
import io

logger = logging.getLogger(__name__)

# Function to extract text from PDF with enhanced error handling
def extract_text_from_pdf(file):
    """Extract text from a PDF file with enhanced error handling"""
    try:
        import PyPDF2
        logger.info(f"Beginning PDF extraction with PyPDF2")
        
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Check if PDF is encrypted
        if pdf_reader.is_encrypted:
            logger.error("PDF is encrypted or password-protected")
            return None, "This PDF is encrypted or password-protected and cannot be processed."
        
        # Get the number of pages
        num_pages = len(pdf_reader.pages)
        logger.info(f"PDF has {num_pages} pages")
        
        if num_pages == 0:
            logger.error("PDF has zero pages")
            return None, "The PDF appears to be empty (zero pages detected)."
            
        # Extract text from each page
        text = ""
        for page_num in range(num_pages):
            logger.debug(f"Processing page {page_num+1}/{num_pages}")
            page = pdf_reader.pages[page_num]
            
            try:
                page_text = page.extract_text()
                
                if page_text:
                    text += page_text
                else:
                    logger.warning(f"No text extracted from page {page_num+1}")
            except Exception as page_error:
                logger.warning(f"Error extracting text from page {page_num+1}: {page_error}")
                continue
            
        # Check if we actually got any text
        if not text or text.isspace():
            logger.error("No text could be extracted from PDF")
            return None, "No text could be extracted from this PDF. It may be a scanned document or contain only images."
            
        logger.info(f"Successfully extracted {len(text)} characters from PDF")
        return text, None  # Return text and no error
        
    except Exception as e:
        logger.error(f"Unexpected error extracting text: {str(e)}")
        return None, f"Error extracting text from PDF: {str(e)}"

# Try to import PyMuPDF for better extraction
try:
    import fitz
    HAS_PYMUPDF = True
    logger.info("PyMuPDF (fitz) is available for advanced PDF extraction")
except ImportError:
    HAS_PYMUPDF = False
    logger.warning("PyMuPDF not available, some advanced extraction features will be limited")

# Extract with PyMuPDF
def extract_with_pymupdf(file_path):
    """Extract text using PyMuPDF for better results with complex PDFs"""
    if not HAS_PYMUPDF:
        return None, "PyMuPDF not available"
    
    try:
        doc = fitz.open(file_path)
        text = ""
        
        # Try multiple extraction modes for best results
        for page in doc:
            # Try text extraction mode first
            page_text = page.get_text("text")
            if page_text and len(page_text.strip()) > 20:
                text += page_text
            else:
                # Try blocks mode
                page_text = page.get_text("blocks")
                text += page_text
        
        doc.close()
        
        if not text or len(text.strip()) < 100:
            return None, "Limited text extracted"
            
        logger.info(f"Successfully extracted {len(text)} characters with PyMuPDF")
        return text, None
    except Exception as e:
        logger.error(f"PyMuPDF extraction error: {e}")
        return None, str(e)

# Try to import OCR libraries
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
    logger.info("OCR libraries available for scanned document processing")
except ImportError:
    HAS_OCR = False
    logger.warning("OCR libraries not available, scanned documents cannot be processed")

# Extract with OCR for scanned documents
def extract_with_ocr(file_path):
    """Extract text using OCR for scanned documents"""
    if not HAS_OCR:
        return None, "OCR libraries not available"
    
    try:
        # Try to import pdf2image for PDF to image conversion
        try:
            from pdf2image import convert_from_path
        except ImportError:
            return None, "PDF to image conversion library not available"
        
        logger.info("Starting OCR extraction process")
        
        # Convert PDF pages to images
        images = convert_from_path(file_path)
        
        text = ""
        for i, image in enumerate(images):
            logger.debug(f"OCR processing page {i+1}/{len(images)}")
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n\n"
            
            # Clean up memory
            del image
        
        if not text or len(text.strip()) < 100:
            return None, "OCR extraction yielded insufficient text"
            
        logger.info(f"Successfully extracted {len(text)} characters with OCR")
        return text, None
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return None, str(e)

# Better extraction method that tries multiple approaches
def better_pdf_extraction(file_path):
    """Try multiple methods to extract text from difficult PDFs"""
    # Method 1: Standard PyPDF2
    try:
        with open(file_path, 'rb') as file:
            text, error = extract_text_from_pdf(file)
            if text and len(text) > 100:
                logger.info(f"Successfully extracted {len(text)} characters with PyPDF2")
                return text, None
    except Exception as e:
        logger.error(f"Standard extraction failed: {e}")
    
    logger.info("Standard extraction didn't yield good results, trying alternative method")
    
    # Method 2: Try PyMuPDF
    if HAS_PYMUPDF:
        text, error = extract_with_pymupdf(file_path)
        if text and len(text) > 100:
            logger.info(f"Successfully extracted {len(text)} characters with PyMuPDF")
            return text, None
    else:
        logger.warning("PyMuPDF not installed, skipping alternative extraction")
    
    # Method 3: Try OCR as last resort
    if HAS_OCR:
        logger.info("Attempting OCR extraction")
        text, error = extract_with_ocr(file_path)
        if text and len(text) > 100:
            logger.info(f"Successfully extracted {len(text)} characters with OCR")
            return text, None
    else:
        logger.warning("OCR capabilities not available, skipping OCR extraction")
    
    # Method 4: Last resort - try reading as plain text file
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            if b'%PDF' in content:  # It's definitely a PDF
                logger.warning("PDF extraction failed or returned limited text")
                return None, "Failed to extract text from PDF"
            else:  # Try as text
                text = content.decode('utf-8', errors='ignore')
                if len(text) > 100:
                    return text, None
    except:
        pass
    
    return None, "Failed to extract text from PDF using multiple methods."

# Process batches for large PDFs
def process_large_pdf(file_path, max_pages=None, callback=None):
    """Process a large PDF by extracting and summarizing pages in batches with progress reporting"""
    try:
        import PyPDF2
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Limit pages if needed
                pages_to_process = min(total_pages, max_pages) if max_pages else total_pages
                
                # Process in batches of 10 pages
                batch_size = 10
                all_text = ""
                
                for i in range(0, pages_to_process, batch_size):
                    batch_end = min(i + batch_size, pages_to_process)
                    logger.info(f"Processing page batch {i+1}-{batch_end}")
                    
                    # Report progress
                    if callback:
                        progress = int(100 * i / pages_to_process)
                        callback({
                            "status": "processing", 
                            "progress": progress,
                            "message": f"Processing page batch {i+1}-{batch_end} of {pages_to_process}"
                        })
                    
                    batch_text = ""
                    for j in range(i, batch_end):
                        try:
                            page = pdf_reader.pages[j]
                            page_text = page.extract_text() or ""
                            batch_text += page_text
                        except Exception as e:
                            logger.warning(f"Error processing page {j+1}: {e}")
                            continue
                    
                    all_text += batch_text
                    
                    # Prevent memory buildup by running garbage collection
                    import gc
                    gc.collect()
                
                if not all_text or all_text.isspace():
                    logger.warning("No text extracted from batch processing")
                    return None
                    
                return all_text
        except Exception as e:
            logger.error(f"Error reading PDF file: {e}")
            return None
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        return None

# Function to estimate PDF complexity and processing needs
def estimate_pdf_complexity(file_path):
    """Estimate PDF complexity to determine appropriate processing strategy"""
    try:
        # Basic file size check
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
        
        # Open PDF to check page count and structure
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            page_count = len(pdf.pages)
            
            # Sample a few pages to check for text
            sample_pages = min(5, page_count)
            text_found = False
            scanned_likelihood = 0
            
            for i in range(sample_pages):
                page = pdf.pages[i]
                text = page.extract_text() or ""
                
                if len(text.strip()) > 100:
                    text_found = True
                elif len(text.strip()) < 20:
                    scanned_likelihood += 1
            
            # Check if this might be a scanned document
            if scanned_likelihood >= sample_pages * 0.6:
                return {
                    "size_mb": file_size,
                    "pages": page_count,
                    "likely_scanned": True,
                    "ocr_recommended": True,
                    "complexity": "high" if page_count > 50 else "medium"
                }
                
            # Determine complexity based on size and page count
            complexity = "low"
            if page_count > 100 or file_size > 10:
                complexity = "high"
            elif page_count > 30 or file_size > 5:
                complexity = "medium"
                
            return {
                "size_mb": file_size,
                "pages": page_count,
                "likely_scanned": False,
                "ocr_recommended": False,
                "complexity": complexity,
                "text_extractable": text_found
            }
    except Exception as e:
        logger.error(f"Error estimating PDF complexity: {e}")
        # Default to medium complexity if estimation fails
        return {
            "complexity": "medium",
            "ocr_recommended": False,
            "error": str(e)
        }

# Select the best extraction method based on PDF characteristics
def extract_text_with_best_method(file_path):
    """Analyze PDF and choose the best extraction method"""
    try:
        # Estimate complexity
        complexity = estimate_pdf_complexity(file_path)
        logger.info(f"PDF complexity analysis: {complexity}")
        
        # For scanned documents, use OCR
        if complexity.get("ocr_recommended", False) and HAS_OCR:
            logger.info("Using OCR for likely scanned document")
            return extract_with_ocr(file_path)
        
        # For high complexity documents, try PyMuPDF first
        if complexity.get("complexity") == "high" and HAS_PYMUPDF:
            logger.info("Using PyMuPDF for high complexity document")
            text, error = extract_with_pymupdf(file_path)
            if text and len(text) > 100:
                return text, None
                
        # For large documents, use batch processing
        if complexity.get("pages", 0) > 100:
            logger.info("Using batch processing for large document")
            text = process_large_pdf(file_path)
            if text and len(text) > 100:
                return text, None
        
        # Default to standard extraction
        logger.info("Using standard extraction method")
        with open(file_path, 'rb') as file:
            return extract_text_from_pdf(file)
    except Exception as e:
        logger.error(f"Error selecting extraction method: {e}")
        # Fall back to the better_pdf_extraction method that tries multiple approaches
        return better_pdf_extraction(file_path)