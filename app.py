from flask import Flask, render_template, request, jsonify, make_response
import json
import random
import os
import string
import re
import logging
import time
import hashlib
import secrets
from werkzeug.utils import secure_filename
import threading
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from collections import deque
import uuid

# Import configuration
from config import Config
# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))

# Enable CORS for all routes
CORS(app)

# Add security headers
talisman = Talisman(app, content_security_policy=None, force_https=False)

# Add rate limiting to prevent abuse
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Create a dictionary to store job results
JOB_RESULTS = {}

# Store conversation contexts
CONVERSATION_CONTEXTS = {}

# Configure file uploads
UPLOAD_FOLDER = Config.UPLOAD_FOLDER
CACHE_FOLDER = Config.CACHE_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure required directories exist
for folder in [UPLOAD_FOLDER, CACHE_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)
        logger.info(f"Created directory: {folder}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

# Try to import ML-related libraries with error handling
try:
    from ml_summarizer import MLSummarizer
    HAVE_ML = True
    logger.info("Successfully imported ML summarization libraries")
except ImportError:
    HAVE_ML = False
    logger.warning("ML summarization libraries not found. ML-based summarization will not be available.")

# Initialize NLTK with error handling
try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    
    # Download necessary NLTK data
    nltk_data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data')
    os.makedirs(nltk_data_path, exist_ok=True)
    nltk.data.path.append(nltk_data_path)
    
    for resource, package_name in [
        ('tokenizers/punkt', 'punkt'),
        ('corpora/stopwords', 'stopwords'),
        ('corpora/wordnet', 'wordnet')
    ]:
        try:
            nltk.data.find(resource)
        except LookupError:
            logger.info(f"Downloading NLTK resource: {package_name}")
            nltk.download(package_name, download_dir=nltk_data_path)
            logger.info(f"Downloaded NLTK resource: {package_name}")
            
    # Initialize NLTK resources
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    HAS_NLTK = True
    logger.info("NLTK initialized successfully")
    
except (ImportError, LookupError) as e:
    logger.warning(f"NLTK initialization warning: {e}")
    logger.info("Falling back to basic text processing without NLTK")
    HAS_NLTK = False

# Import summarization functions
from summarization import (
    robust_sentence_tokenize, 
    simple_fallback_summary, 
    academic_excellence_summary,
    generate_summary,
    calculate_optimal_summary_length
)

# Import PDF processor
from pdf_processor import (
    better_pdf_extraction,
    extract_text_from_pdf,
    extract_with_pymupdf,
    extract_with_ocr,
    estimate_pdf_complexity,
    extract_text_with_best_method
)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load knowledge base from a JSON file
def load_knowledge_base(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                logger.info(f"Loading knowledge base from {file_path}")
                kb = json.load(file)
                
                # Ensure Akoo self-references in responses
                for intent in kb["intents"]:
                    for i, response in enumerate(intent["responses"]):
                        if "I'm" in response and "I'm Akoo" not in response:
                            intent["responses"][i] = response.replace("I'm", "I'm Akoo,")
                        elif not any(x in response.lower() for x in ["akoo", "i'm"]):
                            if response[0].isupper():
                                intent["responses"][i] = "Akoo " + response[0].lower() + response[1:]
                            else:
                                intent["responses"][i] = "Akoo " + response
                
                return kb
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            return get_default_knowledge_base()
    else:
        logger.info(f"Knowledge base file not found, using default")
        return get_default_knowledge_base()

# Default knowledge base
def get_default_knowledge_base():
    return {
        "intents": [
            {
                "tag": "greeting",
                "patterns": ["hello", "hi", "hey", "howdy", "greetings"],
                "responses": [
                    "Hello! I'm Akoo, your PDF summarization assistant. How can I help you today?",
                    "Hi there! I'm Akoo, and I specialize in summarizing PDFs and texts. What can I do for you?",
                    "Hey! I'm Akoo, your document summarization bot. Would you like to upload a PDF for me to analyze?"
                ]
            },
            {
                "tag": "goodbye",
                "patterns": ["bye", "goodbye", "see you", "later", "exit"],
                "responses": [
                    "Goodbye! Feel free to return when you need more document summaries. Have a great day!",
                    "See you later! Akoo will be here when you need help summarizing documents again.",
                    "Take care! Remember that Akoo is always available to help with your summarization needs."
                ]
            },
            {
                "tag": "thanks",
                "patterns": ["thanks", "thank you", "appreciate it", "helpful"],
                "responses": [
                    "You're welcome! If you need to summarize more documents, Akoo is here to help.",
                    "Happy to help! Upload another PDF or paste more text if you have other summarization needs.",
                    "Anytime! Akoo is here to make document summarization easier for you."
                ]
            },
            {
                "tag": "pdf_summary",
                "patterns": ["summarize pdf", "pdf summary", "summarize document", "summarize book", "create summary", 
                            "document summary", "extract key points", "condense pdf", "brief overview"],
                "responses": [
                    "Akoo would be happy to summarize a PDF for you. Please upload your document using the upload button, or you can paste the text if you already have it.",
                    "Sure, Akoo can summarize PDF documents. Upload your file or paste the text directly, and I'll extract the key points following academic excellence standards.",
                    "Akoo can create comprehensive summaries of PDF files using my Excellence Framework. Please upload your document to begin, or paste the text if you have it available."
                ]
            },
            {
                "tag": "text_summary", 
                "patterns": ["summarize text", "text summary", "analyze this text", "summarize this for me"],
                "responses": [
                    "Akoo would be happy to summarize your text. Please paste the content you'd like me to analyze, and I'll create a comprehensive summary following academic standards.",
                    "Akoo can summarize text content for you. Simply paste the text you want summarized, and I'll extract the key points and structure them according to academic excellence guidelines.",
                    "Sure, Akoo can analyze and summarize text for you. Paste your content, and I'll create a structured summary that preserves the original meaning and nuances."
                ]
            },
            {
                "tag": "about",
                "patterns": ["who are you", "what are you", "tell me about yourself"],
                "responses": [
                    "I'm Akoo, an AI assistant designed to help you summarize PDF documents and texts. Just upload a PDF or paste text, and I'll create a comprehensive summary following academic excellence standards. How may I help you today?",
                    "Hello! I'm Akoo, your PDF summarization assistant. I can analyze documents and provide structured summaries that capture the essence of the content. You can either upload a PDF or share text in the chat for me to summarize.",
                    "I'm Akoo, a specialized PDF summarization bot. I use advanced techniques to extract key information from documents and present it in a structured format. To get started, you can upload a PDF or share text that needs summarizing."
                ]
            },
            {
                "tag": "help",
                "patterns": ["help", "assist", "support", "what can you do"],
                "responses": [
                    "Akoo can help you summarize PDF documents and text content. Simply upload a PDF using the upload button or paste text directly into our chat. My summaries follow academic excellence standards to ensure quality and comprehensiveness.",
                    "Akoo specializes in creating high-quality summaries of PDFs and text. To use my services, either upload a document or paste text for me to analyze. My Excellence Framework ensures all summaries include key points, evidence, and proper context.",
                    "Akoo is here to assist with document summarization. You can upload PDFs or paste text, and I'll generate a structured summary that captures the main thesis, key arguments, evidence, and conclusions."
                ]
            },
            {
                "tag": "fallback",
                "patterns": [],
                "responses": [
                    "Akoo is specialized in PDF and text summarization. Could you upload a document or paste text for me to analyze? Or you can ask how to use my summarization features.",
                    "Akoo doesn't have an answer for that, but I'd be happy to help you summarize documents or texts. Would you like to upload a PDF or learn more about my summarization capabilities?",
                    "Akoo is focused on document summarization. Please upload a PDF or share text content if you'd like me to create a summary for you."
                ]
            }
        ]
    }

# Initialize knowledge base
knowledge_base = load_knowledge_base('knowledge_base.json')

# Find the most likely intent with context awareness
def find_intent(user_input, conversation_history=None):
    try:
        if not user_input or not user_input.strip():
            # Return fallback for empty input
            for intent in knowledge_base["intents"]:
                if intent["tag"] == "fallback":
                    return intent
        
        processed_input = user_input.lower()
        
        # Context-aware matching
        if conversation_history and len(conversation_history) > 1:
            last_context = conversation_history[-1].lower() if conversation_history[-1].startswith("Akoo:") else ""
            if "summarize" in last_context and "pdf" in processed_input:
                # User is likely continuing a conversation about PDF summarization
                for intent in knowledge_base["intents"]:
                    if intent["tag"] == "pdf_summary":
                        return intent
        
        highest_similarity = 0
        matched_intent = None
        
        # First check for exact matches
        for intent in knowledge_base["intents"]:
            if intent["tag"] == "fallback":
                continue
                
            for pattern in intent["patterns"]:
                if pattern.lower() in processed_input:
                    return intent
        
        # Then try word overlap similarity
        for intent in knowledge_base["intents"]:
            if intent["tag"] == "fallback":
                continue
                
            for pattern in intent["patterns"]:
                pattern_words = set(pattern.lower().split())
                input_words = set(processed_input.split())
                
                # Calculate Jaccard similarity
                if pattern_words and input_words:
                    intersection = pattern_words.intersection(input_words)
                    union = pattern_words.union(input_words)
                    similarity = len(intersection) / len(union)
                    
                    # Boost if there's a high word match percentage
                    if pattern_words and len(intersection) / len(pattern_words) > 0.7:
                        similarity *= 1.5
                    
                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        matched_intent = intent
        
        # Accept match if similarity exceeds threshold
        if matched_intent and highest_similarity > 0.3:
            return matched_intent
        
        # Check if it might be a text to summarize (longer text)
        if len(processed_input.split()) > 30:
            for intent in knowledge_base["intents"]:
                if intent["tag"] == "text_summary":
                    return intent
        
        # Default to fallback
        for intent in knowledge_base["intents"]:
            if intent["tag"] == "fallback":
                return intent
                
    except Exception as e:
        logger.error(f"Error in intent matching: {e}")
        # Return fallback intent on error
        for intent in knowledge_base["intents"]:
            if intent["tag"] == "fallback":
                return intent

# Function to get a contextually relevant response
def get_contextual_response(user_input, conversation_history=None):
    # Create session ID if not existing
    session_id = request.cookies.get('session_id', str(uuid.uuid4()))
    
    # Initialize context if needed
    if session_id not in CONVERSATION_CONTEXTS:
        CONVERSATION_CONTEXTS[session_id] = deque(maxlen=5)
    
    # Find intent considering conversation history
    intent = find_intent(user_input, CONVERSATION_CONTEXTS.get(session_id, []))
    
    if intent:
        # If the input looks like text to summarize (longer)
        if intent["tag"] == "text_summary" and len(user_input.split()) > 50:
            # Try to generate a summary
            try:
                summary = academic_excellence_summary(user_input, "Chat Text", 30)
                response = "Akoo has analyzed your text. Here's the summary:\n\n" + summary
                
                # Add to conversation context
                if session_id in CONVERSATION_CONTEXTS:
                    CONVERSATION_CONTEXTS[session_id].append(f"User: {user_input}")
                    CONVERSATION_CONTEXTS[session_id].append(f"Akoo: [Text Summary Generated]")
                
                return response
            except Exception as e:
                logger.error(f"Error summarizing text input: {e}")
                response = "Akoo had trouble summarizing that text. Could you try again or perhaps upload it as a PDF?"
                
                # Add to conversation context
                if session_id in CONVERSATION_CONTEXTS:
                    CONVERSATION_CONTEXTS[session_id].append(f"User: {user_input}")
                    CONVERSATION_CONTEXTS[session_id].append(f"Akoo: {response}")
                
                return response
        else:
            # Regular response from intent
            response = random.choice(intent["responses"])
            
            # Add to conversation context
            if session_id in CONVERSATION_CONTEXTS:
                CONVERSATION_CONTEXTS[session_id].append(f"User: {user_input}")
                CONVERSATION_CONTEXTS[session_id].append(f"Akoo: {response}")
            
            return response
    else:
        # Fallback response if somehow no intent is found
        fallback = "Akoo is specialized in PDF summarization. Would you like to upload a document for me to analyze?"
        
        # Add to conversation context
        if session_id in CONVERSATION_CONTEXTS:
            CONVERSATION_CONTEXTS[session_id].append(f"User: {user_input}")
            CONVERSATION_CONTEXTS[session_id].append(f"Akoo: {fallback}")
        
        return fallback

# Function to get a response
def get_response(user_input):
    return get_contextual_response(user_input)

# More secure file saving
def secure_save_file(file):
    # Generate a secure random filename
    original_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    secure_filename_value = f"{secrets.token_hex(16)}.{original_ext}"
    path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename_value)
    
    # Check file type with additional verification
    try:
        file_content = file.read(1024)  # Read first 1024 bytes
        file.seek(0)  # Reset file pointer
        
        # Check PDF signature
        if not file_content.startswith(b'%PDF-'):
            return None, "Invalid PDF file - signature verification failed"
    except:
        return None, "Error reading file"
    
    # Save the file
    try:
        file.save(path)
        return path, None
    except Exception as e:
        return None, f"Error saving file: {str(e)}"

# Process PDF asynchronously
def process_pdf_async(file_path, params, callback, job_id=None):
    try:
        logger.info(f"Starting asynchronous processing of {file_path}")
        
        # Update job status if we have a job ID
        if job_id:
            JOB_RESULTS[job_id] = {
                "status": "processing",
                "progress": 20,
                "message": "Extracting text from PDF..."
            }
        
        # Extract text from PDF using better extraction
        text, error = better_pdf_extraction(file_path)
        
        if not text:
            error_msg = error if error else "Failed to extract meaningful text from PDF"
            logger.error(f"All extraction methods failed: {error_msg}")
            
            if job_id:
                JOB_RESULTS[job_id] = {
                    "status": "error",
                    "progress": 100,
                    "message": error_msg
                }
                
            callback({"error": error_msg})
            return
        
        # Update job status
        if job_id:
            JOB_RESULTS[job_id] = {
                "status": "processing",
                "progress": 50,
                "message": "Generating summary..."
            }
        
        # Get parameters from request
        summary_length = params.get('summary_length', 30)
        summary_format = params.get('summary_format', 'paragraph')
        summary_type = params.get('summary_type', 'academic')
        
        # Calculate optimal summary length
        try:
            optimal_length = calculate_optimal_summary_length(text, summary_length)
            if optimal_length != summary_length:
                logger.info(f"Adjusted summary length from {summary_length} to {optimal_length} based on content")
                summary_length = optimal_length
        except Exception as e:
            logger.warning(f"Error calculating optimal length: {e}")
        
        # Try to use ML for large documents if available
        use_ml = False
        if HAVE_ML and len(text) > 10000 and summary_type in ['academic', 'structured']:
            use_ml = True
            
        # Generate summary
        try:
            if use_ml:
                logger.info("Using ML-based summarization")
                # Try to import and use the ML summarizer
                from ml_summarizer import MLSummarizer
                summarizer = MLSummarizer()
                try:
                    summary_text = summarizer.generate_summary(
                        text=text,
                        max_length=max(75, min(1000, summary_length * 30)),
                        min_length=max(50, min(500, summary_length * 15)),
                        outline_format=(summary_type == 'structured')
                    )
                    
                    if summary_text:
                        # Calculate sentence count
                        sentence_count = len(robust_sentence_tokenize(summary_text))
                        
                        if job_id:
                            JOB_RESULTS[job_id] = {
                                "status": "completed",
                                "progress": 100,
                                "message": "Summary generated successfully with AI!",
                                "result": {
                                    "summary": summary_text,
                                    "sentence_count": sentence_count,
                                    "format": summary_format,
                                    "type": "academic",
                                    "used_ml": True
                                }
                            }
                        
                        callback({
                            "summary": summary_text,
                            "sentence_count": sentence_count,
                            "format": summary_format,
                            "type": "academic",
                            "used_ml": True
                        })
                        return
                except Exception as ml_error:
                    logger.error(f"ML summarization failed, falling back to traditional methods: {ml_error}")
            
            # Use traditional summarization methods
            logger.info("Using traditional summarization methods")
            summary, used_ml = generate_summary(
                text=text,
                filename=os.path.basename(file_path),
                num_sentences=summary_length,
                format_type=summary_format,
                summary_type=summary_type
            )
            
            # Calculate sentence count
            sentence_count = len(robust_sentence_tokenize(summary))
            
            # Create result object
            result = {
                "summary": summary,
                "sentence_count": sentence_count,
                "format": summary_format,
                "type": summary_type,
                "used_ml": used_ml
            }
            
            # Store in job results
            if job_id:
                JOB_RESULTS[job_id] = {
                    "status": "completed",
                    "progress": 100,
                    "message": "Summary generated successfully!",
                    "result": result
                }
            
            # Return via callback
            callback(result)
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            
            # Try fallback method
            try:
                summary = simple_fallback_summary(text, summary_length)
                
                # Calculate sentence count
                sentence_count = len(robust_sentence_tokenize(summary))
                
                # Create result object
                result = {
                    "summary": summary,
                    "sentence_count": sentence_count,
                    "format": summary_format,
                    "type": "basic",
                    "used_ml": False
                }
                
                if job_id:
                    JOB_RESULTS[job_id] = {
                        "status": "completed",
                        "progress": 100,
                        "message": "Summary generated successfully (using fallback method).",
                        "result": result
                    }
                    
                callback(result)
            except Exception as fallback_error:
                logger.error(f"Fallback summarization also failed: {fallback_error}")
                
                if job_id:
                    JOB_RESULTS[job_id] = {
                        "status": "error",
                        "progress": 100,
                        "message": f"Error generating summary: {str(e)}"
                    }
                    
                callback({"error": f"Error generating summary: {str(e)}"})
            
    except Exception as e:
        logger.error(f"Unexpected error in async processing: {e}")
        
        if job_id:
            JOB_RESULTS[job_id] = {
                "status": "error",
                "progress": 100,
                "message": f"Unexpected error: {str(e)}"
            }
            
        callback({"error": f"Unexpected error: {str(e)}"})

# Routes
@app.route("/")

def home():
    response = make_response(render_template("chat.html"))
    
    # Set session ID cookie if not already set
    if not request.cookies.get('session_id'):
        session_id = str(uuid.uuid4())
        response.set_cookie('session_id', session_id, max_age=86400*30)  # 30 days
        CONVERSATION_CONTEXTS[session_id] = deque(maxlen=5)
    
    return response

@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    session_id = request.cookies.get('session_id', str(uuid.uuid4()))
    
    # Check if we should use LLM for this query
    if llm_service and should_use_llm(user_text):
        logger.info(f"Processing query with LLM: {user_text}")
        llm_response = llm_service.generate_response(user_text)
        if llm_response.get("success", False):
            response = llm_response["content"]
        else:
            # Fallback to normal chatbot if LLM fails
            logger.warning(f"LLM processing failed, falling back to standard response")
            response = get_contextual_response(user_text, CONVERSATION_CONTEXTS.get(session_id, []))
    else:
        # Use standard chatbot logic
        response = get_contextual_response(user_text, CONVERSATION_CONTEXTS.get(session_id, []))
    
    # Create response with cookie
    http_response = make_response(response)
    
    # Set session ID cookie if not already set
    if not request.cookies.get('session_id'):
        http_response.set_cookie('session_id', session_id, max_age=86400*30)  # 30 days
    
    return http_response

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get('input')
        if not user_input:
            return jsonify({'error': 'No input provided'}), 400
            
        # Record the interaction in conversation history
        session_id = request.cookies.get('session_id', str(uuid.uuid4()))
        if session_id in CONVERSATION_CONTEXTS:
            CONVERSATION_CONTEXTS[session_id].append(f"User: {user_input}")
            
        # Check if we have LLM service available
        if llm_service and llm_service.is_available():
            # Call the LLM service to generate the model response
            response_obj = llm_service.generate_response(user_input)
            
            # Record the response
            if session_id in CONVERSATION_CONTEXTS:
                CONVERSATION_CONTEXTS[session_id].append(f"Akoo: {response_obj['content']}")
                
            return jsonify({'response': response_obj['content']})
        else:
            # Fallback if LLM is not available
            response = get_contextual_response(user_input, CONVERSATION_CONTEXTS.get(session_id, []))
            
            return jsonify({'response': response})
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': 'An unexpected error occurred',
            'response': "I'm sorry, I encountered an error processing your request. I'm specialized in PDF summarization, so perhaps I can help you with a document instead?"
        }), 500

