# 📁 Local File Manager Agent

An **LLM-powered** file system assistant with intelligent function calling. Chat with your files using natural language - powered by **Ollama + Llama 3.1** with a beautiful purple gradient UI.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Flask](https://img.shields.io/badge/Flask-3.0.0-black)
![Ollama](https://img.shields.io/badge/Ollama-llama3.1:8b-purple)

## ✨ Features

- 🤖 **LLM-Powered Intelligence**: Uses Ollama's Llama 3.1:8b with function calling to understand natural language
- 🗣️ **Natural Language Interface**: No need for exact commands - just talk naturally ("search for Python files", "what's taking up space?")
- 📊 **Smart File Operations**: Find files by extension, create folders, list directories, and find largest files
- 🎨 **Beautiful UI**: Purple gradient theme with smooth animations and mobile-responsive design
- 🚀 **Production Ready**: Comprehensive error handling, CORS support, and clean architecture
- 🧠 **Function Calling**: LLM intelligently selects the right tool for each request
- 🌐 **REST API**: Well-documented endpoints for chat and file operations

## 🎯 Supported Operations

The LLM understands natural language, so you can phrase requests however you like!

| Operation | Example Queries | Description |
|-----------|----------------|-------------|
| **Find Files** | "Find all .py files"<br>"Search for Python files"<br>"Locate JavaScript code" | Search for files by extension |
| **Largest Files** | "Show me the largest files"<br>"What's taking up space?"<br>"Which files are biggest?" | Get top 10 largest files in directory tree |
| **Create Folder** | "Create folder my_project"<br>"I need a new directory called test"<br>"Make a folder named docs" | Create a new directory |
| **List Directory** | "List current directory"<br>"Show me what files are in here"<br>"What's in this folder?" | Show contents of a directory |
| **Move Files** | "Move all Screenshot*.png files to archive"<br>"Relocate *.txt files from Downloads to Documents"<br>"Organize report_*.pdf files" | Move files matching a pattern from one directory to another |

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **pip**: Python package installer
- **Ollama**: Local LLM runtime ([Install here](https://ollama.ai))
- **Llama 3.1:8b model**: Run `ollama pull llama3.1:8b` after installing Ollama
- **Modern browser**: Chrome, Firefox, Safari, or Edge

## 🛠️ Installation

### 1. Install and Start Ollama

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
brew services start ollama

# Pull the Llama 3.1:8b model (supports function calling)
ollama pull llama3.1:8b

# Verify Ollama is running
ollama list
```

### 2. Clone or Navigate to Project

```bash
cd /Users/andle/AI/aichat/file-manager-agent
```

### 3. Set Up Backend

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt
```

### 4. Frontend Setup

No installation needed! The frontend is pure HTML/CSS/JavaScript.

## 🚀 Running the Application

### Start the Backend Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
python3 backend/app.py
```

You should see:
```
🚀 Starting Local File Manager Agent...
📁 Base path: /Users/andle
🤖 AI Model: llama3.1:8b (with function calling)
🌐 Server running on http://localhost:5001

✨ LLM-powered intelligent file operations enabled!
```

**Note**: Port 5001 is used instead of 5000 because macOS AirPlay Receiver uses port 5000 by default.

### Open the Frontend

1. Open `frontend/index.html` in your browser, or
2. Serve with a local server (optional):

```bash
# From the frontend directory
cd frontend
python3 -m http.server 8080
```

Then visit: `http://localhost:8080`

## 🎮 Usage

### Via Chat Interface

1. Open the frontend in your browser
2. Wait for the green "Connected" status indicator
3. Type natural language commands (the LLM understands variations!):
   - "Find all .py files" or "Search for Python files"
   - "Show me the largest files" or "What's taking up disk space?"
   - "Create folder test_project" or "I need a new directory called my_project"
   - "List current directory" or "Show me what files are in here"

### Via API (cURL examples)

#### Health Check
```bash
curl http://localhost:5001/api/health
```

#### Chat Endpoint
```bash
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Find all .py files",
    "context": {"directory": "/Users/andle"}
  }'
```

#### Execute Operation
```bash
curl -X POST http://localhost:5001/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "find_by_extension",
    "params": {
      "directory": "/Users/andle",
      "extension": ".py",
      "limit": 50
    }
  }'
```

## 📐 Architecture

```
file-manager-agent/
├── backend/
│   ├── app.py              # Flask server with API endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html         # Chat interface structure
│   ├── styles.css         # Purple gradient theme & animations
│   └── app.js             # Chat logic & API communication
└── README.md              # This file
```

### Backend Components

- **FileOperations**: Handles all file system operations with proper error handling
- **AgentProcessor**: Processes natural language queries (currently keyword-based, ready for LLM integration)
- **API Endpoints**:
  - `POST /api/chat`: Natural language chat interface
  - `POST /api/execute`: Execute specific file operations
  - `GET /api/health`: Health check endpoint

### Frontend Components

- **Chat Interface**: Beautiful message display with user/agent distinction
- **Typing Indicator**: Animated dots while processing
- **Status Indicator**: Real-time connection status with color-coded dot
- **File Results**: Formatted tables for file listings
- **Mobile Responsive**: Adapts to different screen sizes

## 🎨 UI Features

- **Color Scheme**: Purple gradient (#667eea → #764ba2) with dark theme
- **Animations**: Smooth fade-in, slide-down, and typing animations
- **Custom Scrollbar**: Themed scrollbar for chat container
- **Message Types**: Success (green), error (red), and normal messages
- **File Path Display**: Monospace font for file paths and names

## 🧠 How It Works

### LLM Function Calling Architecture

The agent uses **Ollama's function calling** feature to intelligently understand your requests:

1. **User Query**: You type a natural language request like "search for Python files"
2. **LLM Processing**: Llama 3.1:8b analyzes your intent using the system prompt
3. **Function Selection**: The LLM decides which file operation tool to call
4. **Parameter Extraction**: The LLM extracts parameters (e.g., extension=".py")
5. **Execution**: The backend executes the chosen operation
6. **Response**: Results are formatted and displayed in the chat UI

### Available Tools

The LLM has access to 5 file operation tools defined in `backend/app.py:195`:

```python
- find_files_by_extension: Search for files with specific extensions
- get_largest_files: Find files taking up the most space
- create_folder: Make new directories
- list_directory: Show directory contents
- move_files: Move files matching a pattern from one directory to another
```

Each tool has a detailed description that helps the LLM decide when to use it.

### Model Configuration

The system uses **Llama 3.1:8b** because it:
- ✅ Supports function calling (required for tools)
- ✅ Runs locally on Apple Silicon M-series chips
- ✅ Fast enough for real-time chat responses
- ✅ Smart enough to understand natural language variations

**Note**: Models like `qwen2.5-coder` and `deepseek-coder-v2` do NOT support function calling.

### Future Operations

Planned additions:
- **File Search**: Search file contents with regex
- **File Rename**: Rename individual files
- **File Delete**: Safe file deletion with confirmation
- **File Stats**: Detailed file metadata
- **Copy Files**: Copy files matching a pattern

## 🔧 Configuration

### Change LLM Model

Edit `backend/app.py:24`:

```python
OLLAMA_MODEL = "llama3.1:8b"  # Change to any model with function calling support
```

**Compatible models**:
- `llama3.1:8b` (recommended - 4.9GB)
- `llama3.2` (faster - 2GB)
- Other llama models with function calling

**Note**: Make sure to pull the model first: `ollama pull <model-name>`

### Change Base Directory

Edit `backend/app.py:22`:

```python
BASE_PATH = os.path.expanduser("~")  # Change to your preferred path
```

### Adjust File Limits

Edit `backend/app.py:23`:

```python
MAX_FILE_SIZE_DISPLAY = 100  # Maximum files to return
```

### Frontend API URL

Edit `frontend/app.js`:

```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:5001',  // Change if backend runs elsewhere
    TYPING_DELAY: 1000,
    SCROLL_BEHAVIOR: 'smooth'
};
```

## 🐛 Troubleshooting

### Ollama Not Running

**Problem**: `Error in LLM processing: Connection refused`

**Solution**:
```bash
# Check if Ollama is running
brew services list | grep ollama

# Start Ollama if not running
brew services start ollama

# Verify the model is available
ollama list
```

### LLM Slow to Respond

**Problem**: Queries take 10+ seconds

**Solutions**:
- Switch to a smaller model: `llama3.2` (2GB) instead of `llama3.1:8b` (4.9GB)
- Check CPU usage - ensure no other heavy processes are running
- On Apple Silicon, ensure Ollama is using the GPU

### Backend Won't Start

**Problem**: `ModuleNotFoundError: No module named 'flask'` or `'ollama'`

**Solution**:
```bash
# Activate virtual environment first
source venv/bin/activate

# Then install dependencies
pip install -r backend/requirements.txt
```

### Frontend Shows "Disconnected"

**Problem**: Cannot connect to backend

**Solutions**:
1. Ensure backend is running: `python3 backend/app.py`
2. Check backend is on port 5001: `lsof -i :5001`
3. Verify CORS is enabled in `app.py`

### Permission Errors

**Problem**: `PermissionError: [Errno 13] Permission denied`

**Solution**: The app runs with your user permissions. Ensure you have access to directories you're querying.

### Port Already in Use

**Problem**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Find process using port 5001
lsof -i :5001

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

**Note**: If you need to use port 5000 on macOS, you may need to disable AirPlay Receiver in System Preferences.

## 📝 API Documentation

### POST /api/chat

Process natural language queries.

**Request:**
```json
{
  "message": "Find all .py files",
  "context": {
    "directory": "/Users/andle"
  }
}
```

**Response:**
```json
{
  "response": "I'll execute: find_by_extension",
  "action_info": {
    "action": "find_by_extension",
    "params": {
      "directory": "/Users/andle",
      "extension": ".py",
      "limit": 50
    }
  }
}
```

### POST /api/execute

Execute a specific file operation.

**Request:**
```json
{
  "action": "find_by_extension",
  "params": {
    "directory": "/Users/andle",
    "extension": ".py",
    "limit": 50
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "path": "/Users/andle/script.py",
      "name": "script.py",
      "size": 1024,
      "readable_size": "1.00 KB",
      "modified": "2025-10-21T12:00:00"
    }
  ],
  "message": "Found 1 files"
}
```

### Available Actions

| Action | Parameters | Description |
|--------|-----------|-------------|
| `find_by_extension` | directory, extension, limit | Find files by extension |
| `largest_files` | directory, limit | Get largest files |
| `create_folder` | directory, folder_name | Create new folder |
| `list_directory` | directory | List directory contents |
| `move_files` | source_directory, destination_directory, pattern | Move files matching a pattern |

## 📄 License

MIT License - Feel free to use and modify for your projects.

## 🙏 Credits

Built with:
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [Llama 3.1:8b](https://ollama.ai/library/llama3.1) - Meta's LLM with function calling support
- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [Flask-CORS](https://flask-cors.readthedocs.io/) - Cross-origin resource sharing
- Pure HTML/CSS/JavaScript - No frontend frameworks needed

---

**Built with ❤️ and 🤖 for intelligent local file management**
