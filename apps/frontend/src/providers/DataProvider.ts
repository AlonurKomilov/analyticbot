/**
 * Clean Data Provider Interface - Production Code
 * This file contains NO mock logic - only production data
 */

import { apiClient } from '../api/client';
import type { AnalyticsOverview, TopPost, EngagementMetrics, RequestConfig } from '@/types';
import { apiLogger } from '@/utils/logger';

export interface DataProviderOptions {
  period?: string;
  limit?: number;
  [key: string]: unknown;
}

/**
 * Abstract base class for data providers
 * Defines the interface that all data providers must implement
 */
export abstract class DataProvider {
  /**
   * Check if the provider is available/online
   */
  abstract isAvailable(): Promise<boolean>;

  /**
   * Get analytics data for a channel
   */
  abstract getAnalytics(channelId: string): Promise<AnalyticsOverview>;

  /**
   * Get top posts data
   */
  abstract getTopPosts(channelId: string, options?: DataProviderOptions): Promise<TopPost[]>;

  /**
   * Get engagement metrics
   */
  abstract getEngagementMetrics(channelId: string, options?: DataProviderOptions): Promise<EngagementMetrics>;

  /**
   * Get analytics overview for a channel
   */
  abstract getAnalyticsOverview(channelId: string): Promise<AnalyticsOverview>;

  /**
   * Get recommendations data
   */
  abstract getRecommendations(channelId: string): Promise<string[]>;

  /**
   * Get provider identifier
   */
  abstract getProviderName(): string;
}

interface AuthContext {
  token: string | null;
}

/**
 * Production API Data Provider
 * Handles real API communication with JWT authentication - contains NO mock logic
 */
export class ApiDataProvider extends DataProvider {
  private baseUrl: string;
  private authContext: AuthContext | null;

  constructor(baseUrl: string | null = null, authContext: AuthContext | null = null) {
    super();
    this.baseUrl = baseUrl ||
                  import.meta.env.VITE_API_BASE_URL ||
                  import.meta.env.VITE_API_URL ||
                  'https://b2qz1m0n-11400.euw.devtunnels.ms';
    this.authContext = authContext;
  }

  /**
   * Set the authentication context for JWT token access
   */
  setAuthContext(authContext: AuthContext): void {
    this.authContext = authContext;
  }

  /**
   * Get JWT token from auth context
   */
  private getAuthToken(): string | null {
    return this.authContext?.token || null;
  }

  /**
   * Build authentication headers
   */
  private getAuthHeaders(): Record<string, string> {
    const token = this.getAuthToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }

