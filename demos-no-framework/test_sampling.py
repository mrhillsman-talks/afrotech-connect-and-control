#!/usr/bin/env python3
"""Test MCP sampling functionality"""
import asyncio
import sys
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CreateMessageResult, TextContent
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


async def sampling_handler(context, params) -> dict:
    """Handle sampling requests from MCP server"""
    print("\n📝 Server requested sampling")
    print(f"   Messages: {len(params.messages)}")

    texts = []
    for message in params.messages:
        if message.content.type == "text":
            print(f"   Prompt: {message.content.text[:100]}...")

            # Generate response using Gemini (non-interactive for testing)
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(message.content.text)
            texts.append(response.text)
            print(f"   Generated: {response.text[:100]}...")

    return CreateMessageResult(
        role="assistant",
        model="gemini-2.0-flash-exp",
        stopReason="endTurn",
        content=TextContent(
            type="text",
            text="\n".join(texts)
        )
    )


async def test_sampling():
    """Test the create-random-user tool with sampling"""
    print("Testing MCP Sampling Feature...")
    print("=" * 60)

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
                # Initialize session
                print("1. Initializing session with sampling handler...")
                await session.initialize()
                print("   ✓ Session initialized with sampling callback")

                # Call the create-random-user tool
                print("2. Calling 'create-random-user' tool (uses sampling)...")
                result = await session.call_tool("create-random-user", {})

                if result.content:
                    for content in result.content:
                        if isinstance(content, TextContent):
                            print(f"\n✅ Result: {content.text}")

                print("\n" + "=" * 60)
                print("✅ Sampling test completed successfully!")
                return True

    except Exception as e:
        print(f"\n❌ Sampling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_sampling())
    sys.exit(0 if result else 1)
