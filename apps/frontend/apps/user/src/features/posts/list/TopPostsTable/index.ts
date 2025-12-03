/**
 * TopPostsTable - Refactored modular components
 *
 * This is the new, refactored TopPostsTable with separated concerns:
 * - PostTableFilters: Time and sort filter controls
 * - PostSummaryStats: Statistics summary cards
 * - PostTableRow: Individual table row component
 * - PostMetricBadge: Performance badge component
 * - PostActionMenu: Row action menu component
 * - usePostTableLogic: Business logic hook
 * - postTableUtils: Utility functions
 */

export { default } from './TopPostsTable';

// Export individual components for reuse
export { default as PostTableFilters } from './components/PostTableFilters';
export { default as PostSummaryStats } from './components/PostSummaryStats';
export { default as PostTableRow } from './components/PostTableRow';
export { default as PostMetricBadge } from './components/PostMetricBadge';
export { default as PostActionMenu } from './components/PostActionMenu';

// Export hooks and utilities
export { usePostTableLogic } from './hooks/usePostTableLogic';
export * from './utils/postTableUtils';
