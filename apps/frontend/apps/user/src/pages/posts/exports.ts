/**
 * Posts Feature - Public API Exports
 * Following microservice-style architecture pattern
 */

// Main pages
export { default as PostsPage } from './index';
export { default as CreatePostPage } from './create';
export { default as EditPostPage } from './edit';
export { default as PostDetailsPage } from './details';

// Components
export { PostsTable } from './components/PostsTable';
export { PostsGrid } from './components/PostsGrid';
export { PostsFilters } from './components/PostsFilters';
export { PostsViewControls } from './components/PostsViewControls';

// Hooks
export { usePosts } from './hooks/usePosts';
export { usePostFilters } from './hooks/usePostFilters';
export { useColumnVisibility } from './hooks/useColumnVisibility';

// Types
export type { Post, PostMetrics, PostsResponse, PostsFilters as PostsFiltersType, VisibleColumns, ViewMode } from './types/Post';
