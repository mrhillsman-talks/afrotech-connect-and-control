# Quick Start Guide

Get the MCP FastAPI server running with your Next.js frontend in 5 minutes!

## Prerequisites

- Python 3.12+
- Node.js 18+
- Gemini API key

## Backend Setup (FastAPI + MCP)

### 1. Install Dependencies

```bash
cd demos-no-framework

# Create virtual environment (if not exists)
python -m venv .venv

# Activate
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
pip install fastapi requests
```

### 2. Configure Environment

Create `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Start the Server

```bash
python main.py
```

You should see:
```
🚀 Starting MCP FastAPI Server on http://localhost:8000
📚 API docs available at http://localhost:8000/docs
✓ MCP Client initialized: 2 tools, 3 resources
```

### 4. Test the API

```bash
# In another terminal
python test_api.py
```

Or visit http://localhost:8000/docs for interactive API documentation.

## Frontend Setup (Next.js)

### Option 1: Full Next.js App

```bash
# Create new Next.js app
npx create-next-app@latest mcp-chat-app
cd mcp-chat-app

# Copy components from NEXTJS_EXAMPLE.md
# Set up the files as described in the documentation

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

Visit http://localhost:3000

### Option 2: Quick Test with HTML

Create `test-frontend.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Chat Test</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-2xl font-bold mb-4">MCP Chat Test</h1>

        <div id="messages" class="space-y-4 mb-4 h-96 overflow-y-auto"></div>

        <div class="flex gap-2">
            <input
                type="text"
                id="messageInput"
                placeholder="Type a message..."
                class="flex-1 px-4 py-2 border rounded-lg"
            />
            <button
                onclick="sendMessage()"
                class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
                Send
            </button>
        </div>

        <div class="mt-4 flex flex-wrap gap-2">
            <button onclick="setMessage('Create a random user')" class="text-xs px-3 py-1 bg-gray-200 rounded-full">
                Create random user
            </button>
            <button onclick="setMessage('How many users?')" class="text-xs px-3 py-1 bg-gray-200 rounded-full">
                Count users
            </button>
        </div>
    </div>

    <script>
        const API_URL = 'http://localhost:8000';

        function setMessage(msg) {
            document.getElementById('messageInput').value = msg;
        }

        function addMessage(role, content, toolCalls = null) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `p-4 rounded-lg ${role === 'user' ? 'bg-blue-100 ml-auto' : 'bg-gray-100'} max-w-[80%]`;

            let html = `
                <p class="font-semibold mb-1">${role === 'user' ? 'You' : 'Assistant'}</p>
                <p>${content}</p>
            `;

            if (toolCalls && toolCalls.length > 0) {
                html += '<div class="mt-2 pt-2 border-t"><p class="text-sm font-semibold">Tools Used:</p>';
                toolCalls.forEach(call => {
                    html += `<div class="text-sm bg-white p-2 rounded mt-1">
                        <span class="font-mono text-blue-600">${call.tool}</span>
                        <p class="text-xs text-gray-600">${call.result}</p>
                    </div>`;
                });
                html += '</div>';
            }

            messageDiv.innerHTML = html;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (!message) return;

            addMessage('user', message);
            input.value = '';

            try {
                const response = await fetch(`${API_URL}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });

                const data = await response.json();
                addMessage('assistant', data.response, data.tool_calls);
            } catch (error) {
                addMessage('assistant', 'Error: ' + error.message);
            }
        }

        // Send message on Enter key
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // Load initial status
        fetch(`${API_URL}/`)
            .then(r => r.json())
            .then(data => addMessage('assistant', `Connected to ${data.service} v${data.version}`));
    </script>
</body>
</html>
```

Open `test-frontend.html` in your browser!

## Quick Test Commands

### Test Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message": "Create a random user"}'
```

### Get Users

```bash
curl http://localhost:8000/users
```

### Call Tool Directly

```bash
curl -X POST http://localhost:8000/tools/call \
  -H 'Content-Type: application/json' \
  -d '{
    "tool_name": "create-user",
    "arguments": {
      "name": "Test User",
      "email": "test@example.com",
      "address": "123 Test St",
      "phone": "555-0000"
    }
  }'
```

## Architecture Overview

```
┌─────────────────┐
│  Next.js/HTML   │
│   Frontend      │
│  Port: 3000     │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│  FastAPI        │
│  main.py        │
│  Port: 8000     │
└────────┬────────┘
         │ stdio
         ↓
┌─────────────────┐
│  MCP Server     │
│  mcp_server.py  │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌─────┐   ┌──────────┐
│ DB  │   │ Random   │
│ JSON│   │ User API │
└─────┘   └──────────┘
```

## What's Working?

✅ **FastAPI Server**
- Health check endpoint
- Chat with natural language
- Direct tool calling
- Resource reading
- CORS enabled for Next.js

✅ **MCP Integration**
- Client-server communication
- Tool execution
- Resource access
- Sampling support
- Roots support

✅ **Features**
- Create users manually
- Create random users via API
- Natural language queries
- Automatic tool selection
- Error handling

## Common Issues

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### GEMINI_API_KEY Not Found
```bash
# Check .env file exists
cat .env

# Make sure it's loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
```

### MCP Server Won't Start
```bash
# Test MCP server directly
.venv/bin/python mcp_server.py

# Check if mcp_server.py exists
ls -la mcp_server.py
```

### CORS Errors in Browser
- Open browser DevTools → Network tab
- Check if request reaches server
- Verify origin is in CORS allow list
- Ensure `credentials: true` if needed

## Next Steps

1. **Read the docs**
   - `FASTAPI_README.md` - Complete API documentation
   - `NEXTJS_EXAMPLE.md` - Full Next.js integration guide
   - `API_INTEGRATION.md` - RandomUser.me API details

2. **Explore the API**
   - Visit http://localhost:8000/docs
   - Try different endpoints
   - Check out the schemas

3. **Build your frontend**
   - Use provided Next.js examples
   - Customize the chat interface
   - Add your own features

4. **Deploy**
   - Deploy FastAPI to Railway/Render
   - Deploy Next.js to Vercel
   - Set environment variables

## Support

Having issues? Check:
1. Both servers are running
2. Environment variables are set
3. Dependencies are installed
4. Ports aren't blocked
5. Logs for error messages

## Files Created

- `main.py` - FastAPI server
- `test_api.py` - API test suite
- `FASTAPI_README.md` - API documentation
- `NEXTJS_EXAMPLE.md` - Frontend guide
- `QUICKSTART.md` - This file

Enjoy building with MCP! 🚀
