# Next.js Frontend Example

Complete example of integrating the MCP FastAPI server with a Next.js chat application.

## Setup

### 1. Create Next.js App

```bash
npx create-next-app@latest mcp-chat-app
cd mcp-chat-app
npm install
```

### 2. Install Dependencies

```bash
npm install @/components/ui/button @/components/ui/input @/components/ui/card
# or use shadcn/ui
npx shadcn-ui@latest init
```

## Project Structure

```
mcp-chat-app/
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.ts        # API route proxy
│   ├── page.tsx                # Main chat page
│   └── layout.tsx
├── components/
│   ├── Chat.tsx                # Chat component
│   └── UserList.tsx            # User list component
├── lib/
│   └── api.ts                  # API client
└── types/
    └── index.ts                # TypeScript types
```

## Implementation

### 1. TypeScript Types (`types/index.ts`)

```typescript
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  tool_calls?: ToolCall[]
}

export interface ToolCall {
  tool: string
  arguments: Record<string, any>
  result: string
}

export interface ChatResponse {
  response: string
  tool_calls?: ToolCall[]
}

export interface User {
  id: number
  name: string
  email: string
  address: string
  phone: string
}

export interface Tool {
  name: string
  description: string
  input_schema: any
}

export interface Capabilities {
  tools: Tool[]
  resources: any[]
  prompts: any[]
  roots: any[]
}
```

