/**
 * Post Type Definitions
 * Core types for the posts feature module
 */

export interface PostMetrics {
  views: number;
  forwards: number;
  comments_count: number;  // Discussion group comments on channel posts
  replies_count?: number;   // Direct threaded replies in groups/supergroups
  reactions_count: number;
  snapshot_time?: string;
}

export interface Post {
  id: number;
  channel_id: number;
  msg_id: number;
  date: string;
  text: string;
  created_at: string;
  updated_at: string;
  metrics?: PostMetrics;
  channel_name?: string;
  channel_username?: string;
}

export interface PostsResponse {
  posts: Post[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface PostsFilters {
  selectedChannel: number | 'all';
  searchQuery: string;
  page: number;
}

export interface VisibleColumns {
  channel: boolean;
  messageId: boolean;
  content: boolean;
  views: boolean;
  forwards: boolean;
  comments: boolean;    // Discussion group comments
  replies?: boolean;    // Threaded replies (optional, for future use)
  reactions: boolean;
  telegram: boolean;
  date: boolean;
}

export type ViewMode = 'table' | 'grid';
