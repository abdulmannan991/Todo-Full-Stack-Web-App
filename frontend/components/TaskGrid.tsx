"use client";

/**
 * TaskGrid Component
 *
 * Sprint 2 - Tasks: T088 (Structure), T093 (Animations)
 * Owner: @ui-auth-expert (structure), @css-animation-expert (animations)
 *
 * Responsive grid layout for task cards with Framer Motion animations.
 * - Desktop: 3-column grid
 * - Tablet: 2-column grid
 * - Mobile: 1-column layout
 */

import { motion } from "framer-motion";
import TaskCard, { Task } from "./TaskCard";

interface TaskGridProps {
  tasks: Task[];
  onTaskUpdated?: () => void; // Callback to refresh tasks after update
}

export default function TaskGrid({ tasks, onTaskUpdated }: TaskGridProps) {
  /**
   * Framer Motion variants for staggered entrance animations (T093)
   * - Container: Stagger children with 50ms delay
   * - Cards: Fade in from bottom with spring animation
   */
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05, // 50ms delay between children
        delayChildren: 0.1,
      },
    },
  };

  const cardVariants = {
    hidden: {
      opacity: 0,
      y: 20, // Fade in from 20px below
    },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 15,
        mass: 0.5,
      },
    },
  };

  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      layout // Enable layout animations for smooth reordering
    >
      {tasks.map((task) => (
        <motion.div
          key={task.id}
          variants={cardVariants}
          layout // Smooth reposition when tasks are added/removed (T102)
          layoutId={`task-${task.id}`} // Unique ID for layout animations
          transition={{
            layout: {
              type: "spring",
              stiffness: 100,
              damping: 20,
            },
          }}
        >
          <TaskCard task={task} onTaskUpdated={onTaskUpdated} />
        </motion.div>
      ))}
    </motion.div>
  );
}
