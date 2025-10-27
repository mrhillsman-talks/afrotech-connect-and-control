import json
import asyncio
from pathlib import Path
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Root,
    Tool,
    TextContent,
)

# Initialize MCP server with capabilities
server = Server("test-video")

# Path to data directory and users file
DATA_DIR = Path(__file__).parent / "data"
USERS_FILE = DATA_DIR / "users.json"


async def load_users() -> list:
    """Load users from JSON file"""
    with open(USERS_FILE, "r") as f:
        return json.load(f)


async def save_users(users: list) -> None:
    """Save users to JSON file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


async def create_user(name: str, email: str, address: str, phone: str) -> int:
    """Create new user and return assigned ID"""
    users = await load_users()
    user_id = len(users) + 1
    users.append({
        "id": user_id,
        "name": name,
        "email": email,
        "address": address,
        "phone": phone
    })
    await save_users(users)
    return user_id


async def fetch_random_user() -> dict:
    """Fetch random user data from randomuser.me API"""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://randomuser.me/api/")
        response.raise_for_status()
        data = response.json()

        # Extract user data from API response
        user_data = data["results"][0]

        # Map API data to our schema
        name = f"{user_data['name']['first']} {user_data['name']['last']}"
        email = user_data["email"]

        # Format address as a single string
        location = user_data["location"]
        address = f"{location['street']['number']} {location['street']['name']}, {location['city']}, {location['state']}, {location['country']} {location['postcode']}"

        # Use primary phone number
        phone = user_data["phone"]

        return {
            "name": name,
            "email": email,
            "address": address,
            "phone": phone
        }


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources"""
    from pydantic import AnyUrl
    return [
        Resource(
            uri=AnyUrl("users://all"),
            name="Users",
            mimeType="application/json",
            description="Get all users data from the database"
        ),
        Resource(
            uri=AnyUrl("users://{userId}/profile"),
            name="User Details",
            mimeType="application/json",
            description="Get a user's details from the database"
        ),
        Resource(
            uri=AnyUrl(f"file://{USERS_FILE.absolute()}"),
            name="Users JSON File",
            mimeType="application/json",
            description="Direct access to the users.json file from the data directory root"
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Handle resource read requests"""
    # Convert AnyUrl to string if needed
    uri = str(uri)

    if uri == "users://all":
        users = await load_users()
        return json.dumps(users)

    # Handle user-details pattern: users://{userId}/profile
    if uri.startswith("users://") and uri.endswith("/profile"):
        user_id = uri.split("/")[2]
        users = await load_users()
        user = next((u for u in users if u["id"] == int(user_id)), None)

        if user is None:
            return json.dumps({"error": "User not found"})

        return json.dumps(user)

    # Handle file:// URIs for root-based file access
    if uri.startswith("file://"):
        file_path = Path(uri.replace("file://", ""))

        # Security check: ensure file is within DATA_DIR
        try:
            file_path = file_path.resolve()
            DATA_DIR.resolve()

            # Check if file is within or is the data directory
            if not (file_path == USERS_FILE.resolve() or file_path.is_relative_to(DATA_DIR.resolve())):
                raise ValueError(f"Access denied: File is outside data directory")

            if not file_path.exists():
                raise ValueError(f"File not found: {file_path}")

            if file_path.is_file():
                with open(file_path, "r") as f:
                    return f.read()
            else:
                raise ValueError(f"Path is not a file: {file_path}")

        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")

    raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="create-user",
            description="Create a new user in the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "address": {"type": "string"},
                    "phone": {"type": "string"}
                },
                "required": ["name", "email", "address", "phone"]
            }
        ),
        Tool(
            name="create-random-user",
            description="Create a random user with fake data",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution"""
    if name == "create-user":
        try:
            user_id = await create_user(
                name=arguments["name"],
                email=arguments["email"],
                address=arguments["address"],
                phone=arguments["phone"]
            )
            return [TextContent(
                type="text",
                text=f"User {user_id} created successfully"
            )]
        except (KeyError, IOError, json.JSONDecodeError) as e:
            return [TextContent(
                type="text",
                text=f"Failed to save user: {str(e)}"
            )]

    elif name == "create-random-user":
        try:
            # Fetch random user from randomuser.me API
            fake_user = await fetch_random_user()

            # Create user with fetched data
            user_id = await create_user(
                name=fake_user["name"],
                email=fake_user["email"],
                address=fake_user["address"],
                phone=fake_user["phone"]
            )

            return [TextContent(
                type="text",
                text=f"User {user_id} created successfully: {fake_user['name']} ({fake_user['email']})"
            )]
        except httpx.HTTPError as e:
            return [TextContent(
                type="text",
                text=f"Failed to fetch random user from API: {str(e)}"
            )]
        except (KeyError, IOError, json.JSONDecodeError) as e:
            return [TextContent(
                type="text",
                text=f"Failed to create user: {str(e)}"
            )]

    raise ValueError(f"Unknown tool: {name}")


@server.list_prompts()
async def list_prompts() -> list:
    """List available prompts"""
    return [{
        "name": "generate-fake-user",
        "description": "Generate a fake user based on a given name",
        "arguments": [{
            "name": "name",
            "description": "Name for the fake user",
            "required": True
        }]
    }]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> dict:
    """Handle prompt requests"""
    if name == "generate-fake-user":
        user_name = arguments.get("name", "")
        return {
            "messages": [{
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Generate a fake user with the name {user_name}. The user should have a realistic email, address, and phone number."
                }
            }]
        }

    raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())