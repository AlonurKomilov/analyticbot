/**
 * Real Analytics Adapter
 * Handles communication with the actual API
 */

import { configUtils } from '@/__mocks__/config/mockConfig';
import { apiClient } from '@/api/client';
import { getMockEngagementMetrics } from '@/__mocks__';
import type { HealthCheckResponse, Logger } from './types';

export class RealAnalyticsAdapter {
  private logger: Logger;

  constructor() {
    this.logger = configUtils.createLogger('RealAnalyticsAdapter');
  }

  async getAnalyticsOverview(channelId: string): Promise<any> {
    try {
      const response: any = await apiClient.get(`/analytics/historical/overview/${channelId}`);
      return response.data;
    } catch (error: any) {
      this.logger.warn('Real analytics failed, using fallback', error);
      return this._generateFallbackOverview(channelId);
    }
  }

  async getPostDynamics(channelId: string, period: string = '24h'): Promise<any> {
    try {
      const response: any = await apiClient.get(
        `/analytics/posts/dynamics/post-dynamics/${channelId}`,
        { params: { period } }
      );
      return response.data;
    } catch (error: any) {
      this.logger.warn('Post dynamics API failed, using fallback', error);
      return this._generateFallbackPostDynamics(period);
    }
  }

  async getTopPosts(
    channelId: string,
    period: string = 'today',
    sortBy: string = 'views'
  ): Promise<any> {
    try {
      const response: any = await apiClient.get(
        `/analytics/posts/dynamics/top-posts/${channelId}`,
        { params: { period, sortBy } }
      );
      return response.data;
    } catch (error: any) {
      this.logger.warn('Top posts API failed, using fallback', error);
      return this._generateFallbackTopPosts(period, sortBy);
    }
  }

  async getEngagementMetrics(channelId: string, period: string = '7d'): Promise<any> {
    try {
      const response: any = await apiClient.get(
        `/analytics/channels/${channelId}/engagement`,
        { params: { period } }
      );
      return response.data;
    } catch (error: any) {
      this.logger.warn('Engagement metrics API failed, using fallback', error);
      return this._generateFallbackEngagement();
    }
  }

  async getBestTime(channelId: string, timeframe: string = 'week'): Promise<any> {
    try {
      const response: any = await apiClient.get(
        `/analytics/predictive/best-times/${channelId}`,
        { params: { timeframe } }
      );
      return response.data;
    } catch (error: any) {
      this.logger.warn('Best time API failed, using fallback', error);
      return this._generateFallbackBestTime(timeframe);
    }
  }

  async getAIRecommendations(channelId: string): Promise<any> {
    try {
      const response: any = await apiClient.get(`/ai/recommendations/${channelId}`);
      return response.data;
    } catch (error: any) {
      this.logger.warn('AI recommendations API failed, using fallback', error);
      return this._generateFallbackRecommendations();
    }
  }

  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response: any = await apiClient.get('/health');
      return {
        status: 'healthy',
        adapter: 'real_analytics',
        timestamp: Date.now(),
        api_status: response.data,
      };
    } catch (error: any) {
      return {
        status: 'degraded',
        adapter: 'real_analytics',
        timestamp: Date.now(),
        error: error.message,
      };
    }
  }

  // Fallback methods
  private _generateFallbackOverview(channelId: string): any {
    return {
      channelId,
      totalViews: Math.floor(Math.random() * 50000) + 10000,
      totalPosts: Math.floor(Math.random() * 500) + 100,
      engagementRate: Math.round((Math.random() * 8 + 2) * 100) / 100,
      growthRate: Math.round((Math.random() * 20 - 5) * 100) / 100,
      lastUpdated: new Date().toISOString(),
      source: 'fallback',
    };
  }

  private _generateFallbackPostDynamics(period: string): any {
    return {
      dynamics: [],
      source: 'fallback',
      period,
      message: 'Backend mock API unavailable',
    };
  }

  private _generateFallbackTopPosts(period: string, sortBy: string): any {
    return {
      posts: [],
      source: 'fallback',
      period,
      sortBy,
      message: 'Backend mock API unavailable',
    };
  }

  private _generateFallbackEngagement(): any {
    return getMockEngagementMetrics();
  }

  private _generateFallbackBestTime(timeframe: string): any {
    return {
      recommendations: [],
      source: 'fallback',
      timeframe,
      message: 'Backend mock API unavailable',
    };
  }

  private _generateFallbackRecommendations(): any {
    return {
      recommendations: [],
      source: 'fallback',
      message: 'Backend mock API unavailable',
    };
  }
}
