---
name: profile-management
description: Logic for parsing usernames from emails, handling profile image uploads, and formatting joining dates.
version: 1.0.0
owner: ui-auth-expert
tags: [profile, user, upload, forms, validation, next.js]
---

# Profile Management Skill

## Purpose
Implement complete user profile management functionality including intelligent name display, profile image uploads with validation, and human-readable date formatting.

## Scope
- **Owned By**: @ui-auth-expert (frontend), coordinates with @fastapi-jwt-guardian (backend)
- **Technology Stack**: Next.js, React, Better Auth, FastAPI
- **Focus**: Profile UI, image uploads, data formatting, validation

## Core Requirements

### 1. Name Display Logic

**Intelligent Username Generation**

When `user.displayName` is null or empty, automatically generate a display name from the user's email address.

#### Implementation Pattern
```typescript
// utils/profile.ts

/**
 * Get display name from user object.
 * Falls back to email username if displayName is not set.
 */
export function getDisplayName(user: User): string {
  // If displayName exists and is not empty, use it
  if (user.displayName && user.displayName.trim().length > 0) {
    return user.displayName
  }

  // Otherwise, extract username from email
  if (user.email) {
    const username = user.email.split('@')[0]

    // Capitalize first letter for better presentation
    return username.charAt(0).toUpperCase() + username.slice(1)
  }

  // Fallback if no email (should not happen in normal flow)
  return 'User'
}

/**
 * Parse email to extract username portion.
 * Example: "john.doe@example.com" -> "john.doe"
 */
export function parseUsernameFromEmail(email: string): string {
  if (!email || !email.includes('@')) {
    return ''
  }

  return email.split('@')[0]
}

/**
 * Format username for display (capitalize, handle dots/underscores).
 * Example: "john.doe" -> "John Doe"
 */
export function formatUsername(username: string): string {
  if (!username) return ''

  return username
    .split(/[._-]/)  // Split on dots, underscores, hyphens
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}
```

#### Usage in Components
```typescript
// components/ProfileHeader.tsx
import { getDisplayName, formatUsername, parseUsernameFromEmail } from '@/utils/profile'

export function ProfileHeader({ user }: { user: User }) {
  const displayName = getDisplayName(user)

  // Optional: Show email username as secondary info
  const emailUsername = parseUsernameFromEmail(user.email)
  const formattedUsername = formatUsername(emailUsername)

  return (
    <div className="profile-header">
      <h1>{displayName}</h1>
      {!user.displayName && (
        <p className="text-sm text-gray-500">@{emailUsername}</p>
      )}
    </div>
  )
}
```

#### TypeScript Types
```typescript
// types/user.ts

export interface User {
  id: number
  email: string
  displayName: string | null
  profileImage: string | null
  createdAt: string  // ISO 8601 format
  updatedAt: string
}

export interface ProfileDisplayProps {
  user: User
  showEmail?: boolean
  showJoinDate?: boolean
}
```

### 2. Date Formatting - Joining Date

**Human-Readable Date Display**

Format the user's `createdAt` timestamp into a friendly "Member since" format.

#### Implementation Pattern
```typescript
// utils/dateFormat.ts

/**
 * Format joining date to "Member since Month Year" format.
 * Example: "2024-10-15T12:00:00Z" -> "Member since October 2024"
 */
export function formatJoiningDate(dateString: string): string {
  const date = new Date(dateString)

  // Validate date
  if (isNaN(date.getTime())) {
    return 'Member since recently'
  }

  const options: Intl.DateTimeFormatOptions = {
    month: 'long',
    year: 'numeric'
  }

  const formattedDate = date.toLocaleDateString('en-US', options)
  return `Member since ${formattedDate}`
}

/**
 * Get relative joining time (e.g., "Joined 3 months ago").
 */
export function getRelativeJoinTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()

  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays < 1) return 'Joined today'
  if (diffDays === 1) return 'Joined yesterday'
  if (diffDays < 7) return `Joined ${diffDays} days ago`
  if (diffDays < 30) return `Joined ${Math.floor(diffDays / 7)} weeks ago`
  if (diffDays < 365) return `Joined ${Math.floor(diffDays / 30)} months ago`

  const years = Math.floor(diffDays / 365)
  return years === 1 ? 'Joined 1 year ago' : `Joined ${years} years ago`
}

/**
 * Full date format for detailed views.
 * Example: "October 15, 2024"
 */
export function formatFullDate(dateString: string): string {
  const date = new Date(dateString)

  if (isNaN(date.getTime())) {
    return 'Date unknown'
  }

  const options: Intl.DateTimeFormatOptions = {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  }

  return date.toLocaleDateString('en-US', options)
}
```

