import re
import math
import logging
import os
from collections import Counter
import time
import hashlib
import json

logger = logging.getLogger(__name__)

# Create NLTK data directory if it doesn't exist
NLTK_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
os.makedirs(NLTK_DATA_PATH, exist_ok=True)
os.environ['NLTK_DATA'] = NLTK_DATA_PATH

# Try to import NLTK with fallback
try:
    import nltk
    nltk.data.path.append(NLTK_DATA_PATH)
    
    # Download resources if needed
    for resource, package in [
        ('tokenizers/punkt', 'punkt'),
        ('corpora/stopwords', 'stopwords'),
        ('corpora/wordnet', 'wordnet')
    ]:
        try:
            nltk.data.find(resource)
            logger.debug(f"NLTK resource available: {package}")
        except LookupError:
            logger.info(f"Downloading NLTK resource: {package}")
            nltk.download(package, download_dir=NLTK_DATA_PATH, quiet=True)
    
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    logger.warning("NLTK not available, using fallback text processing")
except Exception as e:
    HAS_NLTK = False
    logger.warning(f"NLTK initialization error: {e}")
    logger.warning("Using fallback text processing methods")

# More robust sentence tokenization
def robust_sentence_tokenize(text):
    """More robust sentence tokenization that handles common issues"""
    if not text or len(text.strip()) == 0:
        return []
        
    try:
        # Try NLTK's sentence tokenizer if available
        if HAS_NLTK:
            try:
                return sent_tokenize(text)
            except Exception as e:
                logger.warning(f"NLTK sentence tokenization failed: {e}")
    except Exception as e:
        logger.warning(f"Error in NLTK tokenization attempt: {e}")
    
    # Fallback to regex-based sentence splitting
    try:
        # Match periods, exclamation points, or question marks followed by whitespace and capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            # If no sentences were found, try a simpler split on punctuation
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
        logger.info(f"Regex tokenization found {len(sentences)} sentences")
        return sentences
    except Exception as e:
        logger.error(f"Regex sentence tokenization failed: {e}")
        # Ultimate fallback: just split by newlines and return non-empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return lines

# Cache for summarizations
def get_cache_path():
    """Get cache directory path and ensure it exists"""
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def cache_summary(text, params, summary):
    """Cache a summary for future retrieval"""
    try:
        cache_dir = get_cache_path()
        
        # Create unique key for this text and parameters
        text_hash = hashlib.md5(text.encode()).hexdigest()
        param_hash = hashlib.md5(str(params).encode()).hexdigest()
        cache_key = f"{text_hash}_{param_hash}"
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        # Save to cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": summary,
                "params": params,
                "timestamp": time.time()
            }, f)
        
        logger.info(f"Saving summary to cache: {cache_file}")
        return cache_key
    except Exception as e:
        logger.error(f"Error caching summary: {e}")
        return None

def get_cached_summary(text, params):
    """Try to retrieve a cached summary"""
    try:
        cache_dir = get_cache_path()
        
        # Create unique key for this text and parameters
        text_hash = hashlib.md5(text.encode()).hexdigest()
        param_hash = hashlib.md5(str(params).encode()).hexdigest()
        cache_key = f"{text_hash}_{param_hash}"
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Retrieved summary from cache: {cache_file}")
                return data["summary"]
        return None
    except Exception as e:
        logger.error(f"Error accessing cached summary: {e}")
        return None

# Simple text preprocessing (used as fallback if NLTK isn't available)
def simple_preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Split into words
    words = text.split()
    
    return words

# NLTK-based text preprocessing
def nltk_preprocess_text(text):
    # Tokenize the text
    try:
        tokens = word_tokenize(text.lower())
        
        # Remove punctuation and stop words
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens 
                  if word.isalnum() and word not in stop_words]
        
        return tokens
    except Exception as e:
        logger.warning(f"NLTK preprocessing failed: {e}")
        return simple_preprocess_text(text)

# Choose the appropriate preprocessing function
def preprocess_text(text):
    if HAS_NLTK:
        try:
            return nltk_preprocess_text(text)
        except Exception as e:
            logger.warning(f"NLTK processing error: {e}")
            return simple_preprocess_text(text)
    else:
        return simple_preprocess_text(text)

