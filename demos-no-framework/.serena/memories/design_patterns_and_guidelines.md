# Design Patterns and Guidelines

## MCP Architecture Pattern

### Server-Client Separation
The project follows a clean separation between MCP server and client:
- **Server** (`mcp_server.py`): Implements MCP protocol handlers
- **Client** (`mcp_client.py`): Consumes MCP server via stdio transport
- **API Layer** (`main.py`): Wraps client for HTTP access

### Communication Patterns

#### Stdio Transport
MCP server and client communicate via stdin/stdout:
```python
# Server uses stdio transport
server = Server("users-db")
stdio = server.run()

# Client spawns server process
params = InitializeParams(...)
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        # Interact with server
```

#### REST API Wrapper
FastAPI provides HTTP interface to MCP functionality:
- Chat endpoint: Natural language → tool selection → execution
- Tool endpoint: Direct tool calling
- Resource endpoint: Direct resource reading

## Async/Await Pattern
All I/O operations are async:
- HTTP requests (httpx)
- MCP client-server communication
- File operations when needed
- API calls to external services

## Tool Design Pattern

### Tool Schema
Tools follow MCP specification with:
- Name (kebab-case)
- Description
- Input schema (JSON schema)
- Handler function

Example:
```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="create-user",
            description="Create a new user",
            inputSchema={...}
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    # Handle tool execution
```

## Resource Pattern

### URI-based Resources
Resources use URI scheme for identification:
- `users://all` - All users
- `users://{id}` - Specific user

### Content Types
Resources return appropriate MIME types:
- `application/json` for structured data
- `text/plain` for text content

## Error Handling Pattern

### Graceful Degradation
- HTTP errors are caught and reported with status codes
- JSON parsing errors handled with clear messages
- Missing data returns empty results rather than failing
- Tool errors return error messages in standardized format

### Error Responses
```python
# Tool errors return TextContent with error message
return [
    TextContent(
        type="text",
        text=f"Error: {error_message}"
    )
]
```

## Data Persistence Pattern

### JSON File Storage
- Simple JSON file for user data
- Load entire file into memory
- Modify in memory
- Write back to disk
- No database complexity for demo purposes

### Data Structure
```json
{
  "users": [
    {
      "id": 1,
      "name": "string",
      "email": "string",
      "address": "string",
      "phone": "string"
    }
  ],
  "next_id": 2
}
```

## Integration Patterns

### External API Integration
- Use httpx for async HTTP requests
- Map external API responses to internal schema
- Handle API errors gracefully
- No API key required for RandomUser.me

### LLM Integration
- Google Gemini via google-generativeai
- Requires GEMINI_API_KEY environment variable
- Used for natural language query understanding
- Tool selection and argument extraction

## Testing Patterns

### Script-based Tests
Tests are standalone Python scripts (not pytest fixtures):
- Each test function prints results
- Manual execution of test files
- Request/response validation
- Integration testing with running server

### Test Structure
```python
def test_feature():
    print("Testing feature...")
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
```

## Configuration Patterns

### Environment Variables
- Use python-dotenv for .env file loading
- Required: GEMINI_API_KEY
- Optional: API keys for other services

### MCP Server Configuration
- .mcp.json for MCP server definitions
- Supports multiple MCP servers
- Environment variable injection
- Different transport types (stdio, SSE)

## Code Organization Guidelines

### Single Responsibility
- One file per major component
- Server, client, API layer separated
- Test files focused on specific functionality

### Minimal Dependencies
- Keep dependencies lean
- Only include what's needed
- Parent project has extended dependencies

### Educational Focus
- Code optimized for learning
- Clear, readable implementations
- Comments explain MCP concepts
- Documentation-heavy approach
