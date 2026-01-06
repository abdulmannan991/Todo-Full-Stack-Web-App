/**
 * StatusBadge Component
 *
 * Sprint 2 - Task: T091
 * Owner: @css-animation-expert
 *
 * Displays task status with Premium Midnight theme styling.
 * - "Pending" badge: Electric violet background
 * - "Completed" badge: Green background
 */

interface StatusBadgeProps {
  status: "pending" | "completed";
  className?: string;
}

export default function StatusBadge({ status, className = "" }: StatusBadgeProps) {
  const isPending = status === "pending";

  return (
    <span
      className={`
        inline-flex items-center px-3 py-1 rounded-full text-xs font-medium
        ${
          isPending
            ? "bg-primary-violet/20 text-primary-violet"
            : "bg-green-500/20 text-green-500"
        }
        ${className}
      `}
      aria-label={`Status: ${status}`}
    >
      {/* Status Icon */}
      {isPending ? (
        <svg
          className="w-3 h-3 mr-1.5"
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <circle cx="10" cy="10" r="6" />
        </svg>
      ) : (
        <svg
          className="w-3 h-3 mr-1.5"
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
      )}

      {/* Status Text */}
      <span className="capitalize">{status}</span>
    </span>
  );
}
