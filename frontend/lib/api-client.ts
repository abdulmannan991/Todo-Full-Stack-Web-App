/**
 * API Client Wrapper for Midnight Genesis
 *
 * Automatically includes JWT token from Better Auth session in requests
 * Created by @ui-auth-expert (T037)
 */

import { API_BASE_URL } from './config'

/**
 * Get the session token from cookies
 * Better Auth stores the token in a cookie named 'better-auth.session_token'
 */
function getSessionToken(): string | null {
  if (typeof document === 'undefined') {
    return null // Server-side
  }

  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=')
    if (name === 'auth_token') {
      
      return value
    }
  }
  return null
}

/**
 * API client that automatically includes JWT token in Authorization header
 *
 * @param url - API endpoint path (e.g., '/users/me')
 * @param options - Fetch options (method, body, headers, etc.)
 * @returns Fetch response
 *
 * @throws Redirects to /login if 401 Unauthorized
 *
 * @example
 * const response = await apiClient('/users/me')
 * const data = await response.json()
 */
export async function apiClient(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getSessionToken();
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(fullUrl, { ...options, headers });

    // ONLY redirect if the server explicitly says 401
    if (response.status === 401) {
      if (typeof window !== 'undefined') {
        // Optional: Only redirect if you really want to force logout
        // window.location.href = '/login'; 
      }
      throw new Error('Unauthorized');
    }

    return response;
  } catch (error) {
    // Check if it's a network error
    if (error instanceof TypeError || (error instanceof Error && error.message.includes('fetch'))) {
       console.warn('[API] Network error detected - preserving session');
       // Throw a specific error type so the UI knows not to log out
       throw new Error('NETWORK_ERROR');
    }
    throw error;
  }
}
/**
 * Convenience method for GET requests
 */
export async function apiGet(url: string): Promise<Response> {
  return apiClient(url, { method: 'GET' })
}

/**
 * Convenience method for POST requests
 */
export async function apiPost(url: string, data: any): Promise<Response> {
  return apiClient(url, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

/**
 * Convenience method for PUT requests
 */
export async function apiPut(url: string, data: any): Promise<Response> {
  return apiClient(url, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

/**
 * Convenience method for DELETE requests
 */
export async function apiDelete(url: string): Promise<Response> {
  return apiClient(url, { method: 'DELETE' })
}

/**
 * Convenience method for PATCH requests
 */
export async function apiPatch(url: string, data: any): Promise<Response> {
  return apiClient(url, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

/**
 * Safe JSON parser - checks response.ok before parsing
 * Throws error with status code and error message if response is not OK
 *
 * @param response - Fetch response
 * @returns Parsed JSON data
 * @throws Error if response is not OK or JSON parsing fails
 *
 * @example
 * const response = await apiClient('/tasks')
 * const data = await safeJsonParse(response)
 */
export async function safeJsonParse<T = any>(response: Response): Promise<T> {
  // Check if response is OK (status 200-299)
  if (!response.ok) {
    // Try to parse error response
    let errorMessage = `HTTP ${response.status} ${response.statusText}`
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch {
      // If JSON parsing fails, use status text
    }

    throw new Error(errorMessage)
  }

  // Check if response has content
  const contentType = response.headers.get('content-type')
  if (!contentType || !contentType.includes('application/json')) {
    // Empty response or non-JSON response
    if (response.status === 204) {
      // 204 No Content is expected to have no body
      return null as T
    }
    throw new Error('Response is not JSON')
  }

  // Parse JSON
  return await response.json()
}
