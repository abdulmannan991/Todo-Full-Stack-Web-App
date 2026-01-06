/**
 * TaskSkeleton Component
 *
 * Sprint 2 - Task: T094
 * Owner: @css-animation-expert
 *
 * Loading skeleton displayed during task fetch.
 * Pulsing glassmorphic cards with smooth transitions.
 */

export default function TaskSkeleton({ count = 3 }: { count?: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className="glass-card p-6 animate-pulse"
          role="status"
          aria-label="Loading task"
        >
          {/* Status Badge Skeleton */}
          <div className="flex items-start justify-between mb-3">
            <div className="h-6 w-20 bg-white/10 rounded-full"></div>
            <div className="h-4 w-16 bg-white/10 rounded"></div>
          </div>

          {/* Title Skeleton */}
          <div className="space-y-2 mb-3">
            <div className="h-6 w-3/4 bg-white/10 rounded"></div>
            <div className="h-6 w-1/2 bg-white/10 rounded"></div>
          </div>

          {/* Description Skeleton */}
          <div className="space-y-2">
            <div className="h-4 w-full bg-white/5 rounded"></div>
            <div className="h-4 w-5/6 bg-white/5 rounded"></div>
            <div className="h-4 w-2/3 bg-white/5 rounded"></div>
          </div>
        </div>
      ))}
    </>
  );
}
