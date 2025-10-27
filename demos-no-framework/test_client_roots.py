#!/usr/bin/env python3
"""Quick test to verify the client shows roots properly"""
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
    data_dir = Path(__file__).parent / "data"
    return [
        Root(
            uri=f"file://{data_dir.absolute()}",
            name="User Data Directory"
        )
    ]


async def main():
    """Quick test of client with roots"""
    server_params = StdioServerParameters(
        command=".venv/bin/python",
        args=["mcp_server.py"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read,
            write,
            sampling_callback=sampling_handler,
            list_roots_callback=list_roots_callback
        ) as session:
            await session.initialize()

            tools = (await session.list_tools()).tools
            resources = (await session.list_resources()).resources
            prompts = (await session.list_prompts()).prompts

            # Show what we have
            print("You are connected!")
            print(f"Server capabilities: {len(tools)} tools, {len(resources)} resources, {len(prompts)} prompts")

            client_roots = await list_roots_callback(None)
            print(f"Client roots exposed: {len(client_roots)} root(s)")

            for root in client_roots:
                print(f"  📁 {root.name}: {root.uri}")

            # Show file:// resources
            file_resources = [r for r in resources if str(r.uri).startswith("file://")]
            print(f"\nFile resources available: {len(file_resources)}")
            for r in file_resources:
                print(f"  📄 {r.name}: {r.uri}")


if __name__ == "__main__":
    asyncio.run(main())
