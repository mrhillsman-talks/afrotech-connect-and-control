import type {
  ChatResponse,
  Capabilities,
  UsersResponse,
  ToolCallRequest,
  ToolCallResponse,
  ResourceReadRequest,
  ResourceReadResponse,
  HealthResponse,
} from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * API client for MCP FastAPI server
 */
export const api = {
  /**
   * Send a chat message and get AI response with optional tool calls
   */
  async chat(message: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message }),
    })

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.statusText}`)
    }

    return response.json()
  },

  /**
   * Get MCP server capabilities (tools, resources, prompts)
   */
  async getCapabilities(): Promise<Capabilities> {
    const response = await fetch(`${API_BASE}/capabilities`)

    if (!response.ok) {
      throw new Error(`Failed to get capabilities: ${response.statusText}`)
    }

    return response.json()
  },

  /**
   * Get all users from the database
   */
  async getUsers(): Promise<UsersResponse> {
    const response = await fetch(`${API_BASE}/users`)

    if (!response.ok) {
      throw new Error(`Failed to get users: ${response.statusText}`)
    }

    return response.json()
  },

  /**
   * Call an MCP tool directly
   */
  async callTool(toolName: string, args: Record<string, any>): Promise<ToolCallResponse> {
    const request: ToolCallRequest = {
      tool_name: toolName,
      arguments: args,
    }

    const response = await fetch(`${API_BASE}/tools/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Tool call failed: ${response.statusText}`)
    }

    return response.json()
  },

  /**
   * Read an MCP resource by URI
   */
  async readResource(uri: string): Promise<ResourceReadResponse> {
    const request: ResourceReadRequest = { uri }

    const response = await fetch(`${API_BASE}/resources/read`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      throw new Error(`Resource read failed: ${response.statusText}`)
    }

    return response.json()
  },

  /**
   * Health check endpoint
   */
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${API_BASE}/`)

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`)
    }

    return response.json()
  },
}
