/**
 * ChatInterface Wrapper Component
 *
 * Owner: @ui-expert
 * Task: T334
 *
 * Provides a wrapper around OpenAI ChatKit components for the Flow Assistant.
 * Handles message rendering, input, and loading states.
 *
 * Features:
 * - Message list with user/assistant distinction
 * - Input field with send button
 * - Loading indicator during AI processing
 * - Error message display
 * - Tool call transparency (expandable details)
 */

'use client';

import { useState } from 'react';
import { ChatMessage, ToolCall } from '@/types/chat';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
  error?: string | null;
  errorType?: '401' | '503' | '500' | 'generic' | null;
}

// T411: Helper to format tool calls in a user-friendly way
function formatToolCall(toolCall: ToolCall): string {
  const toolNames: Record<string, string> = {
    'add_task': '➕ Creating task',
    'list_tasks': '📋 Listing tasks',
    'complete_task': '✅ Completing task',
    'delete_task': '🗑️ Deleting task',
    'update_task': '✏️ Updating task'
  };

  return toolNames[toolCall.tool] || `🔧 ${toolCall.tool}`;
}


export function ChatInterface({
  messages,
  onSendMessage,
  isLoading,
  error,
  errorType
}: ChatInterfaceProps) {
  const [inputValue, setInputValue] = useState('');
  const [expandedToolCalls, setExpandedToolCalls] = useState<Set<number>>(new Set());

  const toggleToolCalls = (index: number) => {
    const newExpanded = new Set(expandedToolCalls);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedToolCalls(newExpanded);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading) {
      return;
    }

    const message = inputValue.trim();
    setInputValue('');

    try {
      await onSendMessage(message);
    } catch (err) {
      // Error handled by parent component
      console.error('Failed to send message:', err);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg font-medium">Welcome to Flow Assistant!</p>
            <p className="mt-2">Start a conversation to manage your tasks with natural language.</p>
            <p className="mt-4 text-sm">Try: "Add a task to buy groceries" or "Show my tasks"</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-primary-violet to-secondary-indigo text-white'
                    : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>

                {/* T410-T411: Tool Call Transparency */}
                {msg.tool_calls && msg.tool_calls.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
                    {msg.tool_calls.map((toolCall, tcIndex) => (
                      <div key={tcIndex} className="text-sm">
                        <button
                          onClick={() => toggleToolCalls(index)}
                          className="flex items-center space-x-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
                        >
                          <span className="font-medium">{formatToolCall(toolCall)}</span>
                          <span className="text-xs">{expandedToolCalls.has(index) ? '▼' : '▶'}</span>
                        </button>
                        {expandedToolCalls.has(index) && (
                          <div className="ml-4 mt-2 p-2 bg-white/50 dark:bg-gray-900/50 rounded text-xs space-y-1">
                            <div className="text-gray-600 dark:text-gray-400">
                              <span className="font-semibold">Result:</span> {toolCall.result}
                            </div>
                            {Object.keys(toolCall.arguments).length > 0 && (
                              <div className="text-gray-600 dark:text-gray-400">
                                <span className="font-semibold">Arguments:</span>{' '}
                                {JSON.stringify(toolCall.arguments, null, 2)}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        {/* T402-T404: Enhanced Error Messages with Friendly UI */}
        {error && (
          <div className={`rounded-lg p-4 border ${
            errorType === '401'
              ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
              : errorType === '503'
              ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
              : errorType === '500'
              ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
              : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
          }`}>
            <div className="flex items-start space-x-3">
              {/* Error Icon */}
              <div className="flex-shrink-0">
                {errorType === '401' ? (
                  <svg className="w-5 h-5 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                ) : errorType === '503' ? (
                  <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                )}
              </div>

              {/* Error Content */}
              <div className="flex-1">
                <p className={`text-sm font-medium ${
                  errorType === '401'
                    ? 'text-yellow-800 dark:text-yellow-200'
                    : errorType === '503'
                    ? 'text-blue-800 dark:text-blue-200'
                    : 'text-red-800 dark:text-red-200'
                }`}>
                  {error}
                </p>

                {/* Action Buttons */}
                {errorType === '401' && (
                  <button
                    onClick={() => window.location.href = '/login'}
                    className="mt-2 text-sm font-medium text-yellow-700 dark:text-yellow-300 hover:text-yellow-900 dark:hover:text-yellow-100 underline"
                  >
                    Go to Login →
                  </button>
                )}
                {errorType === '503' && (
                  <p className="mt-1 text-xs text-blue-600 dark:text-blue-400">
                    The assistant will be back shortly. You can try sending your message again.
                  </p>
                )}
                {errorType === '500' && (
                  <p className="mt-1 text-xs text-red-600 dark:text-red-400">
                    If this problem persists, please contact support.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="border-t border-gray-200 dark:border-gray-700 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            maxLength={2000}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="px-6 py-2 bg-gradient-to-r from-primary-violet to-secondary-indigo text-white rounded-lg hover:bg-gradient-to-r from-primary-violet-700 to-secondary-indigo-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
          Press Enter to send • {inputValue.length}/2000 characters
        </p>
      </div>
    </div>
  );
}
