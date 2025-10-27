#!/usr/bin/env python3
"""Simple test to verify MCP server-client communication"""
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp():
    """Test basic MCP functionality"""
    print("Starting MCP integration test...")

    # Server parameters
    server_params = StdioServerParameters(
        command=".venv/bin/python",
        args=["mcp_server.py"],
        env=None
    )

    try:
        # Connect to MCP server
        print("1. Connecting to MCP server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize connection
                print("2. Initializing session...")
                await session.initialize()
                print("   ✓ Session initialized")

                # Test listing tools
                print("3. Listing tools...")
                tools_result = await session.list_tools()
                tools = tools_result.tools
                print(f"   ✓ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"     - {tool.name}: {tool.description}")

                # Test listing resources
                print("4. Listing resources...")
                resources_result = await session.list_resources()
                resources = resources_result.resources
                print(f"   ✓ Found {len(resources)} resources:")
                for resource in resources:
                    print(f"     - {resource.name}: {resource.description}")

                # Test listing prompts
                print("5. Listing prompts...")
                prompts_result = await session.list_prompts()
                prompts = prompts_result.prompts
                print(f"   ✓ Found {len(prompts)} prompts:")
                for prompt in prompts:
                    print(f"     - {prompt.name}: {prompt.description}")

                # Test reading a resource
                print("6. Reading resource 'users://all'...")
                result = await session.read_resource("users://all")
                if result.contents:
                    import json
                    users = json.loads(result.contents[0].text)
                    print(f"   ✓ Retrieved {len(users)} users")

                # Test calling a tool
                print("7. Testing 'create-user' tool...")
                tool_result = await session.call_tool(
                    "create-user",
                    {
                        "name": "Test User",
                        "email": "test@example.com",
                        "address": "123 Test St",
                        "phone": "555-0000"
                    }
                )
                if tool_result.content:
                    print(f"   ✓ Tool result: {tool_result.content[0].text}")

                print("\n✅ All tests passed! MCP server and client are working correctly.")
                return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_mcp())
    sys.exit(0 if result else 1)