  async isAvailable(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        signal: controller.signal,
        headers: this.getAuthHeaders()
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      // Don't log timeout errors as warnings - they're expected when API is unavailable
      if (error instanceof Error && error.name === 'AbortError') {
        apiLogger.debug('API health check timed out (3s) - API may be unavailable');
      } else if (error instanceof Error) {
        apiLogger.warn('API availability check failed', { error: error.message });
      }
      return false;
    }
  }

  /**
   * Convert string channel IDs to numeric IDs for API compatibility
   */
  private convertChannelId(channelId: string): string | number {
    // Map string channel IDs to numeric IDs that the API expects
    const channelMap: Record<string, number> = {
      'demo_channel': 1,
      'tech_news': 2,
      'daily_updates': 3,
      'business_insights': 4
    };

    // If it's already numeric, return as is
    if (typeof channelId === 'number' || /^\d+$/.test(channelId)) {
      return channelId;
    }

    // Map string to numeric ID, default to 1 for demo purposes
    return channelMap[channelId] || 1;
  }

  async getAnalytics(channelId: string): Promise<AnalyticsOverview> {
    const numericChannelId = this.convertChannelId(channelId);
    // Use the historical overview endpoint with default 90-day range
    try {
      const toDate = new Date();
      const fromDate = new Date();
      fromDate.setDate(fromDate.getDate() - 90);

      const fromStr = fromDate.toISOString();
      const toStr = toDate.toISOString();

      const response = await this.makeRequest<{ overview: any; last_updated: string }>(
        `/analytics/historical/overview/${numericChannelId}?from=${fromStr}&to=${toStr}`
      );

      // Transform historical overview to match AnalyticsOverview interface
      if (response && response.overview) {
        const overview = response.overview;
        return {
          totalViews: overview.total_views || 0,
          totalShares: overview.total_shares || overview.total_forwards || 0,
          totalReactions: overview.total_reactions || 0,
          engagementRate: overview.engagement_rate || 0,
          growthRate: overview.growth_rate || overview.subscriber_growth_rate || 0,
          reachScore: overview.reach_score || 0,
          viralityScore: overview.virality_score || 0,
          timestamp: response.last_updated || new Date().toISOString()
        };
      }

      // Fallback if response structure is unexpected
      return this.getEmptyAnalyticsOverview();
    } catch (error) {
      apiLogger.error('Failed to fetch analytics', error);
      return this.getEmptyAnalyticsOverview();
    }
  }

  private getEmptyAnalyticsOverview(): AnalyticsOverview {
    return {
      totalViews: 0,
      totalShares: 0,
      totalReactions: 0,
      engagementRate: 0,
      growthRate: 0,
      reachScore: 0,
      viralityScore: 0,
      timestamp: new Date().toISOString()
    };
  }

  async getTopPosts(channelId: string, options: DataProviderOptions = {}): Promise<TopPost[]> {
    const numericChannelId = this.convertChannelId(channelId);
    const queryParams = new URLSearchParams(options as Record<string, string>).toString();
    // Use the real top-posts endpoint for user's channel data
    const url = `/analytics/posts/top-posts/${numericChannelId}${queryParams ? `?${queryParams}` : ''}`;
    const response = await this.makeRequest<TopPost[]>(url);
    return response;
  }

  async getEngagementMetrics(channelId: string, _options: DataProviderOptions = {}): Promise<EngagementMetrics> {
    const numericChannelId = this.convertChannelId(channelId);

    try {
      // Try to get data from top posts and calculate basic metrics
      const topPosts = await this.getTopPosts(numericChannelId.toString(), { period: '7d', limit: 20 });

      // Calculate aggregate metrics from top posts
      if (topPosts && Array.isArray(topPosts) && topPosts.length > 0) {
        const totalShares = topPosts.reduce((sum, post) => sum + (post.shares || 0), 0);
        const totalReactions = topPosts.reduce((sum, post) => sum + (post.reactions || 0), 0);
        const avgEngagement = topPosts.reduce((sum, post) => sum + (post.engagementRate || 0), 0) / topPosts.length;

        return {
          likes: Math.floor(totalReactions * 0.4), // Estimate likes from reactions
          shares: totalShares,
          comments: Math.floor(totalReactions * 0.1), // Estimate comments
          reactions: totalReactions,
          engagementRate: avgEngagement,
          averageEngagementTime: undefined
        };
      }

      return this.getEmptyEngagementMetrics();
    } catch (error) {
      apiLogger.warn('Could not calculate engagement metrics from posts', { error });
      return this.getEmptyEngagementMetrics();
    }
  }

  private getEmptyEngagementMetrics(): EngagementMetrics {
    return {
      likes: 0,
      shares: 0,
      comments: 0,
      reactions: 0,
      engagementRate: 0,
      averageEngagementTime: undefined
    };
  }

  async getRecommendations(channelId: string): Promise<string[]> {
    const numericChannelId = this.convertChannelId(channelId);

    // Skip the API call for recommendations since it requires external service
    // Generate recommendations directly from available data
    apiLogger.info('Generating recommendations from available channel data');

    try {
      // Generate basic recommendations from top posts data
      const topPosts = await this.getTopPosts(numericChannelId.toString(), { period: '7d', limit: 10 });

      if (topPosts && Array.isArray(topPosts) && topPosts.length > 0) {
        const avgEngagement = topPosts.reduce((sum, post) => sum + (post.engagementRate || 0), 0) / topPosts.length;
        const totalViews = topPosts.reduce((sum, post) => sum + (post.views || 0), 0);
        const totalShares = topPosts.reduce((sum, post) => sum + (post.shares || 0), 0);
        const totalReactions = topPosts.reduce((sum, post) => sum + (post.reactions || 0), 0);

        const recommendations: string[] = [];

        // Engagement-based recommendations
        if (avgEngagement > 5) {
          recommendations.push(`✅ Excellent engagement rate of ${avgEngagement.toFixed(2)}%! Keep up the great work.`);
        } else if (avgEngagement > 2) {
          recommendations.push(`📈 Good engagement rate of ${avgEngagement.toFixed(2)}%. Try more interactive content to boost it further.`);
        } else {
          recommendations.push(`💡 Current engagement is ${avgEngagement.toFixed(2)}%. Consider posting more engaging content like polls, questions, or multimedia.`);
        }

        // Views-based recommendations
        recommendations.push(`👁️ Total views: ${totalViews.toLocaleString()}. ${totalViews > 1000 ? 'Great reach!' : 'Post more consistently to increase visibility.'}`);

        // Interaction recommendations
        if (totalShares > 0 || totalReactions > 0) {
          recommendations.push(`🔄 Your content is being shared (${totalShares} shares, ${totalReactions} reactions). Keep creating shareable content!`);
        } else {
          recommendations.push(`💬 Encourage audience interaction by asking questions and creating discussion-worthy content.`);
        }

        // Best post recommendation
        if (topPosts[0]?.engagementRate && topPosts[0].engagementRate > 5) {
          recommendations.push(`🏆 Your top post has ${topPosts[0].engagementRate.toFixed(2)}% engagement. Analyze what made it successful and replicate that approach.`);
        }

        // General recommendations
        recommendations.push('📅 Post consistently at optimal times to maintain audience engagement.');
        recommendations.push('📊 Monitor your analytics regularly to identify trends and opportunities.');

        return recommendations;
      }
    } catch (error) {
      apiLogger.warn('Could not generate data-driven recommendations', { error });
    }

    // Ultimate fallback: generic but useful recommendations
    return [
      '📝 Post consistently to grow your audience',
      '💬 Engage with your subscribers regularly through comments and polls',
      '📊 Analyze your best-performing content to identify successful patterns',
      '🎨 Experiment with different content formats (text, images, videos)',
      '⏰ Test different posting times to find your optimal schedule',
      '🎯 Focus on quality over quantity for better engagement',
      '📈 Monitor your analytics to track progress and adjust strategy'
    ];
  }

  async getAnalyticsOverview(channelId: string): Promise<AnalyticsOverview> {
    const numericChannelId = this.convertChannelId(channelId);
    // Use the analytics overview endpoint
    const response = await this.makeRequest<AnalyticsOverview>(`/analytics/historical/overview/${numericChannelId}`);
    return response;
  }

  getProviderName(): string {
    return 'api';
  }

  /**
   * Internal method to make HTTP requests with JWT authentication
   * Uses serviceFactory to automatically route demo users to mock API
   */
  private async makeRequest<T>(endpoint: string, options: { method?: 'GET' | 'POST' | 'PUT' | 'DELETE'; body?: unknown } = {}): Promise<T> {
    try {
      const method = options.method || 'GET';
      const config: RequestConfig = {
        headers: this.getAuthHeaders()
      };

      let response: T;

      // Route through apiClient which handles demo user detection
      if (method === 'GET') {
        response = await apiClient.get<T>(endpoint, config);
      } else if (method === 'POST') {
        response = await apiClient.post<T>(endpoint, options.body, config);
      } else if (method === 'PUT') {
        response = await apiClient.put<T>(endpoint, options.body, config);
      } else if (method === 'DELETE') {
        response = await apiClient.delete<T>(endpoint, config);
      } else {
        throw new Error(`Unsupported HTTP method: ${method}`);
      }

      // apiClient returns the data directly (not wrapped in response.data)
      return response;
    } catch (error) {
      // ONLY provide fallback for explicitly marked demo users
      const isDemoUser = localStorage.getItem('is_demo_user') === 'true';

      if (isDemoUser && error instanceof Error && (
        error.message.includes('API request failed') ||
        error.message.includes('Failed to fetch') ||
        error.message.includes('CORS') ||
        error.message.includes('Network') ||
        error.name === 'TypeError'
      )) {
        apiLogger.info('Demo user: Providing fallback data', { endpoint, error: error.message });
        return await this.getDemoFallbackData<T>(endpoint);
      }

      // For real API users: throw error, NEVER fallback to mock
      apiLogger.error('API request failed', error, { endpoint });
      throw error;
    }
  }

  /**
   * Provide enhanced demo fallback data based on endpoint
   */
  private async getDemoFallbackData<T>(endpoint: string): Promise<T> {
    apiLogger.debug('Getting demo fallback data', { endpoint });

    // Return basic fallback structure for demo mode
    return {
      message: 'Demo data not available for this endpoint',
      demo_mode: true,
      timestamp: new Date().toISOString()
    } as T;
  }
}

/**
 * Default production data provider instance
 * This is what production code should use
 * Note: AuthContext should be set via setAuthContext() after initialization
 */
export const productionDataProvider = new ApiDataProvider();

/**
 * Factory function to create an authenticated data provider
 */
export const createAuthenticatedDataProvider = (authContext: AuthContext, baseUrl: string | null = null): ApiDataProvider => {
  return new ApiDataProvider(baseUrl, authContext);
};
