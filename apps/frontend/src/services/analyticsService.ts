/**
 * Unified Analytics Service
 * Consolidates all analytics-related functionality into a single, comprehensive service
 * Replaces: analyticsAPIService, demoAnalyticsService, mockService (analytics portions), dataService
 *
 * Features:
 * - Clean adapter pattern for mock/real data switching
 * - Intelligent caching with TTL
 * - Realistic delay simulation
 * - Comprehensive error handling
 * - Consistent API across all methods
 * - Performance monitoring
 */

import { dataSourceManager } from '../utils/dataSourceManager';

// Import centralized mock config from __mocks__
import { MOCK_CONFIG, configUtils } from '../__mocks__/config/mockConfig';
import { DEFAULT_DEMO_CHANNEL_ID } from '../__mocks__/constants';

// Import unified API client
import { apiClient } from '../api/client';

// Import mock data generators (for fallback compatibility)
import {
    getMockEngagementMetrics
} from '../__mocks__/index';

// =====================================
// Types and Interfaces
// =====================================

interface CacheEntry {
    data: any;
    timestamp: number;
    ttl: number;
}

interface CacheStats {
    size: number;
    maxSize: number;
    keys: string[];
    hitRatio: number;
}

interface HealthCheckResponse {
    status: 'healthy' | 'degraded';
    adapter: string;
    timestamp: number;
    api_status?: any;
    error?: string;
    features?: string[];
    performance?: {
        avgResponseTime: string;
        cacheHitRate: string;
    };
}

interface Metrics {
    requests: number;
    cacheHits: number;
    errors: number;
    totalResponseTime: number;
}

interface ServiceMetrics {
    requests: Metrics;
    cache: CacheStats;
    currentAdapter: 'api' | 'mock';
    adapters: {
        real: string;
        mock: string;
    };
}

interface Logger {
    debug: (message: string, ...args: any[]) => void;
    info: (message: string, ...args: any[]) => void;
    warn: (message: string, ...args: any[]) => void;
    error: (message: string, ...args: any[]) => void;
}

// =====================================
// Cache Manager
// =====================================

class AnalyticsCacheManager {
    private cache: Map<string, CacheEntry>;
    private defaultTTL: number;
    private maxCacheSize: number;
    private logger: Logger;
    private hitCount: number = 0;
    private missCount: number = 0;

    constructor() {
        this.cache = new Map();
        this.defaultTTL = MOCK_CONFIG.MOCK_CACHE_TTL || 5 * 60 * 1000; // 5 minutes
        this.maxCacheSize = 100;
        this.logger = configUtils.createLogger('AnalyticsCacheManager');
    }

    generateKey(method: string, params: any[]): string {
        return `${method}_${JSON.stringify(params)}`;
    }

    get(key: string): any | null {
        const cached = this.cache.get(key);
        if (!cached) {
            this.missCount++;
            return null;
        }

        if (Date.now() - cached.timestamp > cached.ttl) {
            this.cache.delete(key);
            this.missCount++;
            return null;
        }

        this.hitCount++;
        this.logger.debug(`Cache hit for ${key}`);
        return cached.data;
    }

    set(key: string, data: any, ttl: number = this.defaultTTL): void {
        // Implement LRU eviction
        if (this.cache.size >= this.maxCacheSize) {
            const firstKey = this.cache.keys().next().value;
            if (firstKey) {
                this.cache.delete(firstKey);
            }
        }

        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl
        });

        this.logger.debug(`Cached data for ${key} (TTL: ${ttl}ms)`);
    }

    clear(pattern: string | null = null): void {
        if (pattern) {
            const regex = new RegExp(pattern);
            for (const key of this.cache.keys()) {
                if (regex.test(key)) {
                    this.cache.delete(key);
                }
            }
        } else {
            this.cache.clear();
        }
    }

    getStats(): CacheStats {
        return {
            size: this.cache.size,
            maxSize: this.maxCacheSize,
            keys: Array.from(this.cache.keys()),
            hitRatio: this.hitCount / (this.hitCount + this.missCount) || 0
        };
    }
}

// =====================================
// Real Analytics Adapter
// =====================================

class RealAnalyticsAdapter {
    private logger: Logger;

    constructor() {
        this.logger = configUtils.createLogger('RealAnalyticsAdapter');
    }

