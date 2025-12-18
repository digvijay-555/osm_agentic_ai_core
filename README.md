# 🚀 OSM Agentic AI

A production-grade intelligent agent system that automatically discovers, enriches, and stores business leads from OpenStreetMap (OSM) data using AI-powered data cleaning and normalization.

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Docker Deployment](#docker-deployment)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

OSM Agentic AI is an autonomous agent system that:

1. **Searches** for businesses using OpenStreetMap's Overpass API (via Overpass QL)
2. **Enriches** raw business data using Large Language Models (LLM) via Ollama
3. **Deduplicates** leads using vector similarity search (FAISS + Sentence Transformers)
4. **Stores** cleaned and normalized data in Google Sheets

The system consists of:
- **FastAPI Backend**: RESTful API for agent orchestration
- **Streamlit UI**: Interactive web interface for querying and monitoring
- **Agent Core**: Intelligent processing pipeline with LLM integration
- **Vector Store**: In-memory duplicate detection using semantic similarity

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Streamlit UI   │  Port 8501
│   (Frontend)    │
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────┐
│  FastAPI API    │  Port 8000
│   (Backend)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│           Agent Processing Pipeline              │
├─────────────────────────────────────────────────┤
│  1. Overpass Search → Raw Business Data         │
│  2. LLM Enrichment → Cleaned & Normalized       │
│  3. Vector Similarity → Duplicate Detection     │
│  4. Google Sheets → Persistent Storage          │
└─────────────────────────────────────────────────┘
         │
         ├──→ Ollama LLM (Local/Remote)
         ├──→ FAISS Vector Store (In-Memory)
         └──→ Google Sheets API
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Application Layer                     │
├─────────────────────────────────────────────────────────────┤
│  UI (Streamlit)          │  API (FastAPI)                   │
└──────────────┬───────────┴──────────────┬──────────────────┘
               │                           │
┌──────────────▼───────────────────────────▼──────────────────┐
│                      Agent Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Agent      │  │   Planner    │  │   Prompt     │     │
│  │ Orchestrator │→ │  (Enrich)    │→ │  Templates   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────┬───────────────────────────┬──────────────────┘
               │                           │
┌──────────────▼───────────────────────────▼──────────────────┐
│                    Service Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Tools      │  │   Memory     │  │  Services    │     │
│  │ - Overpass   │  │ - Vector DB  │  │ - Sheets     │     │
│  │ - Scraper    │  │ - FAISS      │  │ - UUID       │     │
│  │ - Email      │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────┬───────────────────────────┬──────────────────┘
               │                           │
┌──────────────▼───────────────────────────▼──────────────────┐
│                  External Integrations                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Ollama     │  │  Overpass    │  │ Google Sheets│     │
│  │   LLM API    │  │  OSM Search  │  │     API      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → Streamlit UI receives search query
2. **API Request** → FastAPI endpoint triggers agent in background
3. **Search Phase** → Overpass returns raw OSM business objects
4. **Enrichment Phase** → Each raw result is sent to LLM for cleaning
5. **Deduplication** → Vector similarity check against existing leads
6. **Storage** → Valid leads appended to Google Sheets with UUID

---

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server for FastAPI

### AI/ML Components
- **Ollama** - Local LLM inference server
- **Sentence Transformers** - Semantic embeddings (all-MiniLM-L6-v2)
- **FAISS** - Facebook AI Similarity Search for vector operations

### Data Processing
- **BeautifulSoup4** - Web scraping and HTML parsing
- **Requests** - HTTP client for API calls
- **Pandas** - Data manipulation (if needed)

### Storage & Integration
- **Google Sheets API** - Persistent data storage via gspread
- **OAuth2** - Google service account authentication

### Frontend
- **Streamlit** - Interactive web UI framework

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Python 3.10** - Runtime environment

### Development Tools
- **python-dotenv** - Environment variable management

---

## 📁 Project Structure

```
osm-agentic-ai/
│
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   │
│   ├── agent/                   # Agent orchestration logic
│   │   ├── __init__.py
│   │   ├── agent.py             # Main agent runner
│   │   ├── planner.py           # Lead enrichment logic
│   │   └── prompt.py            # LLM prompt templates
│   │
│   ├── llm/                     # LLM integration
│   │   ├── __init__.py
│   │   └── ollama_client.py     # Ollama API client
│   │
│   ├── tools/                   # External tool integrations
│   │   ├── __init__.py
│   │   ├── overpass.py          # OSM Overpass-based place search
│   │   ├── nominatim.py         # Backward-compat shim importing from overpass
│   │   ├── scraper.py           # Web scraping utilities
│   │   └── email.py             # Email extraction
│   │
│   ├── memory/                  # Vector store for deduplication
│   │   ├── __init__.py
│   │   └── vector_store.py      # FAISS-based similarity search
│   │
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── sheets.py            # Google Sheets integration
│   │   └── uuid_service.py      # UUID generation utilities
│   │
│   └── models/                  # Data models
│       └── lead.py              # Lead data structure
│
├── ui/                          # Streamlit frontend
│   └── app.py                   # Streamlit application
│
├── Dockerfile                   # Main Dockerfile
├── Dockerfile.api               # API service Dockerfile
├── Dockerfile.ui                # UI service Dockerfile
├── docker-compose.yml           # Multi-container orchestration
├── .dockerignore                # Docker build exclusions
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create this)
├── .gitignore                   # Git exclusions
└── README.md                    # This file
```

### Key Files Explained

- **`app/main.py`**: FastAPI application with `/run` endpoint
- **`app/agent/agent.py`**: Core agent loop that orchestrates search → enrich → dedupe → store
- **`app/agent/planner.py`**: Calls LLM to clean and normalize raw business data
- **`app/memory/vector_store.py`**: FAISS-based duplicate detection using semantic similarity
- **`app/services/sheets.py`**: Google Sheets API wrapper for data persistence
- **`ui/app.py`**: Streamlit interface for user interaction

---

## ✨ Features

- 🔍 **Intelligent Search**: Leverages OpenStreetMap's Overpass API for flexible, structured business discovery
- 🤖 **AI-Powered Enrichment**: Uses LLM to clean, normalize, and structure raw business data
- 🔄 **Smart Deduplication**: Vector similarity search prevents duplicate entries
- 📊 **Google Sheets Integration**: Automatic storage with structured data format
- 🐳 **Dockerized**: Fully containerized for easy deployment
- 🎨 **Modern UI**: Streamlit-based interactive interface
- ⚡ **Async Processing**: Background task execution for non-blocking operations
- 🔐 **Secure**: Environment-based configuration and credential management

---

## 📦 Prerequisites

### Required Software

1. **Python 3.10+** - [Download](https://www.python.org/downloads/)
2. **Docker & Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
3. **Ollama** (for LLM) - [Install Ollama](https://ollama.ai/)
4. **Google Cloud Project** with Sheets API enabled

### Required Services

1. **Ollama Server** running locally or remotely
   ```bash
   # Install and start Ollama
   curl https://ollama.ai/install.sh | sh
   ollama serve
   ```

2. **Google Service Account** with Sheets API access
   - Create a service account in Google Cloud Console
   - Download `credentials.json`
   - Share your Google Sheet with the service account email

3. **Google Sheet** prepared with headers:
   - Column A: UUID
   - Column B: Name
   - Column C: Address
   - Column D: Phone
   - Column E: Website
   - Column F: Email

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd osm-agentic-ai
```

### Step 2: Create Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Ollama Configuration
OLLAMA_MODEL=llama2  # or your preferred model
OLLAMA_BASE_URL=http://localhost:11434

# Overpass / OSM Configuration
USER_AGENT=YourAppName/1.0  # Required user-agent for OSM APIs

# Google Sheets (already configured in sheets.py)
# SPREADSHEET_ID=your_sheet_id_here
```

### Step 5: Set Up Google Sheets Credentials

1. Place your `credentials.json` file in the project root
2. Ensure the service account has access to your Google Sheet
3. Update `SPREADSHEET_ID` in `app/services/sheets.py` if needed

### Step 6: Start Ollama (if running locally)

```bash
ollama serve
# In another terminal, pull a model:
ollama pull llama2
```

### Step 7: Run the Application

#### Option A: Run Locally (Development)

**Terminal 1 - Start FastAPI Backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Streamlit UI:**
```bash
streamlit run ui/app.py --server.port 8501
```

#### Option B: Run with Docker Compose (Production)

```bash
docker-compose up --build
```

Access:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **UI**: http://localhost:8501

---

## 🐳 Docker Deployment

### Quick Start with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Docker Builds

#### Build API Service
```bash
docker build -f Dockerfile.api -t osm-agentic-api .
docker run -p 8000:8000 --env-file .env -v $(pwd)/credentials.json:/app/credentials.json osm-agentic-api
```

#### Build UI Service
```bash
docker build -f Dockerfile.ui -t osm-agentic-ui .
docker run -p 8501:8501 osm-agentic-ui
```

### Docker Environment Variables

Create a `.env` file or pass environment variables:

```bash
docker run -e OLLAMA_MODEL=llama2 \
           -e USER_AGENT=MyApp/1.0 \
           -p 8000:8000 \
           osm-agentic-api
```

### Docker Compose Services

- **`api`**: FastAPI backend service (port 8000)
- **`ui`**: Streamlit frontend service (port 8501)

Both services include health checks and automatic restart policies.

---

## 📖 Usage

### Using the Streamlit UI

1. Open http://localhost:8501
2. Enter a business search query (e.g., "restaurants in New York")
3. Click "Run Agent"
4. Monitor the background processing
5. Check your Google Sheet for results

### Using the API Directly

```bash
# Start agent via API
curl -X POST "http://localhost:8000/run?query=coffee shops in San Francisco"

# Response
{"status": "Agent started"}
```

### API Endpoints

#### `POST /run`
Triggers the agent to process a search query.

**Parameters:**
- `query` (query string): Business search query

**Example:**
```bash
curl -X POST "http://localhost:8000/run?query=dentists in Los Angeles"
```

**Response:**
```json
{
  "status": "Agent started"
}
```

### View API Documentation

FastAPI provides interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OLLAMA_MODEL` | Ollama model name | `llama2` | Yes |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` | No |
| `USER_AGENT` | OSM/Overpass user agent | - | Yes |
| `SPREADSHEET_ID` | Google Sheet ID | Set in code | Yes |

### Google Sheets Configuration

Edit `app/services/sheets.py`:
```python
SPREADSHEET_ID = "your_sheet_id_here"
```

### Vector Store Configuration

Edit `app/memory/vector_store.py`:
```python
# Adjust similarity threshold (0.0 - 1.0)
def is_duplicate(lead, threshold=0.85):  # Default: 85% similarity
```

### LLM Prompt Customization

Edit `app/agent/prompt.py` to modify the enrichment prompt.

---

## 🔧 Development

### Project Setup for Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (if configured)
pre-commit install

# Run tests (if available)
pytest
```

### Code Structure Guidelines

- **Absolute Imports**: Always use `from app.module import ...`
- **Type Hints**: Use type annotations for better code clarity
- **Error Handling**: Wrap external API calls in try-except blocks
- **Logging**: Use Python's logging module for debugging

### Adding New Tools

1. Create a new file in `app/tools/`
2. Implement your tool function
3. Import and use in `app/agent/agent.py`

### Adding New Services

1. Create a new file in `app/services/`
2. Implement service logic
3. Import where needed

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Ollama Connection Error
```
Error: Connection refused to Ollama server
```
**Solution**: Ensure Ollama is running:
```bash
ollama serve
# Verify: curl http://localhost:11434/api/tags
```

#### 2. Google Sheets Authentication Error
```
Error: FileNotFoundError: credentials.json
```
**Solution**: 
- Place `credentials.json` in project root
- Verify service account has Sheet access
- Check file permissions

#### 3. Import Errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**: 
- Ensure you're running from project root
- Verify `__init__.py` files exist in all packages
- Use absolute imports: `from app.module import ...`

#### 4. Vector Store Memory Issues
```
Error: FAISS index not initialized
```
**Solution**: The vector store initializes on first use. Ensure `sentence-transformers` is installed.

#### 5. Docker Build Fails
```
Error: Failed to build Docker image
```
**Solution**:
- Check Docker daemon is running
- Verify Dockerfile syntax
- Clear Docker cache: `docker system prune -a`

### Debug Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks

```bash
# Check API health
curl http://localhost:8000/docs

# Check UI health
curl http://localhost:8501/_stcore/health

# Check Ollama
curl http://localhost:11434/api/tags
```

---

## 📊 Performance Considerations

- **Vector Store**: In-memory FAISS index (resets on restart)
- **LLM Calls**: Sequential processing (consider batching for scale)
- **Overpass Usage**: Be a good citizen; avoid overly aggressive, repetitive queries
- **Google Sheets**: Batch writes for better performance

---

## 🔒 Security Notes

- Never commit `credentials.json` or `.env` files
- Use environment variables for sensitive data
- Rotate service account keys regularly
- Implement rate limiting for production
- Use HTTPS in production deployments

---

## 📝 License

[Specify your license here]

---

## 🤝 Contributing

[Add contribution guidelines if applicable]

---

## 📧 Contact & Support

[Add contact information]

---

## 🎯 Roadmap

- [ ] Persistent vector store (Redis/PostgreSQL)
- [ ] Batch processing optimization
- [ ] Real-time progress tracking
- [ ] Advanced filtering and search
- [ ] Multi-language support
- [ ] Export to multiple formats (CSV, JSON, etc.)

---

**Built with ❤️ using FastAPI, Streamlit, and Ollama**
