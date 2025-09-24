/**
 * Data Adapter Factory
 * Provides clean abstraction for switching between real API and mock data
 */

import { dataSourceManager } from '../utils/dataSourceManager.js';
import { mockService } from '../services/mockService.js';
import { API_CONFIG, configUtils } from '../config/mockConfig.js';
import { DEFAULT_DEMO_CHANNEL_ID } from '../__mocks__/constants.js';

class ApiAdapter {
    constructor() {
        this.logger = configUtils.createLogger('ApiAdapter');
        this.baseUrl = API_CONFIG.BASE_URL;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            this.logger.error('API request failed:', error);
            throw error;
        }
    }
    
    async getInitialData() {
        return await this.request(API_CONFIG.ENDPOINTS.INITIAL_DATA);
    }
    
    async getAnalyticsOverview(channelId) {
        return await this.request(`${API_CONFIG.ENDPOINTS.ANALYTICS_OVERVIEW}/${channelId}`);
    }
    
    async getPostDynamics(channelId, period = '24h') {
        return await this.request(`${API_CONFIG.ENDPOINTS.POST_DYNAMICS}/${channelId}?period=${period}`);
    }
    
    async getTopPosts(channelId, period = 'today', sortBy = 'views') {
        return await this.request(`${API_CONFIG.ENDPOINTS.ANALYTICS_TOP_POSTS}/${channelId}?period=${period}&sort=${sortBy}`);
    }
    
    async getBestTime(channelId, timeframe = 'week') {
        return await this.request(`${API_CONFIG.ENDPOINTS.BEST_TIME}/${channelId}?timeframe=${timeframe}`);
    }
    
    async getEngagementMetrics(channelId, period = '7d') {
        return await this.request(`${API_CONFIG.ENDPOINTS.ENGAGEMENT_METRICS}/${channelId}?period=${period}`);
    }
    
    async healthCheck() {
        return await this.request(API_CONFIG.ENDPOINTS.HEALTH);
    }
}

class MockAdapter {
    constructor() {
        this.logger = configUtils.createLogger('MockAdapter');
    }
    
    async getInitialData() {
        return await mockService.getInitialData();
    }
    
    async getAnalyticsOverview(channelId) {
        return await mockService.getAnalyticsOverview(channelId);
    }
    
    async getPostDynamics(channelId, period = '24h') {
        return await mockService.getPostDynamics(channelId, period);
    }
    
    async getTopPosts(channelId, period = 'today', sortBy = 'views') {
        return await mockService.getTopPosts(channelId, period, sortBy);
    }
    
    async getBestTime(channelId, timeframe = 'week') {
        return await mockService.getBestTime(channelId, timeframe);
    }
    
    async getEngagementMetrics(channelId, period = '7d') {
        return await mockService.getEngagementMetrics(channelId, period);
    }
    
    async healthCheck() {
        return await mockService.healthCheck();
    }
}

class DataAdapterFactory {
    constructor() {
        this.apiAdapter = new ApiAdapter();
        this.mockAdapter = new MockAdapter();
        this.logger = configUtils.createLogger('DataAdapterFactory');
    }
    
    getAdapter(source = null) {
        const dataSource = source || dataSourceManager.getDataSource();
        
        if (dataSource === 'api') {
            this.logger.debug('Using API adapter');
            return this.apiAdapter;
        } else {
            this.logger.debug('Using Mock adapter');
            return this.mockAdapter;
        }
    }
    
    async getCurrentAdapter() {
        const currentSource = dataSourceManager.getDataSource();
        
        // If using API, check if it's actually available
        if (currentSource === 'api') {
            try {
                await this.apiAdapter.healthCheck();
                return this.apiAdapter;
            } catch (error) {
                this.logger.warn('API adapter failed health check - maintaining current data source');
                // No auto-switch - let backend handle demo data through proper authentication
                // Return API adapter to let it handle the error appropriately
                return this.apiAdapter;
            }
        }
        
        return this.mockAdapter;
    }
}

// Create singleton factory
const dataAdapterFactory = new DataAdapterFactory();

/**
 * Unified Data Service
 * Provides a single interface for all data operations with automatic adapter switching
 */
export class UnifiedDataService {
    constructor() {
        this.factory = dataAdapterFactory;
        this.logger = configUtils.createLogger('UnifiedDataService');
    }
    
    async getInitialData() {
        const adapter = await this.factory.getCurrentAdapter();
        return await adapter.getInitialData();
    }
    
    async getAnalyticsOverview(channelId = DEFAULT_DEMO_CHANNEL_ID) {
        const adapter = await this.factory.getCurrentAdapter();
        return await adapter.getAnalyticsOverview(channelId);
    }
    
    async getPostDynamics(channelId = DEFAULT_DEMO_CHANNEL_ID, period = '24h') {
        const adapter = await this.factory.getCurrentAdapter();
        return await adapter.getPostDynamics(channelId, period);
    }
    
    async getTopPosts(channelId = DEFAULT_DEMO_CHANNEL_ID, period = 'today', sortBy = 'views') {
        const adapter = await this.factory.getCurrentAdapter();
        return await adapter.getTopPosts(channelId, period, sortBy);
    }
    
    async getBestTime(channelId = DEFAULT_DEMO_CHANNEL_ID, timeframe = 'week') {
        const adapter = await this.factory.getCurrentAdapter();
        return await adapter.getBestTime(channelId, timeframe);
    }
    
    async getEngagementMetrics(channelId = DEFAULT_DEMO_CHANNEL_ID, period = '7d') {
        const adapter = await this.factory.getCurrentAdapter();
        return await adapter.getEngagementMetrics(channelId, period);
    }
    
    async healthCheck() {
        const adapter = this.factory.getAdapter(); // Don't use getCurrentAdapter to avoid recursion
        return await adapter.healthCheck();
    }
    
    // Batch operations
    async getAllAnalytics(channelId = DEFAULT_DEMO_CHANNEL_ID) {
        const adapter = await this.factory.getCurrentAdapter();
        
        try {
            const [overview, postDynamics, topPosts, bestTime, engagement] = await Promise.all([
                adapter.getAnalyticsOverview(channelId),
                adapter.getPostDynamics(channelId),
                adapter.getTopPosts(channelId),
                adapter.getBestTime(channelId),
                adapter.getEngagementMetrics(channelId)
            ]);
            
            return {
                overview,
                postDynamics,
                topPosts,
                bestTime,
                engagement,
                timestamp: new Date().toISOString(),
                source: dataSourceManager.getDataSource()
            };
        } catch (error) {
            this.logger.error('Batch analytics fetch failed:', error);
            throw error;
        }
    }
    
    // Utility methods
    getCurrentDataSource() {
        return dataSourceManager.getDataSource();
    }
    
    isUsingRealAPI() {
        return dataSourceManager.isUsingRealAPI();
    }
    
    async switchDataSource(source, reason = 'programmatic') {
        return dataSourceManager.setDataSource(source, reason);
    }
}

// Export singleton instance
export const unifiedDataService = new UnifiedDataService();

// Export individual adapters for direct use if needed
export { ApiAdapter, MockAdapter, DataAdapterFactory };

// Export factory instance
export { dataAdapterFactory };

// Export with alternative name for compatibility
export const dataServiceFactory = dataAdapterFactory;