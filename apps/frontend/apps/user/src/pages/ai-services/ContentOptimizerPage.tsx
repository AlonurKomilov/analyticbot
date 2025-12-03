/**
 * Content Optimizer Page
 * Re-exports the modular component from features
 *
 * The actual implementation with proper component separation is in:
 * @features/ai-services/ContentOptimizer/
 *
 * This file exists for compatibility with the pages/ barrel exports
 */

// Re-export from the modular features implementation
export { ContentOptimizerPage as default } from '@features/ai-services/ContentOptimizer';
