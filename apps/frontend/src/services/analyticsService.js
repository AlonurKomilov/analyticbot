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

import { dataSourceManager } from '../utils/dataSourceManager.js';
import { analyticsPosts } from '../domains/analytics';

// Import centralized mock config from __mocks__
import { MOCK_CONFIG, API_CONFIG, configUtils } from '../__mocks__/config/mockConfig.js';
import { DEFAULT_DEMO_CHANNEL_ID } from '../__mocks__/constants.js';

// Import unified API client
import { apiClient } from '../api/client.js';

// Import mock data generators (for fallback compatibility)
import {
    mockAnalyticsData,
    getMockPostDynamics,
    getMockTopPosts,
    getMockBestTime,
    getMockEngagementMetrics
} from '../__mocks__/index.js';

/**
 * Cache Manager for analytics data
 */
class AnalyticsCacheManager {
    constructor() {
        this.cache = new Map();
        this.defaultTTL = MOCK_CONFIG.CACHE_TTL_MS || 5 * 60 * 1000; // 5 minutes
        this.maxCacheSize = 100;
        this.logger = configUtils.createLogger('AnalyticsCacheManager');
    }

    generateKey(method, params) {
        return `${method}_${JSON.stringify(params)}`;
    }

    get(key) {
        const cached = this.cache.get(key);
        if (!cached) return null;

        if (Date.now() - cached.timestamp > cached.ttl) {
            this.cache.delete(key);
            return null;
        }

        this.logger.debug(`Cache hit for ${key}`);
        return cached.data;
    }

    set(key, data, ttl = this.defaultTTL) {
        // Implement LRU eviction
        if (this.cache.size >= this.maxCacheSize) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }

        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl
        });

        this.logger.debug(`Cached data for ${key} (TTL: ${ttl}ms)`);
    }

    clear(pattern = null) {
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

    getStats() {
        return {
            size: this.cache.size,
            maxSize: this.maxCacheSize,
            keys: Array.from(this.cache.keys()),
            hitRatio: this.hitCount / (this.hitCount + this.missCount) || 0
        };
    }
}

/**
 * Real Analytics Adapter - handles API communication
 */
class RealAnalyticsAdapter {
    constructor() {
        this.logger = configUtils.createLogger('RealAnalyticsAdapter');
    }

    async getAnalyticsOverview(channelId) {
        try {
            const response = await apiClient.get(`/analytics/overview/${channelId}`);
            return response.data;
        } catch (error) {
            this.logger.warn('Real analytics failed, using fallback', error);
            // Fallback to demo data when API fails
            return this._generateFallbackOverview(channelId);
        }
    }

    async getPostDynamics(channelId, period = '24h') {
        try {
            const response = await apiClient.get(`/analytics/post-dynamics/${channelId}`, {
                params: { period }
            });
            return response.data;
        } catch (error) {
            this.logger.warn('Post dynamics API failed, using fallback', error);
            return this._generateFallbackPostDynamics(period);
        }
    }

    async getTopPosts(channelId, period = 'today', sortBy = 'views') {
        try {
            const response = await apiClient.get(`/analytics/top-posts/${channelId}`, {
                params: { period, sortBy }
            });
            return response.data;
        } catch (error) {
            this.logger.warn('Top posts API failed, using fallback', error);
            return this._generateFallbackTopPosts(period, sortBy);
        }
    }

    async getEngagementMetrics(channelId, period = '7d') {
        try {
            const response = await apiClient.get(`/analytics/engagement/${channelId}`, {
                params: { period }
            });
            return response.data;
        } catch (error) {
            this.logger.warn('Engagement metrics API failed, using fallback', error);
            return this._generateFallbackEngagement(period);
        }
    }

    async getBestTime(channelId, timeframe = 'week') {
        try {
            const response = await apiClient.get(`/analytics/best-time/${channelId}`, {
                params: { timeframe }
            });
            return response.data;
        } catch (error) {
            this.logger.warn('Best time API failed, using fallback', error);
            return this._generateFallbackBestTime(timeframe);
        }
    }