### 2. API Client (`lib/api.ts`)

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = {
  // Chat endpoint
  async chat(message: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    })

    if (!response.ok) {
      throw new Error('Chat request failed')
    }

    return response.json()
  },

  // Get capabilities
  async getCapabilities(): Promise<Capabilities> {
    const response = await fetch(`${API_BASE}/capabilities`)
    return response.json()
  },

  // Get users
  async getUsers(): Promise<{ users: User[], count: number }> {
    const response = await fetch(`${API_BASE}/users`)
    return response.json()
  },

  // Call tool directly
  async callTool(toolName: string, args: Record<string, any>) {
    const response = await fetch(`${API_BASE}/tools/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tool_name: toolName,
        arguments: args
      })
    })
    return response.json()
  },

  // Health check
  async health() {
    const response = await fetch(`${API_BASE}/`)
    return response.json()
  }
}
```

### 3. Chat Component (`components/Chat.tsx`)

```typescript
'use client'

import { useState } from 'react'
import { api } from '@/lib/api'
import type { ChatMessage } from '@/types'

export default function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: input
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await api.chat(input)

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        tool_calls: response.tool_calls
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="mb-4">
        <h1 className="text-2xl font-bold">MCP Chat Assistant</h1>
        <p className="text-gray-600">Powered by Gemini + MCP</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((message, i) => (
          <div
            key={i}
            className={`p-4 rounded-lg ${
              message.role === 'user'
                ? 'bg-blue-100 ml-auto max-w-[80%]'
                : 'bg-gray-100 mr-auto max-w-[80%]'
            }`}
          >
            <p className="font-semibold mb-1">
              {message.role === 'user' ? 'You' : 'Assistant'}
            </p>
            <p className="whitespace-pre-wrap">{message.content}</p>

            {/* Show tool calls */}
            {message.tool_calls && message.tool_calls.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-300">
                <p className="text-sm font-semibold mb-2">Tools Used:</p>
                {message.tool_calls.map((call, j) => (
                  <div key={j} className="text-sm bg-white p-2 rounded mb-1">
                    <span className="font-mono text-blue-600">{call.tool}</span>
                    <p className="text-gray-600 text-xs mt-1">{call.result}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="bg-gray-100 p-4 rounded-lg max-w-[80%]">
            <p className="text-gray-600">Thinking...</p>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message... (e.g., 'Create a random user')"
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Send
        </button>
      </form>

      {/* Example prompts */}
      <div className="mt-4 flex flex-wrap gap-2">
        <p className="text-sm text-gray-600 w-full">Try these:</p>
        {[
          'Create a random user',
          'How many users are in the database?',
          'Create a user named John Doe with email john@example.com'
        ].map((prompt) => (
          <button
            key={prompt}
            onClick={() => setInput(prompt)}
            className="text-xs px-3 py-1 bg-gray-200 rounded-full hover:bg-gray-300"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  )
}
```

### 4. User List Component (`components/UserList.tsx`)

```typescript
'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import type { User } from '@/types'

export default function UserList() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const data = await api.getUsers()
      setUsers(data.users)
    } catch (error) {
      console.error('Failed to load users:', error)
    } finally {
      setLoading(false)
    }
  }

  const createRandomUser = async () => {
    try {
      await api.callTool('create-random-user', {})
      await loadUsers() // Refresh list
    } catch (error) {
      console.error('Failed to create user:', error)
    }
  }

  if (loading) {
    return <div>Loading users...</div>
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Users ({users.length})</h2>
        <button
          onClick={createRandomUser}
          className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
        >
          Add Random User
        </button>
      </div>

      <div className="grid gap-4">
        {users.map((user) => (
          <div key={user.id} className="p-4 border rounded-lg hover:shadow-md">
            <div className="flex justify-between">
              <div>
                <h3 className="font-semibold">{user.name}</h3>
                <p className="text-sm text-gray-600">{user.email}</p>
              </div>
              <span className="text-gray-400">#{user.id}</span>
            </div>
            <div className="mt-2 text-sm text-gray-600">
              <p>📍 {user.address}</p>
              <p>📞 {user.phone}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

### 5. Main Page (`app/page.tsx`)

```typescript
'use client'

import { useState } from 'react'
import Chat from '@/components/Chat'
import UserList from '@/components/UserList'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'users'>('chat')

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Tabs */}
      <div className="border-b bg-white">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex gap-4">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-3 border-b-2 transition-colors ${
                activeTab === 'chat'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Chat
            </button>
            <button
              onClick={() => setActiveTab('users')}
              className={`px-4 py-3 border-b-2 transition-colors ${
                activeTab === 'users'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Users
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto">
        {activeTab === 'chat' ? <Chat /> : <UserList />}
      </div>
    </main>
  )
}
```

### 6. Environment Variables (`.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 7. API Route (Optional) (`app/api/chat/route.ts`)

If you want to proxy through Next.js API routes:

```typescript
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

Then update API client to use `/api/chat` instead of direct calls.

## Running the Application

### 1. Start the FastAPI Server

```bash
cd demos-no-framework
python main.py
```

Server runs on `http://localhost:8000`

### 2. Start Next.js Dev Server

```bash
cd mcp-chat-app
npm run dev
```

App runs on `http://localhost:3000`

### 3. Open Browser

Visit `http://localhost:3000`

## Features

### Chat Interface
- Natural language conversations
- Automatic tool calling
- Visual feedback for tool usage
- Example prompts
- Message history

### User Management
- View all users
- Create random users with one click
- Auto-refresh after creation
- User details display

### Real-time Updates
- Loading states
- Error handling
- Optimistic updates
- Toast notifications (optional)

## Advanced Features

### Streaming Responses

For real-time streaming, modify the chat endpoint:

```typescript
// FastAPI
from fastapi.responses import StreamingResponse

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        # Stream tokens as they arrive
        for token in generate_response(request.message):
            yield f"data: {json.dumps({'token': token})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

```typescript
// Next.js
const response = await fetch('/api/chat/stream', {
  method: 'POST',
  body: JSON.stringify({ message })
})

const reader = response.body?.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break

  const chunk = decoder.decode(value)
  // Update UI with streaming text
}
```

### Authentication

Add auth to FastAPI:

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/chat")
async def chat(
    request: ChatRequest,
    credentials = Depends(security)
):
    # Verify token
    if not verify_token(credentials.credentials):
        raise HTTPException(401, "Invalid token")
    # ...
```

### WebSocket Support

For real-time bidirectional communication:

```python
# FastAPI
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = await process_message(data)
        await websocket.send_json(response)
```

```typescript
// Next.js
const ws = new WebSocket('ws://localhost:8000/ws/chat')

ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  // Handle response
}

ws.send(JSON.stringify({ message: 'Hello' }))
```

## Deployment

### Vercel (Next.js)

```bash
vercel deploy
```

Set environment variable:
```
NEXT_PUBLIC_API_URL=https://your-api.com
```

### Railway/Render (FastAPI)

Deploy with `Dockerfile`:

```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### CORS Errors
- Ensure FastAPI CORS middleware includes your Next.js URL
- Check browser console for specific errors
- Verify fetch requests include correct headers

### API Not Connecting
- Confirm both servers are running
- Check `NEXT_PUBLIC_API_URL` is correct
- Use browser network tab to debug requests

### Tool Calls Not Working
- Check Gemini API key is set
- Verify tool schemas are correct
- Check FastAPI logs for errors

## Best Practices

1. **Error Boundaries**: Wrap components in error boundaries
2. **Loading States**: Show spinners/skeletons while loading
3. **Optimistic Updates**: Update UI before API confirms
4. **Debouncing**: Debounce chat input for better UX
5. **Caching**: Use SWR or React Query for data caching
6. **Type Safety**: Use TypeScript throughout
7. **Environment Vars**: Never expose secrets in client code

## Next Steps

- Add user authentication
- Implement conversation history
- Add file upload support
- Create admin dashboard
- Add analytics and monitoring
- Implement rate limiting
- Add unit and e2e tests

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [MCP Specification](https://spec.modelcontextprotocol.io)
- [Gemini API](https://ai.google.dev)
