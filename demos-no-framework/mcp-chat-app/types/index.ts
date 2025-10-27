// Chat message types
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  tool_calls?: ToolCall[]
}

export interface ToolCall {
  tool: string
  arguments: Record<string, any>
  result: string
}

export interface ChatResponse {
  response: string
  tool_calls?: ToolCall[]
}

// User types
export interface User {
  id: number
  name: string
  email: string
  address: string
  phone: string
}

export interface UsersResponse {
  users: User[]
  count: number
}

// MCP types
export interface Tool {
  name: string
  description: string
  input_schema: any
}

export interface Resource {
  uri: string
  name: string
  description?: string
  mimeType?: string
}

export interface Prompt {
  name: string
  description?: string
  arguments?: any[]
}

export interface Capabilities {
  tools: Tool[]
  resources: Resource[]
  prompts: Prompt[]
  roots?: any[]
}

// API request/response types
export interface ToolCallRequest {
  tool_name: string
  arguments: Record<string, any>
}

export interface ToolCallResponse {
  result: string
  success: boolean
}

export interface ResourceReadRequest {
  uri: string
}

export interface ResourceReadResponse {
  data: any
  type: string
}

export interface HealthResponse {
  status: string
  service: string
  version: string
  mcp_connected: boolean
}
