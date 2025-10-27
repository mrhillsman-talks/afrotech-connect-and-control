# Project Structure

## Directory Layout
```
demos-no-framework/
├── data/                          # Data storage directory
│   └── users.json                 # User data (JSON format)
├── .venv/                         # Virtual environment
├── .claude/                       # Claude Code configuration
├── .serena/                       # Serena MCP server data
├── mcp_server.py                  # MCP server implementation
├── mcp_client.py                  # MCP client CLI
├── main.py                        # FastAPI REST API server
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project metadata
├── .mcp.json                      # MCP server configurations
├── README.md                      # Project readme (minimal)
├── QUICKSTART.md                  # Quick start guide
├── API_INTEGRATION.md             # RandomUser.me API documentation
├── FASTAPI_README.md              # FastAPI integration guide
├── NEXTJS_EXAMPLE.md              # Next.js frontend example
└── test_*.py                      # Test files
    ├── test_api.py                # FastAPI endpoint tests
    ├── test_mcp.py                # MCP functionality tests
    ├── test_client_roots.py       # Client roots tests
    ├── test_complete.py           # Complete workflow tests
    ├── test_full_integration.py   # Full integration tests
    ├── test_query.py              # Query handling tests
    ├── test_query_random_user.py  # Random user query tests
    ├── test_random_user.py        # Random user tests
    ├── test_randomuser_api.py     # RandomUser.me API tests
    ├── test_roots.py              # Server roots tests
    └── test_sampling.py           # Sampling tests
```

## Key Files

### Core Implementation
- **mcp_server.py**: MCP server with tools, resources, prompts
  - Tools: `create-user`, `create-random-user`, `count-users`
  - Resources: `users://all`, `users://{id}`
  - Prompts: `code-review`, `user-management`
  - Functions: `load_users`, `save_users`, `create_user`, `fetch_random_user`

- **mcp_client.py**: Interactive MCP client
  - Functions: `handle_query`, `handle_tool`, `handle_resource`, `handle_prompt`
  - Callbacks: `list_roots_callback`, `sampling_handler`

- **main.py**: FastAPI REST API integration
  - Class: `MCPClient` - manages MCP server process
  - Models: `ChatRequest`, `ChatResponse`, `ToolCallRequest`, etc.
  - Endpoints: `/`, `/chat`, `/tools/call`, `/resources/read`, `/users`

### Configuration
- **requirements.txt**: Minimal dependencies (mcp, python-dotenv, questionary, google-generativeai)
- **pyproject.toml**: Project metadata, dependencies configuration
- **.mcp.json**: MCP server configurations (task-master-ai, serena, github, playwright, filesystem, sequentialthinking)

### Documentation
- **QUICKSTART.md**: 5-minute setup guide for getting started
- **API_INTEGRATION.md**: Details on RandomUser.me API integration
- **FASTAPI_README.md**: Complete API documentation
- **NEXTJS_EXAMPLE.md**: Frontend integration examples

### Data
- **data/users.json**: JSON file storing user records with fields: id, name, email, address, phone

## Architecture Flow
```
Frontend (Next.js/HTML)
    ↓ HTTP/REST
FastAPI Server (main.py)
    ↓ stdio
MCP Server (mcp_server.py)
    ↓
    ├→ JSON Database (users.json)
    └→ RandomUser.me API
```
