/**
 * Chat API Client
 *
 * Owner: @ui-expert
 * Tasks: T332, T333
 *
 * Provides:
 * - sendChatMessage: Send message to chat API with JWT authentication
 * - Automatic retry on 409 conflict (optimistic locking)
 * - Error handling for all API responses
 *
 * CRITICAL: All requests include JWT bearer token from Better Auth
 */

import { ChatRequest, ChatResponse, ChatMessage } from '@/types/chat';
import { API_BASE_URL } from '@/lib/config';
const CHAT_API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL
/**
 * Get authentication token from Better Auth
 *
 * @returns JWT token or null if not authenticated
 */
function getAuthToken(): string | null {
  // Better Auth stores token in localStorage or cookies
  // This is a placeholder - actual implementation depends on Better Auth setup
  if (typeof window === 'undefined') return null;

  // Check localStorage for token
  const token = localStorage.getItem('auth_token');
  return token;
}

/**
 * Send a chat message to the backend API
 *
 * @param conversationId - Existing conversation ID or null for new conversation
 * @param message - User message text
 * @param retryCount - Internal retry counter for 409 conflicts
 * @returns ChatResponse with assistant message and tool calls
 * @throws Error on authentication failure, network error, or API error
 */
export async function sendChatMessage(
  conversationId: number | null,
  message: string,
  retryCount: number = 0
): Promise<ChatResponse> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  const requestBody: ChatRequest = {
    conversation_id: conversationId,
    message: message.trim()
  };

  try {
    const response = await fetch(`${CHAT_API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestBody)
    });

    // T333: Handle 409 conflict with retry logic (optimistic locking)
    if (response.status === 409) {
      if (retryCount < 3) {
        // Exponential backoff: 100ms, 200ms, 400ms
        const delay = 100 * Math.pow(2, retryCount);
        await new Promise(resolve => setTimeout(resolve, delay));
        return sendChatMessage(conversationId, message, retryCount + 1);
      } else {
        throw new Error('The conversation was modified by another request. Please try again.');
      }
    }

    // Handle other error responses
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));

      switch (response.status) {
        case 401:
          throw new Error('Authentication failed. Please log in again.');
        case 404:
          throw new Error('Conversation not found.');
        case 500:
          throw new Error('Server error. Please try again later.');
        case 503:
          throw new Error('The assistant is taking longer than expected. Please try again.');
        default:
          throw new Error(errorData.detail || `API error: ${response.status}`);
      }
    }

    const data: ChatResponse = await response.json();
    return data;

  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Network error. Please check your connection.');
  }
}

/**
 * Load conversation history
 *
 * @param conversationId - Conversation ID to load
 * @returns Array of messages in the conversation
 */
export async function loadConversationHistory(
  conversationId: number,
  limit: number = 20
): Promise<ChatMessage[]> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Not authenticated. Please log in.');
  }

  try {
    // CHANGE THIS LINE: Use CHAT_API_URL instead of API_BASE_URL
    const response = await fetch(`${CHAT_API_URL}/api/conversations/${conversationId}/messages?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Conversation not found.');
      }
      throw new Error(`Failed to load conversation history: ${response.status}`);
    }

    const data = await response.json();
    return data.messages;

  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to load conversation history.');
  }
}
