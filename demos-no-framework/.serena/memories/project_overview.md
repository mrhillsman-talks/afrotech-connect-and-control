# Project Overview

## Purpose
This is an **MCP (Model Context Protocol) Workshop** demonstration project called `demos-no-framework`. It serves as an educational resource for learning MCP concepts and implementation without using heavy frameworks.

## What It Does
- Implements a complete MCP server with tools, resources, and prompts
- Provides an MCP client for interacting with the server
- Integrates with FastAPI to expose MCP capabilities via REST API
- Manages user data through a JSON-based storage system
- Integrates with RandomUser.me API for generating realistic fake user data
- Demonstrates MCP concepts including:
  - Tool calling (create users, create random users, count users)
  - Resource reading (user data access)
  - Prompts (code review, user management)
  - Sampling (LLM message creation)
  - Roots (filesystem access patterns)

## Key Features
- **MCP Server** (`mcp_server.py`): Implements tools, resources, and prompts following MCP specification
- **MCP Client** (`mcp_client.py`): CLI client for querying and interacting with tools/resources
- **FastAPI Integration** (`main.py`): REST API wrapper around MCP functionality
- **User Management**: CRUD operations on user data stored in JSON
- **External API Integration**: RandomUser.me for realistic test data generation

## Use Cases
- Learning MCP protocol basics
- Understanding client-server MCP architecture
- Building web frontends for MCP servers (via FastAPI)
- Testing MCP implementations
- Workshop/tutorial demonstrations