    async getAIRecommendations(channelId) {
        try {
            const response = await apiClient.get(`/ai/recommendations/${channelId}`);
            return response.data;
        } catch (error) {
            this.logger.warn('AI recommendations API failed, using fallback', error);
            return this._generateFallbackRecommendations();
        }
    }

    async healthCheck() {
        try {
            const response = await apiClient.get('/health');
            return {
                status: 'healthy',
                adapter: 'real_analytics',
                timestamp: Date.now(),
                api_status: response.data
            };
        } catch (error) {
            return {
                status: 'degraded',
                adapter: 'real_analytics',
                timestamp: Date.now(),
                error: error.message
            };
        }
    }

    // Fallback methods when API fails
    _generateFallbackOverview(channelId) {
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

    _generateFallbackPostDynamics(period) {
        return {
            dynamics: [], // Empty fallback when backend is unavailable
            source: 'fallback',
            period,
            message: 'Backend mock API unavailable'
        };
    }

    _generateFallbackTopPosts(period, sortBy) {
        return {
            posts: [], // Empty fallback when backend is unavailable
            source: 'fallback',
            period,
            sortBy,
            message: 'Backend mock API unavailable'
        };
    }

    _generateFallbackEngagement(period) {
        return getMockEngagementMetrics();
    }

    _generateFallbackBestTime(timeframe) {
        return {
            recommendations: [],
            source: 'fallback',
            timeframe,
            message: 'Backend mock API unavailable'
        };
    }

    _generateFallbackRecommendations() {
        return {
            recommendations: [],
            source: 'fallback',
            message: 'Backend mock API unavailable'
        };
    }
}

/**
 * Mock Analytics Adapter - handles demo/development data
 */
class MockAnalyticsAdapter {
    constructor() {
        this.logger = configUtils.createLogger('MockAnalyticsAdapter');
    }

