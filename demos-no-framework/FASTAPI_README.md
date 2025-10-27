# MCP FastAPI Server

FastAPI REST API that exposes Model Context Protocol (MCP) client functionality for Next.js frontend applications.

## Overview

This server acts as a bridge between your Next.js frontend and the MCP server, providing:
- **Chat endpoint** with natural language processing and automatic tool calling
- **Direct tool execution** for MCP tools
- **Resource access** to read MCP resources
- **Capabilities discovery** to list available tools, resources, and prompts
- **CORS support** for Next.js development

## Architecture

```
Next.js Frontend (Port 3000)
         ↓
    HTTP/REST API
         ↓
FastAPI Server (Port 8000)
         ↓
   MCP Client (stdio)
         ↓
   MCP Server (subprocess)
         ↓
  RandomUser.me API + Database
```

## Quick Start

### 1. Start the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 2. Access API Documentation

Interactive API docs are available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
```http
GET /
```

Response:
```json
{
  "status": "ok",
  "service": "MCP Client API",
  "version": "1.0.0",
  "mcp_connected": true
}
```

### Get Capabilities
```http
GET /capabilities
```

Returns all available MCP tools, resources, prompts, and roots.

Response:
```json
{
  "tools": [
    {
      "name": "create-user",
      "description": "Create a new user in the database",
      "input_schema": {...}
    }
  ],
  "resources": [...],
  "prompts": [...],
  "roots": [...]
}
```

### Chat (Natural Language)
```http
POST /chat
Content-Type: application/json

{
  "message": "Create a random user"
}
```

Response:
```json
{
  "response": "I've created a random user named John Doe with email john.doe@example.com",
  "tool_calls": [
    {
      "tool": "create-random-user",
      "arguments": {},
      "result": "User 10 created successfully: John Doe (john.doe@example.com)"
    }
  ]
}
```

### Call Tool Directly
```http
POST /tools/call
Content-Type: application/json

{
  "tool_name": "create-user",
  "arguments": {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "address": "456 Oak St",
    "phone": "555-1234"
  }
}
```

Response:
```json
{
  "result": "User 11 created successfully",
  "success": true
}
```

### Read Resource
```http
POST /resources/read
Content-Type: application/json

{
  "uri": "users://all"
}
```

Response:
```json
{
  "data": [
    {
      "id": 1,
      "name": "Melvin Hillsman",
      "email": "mrhillsman@test.com",
      "address": "123 Maple St",
      "phone": "555-1234"
    }
  ],
  "type": "json"
}
```

### Get All Users (Convenience)
```http
GET /users
```

Response:
```json
{
  "users": [...],
  "count": 11
}
```

## Features

### 🤖 Automatic Tool Calling

The `/chat` endpoint uses Gemini to:
1. Understand natural language requests
2. Automatically select and call appropriate MCP tools
3. Return conversational responses with tool results

Example:
```
User: "Create a random user"
  → Calls create-random-user tool
  → Returns: "I've created John Doe..."
```

### 🔄 MCP Client Lifecycle

The MCP client connection is:
- Initialized on server startup
- Maintained throughout server lifetime
- Properly cleaned up on shutdown
- Reconnects automatically if needed

### 🌐 CORS Configuration

Pre-configured for Next.js development:
- `localhost:3000` (default Next.js port)
- `localhost:3001`
- `127.0.0.1:3000`
- `127.0.0.1:3001`

Add more origins in `main.py`:
```python
allow_origins=[
    "http://localhost:3000",
    "http://yourapp.vercel.app",  # Production
],
```

### 🛡️ Error Handling

All endpoints include comprehensive error handling:
- HTTP 503: MCP client not initialized
- HTTP 500: Internal server errors
- Tool-specific errors returned with `success: false`

## Testing

### Using Python Requests

```python
import requests

# Chat
response = requests.post(
    "http://localhost:8000/chat",
    json={"message": "Hello!"}
)
print(response.json())

# Create user
response = requests.post(
    "http://localhost:8000/tools/call",
    json={
        "tool_name": "create-user",
        "arguments": {
            "name": "Test User",
            "email": "test@example.com",
            "address": "123 Test St",
            "phone": "555-0000"
        }
    }
)
print(response.json())
```

### Using curl

```bash
# Health check
curl http://localhost:8000/

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a random user"}'

# Get users
curl http://localhost:8000/users
```

### Automated Tests

Run the test suite:
```bash
python test_api.py
```

## Next.js Integration

See `NEXTJS_EXAMPLE.md` for complete Next.js frontend examples.

Quick example:
```typescript
// app/api/chat/route.ts
export async function POST(req: Request) {
  const { message } = await req.json()

  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  })

  const data = await response.json()
  return Response.json(data)
}
```

## Configuration

### Environment Variables

Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Server Settings

Modify `main.py`:
```python
# Change port
uvicorn.run(app, host="0.0.0.0", port=8080)

# Change MCP server path
command=".venv/bin/python",
args=["path/to/mcp_server.py"],
```

## Deployment

### Development
```bash
python main.py
```

### Production with Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Performance

- MCP client connection pooled (single instance)
- Async/await throughout for non-blocking I/O
- Gemini API calls cached where possible
- RandomUser.me API is fast and reliable

## Troubleshooting

### Server won't start
- Check if port 8000 is available
- Ensure `.venv` is activated
- Verify MCP server path is correct

### MCP client not connecting
- Check `mcp_server.py` is in the same directory
- Ensure Python path in server params is correct
- Check logs for connection errors

### CORS errors
- Add your frontend origin to `allow_origins`
- Ensure credentials are set correctly
- Check browser console for specific CORS error

## Security Considerations

### Production Deployment
- Use environment variables for sensitive data
- Enable HTTPS
- Restrict CORS to specific origins
- Implement rate limiting
- Add authentication/authorization
- Validate all user inputs

### API Key Management
- Never commit `.env` files
- Use secure secret management in production
- Rotate keys regularly

## License

MIT

## Support

For issues or questions:
1. Check the API docs at `/docs`
2. Review error messages in logs
3. Test with `test_api.py`
4. Check MCP server logs
