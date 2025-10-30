/**
 * Store Exports
 * Central export point for all domain stores
 * Replaces the monolithic appStore.js
 */

// Domain stores
export { useAuthStore } from './slices/auth/useAuthStore';
export { useChannelStore } from './slices/channels/useChannelStore';
export { usePostStore } from './slices/posts/usePostStore';
export { useAnalyticsStore } from './slices/analytics/useAnalyticsStore';
export { useMediaStore } from './slices/media/useMediaStore';
export { useUIStore } from './slices/ui/useUIStore';
export { useUserBotStore, useBot, useAllBots, useBotLoading, useBotError } from './slices/userBot/useUserBotStore';
export { useMTProtoStore, useMTProtoStatus, useMTProtoLoading, useMTProtoError } from './slices/mtproto/useMTProtoStore';

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
