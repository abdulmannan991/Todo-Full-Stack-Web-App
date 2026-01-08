/**
 * Custom Auth Client for FastAPI Backend
 *
 * Client-side authentication methods that call FastAPI backend directly.
 * Used in client components for session management.
 *
 * Owner: @ui-auth-expert
 */

import * as React from 'react'
import { API_BASE_URL } from './config'

// User data interface
interface User {
  id: number
  email: string
  name?: string | null
  created_at?: string | null
  profile_image_url?: string | null
}

// Session data interface
interface SessionData {
  user: User
  token: string
}

// Store session in localStorage AND cookies (for middleware access)
const setSession = (sessionData: SessionData) => {
  if (typeof window !== 'undefined') {
    // Store in localStorage for client-side access
    localStorage.setItem('auth_token', sessionData.token)
    localStorage.setItem('user_data', JSON.stringify(sessionData.user))

    // Store in cookie for middleware access (NOT HttpOnly so middleware can read)
    // Cookie expires in 7 days to match JWT expiration
    const expires = new Date()
    expires.setDate(expires.getDate() + 7)
    document.cookie = `auth_token=${sessionData.token}; path=/; expires=${expires.toUTCString()}; SameSite=Lax`
  }
}

const getSession = (): SessionData | null => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token')
    const userData = localStorage.getItem('user_data')

    if (token && userData) {
      try {
        return {
          token,
          user: JSON.parse(userData)
        }
      } catch {
        return null
      }
    }
  }
  return null
}

const removeSession = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')

    // Clear the auth_token cookie
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax'
  }
}

// Signup function that calls FastAPI backend
// 🚨 CRITICAL: Signup MUST NOT create auth state (P0 Security Fix)
// User must login explicitly after signup to obtain valid session
export const signUp = {
  email: async ({ email, password, name }: { email: string; password: string; name?: string }) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/sign-up/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ email, password, name }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Signup failed')
    }

    const data = await response.json()
    // ❌ REMOVED: setSession(data) - Signup ≠ Authentication
    // ✅ User MUST login after signup to get valid session
    return data
  },
}

// SignIn function that calls FastAPI backend
export const signIn = {
  email: async ({ email, password }: { email: string; password: string }) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/sign-in/email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const data = await response.json()
    setSession(data)
    return data
  },
}

// SignOut function
export const signOut = async () => {
  removeSession()
  if (typeof window !== 'undefined') {
    window.location.href = '/login'
  }
}

// useSession hook for checking authentication status
// 🚨 CRITICAL: Backend session is single source of truth (P0 Security Fix)
// Local storage is UNTRUSTED - must validate against backend
export const useSession = () => {
  const [session, setSession] = React.useState<SessionData | null>(null)
  const [isPending, setIsPending] = React.useState(true)
  const [error, setError] = React.useState<Error | null>(null)

  // Extract validation logic into a reusable function
  const validateSession = React.useCallback(async () => {
    // Get session from localStorage (UNTRUSTED)
    const localSession = getSession()

    if (!localSession) {
      // No local session - user is unauthenticated
      setSession(null)
      setIsPending(false)
      return
    }

    try {
      // Validate session against backend (TRUSTED)
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localSession.token}`,
        },
        credentials: 'include',
      })

      // Backend rejected session (401/403)
      if (response.status === 401 || response.status === 403) {
        console.warn('[Auth] Backend rejected session - clearing local state')
        // HARD RESET: Clear ALL auth state immediately
        removeSession()
        setSession(null)
        setError(new Error('Session expired or invalid'))
        setIsPending(false)
        return
      }

      // Backend validation failed for other reason
      if (!response.ok) {
        console.error('[Auth] Backend validation failed:', response.status)
        removeSession()
        setSession(null)
        setError(new Error('Session validation failed'))
        setIsPending(false)
        return
      }

      // Backend confirmed session is valid
      const userData = await response.json()
      const updatedSession = {
        token: localSession.token,
        user: {
          id: userData.id,
          email: userData.email,
          name: userData.display_name || userData.email.split('@')[0],
          created_at: userData.created_at,
          profile_image_url: userData.profile_image_url
        }
      }

      // Update both state AND localStorage for consistency
      setSession(updatedSession)
      localStorage.setItem('user_data', JSON.stringify(updatedSession.user))
      setError(null)
    } catch (err) {
      console.error('[Auth] Session validation error:', err)

      // CRITICAL: Distinguish between network errors and auth failures
      // Network errors (TypeError, DNS, CORS, timeout) should PRESERVE the session
      // Only actual auth failures should clear the session

      if (err instanceof TypeError || (err instanceof Error && err.message.includes('fetch'))) {
        // Network error (Failed to fetch, DNS, CORS, ERR_NETWORK_CHANGED)
        // Keep the session alive - this is just a connectivity issue
        console.warn('[Auth] Network error during validation - keeping session alive:', err.message)
        setSession(localSession) // Keep local session active
        setError(null) // Don't set error state - session is still valid
      } else {
        // Unknown error - be conservative and clear session
        console.error('[Auth] Unknown error during validation - clearing session')
        removeSession()
        setSession(null)
        setError(err instanceof Error ? err : new Error('Session validation failed'))
      }
    } finally {
      setIsPending(false)
    }
  }, [])

  // Expose refresh function for manual re-validation
  const refreshSession = React.useCallback(async () => {
    setIsPending(true)
    await validateSession()
  }, [validateSession])

  React.useEffect(() => {
    validateSession()
  }, [validateSession]) // Run once on mount

  return {
    data: session,
    isPending,
    error,
    refreshSession, // Expose refresh capability
  }
}
