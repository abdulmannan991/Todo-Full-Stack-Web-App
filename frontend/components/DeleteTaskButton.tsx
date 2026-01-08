"use client";

/**
 * DeleteTaskButton Component
 *
 * Sprint 2 - Tasks: T109-T115 (Task Deletion)
 * Owner: @ui-auth-expert (structure/API), @css-animation-expert (animations)
 *
 * Delete button with confirmation dialog to prevent accidental deletion.
 * Features:
 * - Confirmation modal with fade-in/scale animation (T110, T111)
 * - DELETE /tasks/{id} API integration (T112)
 * - Loading state with spinner (T113)
 * - Accessible keyboard navigation (T114)
 * - Premium Midnight styling with glassmorphic modal (T115)
 */

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { useSession } from "@/lib/auth-client";
import { API_BASE_URL } from "@/lib/config";

interface DeleteTaskButtonProps {
  taskId: number;
  taskTitle: string;
  onTaskDeleted?: () => void; // Callback to refresh task list
}

export default function DeleteTaskButton({
  taskId,
  taskTitle,
  onTaskDeleted,
}: DeleteTaskButtonProps) {
  const { data: session } = useSession();
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  /**
   * Handle task deletion (T112)
   * Calls DELETE /tasks/{id} endpoint
   */
 const handleDelete = async () => {
  setIsDeleting(true);
  try {
    // 1. Get token directly to prevent "Not authenticated" race conditions
    const currentToken = localStorage.getItem('auth_token');
    
    // 2. Use our new resilient apiClient
    const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${currentToken}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        toast.error("Session expired.");
        return;
      }
      throw new Error("Delete failed");
    }

    toast.success("Task deleted");
    if (onTaskDeleted) onTaskDeleted();

  } catch (error) {
    // 3. Catch the NETWORK_ERROR we defined in api-client.ts
    if (error instanceof Error && error.message === 'NETWORK_ERROR') {
      toast.error("Network blink detected. Task might have been deleted, please refresh.");
    } else {
      toast.error("Failed to delete task.");
    }
  }
};

  /**
   * Handle keyboard navigation in modal (T114)
   * - Escape: Close dialog
   * - Enter: Confirm deletion (dangerous, so require explicit button click instead)
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      setShowConfirmDialog(false);
    }
  };

  return (
    <>
      {/* Delete Button (T109) */}
      <button
        onClick={() => setShowConfirmDialog(true)}
        className="text-text-secondary hover:text-red-400
                   transition-colors duration-200
                   p-2 rounded-lg hover:bg-red-400/10
                   focus:outline-none focus:ring-2 focus:ring-red-400/50"
        aria-label="Delete task"
        title="Delete task"
      >
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>

      {/* Confirmation Modal (T110, T111, T115) */}
      <AnimatePresence>
        {showConfirmDialog && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onKeyDown={handleKeyDown}
          >
            {/* Backdrop */}
            <motion.div
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setShowConfirmDialog(false)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />

            {/* Modal Content (T115 - Premium Midnight Styling) */}
            <motion.div
              className="relative glass-card p-6 max-w-md w-full
                         border-red-400/30 shadow-xl shadow-red-400/10"
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              transition={{ type: "spring", stiffness: 300, damping: 25 }}
              role="dialog"
              aria-labelledby="delete-dialog-title"
              aria-describedby="delete-dialog-description"
            >
              {/* Warning Icon */}
              <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4
                            bg-red-400/10 rounded-full">
                <svg
                  className="w-6 h-6 text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>

              {/* Title */}
              <h3
                id="delete-dialog-title"
                className="text-xl font-semibold text-text-primary text-center mb-2"
              >
                Delete Task?
              </h3>

              {/* Description */}
              <p
                id="delete-dialog-description"
                className="text-sm text-text-secondary text-center mb-6"
              >
                Are you sure you want to delete{" "}
                <span className="font-medium text-text-primary">
                  "{taskTitle.length > 50 ? taskTitle.substring(0, 50) + "..." : taskTitle}"
                </span>
                ? This action cannot be undone.
              </p>

              {/* Action Buttons */}
              <div className="flex gap-3">
                {/* Cancel Button */}
                <button
                  onClick={() => setShowConfirmDialog(false)}
                  disabled={isDeleting}
                  className="flex-1 px-4 py-2.5 bg-white/5 hover:bg-white/10
                           text-text-primary font-medium rounded-lg
                           border border-white/10
                           transition-colors duration-200
                           disabled:opacity-50 disabled:cursor-not-allowed
                           focus:outline-none focus:ring-2 focus:ring-primary-violet"
                  autoFocus
                >
                  Cancel
                </button>

                {/* Delete Button (T113 - Loading State) */}
                <button
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="flex-1 px-4 py-2.5 bg-red-500 hover:bg-red-600
                           text-white font-medium rounded-lg
                           transition-colors duration-200
                           disabled:opacity-50 disabled:cursor-wait
                           focus:outline-none focus:ring-2 focus:ring-red-400"
                >
                  {isDeleting ? (
                    <span className="flex items-center justify-center">
                      <svg
                        className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
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
                      Deleting...
                    </span>
                  ) : (
                    "Delete"
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
