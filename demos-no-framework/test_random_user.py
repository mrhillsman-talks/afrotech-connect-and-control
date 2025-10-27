#!/usr/bin/env python3
"""Debug the create-random-user sampling issue"""
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
    print(f"\n📝 Sampling requested")

    texts = []
    for message in params.messages:
        if message.content.type == "text":
            print(f"   Prompt: {message.content.text}")

            # Generate response using Gemini
            model = genai.GenerativeModel("gemini-2.0-flash-exp")
            response = model.generate_content(message.content.text)

            print(f"\n   Generated response:")
            print(f"   {response.text}")
            print()

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


async def main():
    """Test create-random-user"""
    print("=" * 70)
    print("DEBUGGING CREATE-RANDOM-USER")
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
                await session.initialize()

                print("\nCalling create-random-user tool...")
                result = await session.call_tool("create-random-user", {})

                print("\nTool result:")
                if result.content:
                    for content in result.content:
                        if isinstance(content, TextContent):
                            print(f"   {content.text}")

                return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
