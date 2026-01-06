/**
 * EmptyState Component
 *
 * Sprint 2 - Task: T092
 * Owner: @css-animation-expert
 *
 * Displays a friendly empty state message when user has no tasks.
 * Styled with Premium Midnight theme.
 */

export default function EmptyState() {
  return (
    <div
      className="glass-card p-12 text-center"
      role="status"
      aria-live="polite"
    >
      {/* Icon */}
      <div className="flex justify-center mb-6">
        <div className="w-24 h-24 rounded-full bg-primary-violet/10 flex items-center justify-center">
          <svg
            className="w-12 h-12 text-primary-violet"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
      </div>

      {/* Message */}
      <h3 className="text-xl font-semibold text-text-primary mb-2">
        No tasks yet
      </h3>
      <p className="text-text-secondary max-w-md mx-auto">
        Create your first task to get started on your productivity journey!
      </p>

      {/* Decorative Element */}
      <div className="mt-8 flex justify-center gap-2">
        <div className="w-2 h-2 rounded-full bg-primary-violet/30 animate-pulse"></div>
        <div
          className="w-2 h-2 rounded-full bg-secondary-indigo/30 animate-pulse"
          style={{ animationDelay: "0.2s" }}
        ></div>
        <div
          className="w-2 h-2 rounded-full bg-primary-violet/30 animate-pulse"
          style={{ animationDelay: "0.4s" }}
        ></div>
      </div>
    </div>
  );
}