    async getAnalyticsOverview(channelId: string): Promise<any> {
        try {
            const response: any = await apiClient.get(`/analytics/overview/${channelId}`);
            return response.data;
        } catch (error: any) {
            this.logger.warn('Real analytics failed, using fallback', error);
            return this._generateFallbackOverview(channelId);
        }
    }

    async getPostDynamics(channelId: string, period: string = '24h'): Promise<any> {
        try {
            const response: any = await apiClient.get(`/analytics/post-dynamics/${channelId}`, {
                params: { period }
            });
            return response.data;
        } catch (error: any) {
            this.logger.warn('Post dynamics API failed, using fallback', error);
            return this._generateFallbackPostDynamics(period);
        }
    }

    async getTopPosts(channelId: string, period: string = 'today', sortBy: string = 'views'): Promise<any> {
        try {
            const response: any = await apiClient.get(`/analytics/top-posts/${channelId}`, {
                params: { period, sortBy }
            });
            return response.data;
        } catch (error: any) {
            this.logger.warn('Top posts API failed, using fallback', error);
            return this._generateFallbackTopPosts(period, sortBy);
        }
    }

    async getEngagementMetrics(channelId: string, period: string = '7d'): Promise<any> {
        try {
            const response: any = await apiClient.get(`/analytics/engagement/${channelId}`, {
                params: { period }
            });
            return response.data;
        } catch (error: any) {
            this.logger.warn('Engagement metrics API failed, using fallback', error);
            return this._generateFallbackEngagement(period);
        }
    }

    async getBestTime(channelId: string, timeframe: string = 'week'): Promise<any> {
        try {
            const response: any = await apiClient.get(`/analytics/best-time/${channelId}`, {
                params: { timeframe }
            });
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
                api_status: response.data
            };
        } catch (error: any) {
            return {
                status: 'degraded',
                adapter: 'real_analytics',
                timestamp: Date.now(),
                error: error.message
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
            source: 'fallback'
        };
    }

    private _generateFallbackPostDynamics(period: string): any {
        return {
            dynamics: [],
            source: 'fallback',
            period,
            message: 'Backend mock API unavailable'
        };
    }

    private _generateFallbackTopPosts(period: string, sortBy: string): any {
        return {
            posts: [],
            source: 'fallback',
            period,
            sortBy,
            message: 'Backend mock API unavailable'
        };
    }

    private _generateFallbackEngagement(_period: string): any {
        return getMockEngagementMetrics();
    }

    private _generateFallbackBestTime(timeframe: string): any {
        return {
            recommendations: [],
            source: 'fallback',
            timeframe,
            message: 'Backend mock API unavailable'
        };
    }

    private _generateFallbackRecommendations(): any {
        return {
            recommendations: [],
            source: 'fallback',
            message: 'Backend mock API unavailable'
        };
    }
}

// =====================================
// Mock Analytics Adapter
// =====================================

