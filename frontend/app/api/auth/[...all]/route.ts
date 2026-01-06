/**
 * Better Auth API Route Handler
 *
 * This catch-all route handles all Better Auth endpoints:
 * - POST /api/auth/signup - User registration
 * - POST /api/auth/signin - User login
 * - POST /api/auth/signout - User logout
 * - GET /api/auth/session - Get current session
 * - And other Better Auth endpoints
 *
 * Owner: @ui-auth-expert
 */

import { auth } from "@/lib/auth"

export const GET = auth.handler
export const POST = auth.handler
