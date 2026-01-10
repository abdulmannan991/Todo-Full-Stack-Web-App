"use client";

/**
 * TaskCard Component
 *
 * Sprint 2 - Tasks: T087 (Structure), T090 (Styling), T098-T102 (Completion)
 * Owner: @ui-auth-expert (structure/API), @css-animation-expert (styling/animation)
 *
 * Displays a single task with title, description, status badge, and created date.
 * Features:
 * - Glassmorphic styling with violet/indigo border glow
 * - Completion checkbox with green check animation (T098-T102)
 * - Hover effects and smooth transitions
 */

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { useSession } from "@/lib/auth-client";
import { API_BASE_URL } from "@/lib/config";
import StatusBadge from "./StatusBadge";
import EditableTitle from "./EditableTitle";
import DeleteTaskButton from "./DeleteTaskButton";


export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: "pending" | "completed";
  created_at: string;
  updated_at: string;
}



interface TaskCardProps {
  task: Task;
  onTaskUpdated?: () => void; // Callback to refresh task list
}

export default function TaskCard({ task, onTaskUpdated }: TaskCardProps) {
  const { data: session } = useSession();
  const [isUpdating, setIsUpdating] = useState(false);
  const [showCheckAnimation, setShowCheckAnimation] = useState(false);

  /**
   * Handle task completion toggle (T098, T099)
   * Calls PATCH /tasks/{id} with status update
   */
 const handleToggleComplete = async () => {
  if (task.status === "completed" || isUpdating) return;
  setIsUpdating(true);

  try {
    // Use the latest token directly from localStorage if hook is lagging
    const currentToken = localStorage.getItem('auth_token');
    
    const response = await fetch(`${API_BASE_URL}/tasks/${task.id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${currentToken || session?.token || ''}`,
      },
      body: JSON.stringify({ status: "completed" }),
    });

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        toast.error("Session expired. Please log in again.");
        // Let the auth-client handle the redirect, don't force it here
        return;
      }
      throw new Error(`Server error: ${response.status}`);
    }

    setShowCheckAnimation(true);
    toast.success("Task completed!");
    if (onTaskUpdated) onTaskUpdated();
    
  } catch (error) {
    if (error instanceof Error && error.message === 'NETWORK_ERROR') {
      toast.error("Network connection unstable. Retrying...");
    } else {
      console.error("Task update error:", error);
      toast.error("Failed to update task. Please try again.");
    }
  } finally {
    setIsUpdating(false);
  }
};

  /**
   * Format date to human-readable format.
   * Example: "2 hours ago", "Yesterday", "Jan 5, 2026"
   */
  /**
   * Format date to human-readable format with UTC correction.
   */
const formatDate = (dateString: string): string => {
  // 1. If the string doesn't end in Z, add it to FORCE UTC interpretation
  const utcString = dateString.endsWith('Z') ? dateString : `${dateString}Z`;
  
  // 2. new Date(utcString) will now automatically convert 
  // the server's 5:00 AM UTC to 10:00 AM Karachi time
  const date = new Date(utcString);
  const now = new Date();
  
  // 3. Compare using absolute timestamps
  const diffMs = now.getTime() - date.getTime();
  
  // 60-second safety buffer
  if (diffMs < 60000) return "Just now";
  
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);

  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  
  return date.toLocaleDateString();
};

  /**
   * Truncate description to prevent card overflow.
   * Shows first 150 characters with ellipsis.
   */
  const truncateDescription = (text: string | null, maxLength: number = 150): string => {
    if (!text) return "";
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + "...";
  };

  // Completed task styling (T101)
  const cardClassName = task.status === "completed"
    ? "glass-card p-6 border-green-500/50 shadow-green-500/20 transition-all duration-300 ease-out group"
    : "glass-card p-6 border-primary-violet/30 hover:shadow-lg hover:shadow-primary-violet/20 hover:-translate-y-1 transition-all duration-300 ease-out group";

  return (
    <div className={cardClassName} role="article" aria-labelledby={`task-title-${task.id}`}>
      {/* Status Badge, Completion Checkbox, and Delete Button */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <StatusBadge status={task.status} />

          {/* Completion Checkbox (T098) */}
          <button
            onClick={handleToggleComplete}
            disabled={task.status === "completed" || isUpdating}
            className={`
              relative w-6 h-6 rounded border-2 flex items-center justify-center
              transition-all duration-200
              ${
                task.status === "completed"
                  ? "bg-green-500 border-green-500 cursor-not-allowed"
                  : "border-primary-violet hover:border-secondary-indigo hover:bg-primary-violet/10 cursor-pointer"
              }
              ${isUpdating ? "opacity-50 cursor-wait" : ""}
            `}
            aria-label={
              task.status === "completed" ? "Task completed" : "Mark as complete"
            }
            title={
              task.status === "completed"
                ? "Task completed"
                : "Click to mark as complete"
            }
          >
            {/* Green Check Animation (T100) */}
            <AnimatePresence>
              {(task.status === "completed" || showCheckAnimation) && (
                <motion.svg
                  className="w-4 h-4 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  initial={{ scale: 0.5, rotate: 0, opacity: 0 }}
                  animate={{
                    scale: [0.5, 1.2, 1],
                    rotate: [0, 360],
                    opacity: 1,
                  }}
                  exit={{ scale: 0, opacity: 0 }}
                  transition={{
                    duration: 0.3,
                    type: "spring",
                    stiffness: 200,
                    damping: 15,
                  }}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={3}
                    d="M5 13l4 4L19 7"
                  />
                </motion.svg>
              )}
            </AnimatePresence>
          </button>
        </div>

        {/* Date and Delete Button */}
        <div className="flex items-center gap-2">
          <time
          className="text-xs text-text-secondary"
          dateTime={task.created_at}
          title={new Date(task.created_at).toLocaleString()}
        >
            {formatDate(task.created_at)}
          </time>

          {/* Delete Button (T109-T115) */}
          <DeleteTaskButton
            taskId={task.id}
            taskTitle={task.title}
            onTaskDeleted={onTaskUpdated}
          />
        </div>
      </div>

      {/* Task Title - Editable Inline (T104-T108) */}
      <div id={`task-title-${task.id}`}>
        <EditableTitle
          taskId={task.id}
          initialTitle={task.title}
          onTitleUpdated={onTaskUpdated}
        />
      </div>

      {/* Task Description (truncated, T101 - opacity for completed) */}
      {task.description && (
        <p
          className={`
            text-sm text-text-secondary leading-relaxed line-clamp-3
            ${task.status === "completed" ? "opacity-80" : ""}
          `}
        >
          {truncateDescription(task.description)}
        </p>
      )}

      {/* Card Footer - Completion Indicator for Completed Tasks */}
      {task.status === "completed" && (
        <div className="mt-4 pt-4 border-t border-white/5">
          <div className="flex items-center text-green-500 text-xs">
            <svg
              className="w-4 h-4 mr-1.5"
              fill="currentColor"
              viewBox="0 0 20 20"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span>Completed</span>
          </div>
        </div>
      )}
    </div>
  );
}