class MockAnalyticsAdapter {
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
            source: 'mock'
        };

        return {
            ...overview,
            source: 'mock'
        };
    }

    async getPostDynamics(channelId: string, hours: number | string = 24): Promise<any> {
        await this._simulateDelay();

        try {
            const response: any = await this.apiClient.get('/unified-analytics/demo/post-dynamics', {
                params: { channel_id: channelId, hours }
            });
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
                    generated_at: new Date().toISOString()
                }
            };
        }
    }

    async getTopPosts(channelId: string, period: string = 'today', sortBy: string = 'views'): Promise<any> {
        await this._simulateDelay();

        try {
            const response: any = await this.apiClient.get('/unified-analytics/demo/top-posts', {
                params: { channel_id: channelId, period, sort_by: sortBy }
            });
            return {
                channelId,
                period,
                sortBy,
                posts: response.data.posts || [],
                source: 'backend_mock',
                generatedAt: new Date().toISOString()
            };
        } catch (error: any) {
            console.warn('Backend mock API unavailable, using fallback data:', error.message);
            return {
                channelId,
                period,
                sortBy,
                posts: [],
                source: 'fallback',
                generatedAt: new Date().toISOString()
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
            generatedAt: new Date().toISOString()
        };
    }

    async getBestTime(channelId: string, timeframe: string = 'week'): Promise<any> {
        await this._simulateDelay();

        try {
            const response: any = await this.apiClient.get('/unified-analytics/demo/best-time', {
                params: { channel_id: channelId, timeframe }
            });
            return {
                channelId,
                timeframe,
                ...response.data,
                source: 'backend_mock',
                generatedAt: new Date().toISOString()
            };
        } catch (error: any) {
            console.warn('Backend mock API unavailable, using fallback data:', error.message);
            return {
                channelId,
                timeframe,
                recommendations: [],
                source: 'fallback',
                generatedAt: new Date().toISOString(),
                message: 'Backend mock API unavailable'
            };
        }
    }

    async getAIRecommendations(channelId: string): Promise<any> {
        await this._simulateDelay();

        try {
            const response: any = await this.apiClient.get('/unified-analytics/demo/ai-recommendations', {
                params: { channel_id: channelId }
            });
            return {
                channelId,
                ...response.data,
                source: 'backend_mock',
                generatedAt: new Date().toISOString()
            };
        } catch (error: any) {
            console.warn('Backend mock API unavailable, using fallback data:', error.message);
            return {
                channelId,
                recommendations: [],
                source: 'fallback',
                generatedAt: new Date().toISOString(),
                message: 'Backend mock API unavailable'
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
                'ai_recommendations'
            ],
            performance: {
                avgResponseTime: '150ms',
                cacheHitRate: '85%'
            }
        };
    }

    private async _simulateDelay(baseMs: number | null = null): Promise<void> {
        const delay = baseMs || MOCK_CONFIG.MOCK_DELAY || 200;
        const jitter = Math.random() * delay * 0.5;
        await new Promise(resolve => setTimeout(resolve, delay + jitter));
    }
}

// =====================================
// Unified Analytics Service
// =====================================

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
            totalResponseTime: 0
        };
    }

    private _getCurrentAdapter(): RealAnalyticsAdapter | MockAnalyticsAdapter {
        const source = dataSourceManager.getDataSource();
        return source === 'api' ? this.realAdapter : this.mockAdapter;
    }

    private async _executeWithCache(method: string, params: any[], ttl: number | null = null): Promise<any> {
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
            getAIRecommendations: 60 * 60 * 1000
        };
        return ttls[method] || this.cacheManager['defaultTTL'];
    }

    // Public API Methods
    async getAnalyticsOverview(channelId: string = DEFAULT_DEMO_CHANNEL_ID): Promise<any> {
        return this._executeWithCache('getAnalyticsOverview', [channelId]);
    }

    async getPostDynamics(channelId: string = DEFAULT_DEMO_CHANNEL_ID, period: string = '24h'): Promise<any> {
        return this._executeWithCache('getPostDynamics', [channelId, period]);
    }

    async getTopPosts(channelId: string = DEFAULT_DEMO_CHANNEL_ID, period: string = 'today', sortBy: string = 'views'): Promise<any> {
        return this._executeWithCache('getTopPosts', [channelId, period, sortBy]);
    }

    async getEngagementMetrics(channelId: string = DEFAULT_DEMO_CHANNEL_ID, period: string = '7d'): Promise<any> {
        return this._executeWithCache('getEngagementMetrics', [channelId, period]);
    }

    async getBestTime(channelId: string = DEFAULT_DEMO_CHANNEL_ID, timeframe: string = 'week'): Promise<any> {
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
                cacheHitRate: this.metrics.requests > 0 ?
                    (this.metrics.cacheHits / this.metrics.requests * 100).toFixed(2) + '%' : '0%',
                avgResponseTime: this.metrics.requests > 0 ?
                    (this.metrics.totalResponseTime / this.metrics.requests).toFixed(2) + 'ms' : '0ms',
                errorRate: this.metrics.requests > 0 ?
                    (this.metrics.errors / this.metrics.requests * 100).toFixed(2) + '%' : '0%'
            }
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
                mock: 'MockAnalyticsAdapter'
            }
        };
    }
}

// Create and export singleton instance
export const analyticsService = new UnifiedAnalyticsService();

// Export class for testing
export { UnifiedAnalyticsService };

// Export adapters for direct access if needed
export { RealAnalyticsAdapter, MockAnalyticsAdapter, AnalyticsCacheManager };

export default analyticsService;
