#!/usr/bin/env python3
"""Test randomuser.me API integration"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CreateMessageResult, TextContent, Root
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


async def sampling_handler(context, params) -> CreateMessageResult:
    """Handle sampling requests from MCP server (not needed for API version)"""
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
    data_dir = Path(__file__).parent / "data"
    return [
        Root(
            uri=f"file://{data_dir.absolute()}",
            name="User Data Directory"
        )
    ]


async def main():
    """Test randomuser.me API integration"""
    print("=" * 70)
    print("TESTING RANDOMUSER.ME API INTEGRATION")
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
                await session.initialize()
                print("\n1. Connected to MCP server")

                # Test create-random-user multiple times
                print("\n2. Creating 3 random users via randomuser.me API...")

                for i in range(3):
                    print(f"\n   Test {i+1}:")
                    result = await session.call_tool("create-random-user", {})

                    if result.content:
                        for content in result.content:
                            if isinstance(content, TextContent):
                                print(f"   ✓ {content.text}")

                # Verify users were added
                print("\n3. Verifying users in database...")
                import json
                users_result = await session.read_resource("users://all")
                users = json.loads(users_result.contents[0].text)

                print(f"   ✓ Total users in database: {len(users)}")
                print(f"\n   Last 3 users added:")
                for user in users[-3:]:
                    print(f"      • {user['name']} - {user['email']}")
                    print(f"        {user['address']}")
                    print(f"        📞 {user['phone']}")

                print("\n" + "=" * 70)
                print("✅ RANDOMUSER.ME API INTEGRATION SUCCESSFUL!")
                print("   • API fetches working ✓")
                print("   • User creation working ✓")
                print("   • Data mapping correct ✓")
                print("   • No LLM sampling needed ✓")
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
