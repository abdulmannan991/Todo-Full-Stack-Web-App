import type { NextConfig } from 'next'
import path from 'path'

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Explicitly set workspace root to monorepo root (two levels up)
  // This silences the warning about multiple lockfiles
  outputFileTracingRoot: path.join(__dirname, '../../'),

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