@app.route('/check-llm')
def check_llm():
    """Check if LLM service is available and return status"""
    if llm_service and llm_service.is_available():
        return jsonify({
            'available': True,
            'model': llm_service.model_name
        })
    else:
        return jsonify({
            'available': False
        })

@app.route("/upload", methods=["POST"])
@limiter.limit("10 per minute")
def upload_file():
    try:
        logger.info("Received file upload request")
        
        if 'file' not in request.files:
            logger.warning("No file part in the request")
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logger.warning("No file selected")
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            logger.info(f"Processing file: {file.filename}")
            
            # Secure file saving
            temp_path, error = secure_save_file(file)
            if error:
                logger.error(f"Error saving file: {error}")
                return jsonify({"error": error}), 400
            
            # When processing large documents, add progress check points
            progress_data = {"status": "processing", "progress": 10, "message": "Starting document extraction..."}
            logger.info(f"Processing progress: {progress_data}")
            
            # Get parameters for summary generation
            summary_length = int(request.form.get('summary_length', 30))
            summary_format = request.form.get('summary_format', 'paragraph')
            summary_type = request.form.get('summary_type', 'academic')
            
            # Cap the summary length to 1000 sentences
            if summary_length > 1000:
                summary_length = 1000
                logger.info(f"Capped summary length to {summary_length}")
            
            params = {
                'summary_length': summary_length,
                'summary_format': summary_format,
                'summary_type': summary_type,
            }
            
            logger.info(f"Requested summary: {summary_length} sentences, {summary_format} format, {summary_type} type, ML: {HAVE_ML}")
            
            # Define callback for async processing
            def process_complete(result):
                try:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        logger.debug(f"Removed temporary file: {temp_path}")
                except Exception as e:
                    logger.warning(f"Could not remove temp file {temp_path}: {e}")
            
            # Generate a job ID
            job_id = hashlib.md5(f"{file.filename}_{time.time()}".encode()).hexdigest()
            
            # Start processing in a separate thread
            thread = threading.Thread(
                target=process_pdf_async,
                args=(temp_path, params, process_complete, job_id)
            )
            thread.daemon = True
            thread.start()
            
            # Immediately return a response with progress info
            return jsonify({
                "status": "processing",
                "progress": 30,
                "message": "Document extracted, analyzing content...",
                "job_id": job_id
            })
            
        else:
            logger.warning(f"Invalid file format: {file.filename}")
            return jsonify({"error": f"Invalid file format. Please upload a PDF."}), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in upload route: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route("/status/<job_id>", methods=["GET"])
