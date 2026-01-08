/**
 * Centralized Configuration - Single Source of Truth
 *
 * P0 Reliability Fix: Eliminates environment drift and API URL inconsistency
 * that was causing intermittent auth failures and session invalidation.
 *
 * CRITICAL: This is the ONLY place where API_BASE_URL should be defined.
 * All other modules MUST import from here.
 */

/**
 * API Base URL - Single Source of Truth
 *
 * Resolution order:
 * 1. NEXT_PUBLIC_API_URL environment variable (Vercel production/preview)
 * 2. Fallback to localhost:8000 (local development)
 *
 * Usage:
 * ```ts
 * import { API_BASE_URL } from '@/lib/config'
 *
 * fetch(`${API_BASE_URL}/tasks`, { ... })
 * ```
 */
export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

/**
 * Network Error Detection
 *
 * Determines if an error is a network/connectivity issue vs an auth failure.
 *
 * Network errors include:
 * - DNS resolution failures
 * - Connection timeouts
 * - CORS errors
 * - Server unreachable
 *
 * @param error - Error object from fetch
 * @returns true if network error, false if auth/validation error
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof TypeError) {
    // TypeError: Failed to fetch (network/CORS/DNS)
    return true
  }

  if (error instanceof Error) {
    const message = error.message.toLowerCase()
    return (
      message.includes("failed to fetch") ||
      message.includes("network") ||
      message.includes("timeout") ||
      message.includes("cors")
    )
  }

  return false
}

/**
 * Auth Error Detection
 *
 * Determines if an HTTP response indicates an authentication failure.
 *
 * CRITICAL: Sessions should ONLY be invalidated for these statuses.
 *
 * @param status - HTTP status code
 * @returns true if 401 or 403, false otherwise
 */
export function isAuthError(status: number): boolean {
  return status === 401 || status === 403
}
