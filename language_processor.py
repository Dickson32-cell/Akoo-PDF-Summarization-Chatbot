import re
import logging
from typing import List, Dict, Set, Optional
from collections import Counter
import math
import os

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
            logger.info(f"Downloaded NLTK resource: {package}")
        except LookupError:
            logger.info(f"Downloading NLTK resource: {package}")
            nltk.download(package, download_dir=NLTK_DATA_PATH, quiet=True)
    
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer, PorterStemmer
    
    # Initialize NLTK resources
    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))
    
    HAS_NLTK = True
    logger.info("NLTK initialized successfully")
except Exception as e:
    HAS_NLTK = False
    logger.warning(f"NLTK import failed: {e}")
    logger.info("Using fallback text processing without NLTK")

# Try to import spaCy with fallback
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.warning("spaCy model not found, downloading...")
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    
    HAS_SPACY = True
    logger.info("spaCy initialized successfully")
except ImportError:
    HAS_SPACY = False
    logger.warning("spaCy not available, using fallback for advanced NLP tasks")

class TextProcessor:
    def __init__(self):
        self.stop_words = set()
        
        # Set up stop words from either NLTK or fallback
        if HAS_NLTK:
            self.stop_words = set(stopwords.words('english'))
        else:
            # Basic stop words if NLTK is not available
            self.stop_words = {
                'a', 'an', 'the', 'and', 'or', 'but', 'if', 'because', 'as', 
                'what', 'which', 'this', 'that', 'these', 'those', 'then', 'just', 
                'so', 'than', 'such', 'both', 'through', 'about', 'for', 'is', 'of', 
                'while', 'during', 'to', 'from', 'in', 'on', 'at', 'by', 'with'
            }
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """Tokenize text into sentences with fallbacks"""
        if not text:
            return []
            
        # First try with NLTK
        if HAS_NLTK:
            try:
                return sent_tokenize(text)
            except Exception as e:
                logger.warning(f"NLTK sentence tokenization failed: {e}")
        
        # Then try with spaCy
        if HAS_SPACY:
            try:
                doc = nlp(text)
                return [sent.text for sent in doc.sents]
            except Exception as e:
                logger.warning(f"spaCy sentence tokenization failed: {e}")
        
        # Fallback to regex-based splitting
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        if not sentences:
            # If still no sentences, try simpler split
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def tokenize_words(self, text: str) -> List[str]:
        """Tokenize text into words with fallbacks"""
        if not text:
            return []
            
        # First try with NLTK
        if HAS_NLTK:
            try:
                return word_tokenize(text.lower())
            except Exception as e:
                logger.warning(f"NLTK word tokenization failed: {e}")
        
        # Then try with spaCy
        if HAS_SPACY:
            try:
                doc = nlp(text.lower())
                return [token.text for token in doc]
            except Exception as e:
                logger.warning(f"spaCy word tokenization failed: {e}")
        
        # Fallback to regex-based word tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def lemmatize(self, words: List[str]) -> List[str]:
        """Lemmatize words with fallbacks"""
        if not words:
            return []
            
        if HAS_NLTK:
            try:
                return [lemmatizer.lemmatize(word) for word in words]
            except Exception as e:
                logger.warning(f"NLTK lemmatization failed: {e}")
        
        if HAS_SPACY:
            try:
                doc = nlp(" ".join(words))
                return [token.lemma_ for token in doc]
            except Exception as e:
                logger.warning(f"spaCy lemmatization failed: {e}")
        
        # Fallback - just return original words
        return words
    
    def stem(self, words: List[str]) -> List[str]:
        """Stem words with fallbacks"""
        if not words:
            return []
            
        if HAS_NLTK:
            try:
                return [stemmer.stem(word) for word in words]
            except Exception as e:
                logger.warning(f"NLTK stemming failed: {e}")
        
        # Fallback - just return original words
        return words
    
    def remove_stopwords(self, words: List[str]) -> List[str]:
        """Remove stopwords from a list of words"""
        return [word for word in words if word not in self.stop_words]
    
    def preprocess_text(self, text: str, remove_stops: bool = True, lemmatize: bool = True) -> List[str]:
        """Full preprocessing pipeline with fallbacks"""
        if not text:
            return []
            
        # Convert to lowercase and tokenize
        words = self.tokenize_words(text)
        
        # Remove stopwords if requested
        if remove_stops:
            words = self.remove_stopwords(words)
        
        # Lemmatize if requested
        if lemmatize:
            words = self.lemmatize(words)
        
        return words
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Dict]:
        """Extract most important keywords using TF-IDF"""
        sentences = self.tokenize_sentences(text)
        all_words = self.preprocess_text(text)
        word_freq = Counter(all_words)
        
        # Calculate TF-IDF scores for each word
        word_scores = {}
        num_docs = len(sentences)
        
        for word, freq in word_freq.items():
            # Skip very short words
            if len(word) < 3:
                continue
                
            # Calculate term frequency
            tf = freq / max(1, len(all_words))
            
            # Calculate document frequency (in how many sentences this word appears)
            doc_count = sum(1 for sentence in sentences if word in self.preprocess_text(sentence))
            
            # Calculate IDF
            idf = math.log(num_docs / max(1, doc_count))
            
            # Calculate TF-IDF score
            word_scores[word] = tf * idf
        
        # Get top N keywords
        top_keywords = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # Format results
        result = [{"keyword": word, "score": score} for word, score in top_keywords]
        return result
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities with fallbacks"""
        if not text:
            return {}
            
        entities = {
            "people": [],
            "organizations": [],
            "locations": [],
            "dates": []
        }
        
        # Try spaCy first for best entity recognition
        if HAS_SPACY:
            try:
                doc = nlp(text)
                
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        entities["people"].append(ent.text)
                    elif ent.label_ == "ORG":
                        entities["organizations"].append(ent.text)
                    elif ent.label_ == "GPE" or ent.label_ == "LOC":
                        entities["locations"].append(ent.text)
                    elif ent.label_ == "DATE":
                        entities["dates"].append(ent.text)
                
                # Remove duplicates
                for key in entities:
                    entities[key] = list(set(entities[key]))
                
                return entities
            except Exception as e:
                logger.warning(f"spaCy entity extraction failed: {e}")
        
        # Fallback to simpler regex patterns
        # People pattern (capitalized names)
        people_pattern = r'(?:[A-Z][a-z]+ ){1,2}[A-Z][a-z]+'
        entities["people"] = list(set(re.findall(people_pattern, text)))
        
        # Organization pattern (all caps words or capitalized words followed by Inc, Corp, etc.)
        org_pattern = r'(?:[A-Z][A-Za-z]+ )+(?:Inc|Corp|LLC|Ltd|Limited|Association|Organization)'
        entities["organizations"] = list(set(re.findall(org_pattern, text)))
        
        # Location pattern (simple)
        loc_pattern = r'(?:in|at|from|to) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)'
        loc_matches = re.findall(loc_pattern, text)
        entities["locations"] = list(set(loc_matches))
        
        # Date pattern
        date_pattern = r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b'
        entities["dates"] = list(set(re.findall(date_pattern, text)))
        
        return entities
    
    def get_document_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        if not text1 or not text2:
            return 0.0
            
        # Process both texts
        words1 = self.preprocess_text(text1)
        words2 = self.preprocess_text(text2)
        
        # Create word frequency dictionaries
        freq1 = Counter(words1)
        freq2 = Counter(words2)
        
        # Get all unique words
        all_words = set(freq1.keys()) | set(freq2.keys())
        
        # Calculate dot product
        dot_product = sum(freq1.get(word, 0) * freq2.get(word, 0) for word in all_words)
        
        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(freq1.get(word, 0) ** 2 for word in all_words))
        magnitude2 = math.sqrt(sum(freq2.get(word, 0) ** 2 for word in all_words))
        
        # Calculate cosine similarity
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        else:
            return dot_product / (magnitude1 * magnitude2)

    def analyze_document_content(self, text):
        """Analyze document to determine type and structure for better summarization"""
        analysis = {
            "type": "general",
            "structure": "unknown",
            "sections": {},
            "complexity": 0,
            "estimated_sentences": 0
        }
        
        # Estimate document length
        sentences = self.tokenize_sentences(text)
        analysis["estimated_sentences"] = len(sentences)
        
        # Check for academic patterns
        academic_indicators = ["abstract", "introduction", "methodology", "results", "discussion", "conclusion", "references"]
        academic_score = sum(1 for indicator in academic_indicators if indicator.lower() in text.lower())
        if academic_score >= 3:
            analysis["type"] = "academic"
        
        # Check for report patterns
        report_indicators = ["executive summary", "findings", "recommendations", "appendix"]
        report_score = sum(1 for indicator in report_indicators if indicator.lower() in text.lower())
        if report_score >= 2 and academic_score < 3:
            analysis["type"] = "report"
        
        # Check for narrative/story
        if "chapter" in text.lower() and len(re.findall(r'\b(said|thought|felt)\b', text.lower())) > 10:
            analysis["type"] = "narrative"
        
        # Estimate text complexity using sentence length and vocabulary
        words = text.lower().split()
        unique_words = len(set(words))
        avg_sentence_length = len(words) / max(1, len(sentences))
        analysis["complexity"] = min(10, (unique_words / max(1, len(words)) * 5) + (avg_sentence_length / 20 * 5))
        
        # Try to identify document sections
        section_patterns = {
            "abstract": r'abstract[\s\n]*(?:[:\.\-]|\n|$)(.*?)(?=\n\s*[A-Z][^\n]+[\s\n]*(?:[:\.\-]|\n|$)|\Z)',
            "introduction": r'introduction[\s\n]*(?:[:\.\-]|\n|$)(.*?)(?=\n\s*[A-Z][^\n]+[\s\n]*(?:[:\.\-]|\n|$)|\Z)',
            "methodology": r'method(?:s|ology)[\s\n]*(?:[:\.\-]|\n|$)(.*?)(?=\n\s*[A-Z][^\n]+[\s\n]*(?:[:\.\-]|\n|$)|\Z)',
            "results": r'results?[\s\n]*(?:[:\.\-]|\n|$)(.*?)(?=\n\s*[A-Z][^\n]+[\s\n]*(?:[:\.\-]|\n|$)|\Z)',
            "discussion": r'discussion[\s\n]*(?:[:\.\-]|\n|$)(.*?)(?=\n\s*[A-Z][^\n]+[\s\n]*(?:[:\.\-]|\n|$)|\Z)',
            "conclusion": r'conclusion[\s\n]*(?:[:\.\-]|\n|$)(.*?)(?=\n\s*[A-Z][^\n]+[\s\n]*(?:[:\.\-]|\n|$)|\Z)'
        }
        
        for section, pattern in section_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                section_text = match.group(1).strip()
                if len(section_text) > 50:  # Only include substantial sections
                    analysis["sections"][section] = section_text
        
        # Determine document structure based on identified sections
        if len(analysis["sections"]) >= 3:
            analysis["structure"] = "structured"
        else:
            analysis["structure"] = "freeform"
        
        return analysis

    def calculate_optimal_summary_length(self, text, requested_length):
        """Calculate the optimal summary length based on document analysis"""
        analysis = self.analyze_document_content(text)
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