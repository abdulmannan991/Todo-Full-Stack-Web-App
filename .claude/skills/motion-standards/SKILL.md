---
name: motion-standards
description: Best practices for Framer Motion and performant CSS animations in Next.js. Use when implementing UI transitions, gestures, or visual effects.
version: 1.0.0
owner: ui-auth-expert
tags: [animation, framer-motion, performance, ux, next.js]
---

# Motion Standards Skill

## Purpose
Implement smooth, performant, and accessible animations using Framer Motion in Next.js applications while respecting user preferences and maintaining optimal performance.

## Scope
- **Owned By**: @ui-auth-expert
- **Technology Stack**: Framer Motion, Next.js, React, CSS
- **Performance Target**: 60fps animations, GPU-accelerated transforms

## Core Principles

### 1. Performance First
**GPU-Accelerated Properties Only**

Always prefer properties that trigger GPU acceleration to avoid layout recalculations and repaints:

#### ✅ GOOD - GPU-Accelerated
```typescript
import { motion } from 'framer-motion'

// Transform properties (translate, scale, rotate)
<motion.div
  animate={{
    x: 100,           // translateX
    y: 50,            // translateY
    scale: 1.2,       // transform: scale
    rotate: 45,       // transform: rotate
    opacity: 0.8      // opacity
  }}
/>

// Using transform shorthand
<motion.div
  animate={{
    transform: 'translateX(100px) scale(1.2)'
  }}
/>
```

#### ❌ BAD - Triggers Layout/Paint
```typescript
// These cause expensive layout recalculations
<motion.div
  animate={{
    width: 300,       // ❌ Triggers layout
    height: 200,      // ❌ Triggers layout
    top: 100,         // ❌ Triggers layout
    left: 50,         // ❌ Triggers layout
    padding: 20,      // ❌ Triggers layout
    margin: 10,       // ❌ Triggers layout
    backgroundColor: '#ff0000'  // ❌ Triggers paint
  }}
/>
```

#### Performance Hierarchy
1. **Best**: `transform` (translateX/Y, scale, rotate) + `opacity`
2. **Good**: `filter` effects (blur, brightness) - GPU accelerated but heavier
3. **Avoid**: Layout properties (width, height, position)
4. **Never in production**: Background color, border, padding, margin

### 2. UX First - Purposeful Animation

Every animation must serve a purpose:

#### Animation Purposes
- **Feedback**: Confirm user actions (button press, toggle)
- **Attention**: Draw focus to important changes
- **Context**: Show relationships between elements
- **Delight**: Enhance brand personality (use sparingly)

#### Spring Physics for Natural Feel
```typescript
// ✅ Natural, high-quality feel
<motion.div
  animate={{ scale: 1.1 }}
  transition={{
    type: "spring",
    stiffness: 300,    // Higher = snappier
    damping: 20,       // Higher = less bouncy
    mass: 1            // Higher = slower
  }}
/>

// Common spring presets
const springPresets = {
  gentle: { type: "spring", stiffness: 100, damping: 15 },
  snappy: { type: "spring", stiffness: 400, damping: 25 },
  bouncy: { type: "spring", stiffness: 300, damping: 10 },
}
```

#### Timing Guidelines
- **Micro-interactions**: 200-300ms (buttons, toggles)
- **Element transitions**: 300-500ms (cards, modals)
- **Page transitions**: 400-600ms (route changes)
- **Large movements**: 500-800ms (drawers, panels)

```typescript
// Duration-based timing (use for simple animations)
<motion.div
  animate={{ opacity: 1 }}
  transition={{
    duration: 0.3,
    ease: "easeOut"  // or [0.4, 0, 0.2, 1] for custom cubic-bezier
  }}
/>
```

### 3. Accessibility - Reduced Motion

**CRITICAL**: Always respect user OS preferences for reduced motion.

```typescript
'use client'

import { motion, useReducedMotion } from 'framer-motion'

function AnimatedComponent() {
  const shouldReduceMotion = useReducedMotion()

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: shouldReduceMotion ? 0 : 0.5,
        type: shouldReduceMotion ? "tween" : "spring"
      }}
    >
      Content
    </motion.div>
  )
}
```

