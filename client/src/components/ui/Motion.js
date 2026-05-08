"use client";

import { motion } from "framer-motion";

/* ═══════════════════════════════════════════════════════════════════
   Reusable Framer Motion wrappers for consistent animations
   ═══════════════════════════════════════════════════════════════════ */

/**
 * Fade in from below.
 */
export function FadeIn({ children, delay = 0, duration = 0.5, className = "", y = 20 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/**
 * Slide in from the left.
 */
export function SlideIn({ children, delay = 0, duration = 0.5, className = "", x = -30 }) {
  return (
    <motion.div
      initial={{ opacity: 0, x }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/**
 * Scale in with a subtle pop.
 */
export function ScaleIn({ children, delay = 0, duration = 0.4, className = "" }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.92 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/**
 * Stagger container — children animate in sequence.
 * Wrap each child in a <StaggerItem>.
 */
export function StaggerContainer({ children, stagger = 0.08, delay = 0, className = "" }) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: {
          transition: {
            staggerChildren: stagger,
            delayChildren: delay,
          },
        },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/**
 * Child of StaggerContainer.
 */
export function StaggerItem({ children, className = "", y = 15 }) {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y },
        visible: {
          opacity: 1,
          y: 0,
          transition: { duration: 0.45, ease: [0.25, 0.46, 0.45, 0.94] },
        },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/**
 * Hover lift effect for interactive cards.
 */
export function HoverCard({ children, className = "" }) {
  return (
    <motion.div
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/**
 * Number counter animation.
 */
export { motion };
