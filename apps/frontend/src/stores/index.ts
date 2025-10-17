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

// Type exports
export type { PendingMedia } from './media/useMediaStore';
export type {
  PostDynamics,
  TopPost,
  BestTimeRecommendation,
  EngagementMetrics
} from './analytics/useAnalyticsStore';
