import type { NextConfig } from 'next'
import path from 'path'

const nextConfig: NextConfig = {
  reactStrictMode: true,

  // CRITICAL: Monorepo dependency tracing for Vercel deployment
  // This tells Next.js to trace dependencies up to the monorepo root
  // Fixes: 'Error: Cannot find module next/dist/compiled/next-server/server.runtime.prod.js'
  outputFileTracingRoot: path.join(__dirname, '../'),

  // Enable standalone output for better Vercel compatibility
  // This creates a self-contained production build
  output: 'standalone',

  // Performance optimizations for LCP improvement
  experimental: {
    // Optimize package imports to reduce bundle size
    optimizePackageImports: ['framer-motion', 'better-auth', 'sonner'],
  },

  // Production optimizations
  compiler: {
    // Remove console.log in production builds
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // Image optimization (future-ready)
  images: {
    formats: ['image/webp', 'image/avif'],
  },
}

export default nextConfig
