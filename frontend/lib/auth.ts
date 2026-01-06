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

// Build-time fallbacks for Vercel deployment
// These values are only used during build - runtime values come from environment
const BETTER_AUTH_SECRET = process.env.BETTER_AUTH_SECRET || "build_placeholder_secret_min_32_characters_long"
const BETTER_AUTH_URL = process.env.BETTER_AUTH_URL || "http://localhost:3000"

// Warn in development if using fallback values
if (process.env.NODE_ENV === "development") {
  if (!process.env.BETTER_AUTH_SECRET) {
    console.warn("⚠️ BETTER_AUTH_SECRET not set - using build placeholder")
  }
  if (!process.env.BETTER_AUTH_URL) {
    console.warn("⚠️ BETTER_AUTH_URL not set - using localhost fallback")
  }
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

  // JWT configuration (uses fallback during build)
  secret: BETTER_AUTH_SECRET,

  // Base URL for authentication (uses fallback during build)
  baseURL: BETTER_AUTH_URL,

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
