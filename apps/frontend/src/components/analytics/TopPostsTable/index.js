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

export { default } from './TopPostsTable.jsx';

// Export individual components for reuse
export { default as PostTableFilters } from './components/PostTableFilters.jsx';
export { default as PostSummaryStats } from './components/PostSummaryStats.jsx';
export { default as PostTableRow } from './components/PostTableRow.jsx';
export { default as PostMetricBadge } from './components/PostMetricBadge.jsx';
export { default as PostActionMenu } from './components/PostActionMenu.jsx';

// Export hooks and utilities
export { usePostTableLogic } from './hooks/usePostTableLogic.js';
export * from './utils/postTableUtils.js';
