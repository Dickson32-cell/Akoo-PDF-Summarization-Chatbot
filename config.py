import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration settings for the application"""
    
    # Flask settings
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')
    SECRET_KEY = os.getenv('SECRET_KEY', 'akoo-pdf-summarizer-2025-secure-key')
    
    # File upload settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    CACHE_FOLDER = os.getenv('CACHE_FOLDER', 'cache')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 64 * 1024 * 1024))  # 64MB by default
    
    # ML settings
    USE_ML = os.getenv('USE_ML', 'True').lower() in ('true', '1', 't')
    ML_MODEL = os.getenv('ML_MODEL', 'sshleifer/distilbart-cnn-12-6')
    MODEL_CACHE_DIR = os.getenv('MODEL_CACHE_DIR', 'model_cache')
    
    # Processing settings
    DEFAULT_SUMMARY_LENGTH = int(os.getenv('DEFAULT_SUMMARY_LENGTH', 30))
    MAX_SUMMARY_LENGTH = int(os.getenv('MAX_SUMMARY_LENGTH', 1000))
    
    # NLTK data path
    NLTK_DATA_PATH = os.getenv('NLTK_DATA_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nltk_data'))
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'akoo.log')
    
    # LLM settings
    LLM_ENABLED = os.getenv('LLM_ENABLED', 'True').lower() in ('true', '1', 't')
    LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME', 'tinyllama')
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', 500))
    
    # Google Search API settings
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GOOGLE_SEARCH_ENGINE_ID = os.getenv('GOOGLE_SEARCH_ENGINE_ID', '')
    USE_SEARCH_FOR_GENERAL_KNOWLEDGE = os.getenv('USE_SEARCH_FOR_GENERAL_KNOWLEDGE', 'True').lower() in ('true', '1', 't')
    
    # Create necessary directories
    @classmethod
    def setup(cls):
        """Create necessary directories for the application"""
        directories = [cls.UPLOAD_FOLDER, cls.CACHE_FOLDER, cls.MODEL_CACHE_DIR, cls.NLTK_DATA_PATH]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
        
        # Create empty .env file if it doesn't exist
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
        if not os.path.exists(env_file):
            with open(env_file, 'w') as f:
                f.write("""# Akoo PDF Summarization Bot Configuration
# Uncomment and modify settings as needed

# Flask settings
# DEBUG=True
# SECRET_KEY=your-secret-key-here

# File upload settings
# UPLOAD_FOLDER=uploads
# CACHE_FOLDER=cache
# MAX_CONTENT_LENGTH=67108864

# ML settings
# USE_ML=True
# ML_MODEL=sshleifer/distilbart-cnn-12-6
# MODEL_CACHE_DIR=model_cache

# Processing settings
# DEFAULT_SUMMARY_LENGTH=30
# MAX_SUMMARY_LENGTH=1000

# NLTK data path
# NLTK_DATA_PATH=nltk_data

# Logging settings
# LOG_LEVEL=INFO
# LOG_FILE=akoo.log

# LLM settings
# LLM_ENABLED=True
# LLM_MODEL_NAME=tinyllama
# LLM_MAX_TOKENS=500

# Google Search API settings
# GOOGLE_API_KEY=your-google-api-key-here
# GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id-here
# USE_SEARCH_FOR_GENERAL_KNOWLEDGE=True
""")