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
import { storeLogger } from '@/utils/logger';

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
  topPostsSummary: {
    totalViews: number;
    totalForwards: number;
    totalReactions: number;
    totalComments: number;      // Discussion group comments
    totalReplies?: number;      // Threaded replies (optional)
    averageEngagementRate: number;
    postCount: number;
  } | null;
  engagementMetrics: EngagementMetrics | null;
  bestTimes: BestTimeRecommendation[];
  bestDayHourCombinations: any[];  // Advanced: day-hour combinations
  contentTypeRecommendations: any[];  // Advanced: content-type specific recommendations

  // Loading states
  isLoadingOverview: boolean;
  isLoadingGrowth: boolean;
  isLoadingReach: boolean;
  isLoadingPostDynamics: boolean;
  isLoadingTopPosts: boolean;
  isLoadingTopPostsSummary: boolean;
  isLoadingEngagement: boolean;
  isLoadingBestTime: boolean;

  // Error states
  overviewError: string | null;
  growthError: string | null;
  reachError: string | null;
  postDynamicsError: string | null;
  topPostsError: string | null;
  topPostsSummaryError: string | null;
  engagementError: string | null;
  bestTimeError: string | null;

  // Metadata
  selectedPeriod: TimePeriod;
  lastUpdate: number | null;

  // Actions
  fetchOverview: (channelId: string, period?: TimePeriod) => Promise<void>;
  fetchGrowthMetrics: (channelId: string, period?: TimePeriod) => Promise<void>;
  fetchReachMetrics: (channelId: string, period?: TimePeriod) => Promise<void>;
  fetchPostDynamics: (channelId: string, period?: TimePeriod, customDateRange?: { start_date: string; end_date: string }, customTimeRange?: { start_time: string; end_time: string }, silent?: boolean) => Promise<void>;
  fetchTopPosts: (channelId: string, limit?: number, period?: string, sortBy?: string, silent?: boolean) => Promise<void>;
  fetchTopPostsSummary: (channelId: string, period?: string, silent?: boolean) => Promise<void>;
  fetchEngagementMetrics: (channelId: string, period?: TimePeriod) => Promise<void>;
  fetchBestTime: (channelId: string, days?: number | null, silent?: boolean) => Promise<void>;
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
    topPostsSummary: null,
    engagementMetrics: null,
    bestTimes: [],
    bestDayHourCombinations: [],
    contentTypeRecommendations: [],

    // Loading states
    isLoadingOverview: false,
    isLoadingGrowth: false,
    isLoadingReach: false,
    isLoadingPostDynamics: false,
    isLoadingTopPosts: false,
    isLoadingTopPostsSummary: false,
    isLoadingEngagement: false,
    isLoadingBestTime: false,

    // Error states
    overviewError: null,
    growthError: null,
    reachError: null,
    postDynamicsError: null,
    topPostsError: null,
    topPostsSummaryError: null,
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

        storeLogger.debug('Analytics overview loaded', { channelId });
      } catch (error) {
        storeLogger.error('Failed to load analytics overview', { error, channelId });
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

        storeLogger.debug('Growth metrics loaded', { channelId, period });
      } catch (error) {
        storeLogger.error('Failed to load growth metrics', { error, channelId, period });
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

        storeLogger.debug('Reach metrics loaded', { channelId, period });
      } catch (error) {
        storeLogger.error('Failed to load reach metrics', { error, channelId, period });
        const errorMessage = error instanceof Error ? error.message : 'Failed to load reach';
        set({
          reachError: errorMessage,
          isLoadingReach: false
        });
      }
    },

    // Fetch post dynamics (views/reactions/shares over time)
    fetchPostDynamics: async (channelId: string, period: TimePeriod = '7d', customDateRange?: { start_date: string; end_date: string }, customTimeRange?: { start_time: string; end_time: string }, silent: boolean = false) => {
      // Only show loading spinner on initial load, not on auto-refresh
      if (!silent) {
        set({ isLoadingPostDynamics: true, postDynamicsError: null });
      }

      try {
        storeLogger.debug('Fetching post dynamics', { channelId, period, customDateRange, customTimeRange });

        // Use demo endpoint for demo_channel, real endpoint for actual channels
        const endpoint = channelId === 'demo_channel'
          ? '/demo/analytics/post-dynamics'
          : `/analytics/posts/dynamics/post-dynamics/${channelId}`;

        storeLogger.debug('Post dynamics API endpoint', { endpoint });

        // Build params with optional date/time range for drill-down
        const params: any = { period };
        if (customTimeRange) {
          // Minute-level drill-down
          params.start_time = customTimeRange.start_time;
          params.end_time = customTimeRange.end_time;
        } else if (customDateRange) {
          // Hour-level drill-down
          params.start_date = customDateRange.start_date;
          params.end_date = customDateRange.end_date;
        }

        storeLogger.debug('Post dynamics API params', { params });

        const postDynamics = await apiClient.get<PostDynamics>(
          endpoint,
          { params }
        );

        storeLogger.debug('Post dynamics response received', {
          isArray: Array.isArray(postDynamics),
          length: Array.isArray(postDynamics) ? postDynamics.length : 'N/A'
        });

        set({
          postDynamics,
          lastUpdate: Date.now(),
          isLoadingPostDynamics: false
        });

        storeLogger.debug('Post dynamics saved to store');
      } catch (error) {
        storeLogger.error('Failed to load post dynamics', { error, channelId, period });
        const errorMessage = error instanceof Error ? error.message : 'Failed to load post dynamics';
        set({
          postDynamicsError: errorMessage,
          isLoadingPostDynamics: false
        });
      }
    },

    // Fetch top performing posts
    fetchTopPosts: async (channelId: string, limit: number = 10, period: string = '30d', sortBy: string = 'views', silent: boolean = false) => {
      // Only show loading spinner on initial load, not on auto-refresh
      if (!silent) {
        set({ isLoadingTopPosts: true, topPostsError: null });
      }

      try {
        storeLogger.debug('Fetching top posts', { channelId, period, sortBy, limit });

        // Use demo endpoint for demo_channel, real endpoint for actual channels
        const endpoint = channelId === 'demo_channel'
          ? '/demo/analytics/top-posts'
          : `/analytics/posts/top-posts/${channelId}`;  // Updated path to new router

        const response = await apiClient.get<any[]>(endpoint, {
          params: {
            limit,
            sort_by: sortBy,
            period: period
          }
        });

        // Handle both direct array response and wrapped response
        const rawPosts = Array.isArray(response)
          ? response
          : (response as any)?.data?.posts || (response as any)?.posts || [];

        // Transform backend response to frontend format
        // Backend: { msg_id, date, text, views, forwards, comments_count, replies_count, reactions_count, engagement_rate }
        // Frontend: { id, content, views, shares, reactions, comments, replies, engagementRate, publishedTime }
        const transformedPosts = rawPosts.map((post: any) => ({
          id: post.msg_id || post.id,
          content: post.text || post.content || '',
          views: post.views || 0,
          shares: post.forwards || post.shares || 0,
          reactions: post.reactions_count || post.reactions || 0,
          comments: post.comments_count || post.comments || 0,  // Discussion group comments
          replies: post.replies_count || 0,                      // Direct threaded replies
          engagementRate: post.engagement_rate || 0,
          publishedTime: post.date || post.publishedTime || post.created_at,
          // Keep original fields for compatibility
          ...post
        }));

        set({
          topPosts: transformedPosts,
          lastUpdate: Date.now(),
          isLoadingTopPosts: false
        });

        storeLogger.debug('Top posts loaded', { count: transformedPosts?.length || 0 });
      } catch (error) {
        storeLogger.error('Failed to load top posts', { error, channelId, period });

        // Set error state so UI can show it
        set({
          topPostsError: error instanceof Error ? error.message : 'Failed to load top posts',
          isLoadingTopPosts: false,
          // Keep existing posts instead of clearing them
          // topPosts: [] // Don't clear - let UI decide whether to show stale data or error
        });

        storeLogger.warn('Error occurred, keeping existing posts (if any)');
      }
    },

    // Fetch top posts summary statistics (aggregates ALL posts in period)
    fetchTopPostsSummary: async (channelId: string, period: string = '30d', silent: boolean = false) => {
      // Only show loading spinner on initial load, not on auto-refresh
      if (!silent) {
        set({ isLoadingTopPostsSummary: true, topPostsSummaryError: null });
      }

      try {
        storeLogger.debug('Fetching top posts summary', { channelId, period });

        // Use demo endpoint for demo_channel, real endpoint for actual channels
        const endpoint = channelId === 'demo_channel'
          ? '/demo/analytics/top-posts-summary'
          : `/analytics/posts/top-posts/${channelId}/summary`;  // Corrected path

        const response = await apiClient.get<any>(endpoint, {
          params: {
            period: period
          }
        });

        // Handle response
        const summary = response?.data || response || {};

        // Transform to frontend format
        const transformedSummary = {
          totalViews: summary.total_views || 0,
          totalForwards: summary.total_forwards || 0,
          totalReactions: summary.total_reactions || 0,
          totalComments: summary.total_replies || summary.total_comments || 0,  // Backend uses total_replies for comments
          totalReplies: summary.total_threaded_replies || 0,  // Separate field for threaded replies
          averageEngagementRate: summary.average_engagement_rate || 0,
          postCount: summary.post_count || 0
        };

        set({
          topPostsSummary: transformedSummary,
          lastUpdate: Date.now(),
          isLoadingTopPostsSummary: false
        });

        storeLogger.debug('Top posts summary loaded', { postCount: transformedSummary.postCount });
      } catch (error) {
        storeLogger.error('Failed to load top posts summary', { error, channelId, period });

        set({
          topPostsSummaryError: error instanceof Error ? error.message : 'Failed to load summary',
          isLoadingTopPostsSummary: false
        });

        storeLogger.warn('Error occurred loading summary');
      }
    },

    // Fetch engagement metrics
    fetchEngagementMetrics: async (channelId: string, period: TimePeriod = '7d') => {
      set({ isLoadingEngagement: true, engagementError: null });

      try {
        storeLogger.debug('Fetching engagement metrics', { channelId, period });

        const engagementMetrics = await apiClient.get<EngagementMetrics>(
          `/analytics/channels/${channelId}/engagement`,
          { params: { period } }
        );

        set({
          engagementMetrics,
          lastUpdate: Date.now(),
          isLoadingEngagement: false
        });

        storeLogger.debug('Engagement metrics loaded');
      } catch (error) {
        storeLogger.error('Failed to load engagement metrics', { error, channelId, period });
        const errorMessage = error instanceof Error ? error.message : 'Failed to load metrics';
        set({
          engagementError: errorMessage,
          isLoadingEngagement: false
        });
      }
    },

    // Fetch best time to post recommendations
    fetchBestTime: async (channelId: string, days?: number | null, silent: boolean = false) => {
      // Only show loading spinner on initial load, not on auto-refresh
      if (!silent) {
        set({ isLoadingBestTime: true, bestTimeError: null });
      }

      try {
        storeLogger.debug('Fetching best time recommendations', {
          channelId,
          days: days === null ? 'ALL TIME' : (days || 90)
        });

        // Use correct endpoint that matches backend
        // If days is null, omit the parameter to get all-time data
        const url = days !== null && days !== undefined
          ? `/analytics/predictive/best-times/${channelId}?days=${days}`
          : `/analytics/predictive/best-times/${channelId}`;  // No days param = all time

        const response = await apiClient.get<any>(url);

        // Extract all recommendation data from response.data (API wraps in data object)
        const recommendations = response.data?.best_times || [];
        const bestDayHourCombinations = response.data?.best_day_hour_combinations || [];
        const contentTypeRecommendations = response.data?.content_type_recommendations || [];

        storeLogger.debug('Best time API response received', {
          recommendationsCount: recommendations.length,
          dayHourCombosCount: bestDayHourCombinations.length,
          contentTypeRecsCount: contentTypeRecommendations.length
        });

        // Store all recommendations data
        set({
          bestTimes: recommendations,
          bestDayHourCombinations,
          contentTypeRecommendations,
          lastUpdate: Date.now(),
          isLoadingBestTime: false
        });

        storeLogger.debug('Best time recommendations loaded', { count: recommendations.length });
      } catch (error) {
        storeLogger.error('Failed to load best time recommendations', { error, channelId, days });
        const errorMessage = error instanceof Error ? error.message : 'Failed to load recommendations';
        set({
          bestTimeError: errorMessage,
          isLoadingBestTime: false,
          bestTimes: [],
          bestDayHourCombinations: [],
          contentTypeRecommendations: []
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
        topPostsSummary: null,
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
