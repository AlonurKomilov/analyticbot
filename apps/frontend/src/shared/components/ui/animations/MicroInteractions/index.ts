/**
 * Micro-interactions System
 *
 * Refactored from 554 lines to 11 files:
 * - types.ts: Type definitions
 * - keyframes.ts: Shared animation keyframes
 * - InteractiveCard.tsx: Card with hover effects
 * - AnimatedButton.tsx: Button with ripple effect
 * - AnimationContainers.tsx: FloatingElement, StaggeredAnimation
 * - SkeletonLoader.tsx: Loading skeleton
 * - FeedbackAnimation.tsx: Success/error feedback
 * - AnimatedProgress.tsx: Linear/circular progress
 * - TouchRipple.tsx: Mobile touch ripple
 * - index.ts: Barrel exports
 */

// Types
export * from './types';

// Keyframes
export * from './keyframes';

// Components
export { InteractiveCard } from './InteractiveCard';
export { AnimatedButton } from './AnimatedButton';
export { FloatingElement, StaggeredAnimation } from './AnimationContainers';
export { SkeletonLoader } from './SkeletonLoader';
export { FeedbackAnimation } from './FeedbackAnimation';
export { AnimatedProgress } from './AnimatedProgress';
export { TouchRipple } from './TouchRipple';

// Default export for backwards compatibility
export default {
  InteractiveCard: () => import('./InteractiveCard').then((m) => m.InteractiveCard),
  AnimatedButton: () => import('./AnimatedButton').then((m) => m.AnimatedButton),
  FloatingElement: () => import('./AnimationContainers').then((m) => m.FloatingElement),
  StaggeredAnimation: () => import('./AnimationContainers').then((m) => m.StaggeredAnimation),
  SkeletonLoader: () => import('./SkeletonLoader').then((m) => m.SkeletonLoader),
  FeedbackAnimation: () => import('./FeedbackAnimation').then((m) => m.FeedbackAnimation),
  AnimatedProgress: () => import('./AnimatedProgress').then((m) => m.AnimatedProgress),
  TouchRipple: () => import('./TouchRipple').then((m) => m.TouchRipple),
};
