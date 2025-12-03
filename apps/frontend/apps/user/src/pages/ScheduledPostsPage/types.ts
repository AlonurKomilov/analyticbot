/**
 * Type definitions for Scheduled Posts Page
 * Re-exports ScheduledPost from global types and defines component-specific props
 */

// Re-export the main ScheduledPost type from global types
export type { ScheduledPost } from '@/types/models';

export interface ScheduledPostCardProps {
  post: any; // Using any to handle both old and new API formats
  onDelete: (id: string | number) => void;
  isDeleting?: boolean;
}

export interface ScheduledPostsListProps {
  posts: any[]; // Using any to handle both old and new API formats
  onDelete: (id: string | number) => void;
  isDeleting?: boolean;
}

export interface EmptyStateProps {
  message?: string;
  actionText?: string;
  onAction?: () => void;
}

export interface ErrorAlertProps {
  error: string;
  onRetry?: () => void;
}

export interface UseScheduledPostsReturn {
  posts: any[]; // Using any to handle both old and new API formats
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export interface UsePostActionsReturn {
  handleDelete: (id: string | number) => Promise<void>;
  isDeleting: boolean;
}
