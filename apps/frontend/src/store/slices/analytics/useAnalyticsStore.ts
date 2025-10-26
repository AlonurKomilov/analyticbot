/**
 * Analytics Store (TypeScript)
 * Manages analytics data and operations
 * Pure domain logic for analytics - separated from god store
 *
 * IMPORTANT: Uses demo endpoints for consistent demo data
 * - /unified-analytics/demo/top-posts for demo_channel
 * - Falls back to client-side mock data if backend unavailable
 */

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { apiClient } from '@/api/client';
import { generateMockTopPosts } from '@/__mocks__/data/mockTopPosts';

import type {
  AnalyticsOverview,
  GrowthMetrics,
  ReachMetrics,
  PostDynamics,
  TopPost,
  EngagementMetrics,
  BestTimeRecommendation,
  TimePeriod
} from '@/types';

interface AnalyticsState {
  // Data
  overview: AnalyticsOverview | null;
  growthMetrics: GrowthMetrics | null;
  reachMetrics: ReachMetrics | null;
  postDynamics: PostDynamics | null;
  topPosts: TopPost[];
  engagementMetrics: EngagementMetrics | null;
  bestTimes: BestTimeRecommendation[];

  // Loading states
  isLoadingOverview: boolean;
  isLoadingGrowth: boolean;
  isLoadingReach: boolean;
  isLoadingPostDynamics: boolean;
  isLoadingTopPosts: boolean;
  isLoadingEngagement: boolean;
  isLoadingBestTime: boolean;

  // Error states
  overviewError: string | null;
  growthError: string | null;
  reachError: string | null;
  postDynamicsError: string | null;
  topPostsError: string | null;
  engagementError: string | null;
  bestTimeError: string | null;

  // Metadata
  selectedPeriod: TimePeriod;
  lastUpdate: number | null;

  // Actions
  fetchOverview: (channelId: string, period?: TimePeriod) => Promise<void>;
  fetchGrowthMetrics: (channelId: string, period?: TimePeriod) => Promise<void>;
  fetchReachMetrics: (channelId: string, period?: TimePeriod) => Promise<void>;
  fetchPostDynamics: (channelId: string, period?: TimePeriod) => Promise<void>;
  fetchTopPosts: (channelId: string, limit?: number) => Promise<void>;
  fetchEngagementMetrics: (channelId: string, period?: TimePeriod) => Promise<void>;
  fetchBestTime: (channelId: string) => Promise<void>;
  setPeriod: (period: TimePeriod) => void;
  clearAnalytics: () => void;
  clearError: (errorType: string) => void;
}

