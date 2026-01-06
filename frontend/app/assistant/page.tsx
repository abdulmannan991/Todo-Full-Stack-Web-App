'use client'

/**
 * Flow Assistant - AI Chat Interface (Placeholder)
 *
 * Premium glassmorphic chat interface for the AI Flow Assistant
 * Midnight Genesis aesthetic with Hebbia/OneText-inspired design
 *
 * Owner: @ui-auth-expert + @css-animation-expert
 */

import { useState } from 'react'
import { motion } from 'framer-motion'

export default function FlowAssistantPage() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([
    {
      role: 'assistant',
      content: 'Welcome to Flow Assistant! This is a placeholder for the AI-powered task management assistant. Full implementation coming in Phase 3.',
    },
  ])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    // Add user message
    const userMessage = { role: 'user' as const, content: input }
    setMessages((prev) => [...prev, userMessage])

    // Simulate AI response
    setTimeout(() => {
      const aiMessage = {
        role: 'assistant' as const,
        content: `I received your message: "${input}". This is a placeholder response. Full AI integration coming soon!`,
      }
      setMessages((prev) => [...prev, aiMessage])
    }, 500)

    setInput('')
  }

  return (
    <div className="min-h-screen bg-midnight-bg pt-20 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-violet to-secondary-indigo bg-clip-text text-transparent mb-2">
            Flow Assistant
          </h1>
          <p className="text-text-secondary">
            Your AI-powered task management assistant (Coming Soon)
          </p>
        </motion.div>

        {/* Chat Container */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="glass-card p-6 rounded-2xl mb-6 min-h-[500px] flex flex-col"
        >
          {/* Messages */}
          <div className="flex-1 space-y-4 mb-6 overflow-y-auto max-h-[400px]">
            {messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-4 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-primary-violet/20 border border-primary-violet/30'
                      : 'bg-white/5 border border-white/10'
                  }`}
                >
                  <p className="text-text-primary text-sm">{message.content}</p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="flex items-center space-x-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything about your tasks..."
              className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-text-primary placeholder-text-secondary focus:outline-none focus:ring-2 focus:ring-primary-violet focus:border-transparent transition-all"
            />
            <button
              type="submit"
              disabled={!input.trim()}
              className="px-6 py-3 bg-primary-violet hover:bg-secondary-indigo disabled:bg-white/10 disabled:cursor-not-allowed text-text-primary font-medium rounded-lg transition-all duration-200"
            >
              Send
            </button>
          </form>
        </motion.div>

        {/* Feature Preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4"
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
            <h3 className="text-text-primary font-semibold mb-1">Smart Suggestions</h3>
            <p className="text-text-secondary text-sm">
              Get AI-powered task recommendations
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
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>
            <h3 className="text-text-primary font-semibold mb-1">Quick Actions</h3>
            <p className="text-text-secondary text-sm">
              Create and manage tasks via chat
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
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="text-text-primary font-semibold mb-1">Insights</h3>
            <p className="text-text-secondary text-sm">
              Analyze your productivity patterns
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
