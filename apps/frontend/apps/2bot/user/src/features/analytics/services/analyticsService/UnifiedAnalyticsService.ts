/**
 * Unified Analytics Service
 * Consolidates all analytics-related functionality into a single, comprehensive service
 *
 * Features:
 * - Clean adapter pattern for mock/real data switching
 * - Intelligent caching with TTL
 * - Realistic delay simulation
 * - Comprehensive error handling
 * - Consistent API across all methods
 * - Performance monitoring
 */

import { dataSourceManager } from '@/utils/dataSourceManager';
import { configUtils } from '@/__mocks__/config/mockConfig';
import { DEFAULT_DEMO_CHANNEL_ID } from '@/__mocks__/constants';

import { AnalyticsCacheManager } from './CacheManager';
import { RealAnalyticsAdapter } from './RealAnalyticsAdapter';
import { MockAnalyticsAdapter } from './MockAnalyticsAdapter';
import type { Metrics, ServiceMetrics, Logger } from './types';

class UnifiedAnalyticsService {
  private cacheManager: AnalyticsCacheManager;
  private realAdapter: RealAnalyticsAdapter;
  private mockAdapter: MockAnalyticsAdapter;
  private logger: Logger;
  private metrics: Metrics;

  constructor() {
    this.cacheManager = new AnalyticsCacheManager();
    this.realAdapter = new RealAnalyticsAdapter();
    this.mockAdapter = new MockAnalyticsAdapter();
    this.logger = configUtils.createLogger('UnifiedAnalyticsService');

    this.metrics = {
      requests: 0,
      cacheHits: 0,
      errors: 0,
      totalResponseTime: 0,
    };
  }

  private _getCurrentAdapter(): RealAnalyticsAdapter | MockAnalyticsAdapter {
    const source = dataSourceManager.getDataSource();
    return source === 'api' ? this.realAdapter : this.mockAdapter;
  }

  private async _executeWithCache(
    method: string,
    params: any[],
    ttl: number | null = null
  ): Promise<any> {
    const startTime = performance.now();
    this.metrics.requests++;

    try {
      // Check cache first
      const cacheKey = this.cacheManager.generateKey(method, params);
      const cached = this.cacheManager.get(cacheKey);

      if (cached) {
        this.metrics.cacheHits++;
        this.logger.debug(`Cache hit for ${method}`);
        return cached;
      }

      // Execute method
      const adapter = this._getCurrentAdapter();
      const result = await (adapter as any)[method](...params);

      // Cache result
      const cacheTTL = ttl || this._getMethodTTL(method);
      this.cacheManager.set(cacheKey, result, cacheTTL);

      // Track performance
      const responseTime = performance.now() - startTime;
      this.metrics.totalResponseTime += responseTime;

      this.logger.debug(`${method} completed in ${responseTime.toFixed(2)}ms`);
      return result;
    } catch (error) {
      this.metrics.errors++;
      this.logger.error(`Error in ${method}:`, error);
      throw error;
    }
  }

  private _getMethodTTL(method: string): number {
    const ttls: Record<string, number> = {
      getAnalyticsOverview: 2 * 60 * 1000,
      getPostDynamics: 5 * 60 * 1000,
      getTopPosts: 10 * 60 * 1000,
      getEngagementMetrics: 5 * 60 * 1000,
      getBestTime: 30 * 60 * 1000,
      getAIRecommendations: 60 * 60 * 1000,
    };
    return ttls[method] || this.cacheManager.getDefaultTTL();
  }

  // Public API Methods
  async getAnalyticsOverview(channelId: string = DEFAULT_DEMO_CHANNEL_ID): Promise<any> {
    return this._executeWithCache('getAnalyticsOverview', [channelId]);
  }

  async getPostDynamics(
    channelId: string = DEFAULT_DEMO_CHANNEL_ID,
    period: string = '24h'
  ): Promise<any> {
    return this._executeWithCache('getPostDynamics', [channelId, period]);
  }

  async getTopPosts(
    channelId: string = DEFAULT_DEMO_CHANNEL_ID,
    period: string = 'today',
    sortBy: string = 'views'
  ): Promise<any> {
    return this._executeWithCache('getTopPosts', [channelId, period, sortBy]);
  }

  async getEngagementMetrics(
    channelId: string = DEFAULT_DEMO_CHANNEL_ID,
    period: string = '7d'
  ): Promise<any> {
    return this._executeWithCache('getEngagementMetrics', [channelId, period]);
  }

  async getBestTime(
    channelId: string = DEFAULT_DEMO_CHANNEL_ID,
    timeframe: string = 'week'
  ): Promise<any> {
    return this._executeWithCache('getBestTime', [channelId, timeframe]);
  }

  async getAIRecommendations(channelId: string = DEFAULT_DEMO_CHANNEL_ID): Promise<any> {
    return this._executeWithCache('getAIRecommendations', [channelId]);
  }

  async healthCheck(): Promise<any> {
    const adapter = this._getCurrentAdapter();
    const health = await adapter.healthCheck();

    return {
      ...health,
      service: 'unified_analytics',
      cache: this.cacheManager.getStats(),
      performance: {
        totalRequests: this.metrics.requests,
        cacheHitRate:
          this.metrics.requests > 0
            ? ((this.metrics.cacheHits / this.metrics.requests) * 100).toFixed(2) + '%'
            : '0%',
        avgResponseTime:
          this.metrics.requests > 0
            ? (this.metrics.totalResponseTime / this.metrics.requests).toFixed(2) + 'ms'
            : '0ms',
        errorRate:
          this.metrics.requests > 0
            ? ((this.metrics.errors / this.metrics.requests) * 100).toFixed(2) + '%'
            : '0%',
      },
    };
  }

  async refreshCache(method: string | null = null, params: any[] | null = null): Promise<void | any> {
    if (method && params) {
      const cacheKey = this.cacheManager.generateKey(method, params);
      this.cacheManager.clear(cacheKey);
      return this._executeWithCache(method, params);
    } else {
      this.cacheManager.clear();
      this.logger.info('All cache cleared');
    }
  }

  async switchDataSource(source: 'api' | 'mock'): Promise<void> {
    dataSourceManager.setDataSource(source);
    this.cacheManager.clear();
    this.logger.info(`Switched to ${source} data source`);
  }

  getMetrics(): ServiceMetrics {
    return {
      requests: this.metrics,
      cache: this.cacheManager.getStats(),
      currentAdapter: dataSourceManager.getDataSource(),
      adapters: {
        real: 'RealAnalyticsAdapter',
        mock: 'MockAnalyticsAdapter',
      },
    };
  }
}

// Create and export singleton instance
export const analyticsService = new UnifiedAnalyticsService();

// Export class for testing
export { UnifiedAnalyticsService };

export default analyticsService;