    async getAnalyticsOverview(channelId = DEFAULT_DEMO_CHANNEL_ID) {
        await this._simulateDelay();

        // Return basic mock overview data
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

    async getPostDynamics(channelId, hours = 24) {
        await this.addDelay();

        try {
            // Use backend API for mock data (single source of truth)
            const response = await this.apiClient.get('/unified-analytics/demo/post-dynamics', {
                params: { channel_id: channelId, hours }
            });
            return response.data;
        } catch (error) {
            console.warn('Backend mock API unavailable, using fallback data:', error.message);
            // Minimal fallback if backend is down
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

    async getTopPosts(channelId, period = 'today', sortBy = 'views') {
        await this._simulateDelay();

        try {
            // Use backend API for mock data (single source of truth)
            const response = await this.apiClient.get('/unified-analytics/demo/top-posts', {
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
        } catch (error) {
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

    async getEngagementMetrics(channelId, period = '7d') {
        await this._simulateDelay();

        return {
            channelId,
            period,
            ...getMockEngagementMetrics(),
            source: 'mock',
            generatedAt: new Date().toISOString()
        };
    }

    async getBestTime(channelId, timeframe = 'week') {
        await this._simulateDelay();

        try {
            // Use backend API for mock data (single source of truth)
            const response = await this.apiClient.get('/unified-analytics/demo/best-time', {
                params: { channel_id: channelId, timeframe }
            });
            return {
                channelId,
                timeframe,
                ...response.data,
                source: 'backend_mock',
                generatedAt: new Date().toISOString()
            };
        } catch (error) {
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

    async getAIRecommendations(channelId) {
        await this._simulateDelay();

        try {
            // Use backend API for mock data (single source of truth)
            const response = await this.apiClient.get('/unified-analytics/demo/ai-recommendations', {
                params: { channel_id: channelId }
            });
            return {
                channelId,
                ...response.data,
                source: 'backend_mock',
                generatedAt: new Date().toISOString()
            };
        } catch (error) {
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

    async healthCheck() {
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

    async _simulateDelay(baseMs = null) {
        const delay = baseMs || MOCK_CONFIG.NETWORK_DELAY_MS || 200;
        const jitter = Math.random() * delay * 0.5; // Add up to 50% jitter
        await new Promise(resolve => setTimeout(resolve, delay + jitter));
    }

    _parseTimeframeToPeriod(timeframe) {
        const mapping = {
            '1h': 1,
            '6h': 6,
            '12h': 12,
            '24h': 24,
            '1d': 24,
            '7d': 168,
            '1w': 168,
            '30d': 720,
            '1m': 720
        };
        return mapping[timeframe] || 24;
    }
}

/**
 * Unified Analytics Service
 * Main service class that provides consistent interface for all analytics operations
 */
class UnifiedAnalyticsService {
    constructor() {
        this.cacheManager = new AnalyticsCacheManager();
        this.realAdapter = new RealAnalyticsAdapter();
        this.mockAdapter = new MockAnalyticsAdapter();
        this.logger = configUtils.createLogger('UnifiedAnalyticsService');

        // Performance tracking
        this.metrics = {
            requests: 0,
            cacheHits: 0,
            errors: 0,
            totalResponseTime: 0
        };
    }

    /**
     * Get current adapter based on data source configuration
     */
    _getCurrentAdapter() {
        const source = dataSourceManager.getDataSource();
        return source === 'api' ? this.realAdapter : this.mockAdapter;
    }

    /**
     * Execute method with caching, error handling, and performance tracking
     */
    async _executeWithCache(method, params, ttl = null) {
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
            const result = await adapter[method](...params);

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

    /**
     * Get TTL for specific methods
     */
    _getMethodTTL(method) {
        const ttls = {
            getAnalyticsOverview: 2 * 60 * 1000,    // 2 minutes
            getPostDynamics: 5 * 60 * 1000,         // 5 minutes
            getTopPosts: 10 * 60 * 1000,            // 10 minutes
            getEngagementMetrics: 5 * 60 * 1000,    // 5 minutes
            getBestTime: 30 * 60 * 1000,            // 30 minutes
            getAIRecommendations: 60 * 60 * 1000    // 1 hour
        };
        return ttls[method] || this.cacheManager.defaultTTL;
    }

    // Public API Methods

    async getAnalyticsOverview(channelId = DEFAULT_DEMO_CHANNEL_ID) {
        return this._executeWithCache('getAnalyticsOverview', [channelId]);
    }

    async getPostDynamics(channelId = DEFAULT_DEMO_CHANNEL_ID, period = '24h') {
        return this._executeWithCache('getPostDynamics', [channelId, period]);
    }

    async getTopPosts(channelId = DEFAULT_DEMO_CHANNEL_ID, period = 'today', sortBy = 'views') {
        return this._executeWithCache('getTopPosts', [channelId, period, sortBy]);
    }

    async getEngagementMetrics(channelId = DEFAULT_DEMO_CHANNEL_ID, period = '7d') {
        return this._executeWithCache('getEngagementMetrics', [channelId, period]);
    }

    async getBestTime(channelId = DEFAULT_DEMO_CHANNEL_ID, timeframe = 'week') {
        return this._executeWithCache('getBestTime', [channelId, timeframe]);
    }

    async getAIRecommendations(channelId = DEFAULT_DEMO_CHANNEL_ID) {
        return this._executeWithCache('getAIRecommendations', [channelId]);
    }

    async healthCheck() {
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

    /**
     * Force refresh cache for specific method or all
     */
    async refreshCache(method = null, params = null) {
        if (method && params) {
            const cacheKey = this.cacheManager.generateKey(method, params);
            this.cacheManager.clear(cacheKey);
            return this._executeWithCache(method, params);
        } else {
            this.cacheManager.clear();
            this.logger.info('All cache cleared');
        }
    }

    /**
     * Switch data source and clear relevant cache
     */
    async switchDataSource(source) {
        dataSourceManager.switchDataSource(source);
        this.cacheManager.clear(); // Clear cache when switching sources
        this.logger.info(`Switched to ${source} data source`);
    }

    /**
     * Get service metrics and statistics
     */
    getMetrics() {
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