#### Usage in Components
```typescript
// components/ProfileInfo.tsx
import { formatJoiningDate, getRelativeJoinTime } from '@/utils/dateFormat'

export function ProfileInfo({ user }: { user: User }) {
  const joiningDate = formatJoiningDate(user.createdAt)
  const relativeTime = getRelativeJoinTime(user.createdAt)

  return (
    <div className="profile-info">
      <p className="text-gray-600">{joiningDate}</p>
      <p className="text-sm text-gray-500">{relativeTime}</p>
    </div>
  )
}
```

### 3. Profile Image Upload

**Comprehensive Image Upload with Validation and Preview**

#### Frontend Implementation

##### Image Validation
```typescript
// utils/imageValidation.ts

export interface ImageValidationResult {
  valid: boolean
  error?: string
}

export const IMAGE_CONSTRAINTS = {
  MAX_SIZE: 2 * 1024 * 1024,  // 2MB
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/jpg'],
  ALLOWED_EXTENSIONS: ['.jpg', '.jpeg', '.png']
}

/**
 * Validate image file before upload.
 */
export function validateImageFile(file: File): ImageValidationResult {
  // Check file size
  if (file.size > IMAGE_CONSTRAINTS.MAX_SIZE) {
    return {
      valid: false,
      error: `File size must be less than ${IMAGE_CONSTRAINTS.MAX_SIZE / (1024 * 1024)}MB`
    }
  }

  // Check file type
  if (!IMAGE_CONSTRAINTS.ALLOWED_TYPES.includes(file.type)) {
    return {
      valid: false,
      error: 'Only JPG and PNG images are allowed'
    }
  }

  // Additional check: verify file extension
  const fileName = file.name.toLowerCase()
  const hasValidExtension = IMAGE_CONSTRAINTS.ALLOWED_EXTENSIONS.some(
    ext => fileName.endsWith(ext)
  )

  if (!hasValidExtension) {
    return {
      valid: false,
      error: 'Invalid file extension. Use .jpg or .png'
    }
  }

  return { valid: true }
}

/**
 * Generate preview URL for image file.
 */
export function createImagePreviewUrl(file: File): string {
  return URL.createObjectURL(file)
}

/**
 * Clean up preview URL to avoid memory leaks.
 */
export function revokeImagePreviewUrl(url: string): void {
  URL.revokeObjectURL(url)
}
```

