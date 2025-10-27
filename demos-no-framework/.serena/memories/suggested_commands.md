# Suggested Commands

## Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### FastAPI Server (REST API)
```bash
# Start the FastAPI server (default port 8000)
python main.py

# Server will be available at:
# - http://localhost:8000
# - API docs: http://localhost:8000/docs
```

### MCP Server (Direct)
```bash
# Run MCP server directly (stdio mode)
python mcp_server.py
```

### MCP Client (CLI)
```bash
# Run interactive MCP client
python mcp_client.py
```

## Testing
```bash
# Run specific test files
python test_api.py              # Test FastAPI endpoints
python test_mcp.py              # Test MCP functionality
python test_randomuser_api.py   # Test RandomUser.me integration
python test_full_integration.py # Full integration test

# Test with curl
curl http://localhost:8000/
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Create a random user"}'
```

## Development Tools (from parent project)
```bash
# Format code with ruff
ruff format .

# Lint code with ruff
ruff check .
ruff check --fix .  # Auto-fix issues

# Type check with mypy
mypy .

# Run pytest tests (if using pytest)
pytest
pytest -v  # Verbose output
```

## Environment Configuration
```bash
# Create .env file with API keys
echo "GEMINI_API_KEY=your_key_here" > .env

# Verify environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
```

## Utility Commands (Linux)
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Check what's running on port
lsof -i:8000

# View user data
cat data/users.json
cat data/users.json | python -m json.tool  # Pretty print

# Check Python version
python --version

# List installed packages
pip list
pip show mcp  # Show specific package info
```

## Git Commands
```bash
# Check status
git status

# View recent commits
git log --oneline -10

# Current branch
git branch
```

## Project Navigation
```bash
# View project structure
ls -la
tree -L 2  # If tree is installed

# Find files
find . -name "*.py" -type f
```
