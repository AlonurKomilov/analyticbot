/**
 * Post Scheduling Components
 * Re-exports the NEW modular ScheduledPostsList from pages
 *
 * DEPRECATED: The old ScheduledPostsList.tsx in this folder is kept for reference
 * but the actual component now comes from pages/ScheduledPostsPage/components
 */

// Export the new modular component
export { default as ScheduledPostsList } from '@/pages/ScheduledPostsPage/components/ScheduledPostsList';

// Keep old export commented for reference
// export { default as ScheduledPostsList } from './ScheduledPostsList';
