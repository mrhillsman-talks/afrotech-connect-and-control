"""
FastAPI server that exposes MCP client functionality for Next.js frontend
"""
import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import CreateMessageResult, TextContent, Root
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool as GeminiTool

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# Global MCP client session
class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.read_stream = None
        self.write_stream = None
        self.stdio_context = None
        self.session_context = None
        self.tools = []
        self.resources = []
        self.prompts = []
        self.roots = []

    async def initialize(self):
        """Initialize MCP client connection"""
        server_params = StdioServerParameters(
            command=".venv/bin/python",
            args=["mcp_server.py"],
            env=None
        )

        # Start stdio client
        self.stdio_context = stdio_client(server_params)
        self.read_stream, self.write_stream = await self.stdio_context.__aenter__()

        # Create session
        self.session_context = ClientSession(
            self.read_stream,
            self.write_stream,
            sampling_callback=self.sampling_handler,
            list_roots_callback=self.list_roots_callback
        )
        self.session = await self.session_context.__aenter__()

        # Initialize session
        await self.session.initialize()

        # Load capabilities
        tools_result = await self.session.list_tools()
        resources_result = await self.session.list_resources()
        prompts_result = await self.session.list_prompts()

        self.tools = tools_result.tools
        self.resources = resources_result.resources
        self.prompts = prompts_result.prompts
        self.roots = await self.list_roots_callback(None)

        print(f"✓ MCP Client initialized: {len(self.tools)} tools, {len(self.resources)} resources")

    async def cleanup(self):
        """Cleanup MCP client connection"""
        if self.session_context:
            await self.session_context.__aexit__(None, None, None)
        if self.stdio_context:
            await self.stdio_context.__aexit__(None, None, None)

    async def sampling_handler(self, context, params) -> CreateMessageResult:
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

    async def list_roots_callback(self, context) -> list[Root]:
        """Handle roots listing requests from MCP server"""
        data_dir = Path(__file__).parent / "data"
        return [
            Root(
                uri=f"file://{data_dir.absolute()}",
                name="User Data Directory"
            )
        ]


# Create global client instance
mcp_client = MCPClient()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting MCP FastAPI Server...")
    await mcp_client.initialize()
    yield
    # Shutdown
    print("🛑 Shutting down MCP FastAPI Server...")
    await mcp_client.cleanup()


# Create FastAPI app
app = FastAPI(
    title="MCP Client API",
    description="REST API for Model Context Protocol client",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default dev server
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = {}


class ToolCallResponse(BaseModel):
    result: str
    success: bool


class ResourceReadRequest(BaseModel):
    uri: str


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "MCP Client API",
        "version": "1.0.0",
        "mcp_connected": mcp_client.session is not None
    }


@app.get("/capabilities")
async def get_capabilities():
    """Get all MCP server capabilities"""
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in mcp_client.tools
        ],
        "resources": [
            {
                "uri": str(resource.uri),
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mimeType
            }
            for resource in mcp_client.resources
        ],
        "prompts": [
            {
                "name": prompt.name,
                "description": prompt.description,
                "arguments": [
                    {"name": arg.name, "description": arg.description, "required": arg.required}
                    for arg in (prompt.arguments or [])
                ]
            }
            for prompt in mcp_client.prompts
        ],
        "roots": [
            {
                "uri": str(root.uri),
                "name": root.name
            }
            for root in mcp_client.roots
        ]
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Natural language chat endpoint with automatic tool calling
    """
    if not mcp_client.session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")

    try:
        query = request.message

        # Convert MCP tools to Gemini function declarations
        function_declarations = []
        for tool in mcp_client.tools:
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

        gemini_tools = [GeminiTool(function_declarations=function_declarations)] if function_declarations else None

        # Create model with tools
        model = genai.GenerativeModel(
            "gemini-2.0-flash-exp",
            tools=gemini_tools
        )

        chat_session = model.start_chat()
        response = chat_session.send_message(query)

        tool_calls_made = []

        # Handle tool calls
        iteration = 0
        while response.candidates[0].content.parts:
            iteration += 1
            if iteration > 5:
                break

            part = response.candidates[0].content.parts[0]

            if hasattr(part, 'function_call') and part.function_call:
                function_call = part.function_call
                tool_name = function_call.name
                tool_args = dict(function_call.args)

                # Execute MCP tool
                result = await mcp_client.session.call_tool(tool_name, tool_args)

                # Get text from result
                result_text = ""
                if result.content:
                    for content in result.content:
                        if isinstance(content, TextContent):
                            result_text += content.text

                tool_calls_made.append({
                    "tool": tool_name,
                    "arguments": tool_args,
                    "result": result_text
                })

                # Send result back to model
                response = chat_session.send_message(
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
                final_response = response.text if hasattr(response, 'text') else "No response generated."
                return ChatResponse(
                    response=final_response,
                    tool_calls=tool_calls_made if tool_calls_made else None
                )

        return ChatResponse(
            response="Maximum iterations reached",
            tool_calls=tool_calls_made if tool_calls_made else None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    """
    Directly call an MCP tool
    """
    if not mcp_client.session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")

    try:
        result = await mcp_client.session.call_tool(request.tool_name, request.arguments)

        result_text = ""
        if result.content:
            for content in result.content:
                if isinstance(content, TextContent):
                    result_text += content.text

        return ToolCallResponse(
            result=result_text,
            success=True
        )

    except Exception as e:
        return ToolCallResponse(
            result=str(e),
            success=False
        )


@app.post("/resources/read")
async def read_resource(request: ResourceReadRequest):
    """
    Read an MCP resource
    """
    if not mcp_client.session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")

    try:
        result = await mcp_client.session.read_resource(request.uri)

        if result.contents:
            content = result.contents[0]
            if hasattr(content, 'text'):
                try:
                    # Try to parse as JSON
                    data = json.loads(content.text)
                    return {"data": data, "type": "json"}
                except json.JSONDecodeError:
                    # Return as text
                    return {"data": content.text, "type": "text"}

        return {"data": None, "type": "none"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resource read error: {str(e)}")


@app.get("/users")
async def get_users():
    """
    Convenience endpoint to get all users
    """
    if not mcp_client.session:
        raise HTTPException(status_code=503, detail="MCP client not initialized")

    try:
        result = await mcp_client.session.read_resource("users://all")
        users = json.loads(result.contents[0].text)
        return {"users": users, "count": len(users)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MCP FastAPI Server on http://localhost:8000")
    print("📚 API docs available at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
