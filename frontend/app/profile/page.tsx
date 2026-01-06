'use client'

/**
 * Profile Page
 *
 * Sprint 2 - Tasks: T116-T129 (User Profile Management)
 * Owner: @ui-auth-expert (structure/layout), @css-animation-expert (styling/animations)
 *
 * Displays user profile with editable display name and profile image.
 * Features:
 * - Profile image upload with preview (T117-T120)
 * - Display name editing with email fallback (T121-T124)
 * - Account information display (T125-T127)
 * - Premium Midnight styling with glassmorphic cards (T128-T129)
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { useSession } from '@/lib/auth-client'
import { getDisplayName } from '@/utils/profile'
import Footer from '@/components/Footer'
import { toast } from 'sonner'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ProfilePage() {
  const router = useRouter()
  const { data: session, isPending, refreshSession } = useSession()
  const [mounted, setMounted] = useState(false)
  const [displayName, setDisplayName] = useState('')
  const [isEditingName, setIsEditingName] = useState(false)
  const [isSavingName, setIsSavingName] = useState(false)
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)

  // Fix hydration: Only access session after mount
  useEffect(() => {
    setMounted(true)
  }, [])

  // Redirect to login if not authenticated
  useEffect(() => {
    if (mounted && !isPending && !session?.user) {
      router.push('/login')
    }
  }, [mounted, session, isPending, router])

  // Initialize display name from session
  useEffect(() => {
    if (mounted && session?.user) {
      setDisplayName(getDisplayName(session.user))
    }
  }, [mounted, session])

  /**
   * Format date to human-readable format (T127)
   * Example: "January 5, 2026"
   */
  const formatDate = (dateString: string | null | undefined): string => {
    if (!dateString) return 'Unknown'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    })
  }

  /**
   * Handle display name save (T123)
   * Note: This is frontend-only for now. Backend profile update endpoint
   * will be added in future sprint.
   */
  const handleSaveName = async () => {
    if (!displayName.trim()) {
      toast.error('Display name cannot be empty')
      return
    }

    setIsSavingName(true)

    try {
      // TODO: Call PATCH /users/me endpoint when backend is ready
      // For now, just update local state
      toast.success('Display name updated!')
      setIsEditingName(false)
    } catch (error) {
      console.error('Profile update error:', error)
      toast.error('Failed to update display name')
    } finally {
      setIsSavingName(false)
    }
  }

  /**
   * Handle avatar upload (T118-T120)
   * Uploads image to POST /users/me/avatar endpoint
   */
  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    if (!['image/jpeg', 'image/jpg', 'image/png'].includes(file.type)) {
      toast.error('Only JPG and PNG images are allowed')
      return
    }

    // Validate file size (2MB)
    if (file.size > 2 * 1024 * 1024) {
      toast.error('Image must be under 2MB')
      return
    }

    // Create preview
    const reader = new FileReader()
    reader.onload = () => {
      setAvatarPreview(reader.result as string)
    }
    reader.readAsDataURL(file)

    // Upload to backend
    setIsUploadingAvatar(true)

    try {
      if (!session?.token) {
        toast.error('Authentication required')
        return
      }

      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API_BASE_URL}/users/me/avatar`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        let errorMessage = 'Failed to upload avatar'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorMessage
        } catch {
          if (response.status === 401 || response.status === 403) {
            errorMessage = 'Authentication required'
            window.location.href = '/login'
            return
          }
          errorMessage = `Server error (${response.status})`
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      toast.success('Profile picture updated!')

      // Refresh session to sync avatar across all components (Navbar, etc.)
      await refreshSession()
      setAvatarPreview(null) // Clear preview after successful upload
    } catch (error) {
      console.error('Avatar upload error:', error)
      toast.error(error instanceof Error ? error.message : 'Failed to upload avatar')
      setAvatarPreview(null)
    } finally {
      setIsUploadingAvatar(false)
    }
  }

  const isLoading = !mounted || isPending || !session?.user
  const user = session?.user

  return (
    <div className="min-h-screen flex flex-col bg-midnight-bg">
      <main className="flex-1">
        {isLoading ? (
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-text-secondary">Loading...</div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            {/* Page Header */}
            <motion.div
              className="mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
            >
              <h1 className="text-3xl sm:text-4xl font-bold text-text-primary mb-2">
                Profile
              </h1>
              <p className="text-text-secondary">
                Manage your account settings and preferences
              </p>
            </motion.div>

            {/* Profile Card (T116, T128-T129) */}
            <motion.div
              className="glass-card p-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1 }}
            >
              {/* Profile Image Section (T117-T120) */}
              <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 mb-8">
                {/* Profile Image */}
                <div className="relative">
                  {user?.profile_image_url || avatarPreview ? (
                    <img
                      src={avatarPreview || `${API_BASE_URL}${user?.profile_image_url}`}
                      alt="Profile"
                      className="w-24 h-24 rounded-full object-cover shadow-lg border-2 border-primary-violet/30"
                    />
                  ) : (
                    <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary-violet to-secondary-indigo flex items-center justify-center text-white text-3xl font-bold shadow-lg">
                      {user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
                    </div>
                  )}

                  {/* Image Upload Button (T118-T120) */}
                  <input
                    type="file"
                    id="avatar-upload"
                    accept="image/jpeg,image/jpg,image/png"
                    onChange={handleAvatarUpload}
                    disabled={isUploadingAvatar}
                    className="hidden"
                  />
                  <label
                    htmlFor="avatar-upload"
                    className={`absolute bottom-0 right-0 w-8 h-8 bg-primary-violet hover:bg-secondary-indigo rounded-full flex items-center justify-center shadow-lg transition-colors duration-200 cursor-pointer ${isUploadingAvatar ? 'opacity-50 cursor-wait' : ''}`}
                    aria-label="Upload profile image"
                    title="Upload profile image (JPG/PNG, max 2MB)"
                  >
                    {isUploadingAvatar ? (
                      <svg
                        className="animate-spin w-4 h-4 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                    ) : (
                      <svg
                        className="w-4 h-4 text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                        />
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                        />
                      </svg>
                    )}
                  </label>
                </div>

                {/* User Info */}
                <div className="flex-1 text-center sm:text-left">
                  {/* Display Name (T121-T124) */}
                  {!isEditingName ? (
                    <div className="mb-2">
                      <h2 className="text-2xl font-bold text-text-primary mb-1">
                        {displayName}
                      </h2>
                      <button
                        onClick={() => setIsEditingName(true)}
                        className="text-sm text-primary-violet hover:text-secondary-indigo transition-colors duration-200"
                      >
                        Edit display name
                      </button>
                    </div>
                  ) : (
                    <div className="mb-2">
                      <input
                        type="text"
                        value={displayName}
                        onChange={(e) => setDisplayName(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleSaveName()
                          if (e.key === 'Escape') {
                            setDisplayName(getDisplayName(user!))
                            setIsEditingName(false)
                          }
                        }}
                        maxLength={100}
                        className="w-full px-3 py-2 mb-2 bg-white/5 border border-primary-violet rounded-lg text-text-primary focus:outline-none focus:ring-2 focus:ring-secondary-indigo"
                        autoFocus
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={handleSaveName}
                          disabled={isSavingName}
                          className="px-4 py-1.5 bg-primary-violet hover:bg-secondary-indigo text-white text-sm rounded-lg transition-colors duration-200 disabled:opacity-50"
                        >
                          {isSavingName ? 'Saving...' : 'Save'}
                        </button>
                        <button
                          onClick={() => {
                            setDisplayName(getDisplayName(user!))
                            setIsEditingName(false)
                          }}
                          className="px-4 py-1.5 bg-white/5 hover:bg-white/10 text-text-primary text-sm rounded-lg transition-colors duration-200"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  <p className="text-text-secondary">{user?.email}</p>
                </div>
              </div>

              {/* Account Information (T125-T127) */}
              <div className="border-t border-white/10 pt-6">
                <h3 className="text-lg font-semibold text-text-primary mb-4">
                  Account Information
                </h3>

                <div className="space-y-4">
                  {/* Email */}
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-text-secondary">Email</span>
                    <span className="text-sm text-text-primary font-medium">
                      {user?.email}
                    </span>
                  </div>

                  {/* User ID */}
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-text-secondary">User ID</span>
                    <span className="text-sm text-text-primary font-mono">
                      #{user?.id}
                    </span>
                  </div>

                  {/* Member Since (T127) */}
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-text-secondary">Member since</span>
                    <span className="text-sm text-text-primary">
                      {formatDate(user?.created_at)}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Back to Dashboard Button */}
            <motion.div
              className="mt-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.2 }}
            >
              <button
                onClick={() => router.push('/dashboard')}
                className="text-primary-violet hover:text-secondary-indigo transition-colors duration-200 flex items-center gap-2"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 19l-7-7m0 0l7-7m-7 7h18"
                  />
                </svg>
                Back to Dashboard
              </button>
            </motion.div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  )
}