def check_status(job_id):
    """Check the status of an async job"""
    if job_id in JOB_RESULTS:
        return jsonify(JOB_RESULTS[job_id])
    else:
        return jsonify({
            "status": "processing",
            "progress": 50,
            "message": "Still processing your document..."
        })

# Handle text summarization requests
@app.route("/summarize-text", methods=["POST"])
@limiter.limit("20 per minute")
def summarize_text():
    try:
        data = request.json
        text = data.get("text")
        
        if not text or len(text.split()) < 50:
            return jsonify({"error": "Please provide a longer text for summarization"}), 400
        
        summary_length = data.get("length", 30)
        if summary_length > 1000:
            summary_length = 1000
            
        summary, used_ml = generate_summary(
            text=text,
            filename="Chat Text", 
            num_sentences=summary_length,
            format_type="paragraph",
            summary_type="academic"
        )
        
        # Calculate sentence count
        sentence_count = len(robust_sentence_tokenize(summary))
        
        return jsonify({
            "summary": summary,
            "sentence_count": sentence_count,
            "format": "paragraph",
            "type": "academic",
            "used_ml": used_ml
        })
        
    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        return jsonify({"error": f"Error generating summary: {str(e)}"}), 500

# Route to get all possible commands (for help functionality)
@app.route("/commands")
def get_commands():
    commands = []
    for intent in knowledge_base["intents"]:
        if intent["tag"] != "fallback" and intent["patterns"]:
            example = random.choice(intent["patterns"])
            commands.append({
                "tag": intent["tag"],
                "example": example
            })
    return json.dumps(commands)