##### Upload Component
```typescript
// components/ProfileImageUpload.tsx
'use client'

import { useState, useRef, useEffect } from 'react'
import { validateImageFile, createImagePreviewUrl, revokeImagePreviewUrl, IMAGE_CONSTRAINTS } from '@/utils/imageValidation'
import Image from 'next/image'

interface ProfileImageUploadProps {
  currentImageUrl?: string | null
  onUpload: (file: File) => Promise<void>
  isUploading?: boolean
}

export function ProfileImageUpload({
  currentImageUrl,
  onUpload,
  isUploading = false
}: ProfileImageUploadProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Cleanup preview URL on unmount
  useEffect(() => {
    return () => {
      if (previewUrl) {
        revokeImagePreviewUrl(previewUrl)
      }
    }
  }, [previewUrl])

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]

    if (!file) return

    // Reset previous state
    setError(null)
    if (previewUrl) {
      revokeImagePreviewUrl(previewUrl)
    }

    // Validate file
    const validation = validateImageFile(file)

    if (!validation.valid) {
      setError(validation.error || 'Invalid file')
      setPreviewUrl(null)
      setSelectedFile(null)
      return
    }

    // Create preview
    const preview = createImagePreviewUrl(file)
    setPreviewUrl(preview)
    setSelectedFile(file)
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    try {
      setError(null)
      await onUpload(selectedFile)

      // Clear selection after successful upload
      setSelectedFile(null)
      if (previewUrl) {
        revokeImagePreviewUrl(previewUrl)
        setPreviewUrl(null)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    }
  }

  const handleCancel = () => {
    if (previewUrl) {
      revokeImagePreviewUrl(previewUrl)
    }
    setPreviewUrl(null)
    setSelectedFile(null)
    setError(null)

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const displayImage = previewUrl || currentImageUrl

  return (
    <div className="profile-image-upload">
      {/* Current/Preview Image */}
      <div className="relative w-32 h-32 rounded-full overflow-hidden bg-gray-200">
        {displayImage ? (
          <Image
            src={displayImage}
            alt="Profile"
            fill
            className="object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
            </svg>
          </div>
        )}
      </div>

      {/* Preview Label */}
      {previewUrl && (
        <p className="text-sm text-blue-600 mt-2">Preview - Click "Save" to upload</p>
      )}

      {/* File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept={IMAGE_CONSTRAINTS.ALLOWED_TYPES.join(',')}
        onChange={handleFileSelect}
        className="hidden"
        disabled={isUploading}
      />

      {/* Action Buttons */}
      <div className="flex gap-2 mt-4">
        {!previewUrl ? (
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Choose Image
          </button>
        ) : (
          <>
            <button
              type="button"
              onClick={handleUpload}
              disabled={isUploading}
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {isUploading ? 'Uploading...' : 'Save'}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              disabled={isUploading}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 disabled:opacity-50"
            >
              Cancel
            </button>
          </>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <p className="text-sm text-red-600 mt-2">{error}</p>
      )}

      {/* Validation Hints */}
      <p className="text-xs text-gray-500 mt-2">
        Max size: 2MB. Allowed formats: JPG, PNG
      </p>
    </div>
  )
}
```

##### API Client for Upload
```typescript
// lib/api/profile.ts
import { getAuthToken } from '@/lib/auth'

export interface UploadProfileImageResponse {
  imageUrl: string
  message: string
}

/**
 * Upload profile image to FastAPI backend.
 */
export async function uploadProfileImage(file: File): Promise<UploadProfileImageResponse> {
  const token = await getAuthToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  // Create FormData for multipart/form-data upload
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/profile/image`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      // Don't set Content-Type - browser will set it with boundary
    },
    body: formData
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Authentication required')
    }
    if (response.status === 413) {
      throw new Error('File too large')
    }

    const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
    throw new Error(error.detail || 'Upload failed')
  }

  return response.json()
}

/**
 * Update user profile (display name, etc.)
 */
