# Task Completion Checklist

When completing any development task in this project, follow these steps:

## 1. Code Quality

### Formatting
```bash
# Format code with ruff (from parent project tools)
ruff format .
```

### Linting
```bash
# Check for linting issues
ruff check .

# Auto-fix linting issues
ruff check --fix .
```

### Type Checking
```bash
# Run mypy type checker
mypy .
```

## 2. Testing

### Run Relevant Tests
```bash
# If you modified API endpoints
python test_api.py

# If you modified MCP server
python test_mcp.py
python test_full_integration.py

# If you modified RandomUser integration
python test_randomuser_api.py

# Test the running server
curl http://localhost:8000/
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Your test query"}'
```

### Verify Application Runs
```bash
# Start FastAPI server and verify it runs without errors
python main.py

# Should see:
# 🚀 Starting MCP FastAPI Server on http://localhost:8000
# 📚 API docs available at http://localhost:8000/docs
# ✓ MCP Client initialized: X tools, Y resources
```

## 3. Documentation

### Update Documentation
- If you added new features, update relevant markdown files:
  - `QUICKSTART.md` for setup changes
  - `API_INTEGRATION.md` for API changes
  - `FASTAPI_README.md` for endpoint changes
  - `README.md` if project purpose changed

### Code Comments
- Ensure functions have descriptive docstrings
- Add comments for complex logic
- Update type hints if function signatures changed

## 4. Environment Variables

### Check .env Configuration
```bash
# Verify required environment variables
cat .env

# Test environment loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('GEMINI_API_KEY:', 'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET')"
```

## 5. Dependencies

### Update Requirements
```bash
# If you added new packages
pip freeze > requirements.txt

# Or manually add to requirements.txt and pyproject.toml
```

## 6. Git

### Commit Changes
```bash
# Stage changes
git add .

# Review changes
git status
git diff --staged

# Commit with descriptive message
git commit -m "Descriptive message about changes"

# Push if applicable
git push origin main
```

## Quick Checklist

Before marking a task complete, verify:
- [ ] Code formatted with `ruff format`
- [ ] No linting errors (`ruff check`)
- [ ] Type checks pass (`mypy`)
- [ ] Relevant tests run successfully
- [ ] Application starts without errors
- [ ] Documentation updated if needed
- [ ] Environment variables documented
- [ ] Dependencies updated if changed
- [ ] Changes committed to git with good message

## Notes
- Not all steps may be applicable to every task
- For small changes, focused testing is sufficient
- Always test the basic functionality: server starts, basic endpoints work
- Check the FastAPI docs at http://localhost:8000/docs after changes
