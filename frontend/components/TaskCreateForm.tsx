"use client";

/**
 * TaskCreateForm Component
 *
 * Sprint 2 - Tasks: T084 (Structure), T085 (API Integration), T086 (Styling)
 * Owner: @ui-auth-expert (structure/API), @css-animation-expert (styling)
 *
 * Allows users to create new tasks with title and optional description.
 * Enforces client-side validation before submitting to backend.
 */

import { useState } from "react";
import { toast } from "sonner";
import { useSession } from "@/lib/auth-client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface TaskCreateFormProps {
  onTaskCreated?: () => void; // Callback to refresh task list
}

export default function TaskCreateForm({ onTaskCreated }: TaskCreateFormProps) {
  const { data: session } = useSession();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [titleError, setTitleError] = useState("");

  /**
   * Client-side validation for task title.
   * Ensures title is non-empty and within max length (500 chars).
   */
  const validateTitle = (value: string): boolean => {
    setTitleError("");

    if (!value || !value.trim()) {
      setTitleError("Title cannot be empty");
      return false;
    }

    if (value.length > 500) {
      setTitleError("Title must be 500 characters or less");
      return false;
    }

    return true;
  };

  /**
   * Handle form submission.
   * Validates input, calls POST /tasks API, shows toast notifications.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Client-side validation
    if (!validateTitle(title)) {
      return;
    }

    if (description.length > 5000) {
      toast.error("Description must be 5000 characters or less");
      return;
    }

    // Check authentication
    if (!session?.token) {
      toast.error("Authentication required");
      window.location.href = "/login";
      return;
    }

    setIsSubmitting(true);

    try {
      // Call POST /tasks endpoint (T085)
      const response = await fetch(`${API_BASE_URL}/tasks/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.token}`,
        },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim() || undefined,
        }),
      });

      // CRITICAL: Check response.ok BEFORE calling response.json()
      if (!response.ok) {
        // Handle non-JSON error responses (401, 403, 500, etc.)
        let errorMessage = "Failed to create task";

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

      const newTask = await response.json();

      // Success: Show toast, clear form, refresh task list
      toast.success("Task created!");
      setTitle("");
      setDescription("");
      setTitleError("");

      // Trigger task list refresh
      if (onTaskCreated) {
        onTaskCreated();
      }
    } catch (error) {
      console.error("Task creation error:", error);
      toast.error(
        error instanceof Error ? error.message : "Failed to create task"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="glass-card p-6 mb-8"
      aria-label="Create new task"
    >
      <h2 className="text-xl font-semibold text-text-primary mb-4">
        Create New Task
      </h2>

      {/* Title Input */}
      <div className="mb-4">
        <label
          htmlFor="task-title"
          className="block text-sm font-medium text-text-secondary mb-2"
        >
          Title <span className="text-red-400">*</span>
        </label>
        <input
          id="task-title"
          type="text"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value);
            if (titleError) validateTitle(e.target.value);
          }}
          onBlur={() => validateTitle(title)}
          placeholder="Enter task title..."
          maxLength={500}
          className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg
                   text-text-primary placeholder:text-text-secondary/50
                   focus:outline-none focus:ring-2 focus:ring-primary-violet focus:border-transparent
                   transition-all duration-200"
          disabled={isSubmitting}
          aria-required="true"
          aria-invalid={!!titleError}
          aria-describedby={titleError ? "title-error" : undefined}
        />
        {titleError && (
          <p id="title-error" className="mt-1 text-sm text-red-400">
            {titleError}
          </p>
        )}
        <p className="mt-1 text-xs text-text-secondary">
          {title.length}/500 characters
        </p>
      </div>

      {/* Description Textarea */}
      <div className="mb-6">
        <label
          htmlFor="task-description"
          className="block text-sm font-medium text-text-secondary mb-2"
        >
          Description (optional)
        </label>
        <textarea
          id="task-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more details about this task..."
          maxLength={5000}
          rows={4}
          className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg
                   text-text-primary placeholder:text-text-secondary/50
                   focus:outline-none focus:ring-2 focus:ring-primary-violet focus:border-transparent
                   transition-all duration-200 resize-none"
          disabled={isSubmitting}
        />
        <p className="mt-1 text-xs text-text-secondary">
          {description.length}/5000 characters
        </p>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isSubmitting || !title.trim()}
        className="w-full px-6 py-3 bg-primary-violet hover:bg-secondary-indigo
                 text-white font-medium rounded-lg
                 transition-colors duration-200
                 disabled:opacity-50 disabled:cursor-not-allowed
                 focus:outline-none focus:ring-2 focus:ring-primary-violet focus:ring-offset-2 focus:ring-offset-midnight-bg"
      >
        {isSubmitting ? (
          <span className="flex items-center justify-center">
            <svg
              className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
            Creating...
          </span>
        ) : (
          "Create Task"
        )}
      </button>
    </form>
  );
}