# Calculate term frequency
def calculate_term_frequency(text):
    try:
        # Tokenize the text into words
        if HAS_NLTK:
            words = word_tokenize(text.lower())
            # Remove stopwords and punctuation
            stop_words = set(stopwords.words('english'))
            words = [word for word in words if word.isalnum() and word not in stop_words]
        else:
            # Simple tokenization without NLTK
            words = re.findall(r'\b\w+\b', text.lower())
        
        # Calculate frequency of each word
        word_freq = Counter(words)
        
        logger.debug(f"Calculated frequencies for {len(word_freq)} unique words")
        return word_freq
    except Exception as e:
        logger.error(f"Error calculating term frequency: {e}")
        # Fallback to simple word counting
        simple_words = re.findall(r'\b\w+\b', text.lower())
        return Counter(simple_words)

# Calculate TF-IDF for text summarization with enhanced error handling
def calculate_tf_idf_scores(sentences, word_freq, total_words):
    try:
        sentence_scores = {}
        
        for i, sentence in enumerate(sentences):
            # Skip empty sentences
            if not sentence.strip():
                continue
                
            # Tokenize the sentence
            if HAS_NLTK:
                words = word_tokenize(sentence.lower())
                # Remove stopwords
                stop_words = set(stopwords.words('english'))
                words = [word for word in words if word.isalnum() and word not in stop_words]
            else:
                # Simple tokenization without NLTK
                words = re.findall(r'\b\w+\b', sentence.lower())
            
            # Skip empty sentences after tokenization and filtering
            if not words:
                continue
                
            # Score based on word frequency
            score = 0
            for word in words:
                if word in word_freq:
                    # TF (Term Frequency)
                    tf = word_freq[word] / max(1, total_words)  # Avoid division by zero
                    
                    # IDF component (simplified)
                    # Count sentences containing this word
                    sentence_count = 0
                    for s in sentences:
                        if word in s.lower():
                            sentence_count += 1
                    
                    # Calculate IDF with safeguards against division by zero
                    if sentence_count > 0:
                        idf = math.log(len(sentences) / sentence_count)
                    else:
                        idf = 0
                        
                    score += tf * idf
            
            # Normalize by sentence length to avoid bias towards longer sentences
            if len(words) > 0:
                sentence_scores[i] = score / len(words)
        
        return sentence_scores
    except Exception as e:
        logger.error(f"Error calculating TF-IDF scores: {e}")
        # Fallback to simple sentence scoring
        return {i: 1.0 for i in range(len(sentences))}

