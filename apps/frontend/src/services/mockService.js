/**
 * Centralized Mock Service
 * Provides clean, organized mock data with realistic delays and caching
 */

import { MOCK_CONFIG, MOCK_DATA_CONFIG, configUtils } from '../config/mockConfig.js';
import { mockAnalyticsData, getMockPostDynamics, getMockTopPosts, getMockBestTime, getMockEngagementMetrics, getMockInitialData } from '../__mocks__/index.js';  
import { demoAnalyticsService } from '../__mocks__/analytics/demoAnalyticsService.js';

class MockService {
    constructor() {
        this.cache = new Map();
        this.logger = configUtils.createLogger('MockService');
        this.performanceTracker = new Map();
    }
    
    // Cache management
    setCache(key, data, ttl = MOCK_CONFIG.MOCK_CACHE_TTL) {
        if (!MOCK_CONFIG.ENABLE_MOCK_CACHE) return;
        
        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            ttl
        });
    }
    
    getCache(key) {
        if (!MOCK_CONFIG.ENABLE_MOCK_CACHE) return null;
        
        const cached = this.cache.get(key);
        if (!cached) return null;
        
        // Check if expired
        if (Date.now() - cached.timestamp > cached.ttl) {
            this.cache.delete(key);
            return null;
        }
        
        return cached.data;
    }
    
    clearCache(pattern = null) {
        if (pattern) {
            for (const [key] of this.cache.entries()) {
                if (key.includes(pattern)) {
                    this.cache.delete(key);
                }
            }
        } else {
            this.cache.clear();
        }
        this.logger.debug('Cache cleared', pattern || 'all');
    }
    
    // Performance tracking
    startPerformanceTimer(operation) {
        if (MOCK_CONFIG.ENABLE_PERFORMANCE_LOGS) {
            this.performanceTracker.set(operation, performance.now());
        }
    }
    
    endPerformanceTimer(operation) {
        if (!MOCK_CONFIG.ENABLE_PERFORMANCE_LOGS) return;
        
        const startTime = this.performanceTracker.get(operation);
        if (startTime) {
            const duration = performance.now() - startTime;
            this.performanceTracker.delete(operation);
            
            if (duration > 50) { // Only log if > 50ms
                this.logger.debug(`Performance: ${operation} took ${duration.toFixed(2)}ms`);
            }
        }
    }
    
    // Realistic delay simulation
    async simulateNetworkDelay(operation = 'default') {
        if (!MOCK_CONFIG.REALISTIC_DELAYS) return;
        
        let delay = MOCK_CONFIG.MOCK_DELAY;
        
        // Vary delay based on operation type
        const delayMultipliers = {
            'initial_data': 0.8,
            'analytics': 1.2,
            'post_dynamics': 1.5,
            'top_posts': 1.0,
            'best_time': 0.9,
            'engagement': 1.1,
        };
        
        delay *= (delayMultipliers[operation] || 1);
        
        // Add some randomness (+/- 20%)
        delay = delay * (0.8 + Math.random() * 0.4);
        
        await new Promise(resolve => setTimeout(resolve, Math.round(delay)));
    }
    
    // Error simulation
    shouldSimulateError() {
        return Math.random() < MOCK_CONFIG.MOCK_ERROR_RATE;
    }
    
    createMockError(type = 'network') {
        const errors = {
            network: new Error('Simulated network error'),
            timeout: new Error('Request timeout'),
            server: new Error('Internal server error'),
        };
        
        const error = errors[type] || errors.network;
        error.isMockError = true;
        return error;
    }
    
    // Core mock data methods
    async getInitialData() {
        const operation = 'initial_data';
        this.startPerformanceTimer(operation);
        
        const cacheKey = 'initial_data';
        let cached = this.getCache(cacheKey);
        
        if (cached) {
            this.logger.debug('Returning cached initial data');
            await this.simulateNetworkDelay(operation);
            this.endPerformanceTimer(operation);
            return cached;
        }
        
        // Simulate error if configured
        if (this.shouldSimulateError()) {
            await this.simulateNetworkDelay(operation);
            throw this.createMockError();
        }
        
        this.logger.info('Generating fresh initial data');
        await this.simulateNetworkDelay(operation);
        
        const data = await getMockInitialData();
        this.setCache(cacheKey, data);
        
        this.endPerformanceTimer(operation);
        return data;
    }
    
    async getAnalyticsOverview(channelId = 'demo_channel') {
        const operation = 'analytics';
        this.startPerformanceTimer(operation);
        
        const cacheKey = `analytics_overview_${channelId}`;
        let cached = this.getCache(cacheKey);
        
        if (cached) {
            await this.simulateNetworkDelay(operation);
            this.endPerformanceTimer(operation);
            return cached;
        }
        
        if (this.shouldSimulateError()) {
            await this.simulateNetworkDelay(operation);
            throw this.createMockError();
        }
        
        await this.simulateNetworkDelay(operation);
        
        const data = {
            ...mockAnalyticsData,
            channelId,
            timestamp: new Date().toISOString(),
            generated_by: 'MockService'
        };
        
        this.setCache(cacheKey, data);
        this.endPerformanceTimer(operation);
        return data;
    }
    
    async getPostDynamics(channelId = 'demo_channel', period = '24h') {
        const operation = 'post_dynamics';
        this.startPerformanceTimer(operation);
        
        const cacheKey = `post_dynamics_${channelId}_${period}`;
        let cached = this.getCache(cacheKey);
        
        if (cached) {
            await this.simulateNetworkDelay(operation);
            this.endPerformanceTimer(operation);
            return cached;
        }
        
        if (this.shouldSimulateError()) {
            await this.simulateNetworkDelay(operation);
            throw this.createMockError();
        }
        
        await this.simulateNetworkDelay(operation);
        
        const data = await getMockPostDynamics(period);
        data.channelId = channelId;
        
        this.setCache(cacheKey, data);
        this.endPerformanceTimer(operation);
        return data;
    }
    
    async getTopPosts(channelId = 'demo_channel', period = 'today', sortBy = 'views') {
        const operation = 'top_posts';
        this.startPerformanceTimer(operation);
        
        const cacheKey = `top_posts_${channelId}_${period}_${sortBy}`;
        let cached = this.getCache(cacheKey);
        
        if (cached) {
            await this.simulateNetworkDelay(operation);
            this.endPerformanceTimer(operation);
            return cached;
        }
        
        if (this.shouldSimulateError()) {
            await this.simulateNetworkDelay(operation);
            throw this.createMockError();
        }
        
        await this.simulateNetworkDelay(operation);
        
        const data = await getMockTopPosts(period, sortBy);
        data.channelId = channelId;
        
        this.setCache(cacheKey, data);
        this.endPerformanceTimer(operation);
        return data;
    }
    
    async getBestTime(channelId = 'demo_channel', timeframe = 'week') {
        const operation = 'best_time';
        this.startPerformanceTimer(operation);
        
        const cacheKey = `best_time_${channelId}_${timeframe}`;
        let cached = this.getCache(cacheKey);
        
        if (cached) {
            await this.simulateNetworkDelay(operation);
            this.endPerformanceTimer(operation);
            return cached;
        }
        
        if (this.shouldSimulateError()) {
            await this.simulateNetworkDelay(operation);
            throw this.createMockError();
        }
        
        await this.simulateNetworkDelay(operation);
        
        const data = await getMockBestTime(timeframe);
        data.channelId = channelId;
        
        this.setCache(cacheKey, data);
        this.endPerformanceTimer(operation);
        return data;
    }
    
    async getEngagementMetrics(channelId = 'demo_channel', period = '7d') {
        const operation = 'engagement';
        this.startPerformanceTimer(operation);
        
        const cacheKey = `engagement_${channelId}_${period}`;
        let cached = this.getCache(cacheKey);
        
        if (cached) {
            await this.simulateNetworkDelay(operation);
            this.endPerformanceTimer(operation);
            return cached;
        }
        
        if (this.shouldSimulateError()) {
            await this.simulateNetworkDelay(operation);
            throw this.createMockError();
        }
        
        await this.simulateNetworkDelay(operation);
        
        const data = await getMockEngagementMetrics(period);
        data.channelId = channelId;
        
        this.setCache(cacheKey, data);
        this.endPerformanceTimer(operation);
        return data;
    }
    
    // Convenience methods for different data types
    async getChannels() {
        const initialData = await this.getInitialData();
        return initialData.channels || [];
    }
    
    async getScheduledPosts() {
        const initialData = await this.getInitialData();
        return initialData.scheduled_posts || [];
    }
    
    async getUserData() {
        const initialData = await this.getInitialData();
        return {
            user: initialData.user,
            plan: initialData.plan
        };
    }
    
    // Health check
    async healthCheck() {
        await this.simulateNetworkDelay('health');
        return {
            status: 'healthy',
            service: 'MockService',
            timestamp: new Date().toISOString(),
            cache_size: this.cache.size,
            performance_tracking: MOCK_CONFIG.ENABLE_PERFORMANCE_LOGS
        };
    }
    
    // Statistics
    getStats() {
        return {
            cache_entries: this.cache.size,
            performance_timers: this.performanceTracker.size,
            config: {
                delays_enabled: MOCK_CONFIG.REALISTIC_DELAYS,
                cache_enabled: MOCK_CONFIG.ENABLE_MOCK_CACHE,
                error_rate: MOCK_CONFIG.MOCK_ERROR_RATE,
                default_delay: MOCK_CONFIG.MOCK_DELAY
            }
        };
    }
    
    /**
     * Get storage files (for file management functionality)
     */
    async getStorageFiles(limit = 20, offset = 0) {
        await this.simulateNetworkDelay('storage_files');
        
        const mockFiles = [
            { id: 1, name: 'analytics_report.csv', size: 15234, type: 'csv', created: '2025-09-10T10:30:00Z' },
            { id: 2, name: 'post_dynamics.png', size: 45621, type: 'png', created: '2025-09-09T15:45:00Z' },
            { id: 3, name: 'engagement_chart.pdf', size: 78943, type: 'pdf', created: '2025-09-08T09:15:00Z' },
            { id: 4, name: 'weekly_summary.xlsx', size: 23456, type: 'xlsx', created: '2025-09-07T14:20:00Z' },
            { id: 5, name: 'content_backup.zip', size: 156789, type: 'zip', created: '2025-09-06T11:30:00Z' }
        ];
        
        const startIndex = offset;
        const endIndex = Math.min(offset + limit, mockFiles.length);
        const paginatedFiles = mockFiles.slice(startIndex, endIndex);
        
        return {
            files: paginatedFiles,
            total: mockFiles.length,
            limit,
            offset,
            hasMore: endIndex < mockFiles.length
        };
    }
    
    // Demo Analytics Endpoints (moved from backend API)
    async getDemoPostDynamics(hours = 24) {
        this.startPerformanceTimer('demo_post_dynamics');
        
        const cacheKey = `demo_post_dynamics_${hours}`;
        const cached = this.getCache(cacheKey);
        if (cached) {
            this.endPerformanceTimer('demo_post_dynamics');
            return cached;
        }
        
        await this.simulateNetworkDelay('demo_data');
        
        const data = demoAnalyticsService.getPostDynamics(hours);
        this.setCache(cacheKey, data, 5 * 60 * 1000); // 5 minutes cache
        
        this.endPerformanceTimer('demo_post_dynamics');
        return data;
    }
    
    async getDemoTopPosts(count = 10) {
        this.startPerformanceTimer('demo_top_posts');
        
        const cacheKey = `demo_top_posts_${count}`;
        const cached = this.getCache(cacheKey);
        if (cached) {
            this.endPerformanceTimer('demo_top_posts');
            return cached;
        }
        
        await this.simulateNetworkDelay('demo_data');
        
        const data = demoAnalyticsService.getTopPosts(count);
        this.setCache(cacheKey, data, 10 * 60 * 1000); // 10 minutes cache
        
        this.endPerformanceTimer('demo_top_posts');
        return data;
    }
    
    async getDemoBestTimes() {
        this.startPerformanceTimer('demo_best_times');
        
        const cacheKey = 'demo_best_times';
        const cached = this.getCache(cacheKey);
        if (cached) {
            this.endPerformanceTimer('demo_best_times');
            return cached;
        }
        
        await this.simulateNetworkDelay('demo_data');
        
        const data = demoAnalyticsService.getBestTimes();
        this.setCache(cacheKey, data, 30 * 60 * 1000); // 30 minutes cache
        
        this.endPerformanceTimer('demo_best_times');
        return data;
    }
    
    async getDemoAIRecommendations() {
        this.startPerformanceTimer('demo_ai_recommendations');
        
        const cacheKey = 'demo_ai_recommendations';
        const cached = this.getCache(cacheKey);
        if (cached) {
            this.endPerformanceTimer('demo_ai_recommendations');
            return cached;
        }
        
        await this.simulateNetworkDelay('ai_processing');
        
        const data = demoAnalyticsService.getAIRecommendations();
        this.setCache(cacheKey, data, 15 * 60 * 1000); // 15 minutes cache
        
        this.endPerformanceTimer('demo_ai_recommendations');
        return data;
    }

    // Cleanup
    destroy() {
        this.clearCache();
        this.performanceTracker.clear();
        demoAnalyticsService.clearCache(); // Clear demo service cache too
        this.logger.info('MockService destroyed');
    }
}

// Create and export singleton instance
export const mockService = new MockService();

// Export class for testing
export { MockService };

// Convenience exports for direct use
export const getMockData = {
    // Demo Analytics Data (clean API replacement)
    demoPostDynamics: (hours = 24) => mockService.getDemoPostDynamics(hours),
    demoTopPosts: (count = 10) => mockService.getDemoTopPosts(count),
    demoBestTimes: () => mockService.getDemoBestTimes(),
    demoAIRecommendations: () => mockService.getDemoAIRecommendations(),
    initialData: () => mockService.getInitialData(),
    analytics: (channelId) => mockService.getAnalyticsOverview(channelId),
    postDynamics: (channelId, period) => mockService.getPostDynamics(channelId, period),
    topPosts: (channelId, period, sortBy) => mockService.getTopPosts(channelId, period, sortBy),
    bestTime: (channelId, timeframe) => mockService.getBestTime(channelId, timeframe),
    engagement: (channelId, period) => mockService.getEngagementMetrics(channelId, period),
    channels: () => mockService.getChannels(),
    scheduledPosts: () => mockService.getScheduledPosts(),
    userData: () => mockService.getUserData(),
};