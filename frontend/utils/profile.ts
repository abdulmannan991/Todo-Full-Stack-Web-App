/**
 * User Profile Utilities for Midnight Genesis
 *
 * Created by @ui-auth-expert (T031)
 */

/**
 * Extracts display name from user email
 * - Gets the username before @ symbol
 * - Capitalizes first letter
 * - Handles edge cases (no @, empty email)
 *
 * @param user - User object with email property
 * @returns Display name (e.g., "John" from "john@gmail.com")
 *
 * @example
 * getDisplayName({ email: "john@gmail.com" }) // "John"
 * getDisplayName({ email: "alice.smith@company.com" }) // "Alice.smith"
 * getDisplayName({ email: "test" }) // "User"
 * getDisplayName({ email: "" }) // "User"
 * getDisplayName({ email: null }) // "User"
 */
export function getDisplayName(user: { email?: string | null; name?: string | null }): string {
  // If name is provided, use it
  if (user.name && user.name.trim()) {
    return user.name.trim()
  }

  // If email is not provided or empty, return default
  if (!user.email || user.email.trim() === '') {
    return 'User'
  }

  // Extract username before @ symbol
  const atIndex = user.email.indexOf('@')

  if (atIndex === -1) {
    // No @ symbol found - use email as-is or default
    const cleaned = user.email.trim()
    return cleaned || 'User'
  }

  // Get username before @
  const username = user.email.substring(0, atIndex).trim()

  if (username === '') {
    return 'User'
  }

  // Capitalize first letter
  return username.charAt(0).toUpperCase() + username.slice(1)
}