export const useAnalyticsStore = create<AnalyticsState>()(
  subscribeWithSelector((set) => ({
    // Data
    overview: null,
    growthMetrics: null,
    reachMetrics: null,
    postDynamics: null,
    topPosts: [],
    engagementMetrics: null,
    bestTimes: [],

    // Loading states
    isLoadingOverview: false,
    isLoadingGrowth: false,
    isLoadingReach: false,
    isLoadingPostDynamics: false,
    isLoadingTopPosts: false,
    isLoadingEngagement: false,
    isLoadingBestTime: false,

    // Error states
    overviewError: null,
    growthError: null,
    reachError: null,
    postDynamicsError: null,
    topPostsError: null,
    engagementError: null,
    bestTimeError: null,

    // Metadata
    selectedPeriod: '7d',
    lastUpdate: null,

    // Fetch analytics overview
    fetchOverview: async (channelId: string, period: TimePeriod = '7d') => {
      set({ isLoadingOverview: true, overviewError: null });

      try {
        const overview = await apiClient.get<AnalyticsOverview>(
          `/analytics/historical/overview/${channelId}`,
          { params: { period } }
        );

        set({
          overview,
          lastUpdate: Date.now(),
          isLoadingOverview: false
        });

        console.log('✅ Analytics overview loaded');
      } catch (error) {
        console.error('❌ Failed to load analytics overview:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load overview';
        set({
          overviewError: errorMessage,
          isLoadingOverview: false
        });
      }
    },

    // Fetch growth metrics
    fetchGrowthMetrics: async (channelId: string, period: TimePeriod = '7d') => {
      set({ isLoadingGrowth: true, growthError: null });

      try {
        const growthMetrics = await apiClient.get<GrowthMetrics>(
          `/analytics/historical/growth/${channelId}`,
          { params: { period } }
        );

        set({
          growthMetrics,
          lastUpdate: Date.now(),
          isLoadingGrowth: false
        });

        console.log('✅ Growth metrics loaded');
      } catch (error) {
        console.error('❌ Failed to load growth metrics:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load growth';
        set({
          growthError: errorMessage,
          isLoadingGrowth: false
        });
      }
    },

    // Fetch reach metrics
    fetchReachMetrics: async (channelId: string, period: TimePeriod = '7d') => {
      set({ isLoadingReach: true, reachError: null });

      try {
        const reachMetrics = await apiClient.get<ReachMetrics>(
          `/analytics/channels/${channelId}/reach`,
          { params: { period } }
        );

        set({
          reachMetrics,
          lastUpdate: Date.now(),
          isLoadingReach: false
        });

        console.log('✅ Reach metrics loaded');
      } catch (error) {
        console.error('❌ Failed to load reach metrics:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load reach';
        set({
          reachError: errorMessage,
          isLoadingReach: false
        });
      }
    },

    // Fetch post dynamics (views/likes/shares over time)
    fetchPostDynamics: async (channelId: string, period: TimePeriod = '7d') => {
      set({ isLoadingPostDynamics: true, postDynamicsError: null });

      try {
        console.log('📊 Fetching post dynamics for channel:', channelId);

        // Use demo endpoint for demo_channel, real endpoint for actual channels
        const endpoint = channelId === 'demo_channel'
          ? '/demo/analytics/post-dynamics'
          : `/analytics/posts/dynamics/post-dynamics/${channelId}`;

        const postDynamics = await apiClient.get<PostDynamics>(
          endpoint,
          { params: { period } }
        );

        set({
          postDynamics,
          lastUpdate: Date.now(),
          isLoadingPostDynamics: false
        });

        console.log('✅ Post dynamics loaded');
      } catch (error) {
        console.error('❌ Failed to load post dynamics:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load post dynamics';
        set({
          postDynamicsError: errorMessage,
          isLoadingPostDynamics: false
        });
      }
    },

    // Fetch top performing posts
    fetchTopPosts: async (channelId: string, limit: number = 10) => {
      set({ isLoadingTopPosts: true, topPostsError: null });

      try {
        console.log('🏆 Fetching top posts for channel:', channelId);

        // Use demo endpoint for demo_channel, real endpoint for actual channels
        const endpoint = channelId === 'demo_channel'
          ? '/demo/analytics/top-posts'
          : `/analytics/posts/dynamics/top-posts/${channelId}`;

        const topPosts = await apiClient.get<TopPost[]>(endpoint, {
          params: {
            channel_id: channelId,
            limit,
            sort_by: 'views'
          }
        });

        // Handle both direct array response and wrapped response
        const postsData = Array.isArray(topPosts)
          ? topPosts
          : (topPosts as any)?.data?.posts || (topPosts as any)?.posts || [];

        set({
          topPosts: postsData,
          lastUpdate: Date.now(),
          isLoadingTopPosts: false
        });

        console.log('✅ Top posts loaded:', postsData?.length || 0);
      } catch (error) {
        console.error('❌ Failed to load top posts:', error);

        // Fallback to client-side mock data when backend unavailable
        console.info('💡 Using client-side fallback mock data (backend unavailable)');
        const fallbackPosts = generateMockTopPosts(limit);

        set({
          topPosts: fallbackPosts,
          topPostsError: null, // Clear error since we have fallback data
          isLoadingTopPosts: false
        });

        console.log('✅ Using fallback data:', fallbackPosts.length, 'posts');
      }
    },

    // Fetch engagement metrics
    fetchEngagementMetrics: async (channelId: string, period: TimePeriod = '7d') => {
      set({ isLoadingEngagement: true, engagementError: null });

      try {
        console.log('📈 Fetching engagement metrics for channel:', channelId);

        const engagementMetrics = await apiClient.get<EngagementMetrics>(
          `/analytics/channels/${channelId}/engagement`,
          { params: { period } }
        );

        set({
          engagementMetrics,
          lastUpdate: Date.now(),
          isLoadingEngagement: false
        });

        console.log('✅ Engagement metrics loaded');
      } catch (error) {
        console.error('❌ Failed to load engagement metrics:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load metrics';
        set({
          engagementError: errorMessage,
          isLoadingEngagement: false
        });
      }
    },

    // Fetch best time to post recommendations
    fetchBestTime: async (channelId: string) => {
      set({ isLoadingBestTime: true, bestTimeError: null });

      try {
        console.log('⏰ Fetching best time recommendations for channel:', channelId);

        const recommendations = await apiClient.get<BestTimeRecommendation[]>(
          `/analytics/channels/${channelId}/best-time`
        );

        // Store recommendations
        set({
          bestTimes: recommendations,
          lastUpdate: Date.now(),
          isLoadingBestTime: false
        });

        console.log('✅ Best time recommendations loaded:', recommendations.length);
      } catch (error) {
        console.error('❌ Failed to load best time:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load recommendations';
        set({
          bestTimeError: errorMessage,
          isLoadingBestTime: false,
          bestTimes: []
        });
      }
    },

    // Set selected period
    setPeriod: (period: TimePeriod) => {
      set({ selectedPeriod: period });
    },

    // Clear all analytics data
    clearAnalytics: () => {
      set({
        overview: null,
        growthMetrics: null,
        reachMetrics: null,
        postDynamics: null,
        topPosts: [],
        engagementMetrics: null,
        bestTimes: [],
        lastUpdate: null
      });
    },

    // Clear specific error
    clearError: (errorType: string) => {
      set({ [`${errorType}Error`]: null } as Partial<AnalyticsState>);
    }
  }))
);

export default useAnalyticsStore;
