# Technology Stack

## Core Dependencies
- **Python**: 3.12+ (required)
- **MCP SDK**: `mcp>=1.17.0` - Model Context Protocol implementation
- **FastAPI**: `fastapi[standard]>=0.116.1` - REST API framework
- **Google Generative AI**: `google-generativeai>=0.8.5` - Gemini LLM integration
- **httpx**: Async HTTP client (included with mcp package)
- **python-dotenv**: `python-dotenv>=1.1.1` - Environment variable management
- **questionary**: `questionary>=2.1.1` - Interactive CLI prompts

## Development Dependencies (from parent project)
- **ruff**: Linting and formatting
- **mypy**: Static type checking
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support

## Additional Parent Project Dependencies
The parent workspace includes additional packages for extended functionality:
- agno, ddgs, groq, lancedb, matplotlib, pandas, psycopg, pygithub, pypdf, sqlalchemy, tantivy, textual

## External Services
- **RandomUser.me API**: Free API for generating realistic fake user data (no API key required)
- **Gemini API**: Requires GEMINI_API_KEY environment variable

## Data Storage
- JSON files (`data/users.json`) for user data persistence

## MCP Servers Configured (.mcp.json)
- task-master-ai
- sequentialthinking
- serena (IDE assistant)
- github
- playwright
- filesystem
