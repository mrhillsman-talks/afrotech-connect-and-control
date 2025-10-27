# Code Style and Conventions

## Formatting and Linting
The project uses **Ruff** for both linting and formatting (configured in parent `pyproject.toml`):
- **Line length**: 120 characters
- **Excluded directories**: `.venv*`
- **Import rules**: F401 and F403 ignored in `__init__.py` files

## Type Checking
**MyPy** configuration (from parent project):
- Type checking enabled for untyped definitions: `check_untyped_defs = true`
- No implicit optional types: `no_implicit_optional = true`
- Warn on unused configs: `warn_unused_configs = true`
- Pydantic plugin enabled
- Excluded directories: `.venv*`
- Ignored imports: pgvector, setuptools, nest_asyncio, agno, requests

## Python Conventions
- **Python version**: 3.12+
- **Type hints**: Expected throughout the codebase
- **Async/await**: Used for MCP operations and HTTP requests
- **Docstrings**: Present for functions explaining purpose

## Naming Conventions
Based on code review:
- **Functions**: snake_case (e.g., `fetch_random_user`, `load_users`)
- **Classes**: PascalCase (e.g., `MCPClient`, `ChatRequest`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DATA_DIR`, `USERS_FILE`, `BASE_URL`)
- **Variables**: snake_case

## Code Organization
- **MCP Server**: All server logic in `mcp_server.py`
- **MCP Client**: Client interactions in `mcp_client.py`
- **API Layer**: FastAPI endpoints in `main.py`
- **Tests**: Separate files prefixed with `test_`
- **Data**: Stored in `data/` directory

## Error Handling
- HTTP errors handled with proper status codes
- JSON parsing errors caught and reported
- Database/file errors handled gracefully
- Tool execution errors returned in standardized format

## Dependencies Management
- `requirements.txt` for pip-based installation
- `pyproject.toml` for project metadata and tool configuration
- UV package manager support configured
