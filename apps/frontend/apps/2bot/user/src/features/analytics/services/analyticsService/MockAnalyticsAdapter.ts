/**
 * Mock Analytics Adapter
 * Provides mock data for demo/development mode
 */

import { MOCK_CONFIG } from '@/__mocks__/config/mockConfig';
import { DEFAULT_DEMO_CHANNEL_ID } from '@/__mocks__/constants';
import { apiClient } from '@/api/client';
import { getMockEngagementMetrics } from '@/__mocks__';
import type { HealthCheckResponse } from './types';

export class MockAnalyticsAdapter {
  private apiClient: typeof apiClient;

  constructor() {
    this.apiClient = apiClient;
  }

  async getAnalyticsOverview(channelId: string = DEFAULT_DEMO_CHANNEL_ID): Promise<any> {
    await this._simulateDelay();

    const overview = {
      channel_id: channelId,
      subscribers: 12500,
      views: 450000,
      posts: 156,
      engagement_rate: 8.5,
      growth_rate: 12.3,
      avg_views_per_post: 2885,
      period: '30d',
      source: 'mock',
    };

    return {
      ...overview,
      source: 'mock',
    };
  }

  async getPostDynamics(channelId: string, hours: number | string = 24): Promise<any> {
    await this._simulateDelay();

    try {
      const response: any = await this.apiClient.get(
        '/unified-analytics/demo/post-dynamics',
        { params: { channel_id: channelId, hours } }
      );
      return response.data;
    } catch (error: any) {
      console.warn('Backend mock API unavailable, using fallback data:', error.message);
      return {
        success: true,
        data: {
          channel_id: channelId,
          time_range: `${hours} hours`,
          dynamics: [],
          source: 'fallback_data',
          generated_at: new Date().toISOString(),
        },
      };
    }
  }

  async getTopPosts(
    channelId: string,
    period: string = 'today',
    sortBy: string = 'views'
  ): Promise<any> {
    await this._simulateDelay();

    try {
      const response: any = await this.apiClient.get('/unified-analytics/demo/top-posts', {
        params: { channel_id: channelId, period, sort_by: sortBy },
      });
      return {
        channelId,
        period,
        sortBy,
        posts: response.data.posts || [],
        source: 'backend_mock',
        generatedAt: new Date().toISOString(),
      };
    } catch (error: any) {
      console.warn('Backend mock API unavailable, using fallback data:', error.message);
      return {
        channelId,
        period,
        sortBy,
        posts: [],
        source: 'fallback',
        generatedAt: new Date().toISOString(),
      };
    }
  }

  async getEngagementMetrics(channelId: string, period: string = '7d'): Promise<any> {
    await this._simulateDelay();

    return {
      channelId,
      period,
      ...getMockEngagementMetrics(),
      source: 'mock',
      generatedAt: new Date().toISOString(),
    };
  }

  async getBestTime(channelId: string, timeframe: string = 'week'): Promise<any> {
    await this._simulateDelay();

    try {
      const response: any = await this.apiClient.get('/unified-analytics/demo/best-time', {
        params: { channel_id: channelId, timeframe },
      });
      return {
        channelId,
        timeframe,
        ...response.data,
        source: 'backend_mock',
        generatedAt: new Date().toISOString(),
      };
    } catch (error: any) {
      console.warn('Backend mock API unavailable, using fallback data:', error.message);
      return {
        channelId,
        timeframe,
        recommendations: [],
        source: 'fallback',
        generatedAt: new Date().toISOString(),
        message: 'Backend mock API unavailable',
      };
    }
  }

  async getAIRecommendations(channelId: string): Promise<any> {
    await this._simulateDelay();

    try {
      const response: any = await this.apiClient.get(
        '/unified-analytics/demo/ai-recommendations',
        { params: { channel_id: channelId } }
      );
      return {
        channelId,
        ...response.data,
        source: 'backend_mock',
        generatedAt: new Date().toISOString(),
      };
    } catch (error: any) {
      console.warn('Backend mock API unavailable, using fallback data:', error.message);
      return {
        channelId,
        recommendations: [],
        source: 'fallback',
        generatedAt: new Date().toISOString(),
        message: 'Backend mock API unavailable',
      };
    }
  }

  async healthCheck(): Promise<HealthCheckResponse> {
    await this._simulateDelay(100);

    return {
      status: 'healthy',
      adapter: 'mock_analytics',
      timestamp: Date.now(),
      features: [
        'analytics_overview',
        'post_dynamics',
        'top_posts',
        'engagement_metrics',
        'best_time',
        'ai_recommendations',
      ],
      performance: {
        avgResponseTime: '150ms',
        cacheHitRate: '85%',
      },
    };
  }

  private async _simulateDelay(baseMs: number | null = null): Promise<void> {
    const delay = baseMs || MOCK_CONFIG.MOCK_DELAY || 200;
    const jitter = Math.random() * delay * 0.5;
    await new Promise((resolve) => setTimeout(resolve, delay + jitter));
  }
}
