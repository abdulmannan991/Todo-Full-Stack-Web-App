/**
 * Better Auth Configuration for FlowTask
 *
 * Configured with:
 * - PostgreSQL database persistence (Neon Serverless)
 * - Email/password provider
 * - JWT-based sessions
 *
 * Owner: @ui-auth-expert
 */

import { betterAuth } from "better-auth"
import { Pool } from "@neondatabase/serverless"

if (!process.env.BETTER_AUTH_SECRET) {
  throw new Error(
    "BETTER_AUTH_SECRET is not defined. Please add it to .env.local"
  )
}

if (!process.env.BETTER_AUTH_URL) {
  throw new Error(
    "BETTER_AUTH_URL is not defined. Please add it to .env.local"
  )
}

// Database connection using Neon Serverless
const pool = process.env.DATABASE_URL
  ? new Pool({ connectionString: process.env.DATABASE_URL })
  : undefined

export const auth = betterAuth({
  // Database configuration
  database: pool
    ? {
        provider: "pg",
        pool: pool,
      }
    : undefined,

  // Email and Password authentication
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },

  // JWT configuration
  secret: process.env.BETTER_AUTH_SECRET,

  // Base URL for authentication
  baseURL: process.env.BETTER_AUTH_URL,

  // Session configuration
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
  },

  // Advanced settings
  advanced: {
    useSecureCookies: process.env.NODE_ENV === "production",
    generateId: () => Math.random().toString(36).substring(2, 15),
  },
})
