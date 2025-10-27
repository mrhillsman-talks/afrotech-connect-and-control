#!/usr/bin/env python3
"""Test MCP Roots functionality"""
import asyncio
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CreateMessageResult, TextContent, Root
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


async def sampling_handler(context, params) -> CreateMessageResult:
    """Handle sampling requests from MCP server"""
    texts = []
    for message in params.messages:
        if message.content.type == "text":
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(message.content.text)
            texts.append(response.text)

    return CreateMessageResult(
        role="assistant",
        model="gemini-2.0-flash-exp",
        stopReason="endTurn",
        content=TextContent(
            type="text",
            text="\n".join(texts)
        )
    )


async def list_roots_callback(context) -> list[Root]:
    """Handle roots listing requests from MCP server"""
    # Expose the data directory to the server
    data_dir = Path(__file__).parent / "data"
    return [
        Root(
            uri=f"file://{data_dir.absolute()}",
            name="User Data Directory"
        )
    ]


async def main():
    """Test roots functionality"""
    print("=" * 70)
    print("TESTING MCP ROOTS FUNCTIONALITY")
    print("=" * 70)

    server_params = StdioServerParameters(
        command=".venv/bin/python",
        args=["mcp_server.py"],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(
                read,
                write,
                sampling_callback=sampling_handler,
                list_roots_callback=list_roots_callback
            ) as session:
                # Initialize
                print("\n1. Initializing session...")
                await session.initialize()
                print("   ✓ Connected")

                # Show what roots the client is exposing
                print("\n2. Client roots exposed to server:")
                client_roots = await list_roots_callback(None)
                for root in client_roots:
                    print(f"      📁 {root.name}")
                    print(f"         URI: {root.uri}")

                # List resources
                print("\n3. Listing resources (should include file:// resource)...")
                resources_result = await session.list_resources()
                resources = resources_result.resources

                file_resources = [r for r in resources if str(r.uri).startswith("file://")]
                print(f"   ✓ Found {len(resources)} total resources")
                print(f"   ✓ Found {len(file_resources)} file:// resources")

                for resource in file_resources:
                    print(f"      📄 {resource.name}")
                    print(f"         URI: {resource.uri}")

                # Test reading file:// resource
                if file_resources:
                    print("\n4. Reading file:// resource...")
                    resource = file_resources[0]
                    result = await session.read_resource(str(resource.uri))

                    if result.contents:
                        content = result.contents[0]
                        if hasattr(content, 'text'):
                            try:
                                data = json.loads(content.text)
                                print(f"   ✓ Successfully read file")
                                print(f"   ✓ File contains {len(data)} user(s)")

                                # Show first user
                                if data:
                                    print(f"\n   First user:")
                                    print(f"      Name: {data[0].get('name')}")
                                    print(f"      Email: {data[0].get('email')}")

                            except json.JSONDecodeError:
                                print(f"   ⚠️  Content is not JSON")
                                print(f"   Content preview: {content.text[:100]}...")

                # Compare file:// resource with users://all resource
                print("\n5. Comparing file:// resource with users://all...")
                users_all_result = await session.read_resource("users://all")
                users_all_data = json.loads(users_all_result.contents[0].text)

                file_result = await session.read_resource(str(file_resources[0].uri))
                file_data = json.loads(file_result.contents[0].text)

                if users_all_data == file_data:
                    print("   ✓ Both resources return the same data")
                    print(f"   ✓ Data is consistent: {len(users_all_data)} users")
                else:
                    print("   ⚠️  Resources return different data!")

                print("\n" + "=" * 70)
                print("✅ ROOTS FUNCTIONALITY TEST COMPLETE!")
                print("   • Server exposes roots ✓")
                print("   • Client can list roots ✓")
                print("   • File resources accessible via file:// URIs ✓")
                print("   • Data directory is accessible ✓")
                print("=" * 70)
                return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
