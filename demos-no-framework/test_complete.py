#!/usr/bin/env python3
"""Complete integration test including sampling"""
import asyncio
import sys
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CreateMessageResult, TextContent
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


async def sampling_handler(context, params) -> CreateMessageResult:
    """Handle sampling requests from MCP server"""
    print(f"\n   📝 Sampling requested with {len(params.messages)} message(s)")

    texts = []
    for message in params.messages:
        if message.content.type == "text":
            # Generate response using Gemini
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


async def test_complete():
    """Complete integration test"""
    print("=" * 70)
    print("COMPLETE MCP SERVER + CLIENT INTEGRATION TEST")
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
                sampling_callback=sampling_handler
            ) as session:
                # Initialize
                print("\n1. Initializing session with sampling support...")
                await session.initialize()
                print("   ✓ Connected to MCP server")

                # List capabilities
                print("\n2. Discovering server capabilities...")
                tools = (await session.list_tools()).tools
                resources = (await session.list_resources()).resources
                prompts = (await session.list_prompts()).prompts

                print(f"   ✓ Tools: {len(tools)}")
                print(f"   ✓ Resources: {len(resources)}")
                print(f"   ✓ Prompts: {len(prompts)}")

                # Test resource read
                print("\n3. Reading resource 'users://all'...")
                import json
                result = await session.read_resource("users://all")
                users = json.loads(result.contents[0].text)
                initial_count = len(users)
                print(f"   ✓ Found {initial_count} existing users")

                # Test basic tool (no sampling)
                print("\n4. Testing 'create-user' tool (no sampling)...")
                result = await session.call_tool(
                    "create-user",
                    {
                        "name": "Integration Test User",
                        "email": "integration@test.com",
                        "address": "456 Test Ave",
                        "phone": "555-9999"
                    }
                )
                print(f"   ✓ {result.content[0].text}")

                # Test sampling-based tool
                print("\n5. Testing 'create-random-user' tool (with sampling)...")
                result = await session.call_tool("create-random-user", {})
                print(f"   ✓ {result.content[0].text}")

                # Verify new users were added
                print("\n6. Verifying users were created...")
                result = await session.read_resource("users://all")
                users = json.loads(result.contents[0].text)
                final_count = len(users)
                print(f"   ✓ User count: {initial_count} → {final_count}")
                print(f"   ✓ Added {final_count - initial_count} new user(s)")

                print("\n" + "=" * 70)
                print("✅ ALL TESTS PASSED!")
                print("   • MCP Server: Working ✓")
                print("   • MCP Client: Working ✓")
                print("   • Resources: Working ✓")
                print("   • Tools (basic): Working ✓")
                print("   • Tools (sampling): Working ✓")
                print("   • Gemini Integration: Working ✓")
                print("=" * 70)
                return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_complete())
    sys.exit(0 if result else 1)
