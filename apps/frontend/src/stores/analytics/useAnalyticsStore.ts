/**
 * Analytics Store
 * Manages analytics data and operations
 * Pure domain logic for analytics - separated from god store
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client.js';
import { ErrorHandler } from '@/utils/errorHandler.js';

export interface PostDynamics {
  dates: string[];
  views: number[];
  likes: number[];
  shares: number[];
}

export interface TopPost {
  id: string | number;
  content: string;
  views: number;
  engagement_rate: number;
  published_at: string;
}

export interface BestTimeRecommendation {
  hour: number;
  day_of_week: number;
  engagement_score: number;
  recommended: boolean;
}

export interface EngagementMetrics {
  total_views: number;
  total_likes: number;
  total_shares: number;
  engagement_rate: number;
  growth_rate: number;
}

interface AnalyticsState {
  // State
  postDynamics: PostDynamics | null;
  topPosts: TopPost[];
  bestTimeRecommendations: BestTimeRecommendation[] | null;
  engagementMetrics: EngagementMetrics | null;
  lastAnalyticsUpdate: number | null;

  isLoadingPostDynamics: boolean;
  isLoadingTopPosts: boolean;
  isLoadingBestTime: boolean;
  isLoadingEngagementMetrics: boolean;

  error: string | null;

  // Actions
  fetchPostDynamics: (channelId: string | number, timeRange?: string) => Promise<void>;
  fetchTopPosts: (channelId: string | number, limit?: number) => Promise<void>;
  fetchBestTime: (channelId: string | number) => Promise<void>;
  fetchEngagementMetrics: (channelId: string | number) => Promise<void>;
  clearAnalytics: () => void;
  clearError: () => void;
}

export const useAnalyticsStore = create<AnalyticsState>()(
  subscribeWithSelector((set) => ({
    // Initial state
    postDynamics: null,
    topPosts: [],
    bestTimeRecommendations: null,
    engagementMetrics: null,
    lastAnalyticsUpdate: null,

    isLoadingPostDynamics: false,
    isLoadingTopPosts: false,
    isLoadingBestTime: false,
    isLoadingEngagementMetrics: false,

    error: null,

    // Fetch post dynamics (views/likes/shares over time)
    fetchPostDynamics: async (channelId: string | number, timeRange: string = '30d') => {
      set({ isLoadingPostDynamics: true, error: null });

      try {
        console.log('📊 Fetching post dynamics for channel:', channelId);

        const dynamics = await apiClient.get(`/analytics/channels/${channelId}/post-dynamics`, {
          params: { time_range: timeRange }
        });

        set({
          postDynamics: dynamics,
          lastAnalyticsUpdate: Date.now(),
          isLoadingPostDynamics: false
        });

        console.log('✅ Post dynamics loaded');
      } catch (error) {
        console.error('❌ Failed to load post dynamics:', error);
        ErrorHandler.handleError(error, {
          component: 'AnalyticsStore',
          action: 'fetchPostDynamics',
          channelId,
          timeRange
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to load post dynamics';
        set({
          error: errorMessage,
          isLoadingPostDynamics: false
        });
      }
    },

    // Fetch top performing posts
    fetchTopPosts: async (channelId: string | number, limit: number = 10) => {
      set({ isLoadingTopPosts: true, error: null });

      try {
        console.log('🏆 Fetching top posts for channel:', channelId);

        const posts = await apiClient.get(`/analytics/channels/${channelId}/top-posts`, {
          params: { limit }
        });

        set({
          topPosts: posts || [],
          lastAnalyticsUpdate: Date.now(),
          isLoadingTopPosts: false
        });

        console.log('✅ Top posts loaded:', posts?.length || 0);
      } catch (error) {
        console.error('❌ Failed to load top posts:', error);
        ErrorHandler.handleError(error, {
          component: 'AnalyticsStore',
          action: 'fetchTopPosts',
          channelId,
          limit
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to load top posts';
        set({
          error: errorMessage,
          isLoadingTopPosts: false
        });
      }
    },

    // Fetch best time to post recommendations
    fetchBestTime: async (channelId: string | number) => {
      set({ isLoadingBestTime: true, error: null });

      try {
        console.log('⏰ Fetching best time recommendations for channel:', channelId);

        const recommendations = await apiClient.get(`/analytics/channels/${channelId}/best-time`);

        set({
          bestTimeRecommendations: recommendations || [],
          lastAnalyticsUpdate: Date.now(),
          isLoadingBestTime: false
        });

        console.log('✅ Best time recommendations loaded');
      } catch (error) {
        console.error('❌ Failed to load best time:', error);
        ErrorHandler.handleError(error, {
          component: 'AnalyticsStore',
          action: 'fetchBestTime',
          channelId
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to load recommendations';
        set({
          error: errorMessage,
          isLoadingBestTime: false
        });
      }
    },

    // Fetch engagement metrics
    fetchEngagementMetrics: async (channelId: string | number) => {
      set({ isLoadingEngagementMetrics: true, error: null });

      try {
        console.log('📈 Fetching engagement metrics for channel:', channelId);

        const metrics = await apiClient.get(`/analytics/channels/${channelId}/engagement`);

        set({
          engagementMetrics: metrics,
          lastAnalyticsUpdate: Date.now(),
          isLoadingEngagementMetrics: false
        });

        console.log('✅ Engagement metrics loaded');
      } catch (error) {
        console.error('❌ Failed to load engagement metrics:', error);
        ErrorHandler.handleError(error, {
          component: 'AnalyticsStore',
          action: 'fetchEngagementMetrics',
          channelId
        });

        const errorMessage = error instanceof Error ? error.message : 'Failed to load metrics';
        set({
          error: errorMessage,
          isLoadingEngagementMetrics: false
        });
      }
    },

    // Clear all analytics data
    clearAnalytics: () => {
      set({
        postDynamics: null,
        topPosts: [],
        bestTimeRecommendations: null,
        engagementMetrics: null,
        lastAnalyticsUpdate: null,
        error: null
      });
    },

    // Clear error
    clearError: () => {
      set({ error: null });
    }
  }))
);

export default useAnalyticsStore;
