"use client";

/**
 * EditableTitle Component
 *
 * Sprint 2 - Tasks: T104-T108 (Inline Title Editing)
 * Owner: @ui-auth-expert (structure/API), @css-animation-expert (animations)
 *
 * Inline editable title with view/edit mode toggle.
 * Features:
 * - Click to edit mode with auto-focus (T104, T105)
 * - Save on Enter/blur, cancel on Escape (T105)
 * - Real-time validation with character counter (T106)
 * - Premium Midnight styling with glassmorphic input (T107)
 * - Micro-interaction animations (T108)
 */

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { useSession } from "@/lib/auth-client";

interface EditableTitleProps {
  taskId: number;
  initialTitle: string;
  onTitleUpdated?: () => void; // Callback to refresh task list
}

export default function EditableTitle({
  taskId,
  initialTitle,
  onTitleUpdated,
}: EditableTitleProps) {
  const { data: session } = useSession();
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(initialTitle);
  const [tempTitle, setTempTitle] = useState(initialTitle);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  /**
   * Auto-focus input when entering edit mode (T105)
   */
  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select(); // Select all text for easy replacement
    }
  }, [isEditing]);

  /**
   * Validate title (T106)
   * - Non-empty
   * - Max 500 characters
   */
  const validateTitle = (value: string): boolean => {
    setError("");

    if (!value || !value.trim()) {
      setError("Title cannot be empty");
      return false;
    }

    if (value.length > 500) {
      setError("Title must be 500 characters or less");
      return false;
    }

    return true;
  };

  /**
   * Save title to backend (T105)
   * Calls PATCH /tasks/{id} with new title
   */
  const handleSave = async () => {
    const trimmedTitle = tempTitle.trim();

    // Validate
    if (!validateTitle(trimmedTitle)) {
      return;
    }

    // No change - just exit edit mode
    if (trimmedTitle === title) {
      setIsEditing(false);
      setError("");
      return;
    }

    // Check authentication
    if (!session?.token) {
      toast.error("Authentication required");
      window.location.href = "/login";
      return;
    }

    setIsSaving(true);

    try {
      // Call PATCH /tasks/{id} endpoint
      const response = await fetch(`http://localhost:8000/tasks/${taskId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.token}`,
        },
        body: JSON.stringify({
          title: trimmedTitle,
        }),
      });

      // CRITICAL: Check response.ok BEFORE calling response.json()
      if (!response.ok) {
        let errorMessage = "Failed to update title";

        try {
          // Attempt to parse JSON error body if present
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          // Response body is empty or not JSON - use status code
          if (response.status === 401 || response.status === 403) {
            errorMessage = "Authentication required";
            window.location.href = "/login";
            return;
          }
          errorMessage = `Server error (${response.status})`;
        }

        throw new Error(errorMessage);
      }

      // Parse response JSON safely
      await response.json();

      // Success: Update local state
      setTitle(trimmedTitle);
      setIsEditing(false);
      setError("");
      toast.success("Title updated!");

      // Trigger task list refresh
      if (onTitleUpdated) {
        onTitleUpdated();
      }
    } catch (error) {
      console.error("Title update error:", error);
      toast.error(
        error instanceof Error ? error.message : "Failed to update title"
      );
    } finally {
      setIsSaving(false);
    }
  };

  /**
   * Cancel editing - restore original title
   */
  const handleCancel = () => {
    setTempTitle(title);
    setIsEditing(false);
    setError("");
  };

  /**
   * Handle keyboard shortcuts (T105)
   * - Enter: Save
   * - Escape: Cancel
   */
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSave();
    } else if (e.key === "Escape") {
      e.preventDefault();
      handleCancel();
    }
  };

  return (
    <div className="group">
      {/* View Mode: Click to Edit (T104) */}
      {!isEditing ? (
        <motion.h3
          onClick={() => setIsEditing(true)}
          className="text-lg font-semibold mb-2 line-clamp-2 cursor-pointer
                     text-text-primary group-hover:text-primary-violet
                     transition-colors duration-200
                     relative"
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          title="Click to edit title"
        >
          {title}

          {/* Edit Icon (appears on hover - T108) */}
          <motion.span
            className="inline-block ml-2 text-text-secondary opacity-0 group-hover:opacity-100
                       transition-opacity duration-200"
            initial={{ opacity: 0 }}
            whileHover={{ opacity: 1 }}
          >
            <svg
              className="w-4 h-4 inline"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
              />
            </svg>
          </motion.span>
        </motion.h3>
      ) : (
        /* Edit Mode: Input with Auto-Focus (T105, T107) */
        <div className="mb-2">
          <motion.input
            ref={inputRef}
            type="text"
            value={tempTitle}
            onChange={(e) => {
              setTempTitle(e.target.value);
              if (error) validateTitle(e.target.value);
            }}
            onBlur={handleSave} // Save on blur (T105)
            onKeyDown={handleKeyDown}
            disabled={isSaving}
            maxLength={500}
            className="w-full px-3 py-2 text-lg font-semibold
                       bg-white/10 border-2 border-primary-violet
                       rounded-lg text-text-primary
                       focus:outline-none focus:ring-2 focus:ring-secondary-indigo
                       focus:border-transparent
                       backdrop-blur-sm
                       transition-all duration-200
                       disabled:opacity-50 disabled:cursor-wait"
            initial={{ scale: 0.98, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.15, type: "spring" }}
            aria-label="Edit task title"
            aria-invalid={!!error}
          />

          {/* Character Counter (T106) */}
          <div className="flex items-center justify-between mt-1">
            <p
              className={`text-xs ${
                tempTitle.length > 500
                  ? "text-red-400"
                  : "text-text-secondary"
              }`}
            >
              {tempTitle.length}/500 characters
            </p>

            {/* Save/Cancel Hint */}
            <p className="text-xs text-text-secondary">
              Press <kbd className="px-1.5 py-0.5 bg-white/5 rounded">Enter</kbd> to save,{" "}
              <kbd className="px-1.5 py-0.5 bg-white/5 rounded">Esc</kbd> to cancel
            </p>
          </div>

          {/* Error Message (T106) */}
          <AnimatePresence>
            {error && (
              <motion.p
                className="mt-1 text-sm text-red-400"
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                transition={{ duration: 0.15 }}
              >
                {error}
              </motion.p>
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
