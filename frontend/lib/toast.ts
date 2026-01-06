/**
 * Toast Notification Utilities for Midnight Genesis
 *
 * Wraps sonner library with Premium Midnight styling
 * Created by @ui-auth-expert (T029)
 * Styled by @css-animation-expert (T030)
 */

import { toast as sonnerToast } from 'sonner'

/**
 * Show a success toast notification
 * @param message - Success message to display
 */
export function showSuccessToast(message: string) {
  return sonnerToast.success(message, {
    style: {
      background: 'rgba(34, 197, 94, 0.9)', // bg-green-500/90
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(34, 197, 94, 0.2)',
      color: '#FFFFFF',
    },
    duration: 4000,
  })
}

/**
 * Show an error toast notification
 * @param message - Error message to display
 */
export function showErrorToast(message: string) {
  return sonnerToast.error(message, {
    style: {
      background: 'rgba(239, 68, 68, 0.9)', // bg-red-500/90
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(239, 68, 68, 0.2)',
      color: '#FFFFFF',
    },
    duration: 5000,
  })
}

/**
 * Show an info toast notification
 * @param message - Info message to display
 */
export function showInfoToast(message: string) {
  return sonnerToast.info(message, {
    style: {
      background: 'rgba(139, 92, 246, 0.9)', // bg-primary-violet/90
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(139, 92, 246, 0.2)',
      color: '#FFFFFF',
    },
    duration: 4000,
  })
}