# Simple fallback summarization method
def simple_fallback_summary(text, num_sentences=10):
    """A simpler, more robust summarization method for when the primary method fails"""
    try:
        logger.info("Using fallback summarization method")
        
        # Split text into sentences using the robust tokenizer
        sentences = robust_sentence_tokenize(text)
        logger.debug(f"Split text into {len(sentences)} sentences")
        
        if len(sentences) <= num_sentences:
            logger.info("Text has fewer sentences than requested summary length, returning full text")
            return text
        
        # For fallback with larger summaries, use a more distributed approach
        if num_sentences > 30:
            # Get sentences from throughout the document
            indices = []
            
            # Get 20% from beginning (introduction)
            intro_count = max(1, min(int(num_sentences * 0.2), 20))
            indices.extend(range(min(intro_count, len(sentences))))
            
            # Get 60% from middle, distributed evenly
            middle_count = max(1, int(num_sentences * 0.6))
            if len(sentences) > intro_count + 5:
                middle_section = sentences[intro_count:-min(int(len(sentences) * 0.2), 20)]
                step = max(1, len(middle_section) // middle_count)
                middle_indices = list(range(intro_count, intro_count + len(middle_section), step))[:middle_count]
                indices.extend(middle_indices)
            
            # Get 20% from end (conclusion)
            conclusion_count = max(1, min(int(num_sentences * 0.2), 20))
            if conclusion_count > 0 and len(sentences) > conclusion_count:
                indices.extend(range(len(sentences) - conclusion_count, len(sentences)))
            
            # Ensure we don't have duplicates and stay within bounds
            indices = sorted(set([i for i in indices if i < len(sentences)]))
            
            # If we need more sentences to reach the requested count, add more from middle
            if len(indices) < num_sentences and len(sentences) > len(indices):
                available_indices = [i for i in range(len(sentences)) if i not in indices]
                additional_needed = min(num_sentences - len(indices), len(available_indices))
                if additional_needed > 0:
                    # Take evenly spaced sentences from available indices
                    step = max(1, len(available_indices) // additional_needed)
                    additional_indices = available_indices[::step][:additional_needed]
                    indices.extend(additional_indices)
                    indices.sort()
            
            summary_sentences = [sentences[i] for i in indices]
            summary = ' '.join(summary_sentences)
            
            logger.info(f"Generated fallback summary with {len(summary_sentences)} sentences")
            return summary
            
        # For smaller summaries, use the original approach
        beginning = sentences[:max(1, num_sentences//3)]
        
        middle_start = len(sentences)//2 - max(1, num_sentences//6)
        middle_end = middle_start + max(1, num_sentences//3)
        middle = sentences[middle_start:middle_end]
        
        end = sentences[-max(1, num_sentences//3):]
        
        summary_sentences = beginning + middle + end
        summary = ' '.join(summary_sentences)
        
        logger.info(f"Generated fallback summary of {len(summary)} characters")
        return summary
    except Exception as e:
        logger.error(f"Error in fallback summarization: {str(e)}")
        # Ultimate fallback - just return the first part of the text
        return text[:4000] + "... [Summary truncated due to processing error]"

# Format summary based on user preference
def format_summary(sentences, format_type='paragraph'):
    try:
        if format_type == 'bullet':
            return '\n'.join([f"• {sentence}" for sentence in sentences])
        elif format_type == 'numbered':
            return '\n'.join([f"{i+1}. {sentence}" for i, sentence in enumerate(sentences)])
        else:  # paragraph format (default)
            return ' '.join(sentences)
    except Exception as e:
        logger.error(f"Error formatting summary: {e}")
        # Fallback to simple joining
        return ' '.join(sentences)

# ====== Structured Summary Functions ======

def extract_document_metadata(text, filename):
    """Attempt to extract document metadata like title, author, and date"""
    metadata = {
        "title": filename.replace(".pdf", ""),
        "author": "Unknown",
        "date": "Unknown",
        "document_type": "Document"
    }
    
    # Try to extract title from first few lines
    first_lines = text.split('\n')[:10]
    potential_title_line = None
    
    # Look for title patterns (typically first non-empty line or ALL CAPS line)
    for line in first_lines:
        line = line.strip()
        if line and len(line) > 10 and len(line) < 100:
            potential_title_line = line
            break
    
    if potential_title_line:
        metadata["title"] = potential_title_line
    
    # Try to identify document type
    lower_text = text.lower()
    if "abstract" in lower_text and "references" in lower_text and "methodology" in lower_text:
        metadata["document_type"] = "Academic Article"
    elif "executive summary" in lower_text or "policy brief" in lower_text:
        metadata["document_type"] = "Policy Paper"
    elif "chapter" in lower_text and ("book" in lower_text or "volume" in lower_text):
        metadata["document_type"] = "Book Chapter"
    elif "report" in lower_text:
        metadata["document_type"] = "Report"
    
    # Look for author patterns
    author_patterns = [
        r'by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'Author[s]?[\s:]+([A-Za-z\s,\.]+)',
        r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s+(?:PhD|MD|Professor)'
    ]
    
    for pattern in author_patterns:
        author_match = re.search(pattern, text)
        if author_match:
            metadata["author"] = author_match.group(1).strip()
            break
    
    # Look for date patterns
    date_patterns = [
        r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4}',
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}',
        r'\d{4}-\d{2}-\d{2}',
        r'\d{2}/\d{2}/\d{4}'
    ]
    
    for pattern in date_patterns:
        date_match = re.search(pattern, text)
        if date_match:
            metadata["date"] = date_match.group(0)
            break
    
    return metadata

def identify_document_sections(text):
    """Identify logical sections within the document"""
    sections = {}
    lower_text = text.lower()
    
    # Common section identifiers in documents
    potential_sections = {
        "abstract": ["abstract", "summary", "overview"],
        "introduction": ["introduction", "background", "context"],
        "methodology": ["method", "methodology", "approach", "procedure"],
        "results": ["result", "finding", "observation", "analysis"],
        "discussion": ["discussion", "interpretation", "implication"],
        "conclusion": ["conclusion", "summary", "recommendation"]
    }
    
    # For each section type, try to find its start and end
    for section_name, keywords in potential_sections.items():
        for keyword in keywords:
            # Look for section headers (keyword followed by newline or colon)
            pattern = fr'\b{keyword}s?\b[:\s]*\n'
            matches = list(re.finditer(pattern, lower_text, re.IGNORECASE))
            
            if matches:
                start_pos = matches[0].start()
                
                # Find the next section header or end of text
                next_section_pos = len(text)
                for other_section in potential_sections.values():
                    for other_keyword in other_section:
                        if other_keyword == keyword:
                            continue
                        
                        other_matches = list(re.finditer(fr'\b{other_keyword}s?\b[:\s]*\n', lower_text[start_pos+10:], re.IGNORECASE))
                        if other_matches:
                            pos = other_matches[0].start() + start_pos + 10
                            if pos < next_section_pos:
                                next_section_pos = pos
                
                # Extract the section text
                section_text = text[start_pos:next_section_pos].strip()
                sections[section_name] = section_text
                break
    
    return sections

def extract_main_thesis(text, sections):
    """Attempt to identify the main thesis or central argument"""
    thesis = ""
    
    # First look in abstract if available
    if "abstract" in sections:
        abstract = sections["abstract"]
        sentences = robust_sentence_tokenize(abstract)
        
        # Often the main thesis is in the first or last sentence of abstract
        if len(sentences) > 0:
            thesis = sentences[0]  # Default to first sentence
            
            # Look for "argument" or "purpose" indicators
            for sentence in sentences:
                lower_s = sentence.lower()
                if "argue" in lower_s or "purpose" in lower_s or "thesis" in lower_s or "this paper" in lower_s:
                    thesis = sentence
                    break
    
    # If not found in abstract, look in introduction
    if not thesis and "introduction" in sections:
        intro = sections["introduction"]
        sentences = robust_sentence_tokenize(intro)
        
        # In introductions, the thesis often appears toward the end
        thesis_candidates = sentences[-3:] if len(sentences) > 3 else sentences
        
        for sentence in thesis_candidates:
            lower_s = sentence.lower()
            if "argue" in lower_s or "this paper" in lower_s or "purpose" in lower_s or "thesis" in lower_s:
                thesis = sentence
                break
        
        # If still not found, default to last sentence of intro (common pattern)
        if not thesis and sentences:
            thesis = sentences[-1]
    
    # If still nothing, look through the first 10% of the document
    if not thesis:
        sentences = robust_sentence_tokenize(text)
        first_portion = sentences[:max(5, int(len(sentences) * 0.1))]
        
        for sentence in first_portion:
            lower_s = sentence.lower()
            if "argue" in lower_s or "this paper" in lower_s or "purpose" in lower_s or "thesis" in lower_s:
                thesis = sentence
                break
    
    # If still nothing, use TF-IDF to find an important early sentence
    if not thesis and len(sentences) > 5:
        word_freq = calculate_term_frequency(text)
        total_words = sum(word_freq.values())
        
        early_sentences = sentences[:min(10, len(sentences)//4)]
        sentence_scores = calculate_tf_idf_scores(early_sentences, word_freq, total_words)
        
        if sentence_scores:
            # Get highest scoring sentence
            max_score = 0
            for i, score in sentence_scores.items():
                if score > max_score and i < len(early_sentences):
                    max_score = score
                    thesis = early_sentences[i]
    
    return thesis

def extract_key_points(text, sections, num_points=5):
    """Extract key supporting points from the document"""
    key_points = []
    sentences = []
    
    # Prioritize looking in specific sections in this order
    section_priority = ["results", "discussion", "methodology", "introduction", "conclusion"]
    
    for section_name in section_priority:
        if section_name in sections:
            section_sentences = robust_sentence_tokenize(sections[section_name])
            sentences.extend(section_sentences)
    
    # If we don't have enough sentences from known sections, use the whole document
    if len(sentences) < num_points * 3:
        sentences = robust_sentence_tokenize(text)
    
    # Use TF-IDF to score sentences
    word_freq = calculate_term_frequency(text)
    total_words = sum(word_freq.values())
    sentence_scores = calculate_tf_idf_scores(sentences, word_freq, total_words)
    
    if not sentence_scores:
        return key_points
    
    # Get top scoring sentences but maintain their original order
    try:
        import heapq
        top_indices = heapq.nlargest(num_points * 2, sentence_scores, key=sentence_scores.get)
        top_indices.sort()  # Sort to maintain original order
    except Exception as e:
        logger.warning(f"Error selecting top sentences: {e}")
        sorted_scores = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, score in sorted_scores[:num_points * 2]]
        top_indices.sort()
    
    # Filter duplicates or very similar sentences
    for i in top_indices:
        if i >= len(sentences):
            continue
            
        candidate = sentences[i]
        
        # Skip very short sentences
        if len(candidate.split()) < 8:
            continue
            
        # Check if this candidate is too similar to anything we've already added
        is_duplicate = False
        for existing in key_points:
            similarity = len(set(candidate.lower().split()) & set(existing.lower().split()))
            similarity = similarity / max(len(candidate.split()), len(existing.split()))
            
            if similarity > 0.6:  # If more than 60% word overlap
                is_duplicate = True
                break
                
        if not is_duplicate:
            key_points.append(candidate)
            
        if len(key_points) >= num_points:
            break
    
    return key_points

def extract_evidence(text, key_points, num_evidence=3):
    """Extract significant evidence such as statistics, examples, or case studies"""
    evidence = []
    sentences = robust_sentence_tokenize(text)
    
    # Look for sentences with numerical data, citations, or example indicators
    evidence_patterns = [
        r'\d+(\.\d+)?%',  # Percentages
        r'\$\d+(\.\d+)?((\s+|-)(million|billion|trillion))?',  # Money amounts
        r'\b\d+(\.\d+)?\s+(people|subjects|participants|respondents)\b',  # Participant counts
        r'\(([^)]+\d{4}[^)]*)\)',  # Citations
        r'for example', r'for instance', r'such as', r'e\.g\.', # Example indicators
        r'study (showed|found|demonstrated)', # Study findings
        r'according to'  # Attribution phrases
    ]
    
    evidence_candidates = []
    
    for sentence in sentences:
        for pattern in evidence_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                # Check that this isn't too similar to a key point we already have
                is_key_point = False
                for kp in key_points:
                    if len(set(sentence.lower().split()) & set(kp.lower().split())) > len(sentence.split()) * 0.7:
                        is_key_point = True
                        break
                
                if not is_key_point:
                    evidence_candidates.append(sentence)
                    break
    
    # If we don't have enough candidates, look for longer sentences (often contain detailed examples)
    if len(evidence_candidates) < num_evidence:
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 30 and sentence not in evidence_candidates and sentence not in key_points:
                evidence_candidates.append(sentence)
            
            if len(evidence_candidates) >= num_evidence * 2:
                break
    
    # Remove duplicates and get top candidates
    seen = set()
    unique_candidates = []
    for s in evidence_candidates:
        if s not in seen:
            seen.add(s)
            unique_candidates.append(s)
    
    # Use TF-IDF to prioritize if we have too many candidates
    if len(unique_candidates) > num_evidence:
        word_freq = calculate_term_frequency(text)
        total_words = sum(word_freq.values())
        
        candidate_scores = calculate_tf_idf_scores(unique_candidates, word_freq, total_words)
        
        try:
            import heapq
            top_indices = heapq.nlargest(num_evidence, candidate_scores, key=candidate_scores.get)
            for i in top_indices:
                if i < len(unique_candidates):
                    evidence.append(unique_candidates[i])
        except Exception as e:
            # Fallback if heapq fails
            for i in range(min(num_evidence, len(unique_candidates))):
                evidence.append(unique_candidates[i])
    else:
        evidence = unique_candidates[:num_evidence]
    
    return evidence

def extract_methodology(text, sections):
    """Extract information about the methodology or approach"""
    methodology = ""
    
    # First check if we have a methodology section
    if "methodology" in sections:
        method_sentences = robust_sentence_tokenize(sections["methodology"])
        
        # Take first 1-2 sentences from methodology section
        if method_sentences:
            methodology = " ".join(method_sentences[:min(2, len(method_sentences))])
            return methodology
    
    # If no methodology section, look for method-related sentences
    sentences = robust_sentence_tokenize(text)
    
    method_keywords = ["method", "approach", "procedure", "technique", "study design", 
                      "conducted", "performed", "analyzed", "collected", "measured"]
    
    for sentence in sentences:
        lower_s = sentence.lower()
        
        # Check if sentence contains methodology keywords
        if any(keyword in lower_s for keyword in method_keywords):
            # Skip sentences that are likely not about the document's own methodology
            if "could" in lower_s or "would" in lower_s or "should" in lower_s or "might" in lower_s:
                continue
                
            methodology = sentence
            break
    
    return methodology

def extract_conclusions(text, sections):
    """Extract the author's conclusions or recommendations"""
    conclusions = []
    
    # First check if we have a conclusion section
    if "conclusion" in sections:
        conclusion_sentences = robust_sentence_tokenize(sections["conclusion"])
        
        # Take up to 3 sentences from conclusion section
        if conclusion_sentences:
            conclusions = conclusion_sentences[:min(3, len(conclusion_sentences))]
            return conclusions
    
    # If no conclusion section, look for conclusion indicators in the last 10% of text
    sentences = robust_sentence_tokenize(text)
    last_portion = sentences[-max(5, int(len(sentences) * 0.1)):]
    
    conclusion_keywords = ["conclude", "conclusion", "summary", "summarily", "in sum",
                          "recommend", "recommendation", "suggest", "therefore", "thus",
                          "in conclusion", "to conclude", "finally"]
    
    for sentence in last_portion:
        lower_s = sentence.lower()
        
        # Check if sentence contains conclusion keywords
        if any(keyword in lower_s for keyword in conclusion_keywords):
            conclusions.append(sentence)
            
            if len(conclusions) >= 3:
                break
    
    # If still no conclusions found, take the last 1-2 sentences of the document
    if not conclusions and sentences:
        conclusions = sentences[-min(2, len(sentences)):]
    
    return conclusions

def academic_excellence_summary(text, filename="", num_sentences=30):
    """Generate a summary following the Excellence Framework for Article Summarization"""
    
    # Try to get cached summary first
    params = {
        "filename": filename,
        "num_sentences": num_sentences,
        "function": "academic_excellence"
    }
    
    cached = get_cached_summary(text, params)
    if cached:
        return cached
    
    try:
        # Extract document metadata and structure
        metadata = extract_document_metadata(text, filename)
        sections = identify_document_sections(text)
        
        # Multi-layered reading process
        sentences = robust_sentence_tokenize(text)
        
        # First read - capture main thesis and structure
        main_thesis = extract_main_thesis(text, sections)
        
        # Second read - identify supporting evidence and details
        key_points = extract_key_points(text, sections, max(5, num_sentences // 3))
        evidence = extract_evidence(text, key_points, max(3, num_sentences // 4))
        
        # Third read - note connections between sections
        connections = []
        try:
            # Extract sentences that contain connecting words
            connecting_words = ["therefore", "consequently", "as a result", "however", "nevertheless",
                            "furthermore", "moreover", "in addition", "similarly", "in contrast"]
            for sentence in sentences:
                if any(word in sentence.lower() for word in connecting_words):
                    connections.append(sentence)
            connections = connections[:max(2, num_sentences // 6)]  # Limit to 1/6 of requested length
        except:
            connections = []
        
        # Publication context integration
        context_info = f"This summary was created by Akoo based on {metadata['document_type']} titled \"{metadata['title']}\""
        if metadata['author'] != "Unknown":
            context_info += f", authored by {metadata['author']}"
        if metadata['date'] != "Unknown":
            context_info += f", published on {metadata['date']}"
        context_info += "."
        
        # Strategic content mapping
        methodology = extract_methodology(text, sections)
        
        # Identify counterarguments (if any)
        counterarguments = []
        counter_patterns = ["however", "nevertheless", "conversely", "on the other hand", "critics", "limitation", 
                        "drawback", "challenge", "opposing", "contrary", "dispute", "disagree"]
        for sentence in sentences:
            s_lower = sentence.lower()
            if any(pattern in s_lower for pattern in counter_patterns):
                counterarguments.append(sentence)
        counterarguments = counterarguments[:max(2, num_sentences // 8)]  # Limit to 1/8 of requested length
        
        # Get conclusions
        conclusions = extract_conclusions(text, sections)
        
        # Format the summary according to the Excellence Framework
        formatted_summary = "# AKOO DOCUMENT SUMMARY\n\n"
        
        # Context section
        formatted_summary += "## Document Context\n\n"
        formatted_summary += context_info + "\n\n"
        
        # Central thesis and arguments
        formatted_summary += "## Central Thesis & Key Arguments\n\n"
        if main_thesis:
            formatted_summary += "### Main Thesis\n" + main_thesis + "\n\n"
        else:
            formatted_summary += "### Main Thesis\nAkoo could not identify a clear thesis statement in this document.\n\n"
        
        # Key supporting points
        formatted_summary += "### Key Arguments\n\n"
        if key_points:
            for i, point in enumerate(key_points, 1):
                formatted_summary += f"{i}. {point}\n"
        else:
            formatted_summary += "No key arguments could be clearly identified by Akoo.\n"
        formatted_summary += "\n"
        
        # Supporting evidence
        formatted_summary += "## Supporting Evidence & Methodology\n\n"
        if evidence:
            for evidence_item in evidence:
                formatted_summary += f"• {evidence_item}\n"
        else:
            formatted_summary += "Akoo could not identify specific evidence examples in this document.\n"
        formatted_summary += "\n"
        
        # Methodology section
        if methodology:
            formatted_summary += "### Methodology\n" + methodology + "\n\n"
        
        # Counterarguments & limitations
        if counterarguments:
            formatted_summary += "## Counterarguments & Limitations\n\n"
            for counter in counterarguments:
                formatted_summary += f"• {counter}\n"
            formatted_summary += "\n"
        
        # Connections and logical flow
        if connections:
            formatted_summary += "## Logical Connections\n\n"
            for connection in connections:
                formatted_summary += f"• {connection}\n"
            formatted_summary += "\n"
        
        # Conclusions section
        formatted_summary += "## Conclusions\n\n"
        if conclusions:
            for conclusion in conclusions:
                formatted_summary += f"{conclusion}\n"
        else:
            formatted_summary += "Akoo could not identify specific conclusions in this document.\n"
        formatted_summary += "\n"
        
        # APA Reference
        formatted_summary += "## Reference\n\n"
        if metadata['author'] != "Unknown" and metadata['date'] != "Unknown":
            year_match = re.search(r'\b(19|20)\d{2}\b', metadata['date'])
            year = year_match.group(0) if year_match else "n.d."
            
            formatted_summary += f"{metadata['author']}. ({year}). {metadata['title']}.\n"
        else:
            formatted_summary += f"Unknown. (n.d.). {metadata['title']}.\n"
        
        # Add Akoo signature
        formatted_summary += "\n\n---\n*Summary generated by Akoo PDF Summarization Bot*\n"
        
        # Cache the summary for future use
        cache_summary(text, params, formatted_summary)
        
        return formatted_summary
        
    except Exception as e:
        logger.error(f"Error generating academic excellence summary: {e}")
        # Fall back to simple summary if something goes wrong
        return simple_fallback_summary(text, num_sentences)

# Format summary based on type
def generate_summary(text, filename="", num_sentences=30, format_type="paragraph", summary_type="academic"):
    """Main entry point for summarization with fallbacks"""
    logger.info(f"Requested summary: {num_sentences} sentences, {format_type} format, {summary_type} type")
    
    # Try to get cached summary
    params = {
        "filename": filename,
        "num_sentences": num_sentences,
        "format_type": format_type,
        "summary_type": summary_type
    }
    
    cached = get_cached_summary(text, params)
    if cached:
        return cached, False  # Not using ML
    
    # Try ML-based summarization first if requested and available
    ml_succeeded = False
    if summary_type in ['academic', 'structured'] and os.environ.get('USE_ML', 'False').lower() in ('true', '1', 't'):
        try:
            from ml_summarizer import MLSummarizer
            summarizer = MLSummarizer()
            summary = summarizer.generate_summary(
                text=text,
                max_length=max(50, min(1000, num_sentences * 30)),  # Approximate token count
                min_length=max(30, min(500, num_sentences * 15)),
                outline_format=(summary_type == 'structured')
            )
            
            if summary:
                logger.info("ML-based summarization succeeded")
                ml_succeeded = True
                # Format summary
                if format_type != 'paragraph':
                    sentences = robust_sentence_tokenize(summary)
                    return format_summary(sentences[:num_sentences], format_type), True
                return summary, True  # Return summary and ML flag
        except Exception as e:
            logger.warning(f"ML summarization failed: {e}")
            logger.info("Using traditional summarization methods")
    
    # Use traditional methods if ML didn't work or wasn't requested
    if not ml_succeeded:
        if summary_type == 'academic':
            try:
                summary = academic_excellence_summary(text, filename, num_sentences)
                logger.info("Academic excellence summarization succeeded")
                
                # Format if needed
                if format_type != 'paragraph' and not summary.startswith('#'):
                    sentences = robust_sentence_tokenize(summary)
                    return format_summary(sentences, format_type), False
                    
                return summary, False  # Return summary and ML flag
            except Exception as e:
                logger.error(f"Error in academic summarization: {e}")
                # Fall back to simple summary
        
        # Try structured outline if requested
        if summary_type == 'structured':
            try:
                # Create a simplified structured outline
                sentences = robust_sentence_tokenize(text)
                sections = identify_document_sections(text)
                
                structured_summary = "# Document Summary\n\n"
                
                # Create introduction
                structured_summary += "## Introduction\n\n"
                if sentences and len(sentences) > 2:
                    intro_sentences = sentences[:min(3, len(sentences))]
                    structured_summary += " ".join(intro_sentences) + "\n\n"
                
                # Add each identified section
                for section_name, content in sections.items():
                    section_sentences = robust_sentence_tokenize(content)
                    if section_sentences:
                        structured_summary += f"## {section_name.title()}\n\n"
                        section_summary = section_sentences[:min(3, len(section_sentences))]
                        structured_summary += " ".join(section_summary) + "\n\n"
                
                # Add conclusion
                structured_summary += "## Conclusion\n\n"
                if sentences and len(sentences) > 5:
                    conclusion_sentences = sentences[-min(2, len(sentences)):]
                    structured_summary += " ".join(conclusion_sentences) + "\n\n"
                
                # Add signature
                structured_summary += "\n\n---\n*Summary generated by Akoo PDF Summarization Bot*\n"
                
                logger.info("Structured outline summarization succeeded")
                return structured_summary, False
            except Exception as e:
                logger.error(f"Error in structured summarization: {e}")
                # Fall back to basic extraction
        
        # Basic extraction as final fallback
        try:
            sentences = robust_sentence_tokenize(text)
            logger.info(f"Text split into {len(sentences)} sentences")
            
            if len(sentences) <= num_sentences:
                logger.info("Text has fewer sentences than requested summary length, returning full text")
                formatted_summary = format_summary(sentences, format_type)
                return formatted_summary, False
            
            summary_sentences = simple_fallback_summary(text, num_sentences)
            summary_sentences = robust_sentence_tokenize(summary_sentences)
            formatted_summary = format_summary(summary_sentences[:num_sentences], format_type)
            logger.info(f"Generated fallback summary of {len(formatted_summary)} characters")
            return formatted_summary, False
        except Exception as e:
            logger.error(f"Error in fallback summarization: {e}")
            error_msg = "Error generating summary. The document may be too complex or in an unsupported format."
            logger.error(error_msg)
            return error_msg, False

def calculate_optimal_summary_length(text, requested_length):
    """Calculate the optimal summary length based on document analysis"""
    try:
        # Import TextProcessor here to avoid circular imports
        from language_processor import TextProcessor
        processor = TextProcessor()
        
        analysis = processor.analyze_document_content(text)
        total_sentences = analysis["estimated_sentences"]
        
        # Don't summarize more than 40% of very short documents
        if total_sentences < 50:
            return min(requested_length, max(3, int(total_sentences * 0.4)))
        
        # For complex documents, ensure minimum meaningful length
        if analysis["complexity"] > 7:
            return max(requested_length, min(50, int(total_sentences * 0.15)))
        
        # For narrative texts, more summarization is usually better
        if analysis["type"] == "narrative":
            return min(requested_length, max(10, int(total_sentences * 0.1)))
        
        # For structured documents, make sure we capture enough sections
        if analysis["structure"] == "structured" and len(analysis["sections"]) > 3:
            min_section_sentences = 3 * len(analysis["sections"])
            return max(requested_length, min_section_sentences)
        
        # Default - return requested length
        return requested_length
    except Exception as e:
        logger.warning(f"Error calculating optimal summary length: {e}")
        return requested_length  # Default to requested length on error