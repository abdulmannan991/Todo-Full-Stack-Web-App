/**
 * Chat Type Definitions
 *
 * Owner: @ui-expert
 * Tasks: T330, T331
 *
 * Provides TypeScript interfaces for chat functionality:
 * - ChatMessage: Individual message structure
 * - ChatResponse: API response structure
 * - ToolCall: Tool invocation structure
 */

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: ToolCall[];  // T410: Include tool calls for transparency
}

export interface ToolCall {
  tool: string;
  arguments: Record<string, any>;
  result: string;
}

export interface ChatResponse {
  conversation_id: number;
  message: ChatMessage;
  tool_calls: ToolCall[];
  created_at: string;
}

export interface ChatRequest {
  conversation_id: number | null;
  message: string;
}
