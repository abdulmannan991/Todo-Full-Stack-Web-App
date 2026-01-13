'use client'

/**
 * Flow Assistant - AI Chat Interface
 *
 * Premium glassmorphic chat interface for the AI Flow Assistant
 * Midnight Genesis aesthetic with Hebbia/OneText-inspired design
 *
 * Owner: @ui-auth-expert + @css-animation-expert
 * Tasks: T345, T346, T347, T395, T396, T397, T398
 *
 * Features:
 * - Real AI-powered task management via chat
 * - Conversation persistence across sessions (localStorage)
 * - JWT authentication with Better Auth
 * - Tool call transparency
 */

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { ChatInterface } from '@/components/chat/ChatInterface'
import { sendChatMessage, loadConversationHistory } from '@/lib/api/chat'
import { ChatMessage } from '@/types/chat'

export default function FlowAssistantPage() {
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [errorType, setErrorType] = useState<'401' | '503' | '500' | 'generic' | null>(null)
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)

  // T396: Load conversation history on component mount
  useEffect(() => {
    const loadHistory = async () => {
      // T395: Load conversation_id from localStorage
      const storedConversationId = localStorage.getItem('flow_assistant_conversation_id')
      if (storedConversationId) {
        const id = parseInt(storedConversationId, 10)
        if (!isNaN(id)) {
          setConversationId(id)

          // T397: Fetch and display previous messages from conversation
          setIsLoadingHistory(true)
          try {
            const history = await loadConversationHistory(id, 20)
            setMessages(history)
          } catch (err) {
            console.error('Failed to load conversation history:', err)
            // Clear invalid conversation ID
            localStorage.removeItem('flow_assistant_conversation_id')
            setConversationId(null)
          } finally {
            setIsLoadingHistory(false)
          }
        }
      }
    }

    loadHistory()
  }, [])

  // T346: Implement message sending handler
  const handleSendMessage = async (message: string) => {
    setIsLoading(true)
    setError(null)

    // Add user message to UI immediately (optimistic update)
    const userMessage: ChatMessage = {
      role: 'user',
      content: message
    }
    setMessages(prev => [...prev, userMessage])

    // CRITICAL: Timeout mechanism to prevent hanging loading state
    // If the request takes longer than 60 seconds, force reset loading state
    const timeoutId = setTimeout(() => {
      setIsLoading(false)
      setError('Request timed out. The server may be processing your request. Please refresh to see updates.')
      setErrorType('503')
    }, 60000) // 60 seconds timeout

    try {
      // Send message to backend
      const response = await sendChatMessage(conversationId, message)

      // Clear timeout if request completes successfully
      clearTimeout(timeoutId)

      // T395: Store conversation_id in localStorage for persistence
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id)
        localStorage.setItem('flow_assistant_conversation_id', response.conversation_id.toString())
      }

      // T347: Display assistant response with task confirmation
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message.content,
        tool_calls: response.tool_calls  // T410: Include tool calls for transparency
      }
      setMessages(prev => [...prev, assistantMessage])

    } catch (err) {
      // Clear timeout on error to prevent memory leak
      clearTimeout(timeoutId)

      // T402-T404: Enhanced error handling with friendly messages
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message'

      // Detect error type from message content
      if (errorMessage.includes('Authentication failed') || errorMessage.includes('log in again')) {
        setErrorType('401')
        setError('Your session has expired. Please log in again to continue.')
      } else if (errorMessage.includes('taking longer than expected') || errorMessage.includes('503')) {
        setErrorType('503')
        setError('The AI assistant is temporarily unavailable. Please try again in a moment.')
      } else if (errorMessage.includes('Server error') || errorMessage.includes('500')) {
        setErrorType('500')
        setError('Something went wrong on our end. Our team has been notified. Please try again.')
      } else {
        setErrorType('generic')
        setError(errorMessage)
      }

      // Remove optimistic user message on error
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
    }
  }

  // T398: Handle "new conversation" action
  const handleNewConversation = () => {
    setConversationId(null)
    setMessages([])
    localStorage.removeItem('flow_assistant_conversation_id')
    setError(null)
    setErrorType(null)
  }

  return (
    <div className="min-h-screen bg-midnight-bg pt-20 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8 flex items-center justify-between"
        >
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-violet to-secondary-indigo bg-clip-text text-transparent mb-2">
              Flow Assistant
            </h1>
            <p className="text-text-secondary">
              Your AI-powered task management assistant
            </p>
          </div>

          {/* T398: New Conversation Button */}
          {conversationId && (
            <button
              onClick={handleNewConversation}
              className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 text-text-primary rounded-lg transition-all duration-200 text-sm"
            >
              New Conversation
            </button>
          )}
        </motion.div>

        {/* T345: Chat Interface Integration */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="glass-card rounded-2xl overflow-hidden"
          style={{ height: 'calc(100vh - 250px)', minHeight: '500px' }}
        >
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            error={error}
            errorType={errorType}
          />
        </motion.div>

        {/* Feature Preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6"
        >
          <div className="glass-card p-4 rounded-lg">
            <div className="w-10 h-10 rounded-lg bg-primary-violet/20 flex items-center justify-center mb-3">
              <svg
                className="w-6 h-6 text-primary-violet"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
            </div>
            <h3 className="text-text-primary font-semibold mb-1">Create Tasks</h3>
            <p className="text-text-secondary text-sm">
              "Add a task to buy groceries"
            </p>
          </div>

          <div className="glass-card p-4 rounded-lg">
            <div className="w-10 h-10 rounded-lg bg-secondary-indigo/20 flex items-center justify-center mb-3">
              <svg
                className="w-6 h-6 text-secondary-indigo"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-text-primary font-semibold mb-1">Manage Tasks</h3>
            <p className="text-text-secondary text-sm">
              "Show my tasks" or "Mark task 1 as done"
            </p>
          </div>

          <div className="glass-card p-4 rounded-lg">
            <div className="w-10 h-10 rounded-lg bg-primary-violet/20 flex items-center justify-center mb-3">
              <svg
                className="w-6 h-6 text-primary-violet"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <h3 className="text-text-primary font-semibold mb-1">Natural Language</h3>
            <p className="text-text-secondary text-sm">
              Chat naturally with your assistant
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