# Feedback route to collect user feedback on summaries
@app.route("/feedback", methods=["POST"])
@limiter.limit("10 per minute")  # Add rate limiting to prevent abuse
def collect_feedback():
    try:
        data = request.json
        
        # Validate rating
        rating = data.get("rating")
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
        
        # Validate feedback text
        feedback_text = data.get("feedback", "").strip()
        if len(feedback_text) > 1000:
            return jsonify({"error": "Feedback text is too long (max 1000 characters)"}), 400
        
        # Validate file ID
        file_id = data.get("file_id", "unknown").strip()
        if not re.match(r"^[a-zA-Z0-9_\-]+$", file_id):
            return jsonify({"error": "Invalid file ID format"}), 400
        
        # Create feedback directory if it doesn't exist
        feedback_dir = "feedback"
        if not os.path.exists(feedback_dir):
            os.makedirs(feedback_dir, exist_ok=True)
        
        # Save feedback to a file with restricted permissions
        feedback_file = os.path.join(feedback_dir, f"feedback_{time.strftime('%Y%m%d_%H%M%S')}_{file_id}.json")
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump({
                "rating": rating,
                "feedback": feedback_text,
                "file_id": file_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved user feedback: {rating} for file {file_id}")
        
        return jsonify({"success": True, "message": "Thank you for your feedback!"})
    except Exception as e:
        logger.error(f"Error saving feedback: {e}", exc_info=True)  # Log stack trace
        return jsonify({"error": "Error processing feedback"}), 500

if __name__ == "__main__":
    logger.info("Starting Akoo PDF Summarization Chatbot")
    app.run(host='0.0.0.0', debug=Config.DEBUG, port=80)