export async function updateProfile(data: { displayName?: string }): Promise<User> {
  const token = await getAuthToken()

  if (!token) {
    throw new Error('Not authenticated')
  }

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/profile`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Update failed' }))
    throw new Error(error.detail || 'Update failed')
  }

  return response.json()
}
```

##### Usage in Page/Component
```typescript
// app/profile/page.tsx
'use client'

import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { ProfileImageUpload } from '@/components/ProfileImageUpload'
import { uploadProfileImage } from '@/lib/api/profile'
import { getDisplayName } from '@/utils/profile'
import { formatJoiningDate } from '@/utils/dateFormat'

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const [isUploading, setIsUploading] = useState(false)

  const handleImageUpload = async (file: File) => {
    setIsUploading(true)

    try {
      const result = await uploadProfileImage(file)
      console.log('Upload successful:', result)

      // Refresh user data to get new image URL
      await refreshUser()

      // Show success message
      alert('Profile image updated!')
    } catch (error) {
      console.error('Upload error:', error)
      throw error  // Re-throw to let component handle error display
    } finally {
      setIsUploading(false)
    }
  }

  if (!user) {
    return <div>Loading...</div>
  }

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Profile</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <ProfileImageUpload
          currentImageUrl={user.profileImage}
          onUpload={handleImageUpload}
          isUploading={isUploading}
        />

        <div className="mt-6">
          <h2 className="text-xl font-semibold">{getDisplayName(user)}</h2>
          <p className="text-gray-600">{user.email}</p>
          <p className="text-gray-500 mt-2">{formatJoiningDate(user.createdAt)}</p>
        </div>
      </div>
    </div>
  )
}
```

#### Backend Integration (FastAPI)

##### FastAPI Endpoint Pattern
```python
# backend/routers/profile.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from backend.models import User
from backend.database import get_session
from backend.auth import get_current_user
import os
import uuid
from pathlib import Path
from PIL import Image

router = APIRouter(prefix="/api/profile", tags=["profile"])

# Configuration
UPLOAD_DIR = Path("uploads/profile_images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
ALLOWED_CONTENT_TYPES = ["image/jpeg", "image/png"]
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

@router.post("/image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Upload and update user profile image."""

    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG and PNG images are allowed"
        )

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension"
        )

    # Read file content
    contents = await file.read()

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size must be less than 2MB"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)

    # Optional: Validate image (can be opened)
    try:
        with Image.open(file_path) as img:
            img.verify()
    except Exception:
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )

    # Delete old image if exists
    if current_user.profile_image:
        old_path = Path(current_user.profile_image)
        if old_path.exists():
            os.remove(old_path)

    # Update user record
    current_user.profile_image = str(file_path)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return {
        "imageUrl": f"/uploads/profile_images/{unique_filename}",
        "message": "Profile image updated successfully"
    }
```

## Validation Checks

When invoked, this skill will:
1. Verify display name fallback logic is implemented
2. Check email parsing functions exist
3. Validate date formatting utilities
4. Ensure image validation (size, type) is in place
5. Verify preview functionality before upload
6. Check FormData usage for file uploads
7. Validate error handling for upload failures
8. Ensure cleanup of preview URLs (memory leaks)

## Usage

```bash
# Audit profile management implementation
/profile-management

# Check name display logic
/profile-management --check-names

# Validate image upload flow
/profile-management --check-upload

# Test date formatting
/profile-management --check-dates
```

## Success Criteria
- ✅ Display name falls back to email username when null
- ✅ Email parsing handles edge cases (no @, empty string)
- ✅ Joining dates display in "Member since Month Year" format
- ✅ Image validation enforces 2MB max size
- ✅ Only JPG/PNG file types accepted
- ✅ Preview shown before save
- ✅ FormData used for multipart uploads
- ✅ Preview URLs cleaned up to prevent memory leaks
- ✅ Error messages are user-friendly
- ✅ Upload progress/loading states handled

## Integration
This skill integrates with:
- **@ui-auth-expert**: Primary owner for frontend implementation
- **@fastapi-jwt-guardian**: Backend upload endpoint security
- **@database-expert**: Profile data storage and user queries
- **@responsive-validator**: Ensure upload UI works on all devices
- **@auth-guard**: Verify JWT auth on upload endpoints

## Security Considerations

### Frontend
- Validate files client-side before upload (size, type)
- Use FormData for proper multipart encoding
- Include JWT token in Authorization header
- Handle 401 responses (redirect to login)
- Sanitize user-generated display names

### Backend
- Re-validate file size and type server-side (never trust client)
- Use unique filenames (UUID) to prevent overwrites
- Store files outside web root if possible
- Verify image integrity (can be opened by PIL/Pillow)
- Implement rate limiting on upload endpoint
- Delete old images when new ones are uploaded
- Set proper file permissions on upload directory

## Common Edge Cases

### Name Display
- Email without @ symbol → Use fallback "User"
- Empty email string → Use fallback "User"
- Very long email username → Truncate with ellipsis

### Date Formatting
- Invalid date string → Show "Member since recently"
- Future date (clock skew) → Show "Member since recently"
- Very old dates → Handle years correctly

### Image Upload
- File selected but upload canceled → Clean up preview URL
- Network error during upload → Show retry option
- Upload succeeds but refresh fails → Handle gracefully
- Multiple rapid uploads → Debounce or disable button during upload
- Browser back/forward during preview → Clean up preview URLs

## Testing Checklist

- [ ] Display name shows correctly when set
- [ ] Display name falls back to email username when null
- [ ] Email parsing handles various formats correctly
- [ ] Joining date formats correctly
- [ ] Image validation rejects files >2MB
- [ ] Image validation rejects non-JPG/PNG files
- [ ] Preview displays before save
- [ ] Save button uploads to FastAPI
- [ ] Cancel button clears preview
- [ ] Error messages display for invalid files
- [ ] Success feedback after upload
- [ ] Old images are deleted on new upload
- [ ] Preview URLs are cleaned up (no memory leaks)
- [ ] Works across all viewport sizes (300px - 2560px)
