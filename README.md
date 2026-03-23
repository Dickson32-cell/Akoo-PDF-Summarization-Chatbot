# Akoo PDF Summarization Chatbot

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

**Akoo** is an AI-powered chatbot designed to summarize PDF documents and text content using advanced natural language processing techniques.

---

## 🎯 Features

### Core Capabilities
- **📄 PDF Summarization** - Upload PDF files for intelligent summarization
- **📝 Text Summarization** - Paste text content for structured summaries
- **🎛️ Customizable Output** - Choose summary length and format (paragraph, bullet points)
- **💬 Chat Interface** - Conversational AI for document queries
- **📊 Analysis Tools** - Knowledge graphs, mind maps, quizzes, sentiment analysis

### Technical Features
- **🔒 Rate Limiting** - Prevent abuse with configurable request limits
- **🛡️ Secure File Handling** - Ensures secure file uploads and processing
- **💾 Feedback Collection** - Collect user feedback for continuous improvement
- **🤖 LLM Integration** - Uses local LLM (TinyLlama) for conversational responses
- **⚡ Async Processing** - Background processing for large documents
- **📈 Progress Tracking** - Real-time status updates for long-running jobs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Akoo Chatbot                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Web UI     │    │   REST API   │    │   Analysis   │  │
│  │  (Flask)     │    │  (Flask)     │    │   Tools      │  │
│  │  chat.html   │    │  /upload     │    │   - Graph    │  │
│  │  index.html  │    │  /summarize  │    │   - Mindmap  │  │
│  └──────┬───────┘    └──────┬───────┘    │   - Quiz     │  │
│         │                    │           │   - Sentiment│  │
│         └────────────────────┼───────────┴──────────────┘  │
│                              │                              │
│              ┌───────────────▼───────────────┐              │
│              │    NLP Processing Engine      │              │
│              │    - NLTK                     │              │
│              │    - PyMuPDF                  │              │
│              │    - Custom Summarizer        │              │
│              └───────────────┬───────────────┘              │
│                              │                              │
│         ┌────────────────────┼────────────────────┐        │
│         │                    │                    │        │
│  ┌──────▼──────┐    ┌────────▼────────┐   ┌──────▼──────┐ │
│  │   Upload    │    │     Cache       │   │   Feedback  │ │
│  │   Storage   │    │     Storage     │   │   Storage   │ │
│  └─────────────┘    └─────────────────┘   └─────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- (Optional) Docker for containerized deployment

### 1. Clone the Repository

```bash
git clone https://github.com/Dickson32-cell/Akoo-PDF-Summarization-Chatbot.git
cd Akoo-PDF-Summarization-Chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### 4. Create Environment File

```bash
copy .env.example .env
# Edit .env with your settings
```

### 5. Run the Application

```bash
python app.py
```

Open your browser: **http://localhost:5000**

---

## 🐳 Docker Deployment

### Build the Image

```bash
docker build -t akoo-chatbot:latest .
```

### Run with Docker Compose

```bash
cd docker
docker-compose up -d
```

### Run with Docker

```bash
docker run -d -p 5000:5000 \
  -v akoo-uploads:/app/uploads \
  -v akoo-cache:/app/cache \
  -v akoo-feedback:/app/feedback \
  akoo-chatbot:latest
```

Access: **http://localhost:5000**

---

## 📁 Project Structure

```
Akoo-PDF-Summarization-Chatbot/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── .dockerignore              # Docker ignore rules
│
├── docker/                     # Docker deployment files
│   ├── docker-compose.yml
│   └── .env.example
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html             # Landing page
│   └── chat.html              # Chat interface
│
├── static/                     # Static assets
│   ├── css/
│   └── js/
│
├── features/                   # Analysis tools
│   ├── knowledge_graph.py
│   ├── mind_mapper.py
│   └── ...
│
├── core/                       # Core processing logic
│
├── uploads/                    # Uploaded PDFs (created at runtime)
├── cache/                      # Processing cache (created at runtime)
├── feedback/                   # User feedback (created at runtime)
├── logs/                       # Application logs (created at runtime)
└── nltk_data/                  # NLTK data (created at runtime)
```

---

## 🌐 API Endpoints

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET | `/chat` | Chat interface |
| GET | `/get?msg=hello` | Get bot response |
| POST | `/chat` | Send chat message (JSON) |

### PDF Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload PDF file |
| GET | `/status/<job_id>` | Check processing status |

### Text Summarization

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/summarize-text` | Summarize provided text |

### Analysis Tools

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/knowledge-graph` | Generate knowledge graph |
| POST | `/api/mind-map` | Generate mind map |
| POST | `/api/quiz` | Generate quiz questions |
| POST | `/api/sentiment` | Analyze sentiment |
| POST | `/api/citations` | Extract citations |
| POST | `/api/translate` | Translate text (placeholder) |

### Utility

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/commands` | Get all available commands |
| POST | `/feedback` | Submit feedback |
| GET | `/check-llm` | Check LLM availability |

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DEBUG=False

# Server Configuration
PORT=5000

# File Upload Settings (16MB max)
MAX_CONTENT_LENGTH=16777216

# Logging
LOG_LEVEL=INFO
LOG_FILE=akoo.log

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://

# LLM Settings
LLM_ENABLED=True
LLM_MODEL_NAME=tinyllama
LLM_MAX_TOKENS=500
```

---

## 📊 Usage Examples

### Upload a PDF for Summarization

```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@document.pdf" \
  -F "summary_length=30" \
  -F "summary_format=paragraph"
```

### Summarize Text

```bash
curl -X POST http://localhost:5000/summarize-text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your long text here...",
    "length": 30
  }'
```

### Generate Knowledge Graph

```bash
curl -X POST http://localhost:5000/api/knowledge-graph \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Document text..."
  }'
```

### Chat with Akoo

```bash
curl "http://localhost:5000/get?msg=Hello"
```

---

## 🔒 Security Features

- **File Validation** - PDF signature verification
- **Rate Limiting** - 10 requests/minute for uploads
- **CORS Protection** - Cross-origin request handling
- **Secure Cookies** - Session management
- **Input Sanitization** - Prevent injection attacks
- **Feedback Validation** - Restricted file permissions

---

## 🧠 NLP Capabilities

### Summarization Methods
1. **Academic Excellence Framework** - Structured academic summaries
2. **ML-based Summarization** - Transformer models (optional)
3. **Fallback Methods** - Extractive summarization

### Analysis Tools
- **Knowledge Graph** - Entity relationships
- **Mind Map** - Concept hierarchy
- **Quiz Generation** - Comprehension questions
- **Sentiment Analysis** - Tone detection
- **Citation Extraction** - Academic references

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**Abdul Rashid Dickson**

---

## 🙏 Acknowledgments

- NLTK community
- Flask community
- All contributors

---

**Made with ❤️ by Abdul Rashid Dickson**