#### Global Reduced Motion Configuration
```typescript
// app/providers.tsx
'use client'

import { MotionConfig } from 'framer-motion'
import { useReducedMotion } from 'framer-motion'

export function MotionProvider({ children }: { children: React.ReactNode }) {
  const shouldReduceMotion = useReducedMotion()

  return (
    <MotionConfig reducedMotion={shouldReduceMotion ? "always" : "never"}>
      {children}
    </MotionConfig>
  )
}
```

### 4. Clean Code - Variants Pattern

Use variants to separate animation logic from JSX structure.

#### ✅ GOOD - Using Variants
```typescript
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 24
    }
  }
}

function TodoList({ todos }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {todos.map(todo => (
        <motion.li key={todo.id} variants={itemVariants}>
          {todo.title}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

#### ❌ BAD - Inline Animation Objects
```typescript
function TodoList({ todos }) {
  return (
    <motion.ul
      initial={{ opacity: 0 }}
      animate={{
        opacity: 1,
        transition: { staggerChildren: 0.1, delayChildren: 0.2 }
      }}
    >
      {todos.map(todo => (
        <motion.li
          key={todo.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{
            opacity: 1,
            y: 0,
            transition: { type: "spring", stiffness: 300, damping: 24 }
          }}
        >
          {todo.title}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

### 5. Orchestration - Stagger Animations

Create sophisticated sequences for lists and grids.

#### Staggered List Entry
```typescript
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,        // Delay between each child
      delayChildren: 0.1,            // Delay before first child
      staggerDirection: 1,           // 1 = forward, -1 = reverse
    }
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1           // Exit in reverse
    }
  }
}

const itemVariants = {
  hidden: {
    opacity: 0,
    y: 20,
    scale: 0.95
  },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 24
    }
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.2 }
  }
}
```

#### Grid Stagger Pattern
```typescript
// 2D grid stagger (row by row)
const gridContainerVariants = {
  visible: {
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1
    }
  }
}

// For custom stagger order, use custom prop
const customStagger = {
  visible: (custom: number) => ({
    opacity: 1,
    transition: { delay: custom * 0.1 }
  })
}

<motion.div variants={gridContainerVariants} initial="hidden" animate="visible">
  {items.map((item, index) => (
    <motion.div
      key={item.id}
      custom={index}
      variants={customStagger}
    >
      {item.content}
    </motion.div>
  ))}
</motion.div>
```

## Common Patterns

### 1. Button Press Feedback
```typescript
const buttonVariants = {
  rest: { scale: 1 },
  pressed: { scale: 0.95 },
  hover: { scale: 1.05 }
}

<motion.button
  variants={buttonVariants}
  initial="rest"
  whileHover="hover"
  whileTap="pressed"
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  Click me
</motion.button>
```

### 2. Modal/Dialog Entry
```typescript
const modalVariants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: 20
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 30
    }
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.2 }
  }
}

const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
  exit: { opacity: 0 }
}

<AnimatePresence>
  {isOpen && (
    <>
      <motion.div
        className="backdrop"
        variants={backdropVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
      />
      <motion.div
        className="modal"
        variants={modalVariants}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        Modal content
      </motion.div>
    </>
  )}
</AnimatePresence>
```

### 3. Page Transitions
```typescript
// app/template.tsx (wraps all routes)
'use client'

import { motion } from 'framer-motion'

const pageVariants = {
  initial: { opacity: 0, x: -20 },
  enter: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 }
}

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="enter"
      exit="exit"
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      {children}
    </motion.div>
  )
}
```

### 4. Scroll-Triggered Animations
```typescript
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'

function ScrollReveal({ children }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 50 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 50 }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
    >
      {children}
    </motion.div>
  )
}
```

### 5. Gesture Interactions
```typescript
import { motion, useMotionValue, useTransform } from 'framer-motion'

function DraggableCard() {
  const x = useMotionValue(0)
  const rotate = useTransform(x, [-200, 200], [-25, 25])
  const opacity = useTransform(x, [-200, -100, 0, 100, 200], [0, 1, 1, 1, 0])

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={0.7}
      style={{ x, rotate, opacity }}
      onDragEnd={(e, { offset, velocity }) => {
        if (Math.abs(offset.x) > 150) {
          // Swipe action triggered
        }
      }}
    >
      Swipe me
    </motion.div>
  )
}
```

## Anti-Patterns to Avoid

### ❌ Animating Many Items Simultaneously
```typescript
// BAD: Creates performance issues
{todos.map(todo => (
  <motion.div
    key={todo.id}
    animate={{ scale: [1, 1.2, 1] }}  // All animate at once
  />
))}

// GOOD: Use stagger or limit animation scope
<motion.div variants={containerVariants}>
  {todos.map(todo => (
    <motion.div key={todo.id} variants={itemVariants} />
  ))}
</motion.div>
```

### ❌ Layout Animations Without layoutId
```typescript
// BAD: Choppy animation when item moves
<motion.div animate={{ x: position }} />

// GOOD: Smooth shared layout animation
<motion.div layoutId={`item-${id}`} />
```

### ❌ Overusing AnimatePresence
```typescript
// BAD: Wrapping everything
<AnimatePresence>
  <motion.div animate={{ opacity: 1 }}>Static content</motion.div>
</AnimatePresence>

// GOOD: Only for unmounting animations
<AnimatePresence>
  {isVisible && <motion.div exit={{ opacity: 0 }}>Content</motion.div>}
</AnimatePresence>
```

## Performance Optimization

### 1. Use `will-change` Sparingly
```typescript
// Only add will-change for animations that happen frequently
<motion.div
  style={{ willChange: "transform" }}
  whileHover={{ scale: 1.1 }}
/>
```

### 2. Layout Animations
```typescript
// For smooth layout changes
<motion.div layout layoutId="unique-id">
  Content that changes size/position
</motion.div>

// Disable layout animation on specific axis
<motion.div layout="position">  {/* Only animate position changes */}
  Content
</motion.div>
```

### 3. Optimize Re-renders
```typescript
import { memo } from 'react'

// Prevent unnecessary re-renders
const AnimatedItem = memo(({ item }) => (
  <motion.div variants={itemVariants}>
    {item.content}
  </motion.div>
))
```

## Validation Checks

When invoked, this skill will:
1. Scan components for animation property usage
2. Flag non-GPU-accelerated properties (width, height, top, left, etc.)
3. Verify `useReducedMotion` implementation
4. Check for inline animation objects vs. variants
5. Identify missing AnimatePresence for exit animations
6. Validate timing durations against UX guidelines
7. Generate motion performance report

## Usage

```bash
# Audit all animations
/motion-standards

# Check specific component
/motion-standards --component TodoList

# Performance analysis
/motion-standards --performance

# Accessibility audit
/motion-standards --accessibility
```

## Success Criteria
- ✅ All animations use GPU-accelerated properties
- ✅ Reduced motion preferences respected
- ✅ Animation timing follows UX guidelines
- ✅ Variants pattern used for complex animations
- ✅ 60fps maintained during animations
- ✅ No layout thrashing or jank
- ✅ Purposeful animations only (no gratuitous effects)

## Integration
This skill integrates with:
- **@ui-auth-expert**: Primary owner and executor
- **@performance-optimizer**: Animation performance monitoring
- **@responsive-validator**: Ensure animations work across viewports
- **@qa-automation**: Animation regression testing

## Resources

### Framer Motion Docs
- [Animation API](https://www.framer.com/motion/animation/)
- [Variants](https://www.framer.com/motion/animation/#variants)
- [Gestures](https://www.framer.com/motion/gestures/)
- [Layout Animations](https://www.framer.com/motion/layout-animations/)

### Performance
- [CSS Triggers](https://csstriggers.com/) - What properties trigger layout/paint
- [GPU Animation Guide](https://www.html5rocks.com/en/tutorials/speed/high-performance-animations/)

### Accessibility
- [Reduced Motion Media Query](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
- [WCAG 2.1 Animation Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html)
