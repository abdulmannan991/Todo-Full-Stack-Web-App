'use client'

/**
 * Dashboard Page for Midnight Genesis
 *
 * Sprint 2 - Task: T089 (Task Integration)
 * Protected page requiring authentication
 * Created by @ui-auth-expert (T032)
 * Enhanced with Task CRUD functionality (Sprint 2)
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useSession } from '@/lib/auth-client'
import { getDisplayName } from '@/utils/profile'
import Footer from '@/components/Footer'
import TaskCreateForm from '@/components/TaskCreateForm'
import TaskGrid from '@/components/TaskGrid'
import TaskSkeleton from '@/components/TaskSkeleton'
import EmptyState from '@/components/EmptyState'
import { Task } from '@/components/TaskCard'
import { API_BASE_URL } from '@/lib/config'

export default function DashboardPage() {
  const router = useRouter()
  const { data: session, isPending } = useSession()
  const [mounted, setMounted] = useState(false)
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoadingTasks, setIsLoadingTasks] = useState(true)
  const [tasksError, setTasksError] = useState<string | null>(null)
  const [stats, setStats] = useState<{ total_tasks: number; completed_tasks: number } | null>(null)
  const [isLoadingStats, setIsLoadingStats] = useState(true)
  const [statsError, setStatsError] = useState<string | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Fix hydration: Only access session after mount
  useEffect(() => {
    setMounted(true)
  }, [])

  // Redirect to login if not authenticated
  useEffect(() => {
    if (mounted && !isPending && !session?.user) {
      router.push('/login')
    }
  }, [mounted, session, isPending, router])

  /**
   * Fetch user statistics from backend API
   * Uses GET /users/me/stats endpoint with JWT authentication
   */
  const fetchStats = async () => {
    if (!session?.token) return

    setIsLoadingStats(true)
    setStatsError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/users/me/stats`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch stats')
      }

      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Error fetching stats:', error)
      setStatsError('Failed to load statistics')
    } finally {
      setIsLoadingStats(false)
    }
  }

  /**
   * Fetch tasks from backend API (T089)
   * Uses GET /tasks endpoint with JWT authentication
   */
  const fetchTasks = async () => {
    if (!session?.token) return

    setIsLoadingTasks(true)
    setTasksError(null)
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.token}`,
        },
      })

      if (!response.ok) {
        throw new Error('Failed to fetch tasks')
      }

      const data = await response.json()
      setTasks(data)
    } catch (error) {
      console.error('Error fetching tasks:', error)
      setTasksError('Failed to load tasks')
    } finally {
      setIsLoadingTasks(false)
    }
  }

  // Fetch stats and tasks on mount and when session is ready
  useEffect(() => {
    if (mounted && session?.token) {
      fetchStats()
      fetchTasks()
    }
  }, [mounted, session?.token])

  /**
   * Manual refresh handler for user-initiated data sync
   */
  const handleRefresh = async () => {
    setIsRefreshing(true)
    await Promise.all([fetchStats(), fetchTasks()])
    setIsRefreshing(false)
  }

  const isLoading = !mounted || isPending || !session?.user
  const displayName = mounted && session?.user ? getDisplayName(session.user) : 'User'

  return (
    <div className="min-h-screen flex flex-col bg-midnight-bg">
      <main className="flex-1">
        {isLoading ? (
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-text-secondary">Loading...</div>
          </div>
        ) : (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Welcome Heading with Refresh Button */}
          <div className="flex items-center justify-between mb-8">
            <motion.h1
              className="text-3xl sm:text-4xl font-bold text-text-primary"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              Welcome, {displayName}!
            </motion.h1>

            <motion.button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="glass-card px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-primary-violet/10 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg
                className={`w-5 h-5 text-primary-violet ${isRefreshing ? 'animate-spin' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              <span className="text-text-primary text-sm font-medium">
                {isRefreshing ? 'Refreshing...' : 'Refresh'}
              </span>
            </motion.button>
          </div>

          {/* Stats Cards */}
          <motion.div
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
          >
            {statsError ? (
              <div className="col-span-full glass-card p-6 rounded-2xl bg-red-500/10 border border-red-500/20">
                <p className="text-red-400 text-sm">{statsError}</p>
              </div>
            ) : (
              <>
            {/* Total Tasks Card */}
            <div className="glass-card p-6 rounded-2xl">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-text-secondary text-sm font-medium">Total Tasks</h3>
                <svg
                  className="w-8 h-8 text-primary-violet"
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
              <p className="text-3xl font-bold text-text-primary">
                {isLoadingStats ? '...' : stats?.total_tasks ?? 0}
              </p>
            </div>

            {/* Completed Tasks Card */}
            <div className="glass-card p-6 rounded-2xl">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-text-secondary text-sm font-medium">Completed</h3>
                <svg
                  className="w-8 h-8 text-secondary-indigo"
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
              <p className="text-3xl font-bold text-text-primary">
                {isLoadingStats ? '...' : stats?.completed_tasks ?? 0}
              </p>
            </div>

            {/* Completion Rate Card */}
            <div className="glass-card p-6 rounded-2xl">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-text-secondary text-sm font-medium">Completion Rate</h3>
                <svg
                  className="w-8 h-8 text-primary-violet"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
              </div>
              <p className="text-3xl font-bold text-text-primary">
                {isLoadingStats || !stats || stats.total_tasks === 0
                  ? '0%'
                  : `${Math.round((stats.completed_tasks / stats.total_tasks) * 100)}%`}
              </p>
            </div>
              </>
            )}
          </motion.div>

          {/* Task Creation Form (T084-T086) */}
          <TaskCreateForm onTaskCreated={() => {
            fetchTasks()
            fetchStats()
          }} />

          {/* Task List Section (T089) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <h2 className="text-2xl font-bold text-text-primary mb-6">
              Your Tasks
            </h2>

            {/* Error State */}
            {tasksError ? (
              <div className="glass-card p-6 rounded-2xl bg-red-500/10 border border-red-500/20">
                <p className="text-red-400 text-sm">{tasksError}</p>
                <button
                  onClick={() => fetchTasks()}
                  className="mt-4 px-4 py-2 bg-primary-violet hover:bg-primary-violet/80 text-white rounded-lg transition-colors"
                >
                  Retry
                </button>
              </div>
            ) : isLoadingTasks ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <TaskSkeleton count={3} />
              </div>
            ) : tasks.length === 0 ? (
              /* Empty State (T092) */
              <EmptyState />
            ) : (
              /* Task Grid with Animation (T088, T093, T102) */
              <TaskGrid tasks={tasks} onTaskUpdated={() => {
                fetchTasks()
                fetchStats()
              }} />
            )}
          </motion.div>
        </div>
        )}
      </main>
      <Footer />
    </div>
  )
}
