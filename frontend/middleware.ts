/**
 * Route Protection Middleware for Midnight Genesis
 *
 * Created by @ui-auth-expert (T035)
 *
 * Protects routes that require authentication:
 * - /dashboard - requires auth
 * - /profile - requires auth
 *
 * Public routes (no auth required):
 * - / (landing page)
 * - /signup
 * - /login
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Protected routes that require authentication
  const protectedRoutes = ['/dashboard', '/profile', '/assistant']

  // Check if the current path is a protected route
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  )

  if (isProtectedRoute) {
    // 🚨 CRITICAL: Check for auth token in COOKIES ONLY (P0 Security Fix)
    // localStorage is UNTRUSTED and cannot be accessed in middleware
    // Cookie is the single source of truth for route protection
    const authToken = request.cookies.get('auth_token')

    if (!authToken) {
      // No auth token in cookie - redirect to login
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }

    // Cookie exists - allow access (useSession will validate against backend)
  }

  // Allow the request to continue
  return NextResponse.next()
}

// Configure which routes the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
