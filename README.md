# Tag Notes - AI-Powered Resource Tagging System

A POC application that automatically tags web links and text ideas using AI, making it easy to find similar notes later.

## Features

- **User Authentication**: Secure signup/login with JWT tokens (24h expiration)
- **Dual Agent System**: Two specialized agents run concurrently
  - Web Link Analyzer: Fetches and analyzes the first 200 words of web pages
  - Text Analyzer: Analyzes full text content
- **Auto-Tagging**: Each resource gets up to 5 relevant tags
- **Smart Descriptions**: Generates concise 3-sentence descriptions
- **Interactive Note Editing**: Review and customize tags/descriptions before saving
- **Search by Tag**: Quickly find resources by tags
- **React Frontend**: Modern, responsive UI
- **FastAPI Backend**: High-performance Python backend with JWT authentication
- **Local AI**: Uses Ollama for privacy and offline capability

## Prerequisites

- Python 3.12+ with `uv` package manager
- Node.js 18+
- Ollama running locally

## Installation

### 1. Install Ollama and Download Model

```bash
# Install Ollama if not already installed
brew install ollama

# Start Ollama service
ollama serve

# In a new terminal, pull the recommended model
ollama pull llama3.2:3b
```

### 2. Set Up Backend

```bash
# Dependencies are managed with uv
uv sync
```

The backend uses:
- FastAPI for API endpoints
- Langchain with Ollama for AI analysis
- BeautifulSoup4 for web scraping

### 3. Set Up Frontend

```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend

In the project root:

```bash
# Make sure Ollama is running first
uv run python -m main
```

The API will be available at http://localhost:8000

### Start the Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:5173

## Usage

### First Time Setup

1. **Sign Up**:
   - Open http://localhost:5173
   - Click "Sign Up"
   - Enter your email address (used as username)
   - Enter a password (minimum 6 characters)
   - Click "Sign Up" button

2. **Login** (subsequent visits):
   - Enter your email and password
   - Click "Login" button
   - Your JWT token is stored in localStorage for 24 hours

### Using the Application

1. **Add a Resource**:
   - Enter a URL (e.g., `https://example.com`) or text in the input field
   - Click "Analyze & Tag" button
   - Wait for the AI to process (may take 10-30 seconds)
   - Review the parsed note with AI-generated tags and description
   - Click "Yes" to save as-is, or "No" to customize:
     - Remove tags by clicking the X button
     - Add custom tags (max 5 total)
     - Edit the description
     - Click "Save Changes" or "Cancel"

2. **Search by Tag**:
   - Enter a tag in the search field
   - Click "Search" button
   - All resources with that tag will be displayed

3. **Logout**:
   - Click the "Logout" button in the top-right corner

## Configuration

All configuration settings are centralized in `settings.py` in the project root.

### Changing the AI Model

Edit `settings.py` and update the `MODEL_NAME` variable:

```python
MODEL_NAME = "llama3.2:3b"  # Change to your preferred model
```

The file includes model recommendations by RAM:
- **8GB RAM**: llama3.2:1b, qwen2.5:3b, gemma2:2b
- **16GB RAM**: llama3.2:3b (default), mistral:latest, phi3:latest, qwen2.5:7b
- **32GB RAM**: llama3.1:8b, llama3.3:70b

After changing the model:
1. Pull it with Ollama: `ollama pull <model-name>`
2. Update `MODEL_NAME` in `settings.py`
3. Restart the application

### Adjusting Web Page Content Length

Edit `settings.py` and update:

```python
WEB_CONTENT_WORD_LIMIT = 200  # Change to desired word count
```

## API Endpoints

### Authentication (Public)

- `POST /api/auth/signup` - Register a new user
- `POST /api/auth/login` - Login and get JWT token

### Resources (Requires Authentication)

- `POST /api/add` - Add and analyze a new resource
- `POST /api/search` - Search resources by tag
- `GET /api/resources` - Get all resources

### Health

- `GET /health` - Health check (public)

## Architecture

```
Backend (Python)
├── Repository Pattern (dict-based storage)
├── Two Concurrent Agents
│   ├── Web Link Analyzer
│   └── Text Analyzer
└── FastAPI REST API

Frontend (React)
├── Single Page Application
├── Real-time status updates
└── Responsive design
```

## Model Selection Guide

Configure your model in `settings.py` based on your available RAM:

### 8GB RAM

- **llama3.2:1b** - Very fast, decent quality
- **qwen2.5:3b** - Fast and efficient, good balance
- **gemma2:2b** - Google's lightweight model

### 16GB RAM (Most Common)

- **llama3.2:3b** - Default, best balance (recommended)
- **mistral:latest** - Good alternative, fast performance
- **phi3:latest** - Microsoft's efficient model
- **qwen2.5:7b** - Higher quality than 3b version

### 32GB RAM

- **llama3.1:8b** - High quality, OpenAI-level performance
- **llama3.3:70b** - Excellent quality, slower processing

All model options are documented in `settings.py` with easy uncomment-to-use format.

## Development Notes

- User credentials are stored in `users.json` with SHA-256 hashed passwords
- Resource repository uses an in-memory dictionary (data is lost on restart)
- JWT tokens expire after 24 hours
- Both agents run concurrently using ThreadPoolExecutor
- The frontend uses CORS to communicate with the backend
- All analysis is done locally with Ollama for privacy
- Authentication uses a repository pattern interface for easy database migration

### Security Notes

- Change the `JWT_SECRET_KEY` environment variable in production
- Default secret key is "your-secret-key-change-in-production"
- Set it with: `export JWT_SECRET_KEY="your-secure-random-key"`
- User passwords are hashed with SHA-256 before storage
- All authenticated endpoints require a valid JWT Bearer token
