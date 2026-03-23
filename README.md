# Akoo - PDF Summarization Chatbot

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-brightgreen)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

**Akoo** is an AI-powered chatbot designed to summarize PDF documents and text content. It uses advanced techniques, including machine learning and natural language processing, to generate structured summaries that follow academic excellence standards.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Akoo System                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│   │   Browser   │    │  Mobile    │    │    API      │     │
│   │  (Web UI)   │    │   App      │    │  Clients    │     │
│   └──────┬──────┘    └──────┬─────┘    └──────┬─────┘     │
│          │                   │                  │            │
│          └───────────────────┼──────────────────┘            │
│                              │                                 │
│                      ┌───────▼───────┐                        │
│                      │  Flask API    │                        │
│                      │  (Gunicorn)   │                        │
│                      └───────┬───────┘                        │
│                              │                                 │
│    ┌─────────────────────────┼─────────────────────────┐      │
│    │                         │                         │      │
│    ▼                         ▼                         ▼      │
│ ┌──────────┐          ┌───────────┐          ┌──────────┐  │
│ │   PDF    │          │   NLP     │          │    LLM   │  │
│ │ Processor│          │  (NLTK)   │          │ (Optional│  │
│ │ (PyMuPDF)│          │           │          │ TinyLlama│  │
│ └──────────┘          └───────────┘          └──────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## ✨ Features

### Core Features
- **PDF Summarization** - Upload PDF files for intelligent summarization
- **Text Summarization** - Paste text content for structured summaries
- **Chat Interface** - Conversational AI assistant named "Akoo"
- **Customizable Output** - Choose summary length and format (paragraph, bullet points)

### Analysis Tools
- **Knowledge Graph** - Visual representation of document concepts
- **Mind Map** - Hierarchical topic breakdown
- **Quiz Generator** - Create quizzes from document content
- **Sentiment Analysis** - Analyze tone and emotional content
- **Citation Extractor** - Find and extract academic citations

### Security & Performance
- **Rate Limiting** - Prevent abuse with configurable request limits
- **Secure File Handling** - PDF validation, secure filenames
- **Async Processing** - Non-blocking PDF processing
- **Production Ready** - Gunicorn WSGI server

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop (for Docker deployment)
- Git

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Dickson32-cell/Akoo-PDF-Summarization-Chatbot.git
cd Akoo-PDF-Summarization-Chatbot

# Start with Docker
cd docker
cp .env.example .env
docker-compose up -d

# Access the application
open http://localhost:5000
```

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/Dickson32-cell/Akoo-PDF-Summarization-Chatbot.git
cd Akoo-PDF-Summarization-Chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access at http://localhost:5000
```

## 📁 Project Structure

```
Akoo-PDF-Summarization-Chatbot/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker image definition
│
├── core/                     # Core processing modules
├── features/                 # Analysis tools
│   ├── knowledge_graph.py    # Knowledge graph generator
│   ├── mind_mapper.py        # Mind map generator
│   └── ...
│
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   ├── index.html           # Landing page
│   └── chat.html            # Chat interface
│
├── static/                   # Static assets
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript
│
├── docker/                   # Docker deployment
│   ├── docker-compose.yml    # Docker Compose config
│   └── .env.example         # Environment template
│
├── uploads/                  # User-uploaded files
├── cache/                    # Processing cache
├── feedback/                  # User feedback storage
├── logs/                      # Application logs
│
├── nltk_data/                # NLTK resources
├── knowledge_base.json        # Chatbot knowledge
│
├── README.md                 # This file
├── LICENSE                   # GPL v3 License
└── .gitignore               # Git ignore rules
```

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f akoo

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up -d --build

# Restart
docker-compose restart akoo
```

## 🌐 API Endpoints

### Chat Interface
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page |
| `/chat` | GET | Chat interface |
| `/get` | GET | Get bot response (GET params) |
| `/chat` | POST | Chat API endpoint |

### File Processing
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload PDF file |
| `/status/<job_id>` | GET | Check processing status |
| `/summarize-text` | POST | Summarize pasted text |

### Analysis Tools
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/knowledge-graph` | POST | Generate knowledge graph |
| `/api/mind-map` | POST | Generate mind map |
| `/api/quiz` | POST | Generate quiz questions |
| `/api/sentiment` | POST | Analyze sentiment |
| `/api/citations` | POST | Extract citations |

### System
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/check-llm` | GET | Check LLM availability |
| `/commands` | GET | List available commands |
| `/feedback` | POST | Submit feedback |

## ⚙️ Configuration

Create a `.env` file or set environment variables:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-here
DEBUG=False

# File Upload (bytes)
MAX_CONTENT_LENGTH=16777216  # 16MB

# Logging
LOG_LEVEL=INFO

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
```

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `SECRET_KEY` | (random) | Session secret key |
| `DEBUG` | `False` | Enable debug mode |
| `MAX_CONTENT_LENGTH` | `16777216` | Max upload size (16MB) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `USE_ML` | `True` | Enable ML summarization |
| `LLM_ENABLED` | `True` | Enable LLM chat |

## 📊 Usage Examples

### Upload PDF via cURL
```bash
curl -X POST -F "file=@document.pdf" \
     -F "summary_length=30" \
     -F "summary_format=paragraph" \
     http://localhost:5000/upload
```

### Summarize Text via API
```bash
curl -X POST http://localhost:5000/summarize-text \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text here...", "length": 30}'
```

### Generate Knowledge Graph
```bash
curl -X POST http://localhost:5000/api/knowledge-graph \
  -H "Content-Type: application/json" \
  -d '{"text": "Document text to analyze..."}'
```

## 🧪 Development

### Run Tests
```bash
# Start in debug mode
python app.py

# Run with Flask CLI
flask run --host=0.0.0.0 --port=5000
```

### Code Style
- Follow PEP 8
- Use type hints where possible
- Document all new functions

## 🔒 Security

- **Input Validation** - All user inputs are validated
- **File Type Verification** - PDF files checked for valid signatures
- **Rate Limiting** - Prevents abuse (10 uploads/min, 20 summaries/min)
- **Secure Filenames** - Random hex filenames prevent path traversal
- **CORS Enabled** - Cross-origin requests allowed for API access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

See [LICENSE](LICENSE) for details.

## 👨‍💻 Author

**Abdul Rashid Dickson**

## 🙏 Acknowledgments

- NLTK (Natural Language Toolkit)
- PyMuPDF for PDF processing
- Flask framework
- All open-source contributors

---

**Made with ❤️ for academic research and document analysis**
