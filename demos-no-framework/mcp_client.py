import asyncio
import json
import os
from typing import Any, Dict, List

import questionary
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import (
    Tool,
    Prompt,
    TextContent,
    PromptMessage,
    CreateMessageResult,
    Root,
)
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


async def handle_server_message_prompt(message: PromptMessage) -> str | None:
    """Handle prompt message from server and optionally execute with LLM"""
    if message.content.type != "text":
        return None

    print(message.content.text)
    run = await questionary.confirm(
        "Would you like to run the above prompt?",
        default=True
    ).ask_async()

    if not run:
        return None

    # Generate response using Gemini
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(message.content.text)

    return response.text


async def handle_query(session: ClientSession, tools: List[Tool]):
    """Handle natural language query with tool calling"""
    query = await questionary.text("Enter your query:").ask_async()

    # Convert MCP tools to Gemini function declarations
    from google.generativeai.types import FunctionDeclaration, Tool as GeminiTool

    function_declarations = []
    for tool in tools:
        # Convert MCP schema to Gemini format
        # Gemini expects the schema without the root "type": "object"
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
    while response.candidates[0].content.parts:
        part = response.candidates[0].content.parts[0]

        # Check if it's a function call
        if hasattr(part, 'function_call') and part.function_call:
            function_call = part.function_call
            tool_name = function_call.name
            tool_args = dict(function_call.args)

            # Execute MCP tool
            result = await session.call_tool(tool_name, tool_args)

            # Get text from result
            result_text = ""
            if result.content:
                for content in result.content:
                    if isinstance(content, TextContent):
                        result_text += content.text

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
            print(response.text if hasattr(response, 'text') else "No text generated.")
            break


async def handle_tool(session: ClientSession, tool: Tool):
    """Execute a specific MCP tool with user input"""
    args: Dict[str, str] = {}

    # Collect arguments from user
    properties = tool.inputSchema.get("properties", {})
    for key, value in properties.items():
        arg_value = await questionary.text(
            f"Enter value for {key} ({value.get('type', 'string')}):"
        ).ask_async()
        args[key] = arg_value

    # Call tool
    result = await session.call_tool(tool.name, args)

    # Display result
    if result.content:
        for content in result.content:
            if isinstance(content, TextContent):
                print(content.text)


async def handle_resource(session: ClientSession, uri: str):
    """Read an MCP resource with parameter substitution"""
    # Convert AnyUrl to string if needed
    uri_str = str(uri)
    final_uri = uri_str

    # Find and replace URI parameters
    import re
    param_matches = re.findall(r'{([^}]+)}', uri_str)

    for param_name in param_matches:
        param_value = await questionary.text(
            f"Enter value for {param_name}:"
        ).ask_async()
        final_uri = final_uri.replace(f"{{{param_name}}}", param_value)

    # Read resource
    result = await session.read_resource(final_uri)

    # Display result
    if result.contents:
        content = result.contents[0]
        if hasattr(content, 'text'):
            try:
                parsed = json.loads(content.text)
                print(json.dumps(parsed, indent=2))
            except json.JSONDecodeError:
                print(content.text)


async def handle_prompt(session: ClientSession, prompt: Prompt):
    """Get and optionally execute an MCP prompt"""
    args: Dict[str, str] = {}

    # Collect arguments from user
    for arg in prompt.arguments or []:
        arg_value = await questionary.text(
            f"Enter value for {arg.name}:"
        ).ask_async()
        args[arg.name] = arg_value

    # Get prompt
    result = await session.get_prompt(prompt.name, args)

    # Handle messages
    for message in result.messages:
        await handle_server_message_prompt(message)


async def list_roots_callback(context) -> list[Root]:
    """Handle roots listing requests from MCP server"""
    # Expose the data directory to the server
    from pathlib import Path
    data_dir = Path(__file__).parent / "data"

    return [
        Root(
            uri=f"file://{data_dir.absolute()}",
            name="User Data Directory"
        )
    ]


async def sampling_handler(context, params) -> CreateMessageResult:
    """Handle sampling requests from MCP server"""
    texts: List[str] = []

    for message in params.messages:
        text = await handle_server_message_prompt(message)
        if text is not None:
            texts.append(text)

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
    """Main client loop"""
    # Server parameters
    server_params = StdioServerParameters(
        command=".venv/bin/python",
        args=["mcp_server.py"],
        env=None
    )

    # Connect to MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read,
            write,
            sampling_callback=sampling_handler,
            list_roots_callback=list_roots_callback
        ) as session:
            # Initialize connection
            await session.initialize()

            # List all capabilities
            tools_result = await session.list_tools()
            prompts_result = await session.list_prompts()
            resources_result = await session.list_resources()

            tools = tools_result.tools
            prompts = prompts_result.prompts
            resources = resources_result.resources

            # Get exposed client roots
            from pathlib import Path
            data_dir = Path(__file__).parent / "data"
            roots = [
                Root(
                    uri=f"file://{data_dir.absolute()}",
                    name="User Data Directory"
                )
            ]

            print("You are connected!")
            print(f"Server capabilities: {len(tools)} tools, {len(resources)} resources, {len(prompts)} prompts")
            print(f"Client roots exposed: {len(roots)} root(s)")

            # Main interaction loop
            while True:
                option = await questionary.select(
                    "What would you like to do?",
                    choices=["Query", "Tools", "Resources", "Prompts", "Roots", "Exit"]
                ).ask_async()

                if option == "Exit":
                    break
                elif option == "Tools":
                    tool_choices = [
                        questionary.Choice(
                            title=tool.name,
                            value=tool.name
                        ) for tool in tools
                    ]

                    tool_name = await questionary.select(
                        "Select a tool:",
                        choices=tool_choices
                    ).ask_async()

                    tool = next((t for t in tools if t.name == tool_name), None)
                    if tool:
                        await handle_tool(session, tool)
                    else:
                        print("Tool not found.")

                elif option == "Resources":
                    resource_choices = [
                        questionary.Choice(
                            title=f"{r.name} - {r.description or ''}",
                            value=r.uri
                        ) for r in resources
                    ]

                    uri = await questionary.select(
                        "Select a resource:",
                        choices=resource_choices
                    ).ask_async()

                    await handle_resource(session, uri)

                elif option == "Prompts":
                    prompt_choices = [
                        questionary.Choice(
                            title=f"{p.name} - {p.description or ''}",
                            value=p.name
                        ) for p in prompts
                    ]

                    prompt_name = await questionary.select(
                        "Select a prompt:",
                        choices=prompt_choices
                    ).ask_async()

                    prompt = next((p for p in prompts if p.name == prompt_name), None)
                    if prompt:
                        await handle_prompt(session, prompt)
                    else:
                        print("Prompt not found.")

                elif option == "Roots":
                    if not roots:
                        print("No roots available.")
                    else:
                        print("\nAvailable roots:")
                        for root in roots:
                            print(f"  📁 {root.name}")
                            print(f"     URI: {root.uri}")
                            print()

                elif option == "Query":
                    await handle_query(session, tools)


if __name__ == "__main__":
    asyncio.run(main())