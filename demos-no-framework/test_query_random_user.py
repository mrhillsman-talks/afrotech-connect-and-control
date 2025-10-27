#!/usr/bin/env python3
"""Test Query functionality with create-random-user"""
import asyncio
import sys
import os
from typing import List
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool, TextContent, CreateMessageResult
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


async def sampling_handler(context, params) -> CreateMessageResult:
    """Handle sampling requests from MCP server"""
    texts = []
    for message in params.messages:
        if message.content.type == "text":
            # Generate response using Gemini (non-interactive for testing)
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


async def test_query(session: ClientSession, tools: List[Tool], query: str):
    """Test natural language query with tool calling"""
    print(f"\n🔍 Query: {query}")

    # Convert MCP tools to Gemini function declarations
    from google.generativeai.types import FunctionDeclaration, Tool as GeminiTool

    function_declarations = []
    for tool in tools:
        parameters = {}
        if "properties" in tool.inputSchema:
            parameters["type"] = "object"
            parameters["properties"] = tool.inputSchema["properties"]
            if "required" in tool.inputSchema:
                parameters["required"] = tool.inputSchema["required"]

        function_declarations.append(
            FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=parameters if parameters else None
            )
        )

    gemini_tools = [GeminiTool(function_declarations=function_declarations)]

    # Create model with tools
    model = genai.GenerativeModel(
        "gemini-2.0-flash-exp",
        tools=gemini_tools
    )

    chat = model.start_chat()
    response = chat.send_message(query)

    # Handle tool calls
    iteration = 0
    while response.candidates[0].content.parts:
        iteration += 1
        if iteration > 5:
            print("⚠️  Too many iterations, stopping")
            break

        part = response.candidates[0].content.parts[0]

        if hasattr(part, 'function_call') and part.function_call:
            function_call = part.function_call
            tool_name = function_call.name
            tool_args = dict(function_call.args)

            print(f"   🔧 Tool: {tool_name}")

            # Execute MCP tool
            result = await session.call_tool(tool_name, tool_args)

            # Get text from result
            result_text = ""
            if result.content:
                for content in result.content:
                    if isinstance(content, TextContent):
                        result_text += content.text

            print(f"   ✓ {result_text}")

            # Send result back to model
            response = chat.send_message(
                genai.protos.Content(
                    parts=[genai.protos.Part(
                        function_response={
                            "name": tool_name,
                            "response": {"result": result_text}
                        }
                    )]
                )
            )
        else:
            # Final text response
            final_response = response.text if hasattr(response, 'text') else "No text."
            print(f"   💬 {final_response}")
            return final_response

    return None


async def main():
    """Test query with random user creation"""
    print("=" * 70)
    print("TESTING QUERY WITH CREATE-RANDOM-USER")
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
                tools = (await session.list_tools()).tools

                # Test query that triggers create-random-user
                await test_query(session, tools, "Create a random user")

                print("\n" + "=" * 70)
                print("✅ Query with create-random-user works!")
                print("=" * 70)
                return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
