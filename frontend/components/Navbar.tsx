'use client'

/**
 * Premium Glassmorphic Navbar for FlowTask
 *
 * Responsive design with hamburger menu for mobile (< 640px)
 * Hebbia/OneText-inspired design with sticky glass morphism
 *
 * Owner: @css-animation-expert + @ui-auth-expert
 */

import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { useSession, signOut } from '@/lib/auth-client'
import { getDisplayName } from '@/utils/profile'
import { useState, useEffect } from 'react'

export default function Navbar() {
  const router = useRouter()
  const pathname = usePathname()
  const { data: session } = useSession()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [mounted, setMounted] = useState(false)

  // Fix hydration mismatch: Only access session after mount
  useEffect(() => {
    setMounted(true)
  }, [])

  const displayName = mounted && session?.user ? getDisplayName(session.user) : null
  const isAuthenticated = mounted && !!session?.user

  const handleLogout = async () => {
    await signOut()
    setMobileMenuOpen(false)
    router.push('/')
  }

  return (
    <nav className="sticky top-0 z-50 bg-midnight-bg/80 backdrop-blur-md border-b border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center space-x-8">
           <Link
              href="/"
              className="flex-shrink-0"
              prefetch={false}
            >
              <h1 className="text-xl font-bold bg-gradient-to-r from-primary-violet to-secondary-indigo bg-clip-text text-transparent">
                FlowTask
              </h1>
            </Link>

            {/* Navigation Links - Only show when authenticated and on desktop */}
            {isAuthenticated && (
              <div className="hidden md:flex items-center space-x-6">
               <Link
                  href="/dashboard"
                  prefetch={false}
                  className={`text-sm font-medium transition-colors ${
                    pathname === '/dashboard'
                      ? 'text-primary-violet'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  Dashboard
                </Link>
               <Link
                  href="/assistant"
                  prefetch={false}
                  className={`text-sm font-medium transition-colors ${
                    pathname === '/assistant'
                      ? 'text-primary-violet'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  Flow Assistant
                </Link>
              </div>
            )}
          </div>

          {/* Desktop User Profile Section - Hidden on mobile */}
          {isAuthenticated ? (
            <div className="hidden sm:flex items-center space-x-4">
              {/* Profile Info */}
              <Link href={"/profile"}>
              <div className="flex items-center space-x-3">
                {/* Profile Image or Icon */}
                {session?.user?.profile_image_url ? (
                  <img
                    src={`http://localhost:8000${session.user.profile_image_url}`}
                    alt="Profile"
                    className="w-10 h-10 rounded-full object-cover border-2 border-primary-violet/50"
                  />
                ) : (
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-violet/20 to-secondary-indigo/20 border-2 border-primary-violet/50 flex items-center justify-center">
                    <svg
                      className="w-5 h-5 text-primary-violet"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                  </div>
                )}

                {/* Display Name */}
                <span className="hidden md:block text-text-primary font-medium">
                  {displayName}
                </span>
              </div>
              </Link>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium text-primary-violet hover:text-secondary-indigo transition-all duration-200 rounded-lg hover:bg-white/5"
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="hidden sm:flex items-center space-x-4">
              <Link
                href="/login"
                prefetch={false}
                className="px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary transition-colors"
              >
                Login
              </Link>
              <Link
                href="/signup"
                prefetch={false}
                className="px-4 py-2 text-sm font-medium bg-primary-violet hover:bg-secondary-indigo text-text-primary rounded-lg transition-all duration-200"
              >
                Get Started
              </Link>
            </div>
          )}

          {/* Hamburger Menu Button - Only visible on mobile */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="sm:hidden p-2 rounded-lg text-text-secondary hover:text-text-primary hover:bg-white/5 transition-all duration-200"
            aria-label="Toggle menu"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {mobileMenuOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2, ease: 'easeInOut' }}
            className="sm:hidden border-t border-white/10 bg-midnight-bg/95 backdrop-blur-md"
          >
            <div className="px-4 py-4 space-y-3">
              {isAuthenticated ? (
                <>
                  {/* Profile Info */}
                  <div className="flex items-center space-x-3 pb-3 border-b border-white/10">
                    {session?.user?.profile_image_url ? (
                      <img
                        src={`http://localhost:8000${session.user.profile_image_url}`}
                        alt="Profile"
                        className="w-10 h-10 rounded-full object-cover border-2 border-primary-violet/50"
                      />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-violet/20 to-secondary-indigo/20 border-2 border-primary-violet/50 flex items-center justify-center">
                        <svg
                          className="w-5 h-5 text-primary-violet"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                          />
                        </svg>
                      </div>
                    )}
                    <span className="text-text-primary font-medium">
                      {displayName}
                    </span>
                  </div>

                  {/* Navigation Links */}
                  <Link
                    href="/dashboard"
                    prefetch={false}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`block px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      pathname === '/dashboard'
                        ? 'text-primary-violet bg-white/5'
                        : 'text-text-secondary hover:text-text-primary hover:bg-white/5'
                    }`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/assistant"
                    prefetch={false}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`block px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                      pathname === '/assistant'
                        ? 'text-primary-violet bg-white/5'
                        : 'text-text-secondary hover:text-text-primary hover:bg-white/5'
                    }`}
                  >
                    Flow Assistant
                  </Link>

                  {/* Logout Button */}
                  <button
                    onClick={handleLogout}
                    className="w-full px-4 py-2 text-sm font-medium text-primary-violet hover:text-secondary-indigo hover:bg-white/5 rounded-lg transition-all duration-200 text-left"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    prefetch={false}
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary hover:bg-white/5 rounded-lg transition-colors"
                  >
                    Login
                  </Link>
                  <Link
                    href="/signup"
                    prefetch={false}
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-4 py-2 text-sm font-medium bg-primary-violet hover:bg-secondary-indigo text-text-primary rounded-lg transition-all duration-200 text-center"
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}
