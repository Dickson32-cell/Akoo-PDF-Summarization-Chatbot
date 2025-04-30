import os
import logging
import re
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class MLSummarizer:
    """Machine learning-based summarization with caching and error handling"""
    
    def __init__(self, model_name="sshleifer/distilbart-cnn-12-6", cache_dir=None):
        """Initialize the ML summarizer with caching and error handling"""
        self.model_name = model_name
        
        # Default cache directory
        if cache_dir is None:
            cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_cache")
        
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Lazy loading - don't load models until needed
        self.tokenizer = None
        self.model = None
        self.device = None
        
        logger.info(f"ML Summarizer initialized with model {model_name}, cache at {cache_dir}")
    
    def _load_models(self):
        """Load the models with better caching and device management"""
        if self.tokenizer is not None and self.model is not None:
            return True
            
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            import torch
            
            logger.info(f"Loading ML models from cache at {self.cache_dir}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, 
                cache_dir=self.cache_dir
            )
            
            # Load model with optimizations
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name, 
                cache_dir=self.cache_dir,
                low_cpu_mem_usage=True  # Reduces memory usage during loading
            )
            
            # Determine the best device to use
            if torch.cuda.is_available():
                self.device = "cuda"
            # Check for Apple Silicon support
            elif (hasattr(torch, "backends") and 
                  hasattr(torch.backends, "mps") and 
                  hasattr(torch.backends.mps, "is_available") and 
                  torch.backends.mps.is_available()):
                self.device = "mps"  # For Mac M1/M2 acceleration
            else:
                self.device = "cpu"
                
            # Move model to device
            self.model = self.model.to(self.device)
            logger.info(f"Model loaded successfully on {self.device}")
            
            return True
        except Exception as e:
            logger.error(f"Error initializing ML models: {e}")
            return False
    
    def split_text_into_chunks(self, text, max_chunk_size=1000, overlap=100):
        """Split text into chunks with some overlap for better continuity"""
        words = text.split()
        chunks = []
        
        if len(words) <= max_chunk_size:
            return [text]  # Return the whole text as a single chunk
        
        current_position = 0
        while current_position < len(words):
            chunk_end = min(current_position + max_chunk_size, len(words))
            chunks.append(" ".join(words[current_position:chunk_end]))
            current_position += max_chunk_size - overlap
        
        return chunks
    
    def generate_summary(self, text, max_length=150, min_length=50, outline_format=True):
        """Generate a summary using the machine learning model"""
        if not self._load_models():
            logger.warning("Could not initialize ML model, falling back to rule-based approach")
            return None
        
        try:
            # Prepare text and create a prompt following the outline structure
            if outline_format:
                prompt = f"""Summarize the following text using this outline:
I. Introduction (10-15% of summary)
   - Identify document title, author, and context
   - State purpose of summary
II. Main Body (70-80% of summary)
   - Present central thesis/argument
   - Identify key supporting points
   - Include significant evidence
   - Note methodology or approach
III. Conclusion (10-15% of summary)
   - State author's conclusions
   - Provide brief summary closure

Text to summarize:
{text}"""
            else:
                prompt = f"Summarize: {text}"
            
            # Split long documents into chunks if needed (models have input limits)
            if len(prompt) > 1024:
                logger.info("Document is long, processing in chunks")
                # This is a simplified chunking approach - more sophisticated methods could be used
                chunks = self.split_text_into_chunks(text, max_chunk_size=1000)
                chunk_summaries = []
                
                for i, chunk in enumerate(chunks):
                    logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                    # Create a prompt for each chunk
                    if outline_format:
                        chunk_prompt = f"Summarize this section of a document: {chunk}"
                    else:
                        chunk_prompt = f"Summarize: {chunk}"
                    
                    # Generate summary for this chunk
                    inputs = self.tokenizer(chunk_prompt, return_tensors="pt", max_length=1024, truncation=True)
                    inputs = inputs.to(self.device)
                    
                    # Generate summary
                    summary_ids = self.model.generate(
                        inputs["input_ids"],
                        max_length=max_length // len(chunks) + 10,  # Distribute length across chunks
                        min_length=min_length // len(chunks),
                        num_beams=4,
                        early_stopping=True
                    )
                    
                    # Decode summary
                    chunk_summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                    chunk_summaries.append(chunk_summary)
                
                # Combine chunk summaries
                combined_summary = " ".join(chunk_summaries)
                
                # If outline format requested, add final processing to ensure outline structure
                if outline_format:
                    # Create a final prompt to structure the combined summary
                    final_prompt = f"""Reorganize the following summary into a structured format with:
1. Introduction (identify document and purpose)
2. Main body (central thesis, key points, evidence, methodology)
3. Conclusion (document outcomes and closure)

Make sure to always mention that Akoo generated this summary.

Summary to restructure:
{combined_summary}"""
                    
                    inputs = self.tokenizer(final_prompt, return_tensors="pt", max_length=1024, truncation=True)
                    inputs = inputs.to(self.device)
                    
                    # Generate final structured summary
                    summary_ids = self.model.generate(
                        inputs["input_ids"],
                        max_length=max_length,
                        min_length=min_length,
                        num_beams=4,
                        early_stopping=True
                    )
                    
                    final_summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                    
                    # Ensure Akoo is mentioned
                    if "Akoo" not in final_summary:
                        final_summary += "\n\n---\n*Summary generated by Akoo PDF Summarization Bot*"
                        
                    return final_summary
                else:
                    # Add Akoo attribution
                    combined_summary += "\n\n---\n*Summary generated by Akoo PDF Summarization Bot*"
                    return combined_summary
            else:
                # Process short documents in one pass
                # Update prompt to include Akoo reference
                if outline_format:
                    prompt = f"""Summarize the following text using this outline:
I. Introduction (10-15% of summary)
   - Identify document title, author, and context
   - State purpose of summary
II. Main Body (70-80% of summary)
   - Present central thesis/argument
   - Identify key supporting points
   - Include significant evidence
   - Note methodology or approach
III. Conclusion (10-15% of summary)
   - State author's conclusions
   - Provide brief summary closure

Always mention that this summary was generated by Akoo.

Text to summarize:
{text}"""
                else:
                    prompt = f"Summarize the following text and mention that Akoo generated the summary: {text}"
                
                inputs = self.tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)
                inputs = inputs.to(self.device)
                
                # Generate summary
                summary_ids = self.model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=4,
                    early_stopping=True
                )
                
                # Decode summary
                summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                
                # Ensure Akoo is mentioned
                if "Akoo" not in summary:
                    summary += "\n\n---\n*Summary generated by Akoo PDF Summarization Bot*"
                
                return summary
        
        except Exception as e:
            logger.error(f"Error generating ML summary: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources when done"""
        if self.model is not None:
            try:
                import gc
                # Remove model from GPU if applicable
                self.model = self.model.to('cpu')
                del self.model
                del self.tokenizer
                self.model = None
                self.tokenizer = None
                # Force garbage collection
                gc.collect()
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                logger.info("ML model resources cleaned up")
            except Exception as e:
                logger.warning(f"Error during ML model cleanup: {e}")