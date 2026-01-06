/**
 * Framer Motion Animation Variants for Midnight Genesis
 *
 * All variants use GPU-accelerated properties only (transform, opacity)
 * per Constitution performance standards and motion-standards skill.
 *
 * Owner: @css-animation-expert
 */

import { Variants } from "framer-motion"

/**
 * Fade in from bottom animation
 * GPU-safe: Uses transform (translateY) and opacity only
 */
export const fadeInUp: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: [0.25, 0.1, 0.25, 1], // Custom easing for smooth motion
    },
  },
}

/**
 * Stagger container for sequential child animations
 * Used to create staggered entrance effects
 */
export const staggerContainer: Variants = {
  hidden: {
    opacity: 0,
  },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1, // 100ms delay between each child
      delayChildren: 0.1, // Initial delay before first child
    },
  },
}

/**
 * Scale animation for buttons and interactive elements
 * GPU-safe: Uses transform (scale) only
 */
export const scaleOnHover: Variants = {
  rest: {
    scale: 1,
  },
  hover: {
    scale: 1.05,
    transition: {
      type: "spring",
      stiffness: 400,
      damping: 17,
    },
  },
  pressed: {
    scale: 0.95,
  },
}

/**
 * Slide in from right animation (for toast notifications)
 * GPU-safe: Uses transform (translateX) and opacity only
 */
export const slideInRight: Variants = {
  hidden: {
    opacity: 0,
    x: 100,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 30,
    },
  },
  exit: {
    opacity: 0,
    x: 100,
    transition: {
      duration: 0.2,
    },
  },
}
