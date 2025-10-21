/**
 * Store Exports
 * Central export point for all domain stores
 * Replaces the monolithic appStore.js
 */

// Domain stores
export { useAuthStore } from './auth/useAuthStore';
export { useChannelStore } from './channels/useChannelStore';
export { usePostStore } from './posts/usePostStore';
export { useAnalyticsStore } from './analytics/useAnalyticsStore';
export { useMediaStore } from './media/useMediaStore';
export { useUIStore } from './ui/useUIStore';

// Re-export types from @/types for convenience
export type {
  // Auth types
  User,
  UserRole,
  UserPreferences,

  // Channel types
  Channel,
  ChannelMetrics,

  // Post types
  Post,
  ScheduledPost,
  PostStatus,

  // Analytics types
  AnalyticsOverview,
  GrowthMetrics,
  PostDynamics,
  TopPost,
  BestTimeRecommendation,
  EngagementMetrics,

  // Media types
  MediaFile,
  PendingMedia,
  UploadProgress,

  // UI types
  DataSource
} from '@/types';
