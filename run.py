import os
import sys
import logging
import nltk
from config import Config
from app import app

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Setup application directories
Config.setup()

# Set NLTK_DATA environment variable
os.environ['NLTK_DATA'] = Config.NLTK_DATA_PATH

# Ensure NLTK resources are available
def ensure_nltk_resources():
    """Download necessary NLTK resources if they're not already available"""
    try:
        # Create NLTK data directory if it doesn't exist
        nltk_data_path = Config.NLTK_DATA_PATH
        os.makedirs(nltk_data_path, exist_ok=True)
        
        # Add our custom path to NLTK's search paths
        nltk.data.path.append(nltk_data_path)
        
        # Resources we need
        resources = [
            ('tokenizers/punkt', 'punkt'),
            ('corpora/stopwords', 'stopwords'),
            ('corpora/wordnet', 'wordnet')
        ]
        
        # Check and download each resource
        for resource_path, resource_name in resources:
            try:
                nltk.data.find(resource_path)
                logger.info(f"Downloaded NLTK resource: {resource_name}")
            except LookupError:
                logger.info(f"Downloading NLTK resource: {resource_name}")
                nltk.download(resource_name, download_dir=nltk_data_path)
                logger.info(f"Downloaded NLTK resource: {resource_name}")
        
        return True
    except Exception as e:
        logger.error(f"Error ensuring NLTK resources: {e}")
        return False

# Initialize ML summarizer if enabled
def initialize_ml_summarizer():
    """Initialize the ML-based summarizer if enabled in config"""
    if Config.USE_ML:
        try:
            from ml_summarizer import MLSummarizer
            summarizer = MLSummarizer(
                model_name=Config.ML_MODEL,
                cache_dir=Config.MODEL_CACHE_DIR
            )
            logger.info(f"Successfully imported ML summarization libraries")
            return summarizer
        except ImportError as e:
            logger.warning(f"ML summarizer libraries not available: {e}")
            logger.info("Will use traditional summarization methods")
            return None
        except Exception as e:
            logger.error(f"Error initializing ML summarizer: {e}")
            return None
    else:
        logger.info("ML summarization disabled by configuration")
        return None

# Initialize application components
def initialize_app():
    """Initialize all required resources for the application"""
    # Ensure directories exist
    for directory in [Config.UPLOAD_FOLDER, Config.CACHE_FOLDER, Config.MODEL_CACHE_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
    
    # Ensure NLTK resources
    nltk_available = ensure_nltk_resources()
    if nltk_available:
        logger.info("NLTK initialized successfully")
    
    # Initialize ML summarizer if enabled
    ml_summarizer = initialize_ml_summarizer()
    
    # Set global variables or attach to app context if needed
    if hasattr(app, 'config'):
        app.config['NLTK_AVAILABLE'] = nltk_available
        app.config['ML_SUMMARIZER'] = ml_summarizer
    
    # Load knowledge base or other resources
    try:
        from summarization import load_knowledge_base
        knowledge_base = load_knowledge_base('knowledge_base.json')
        logger.info("Loading knowledge base from knowledge_base.json")
        
        if hasattr(app, 'config'):
            app.config['KNOWLEDGE_BASE'] = knowledge_base
    except Exception as e:
        logger.warning(f"Error loading knowledge base: {e}")
    
    logger.info("Starting Akoo PDF Summarization Chatbot")
    return {
        "nltk_available": nltk_available,
        "ml_summarizer": ml_summarizer
    }

if __name__ == "__main__":
    # Initialize the application
    init_status = initialize_app()
    
    # Start the web server
    app.run(host='0.0.0.0', debug=Config.DEBUG, port=5000)