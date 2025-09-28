/**
 * Mock Data Provider - FOR TESTING/DEVELOPMENT ONLY
 * This provider should never be imported by production code
 */

import { DataProvider } from '../providers/DataProvider.js';

/**
 * Mock Data Provider Implementation
 * Uses mock data for testing and development purposes
 */
export class MockDataProvider extends DataProvider {
    constructor(mockData = null) {
        super();
        this.mockData = mockData || this._getDefaultMockData();
        this.delayMs = 100; // Simulate network delay
    }
    
    async isAvailable() {
        // Mock provider is always "available"
        await this._simulateDelay();
        return true;
    }
    
    async getAnalytics(channelId) {
        await this._simulateDelay();
        
        return {
            channelId,
            postDynamics: this.mockData.postDynamics,
            summary: {
                totalPosts: 245,
                totalViews: 125678,
                avgEngagement: 4.2,
                growthRate: 12.5
            },
            timeline: this.mockData.postDynamics.timeline,
            generatedAt: new Date().toISOString()
        };
    }
    
    async getTopPosts(channelId, options = {}) {
        await this._simulateDelay();
        
        const { limit = 10, sortBy = 'views' } = options;
        let posts = [...this.mockData.topPosts];
        
        // Sort by specified criteria
        if (sortBy === 'engagement') {
            posts.sort((a, b) => b.engagementRate - a.engagementRate);
        } else {
            posts.sort((a, b) => b.views - a.views);
        }
        
        return posts.slice(0, limit);
    }
    
    async getEngagementMetrics(channelId, options = {}) {
        await this._simulateDelay();
        
        return {
            channelId,
            metrics: this.mockData.engagementMetrics,
            period: options.period || '30d',
            generatedAt: new Date().toISOString()
        };
    }
    
    async getRecommendations(channelId) {
        await this._simulateDelay();
        
        return {
            channelId,
            recommendations: this.mockData.bestTimeRecommendations,
            generatedAt: new Date().toISOString()
        };
    }
    
    getProviderName() {
        return 'mock';
    }
    
    /**
     * Set custom mock data
     * @param {Object} mockData - Custom mock data to use
     */
    setMockData(mockData) {
        this.mockData = mockData;
    }
    
    /**
     * Set network delay simulation
     * @param {number} delayMs - Delay in milliseconds
     */
    setDelay(delayMs) {
        this.delayMs = delayMs;
    }
    
    /**
     * Simulate network delay
     * @private
     */
    async _simulateDelay() {
        if (this.delayMs > 0) {
            await new Promise(resolve => setTimeout(resolve, this.delayMs));
        }
    }
    
    /**
     * Get default mock data
     * @private
     */
    _getDefaultMockData() {
        return {
            postDynamics: {
                timeline: [
                    { date: '2024-01-01', views: 1200, engagement: 4.2 },
                    { date: '2024-01-02', views: 1150, engagement: 3.8 },
                    { date: '2024-01-03', views: 1350, engagement: 4.6 },
                    { date: '2024-01-04', views: 1100, engagement: 3.9 },
                    { date: '2024-01-05', views: 1400, engagement: 5.1 }
                ]
            },
            topPosts: [
                {
                    id: 1,
                    title: 'Top Performing Post',
                    views: 15420,
                    engagementRate: 8.5,
                    publishedAt: '2024-01-01T10:00:00Z'
                },
                {
                    id: 2,
                    title: 'Second Best Post',
                    views: 12340,
                    engagementRate: 7.2,
                    publishedAt: '2024-01-02T14:30:00Z'
                },
                {
                    id: 3,
                    title: 'Great Content Example',
                    views: 9876,
                    engagementRate: 6.8,
                    publishedAt: '2024-01-03T09:15:00Z'
                }
            ],
            engagementMetrics: {
                avgReactionRate: 5.2,
                avgCommentRate: 2.1,
                avgShareRate: 1.8,
                totalEngagement: 9.1,
                trend: 'increasing'
            },
            bestTimeRecommendations: {
                bestHours: [9, 12, 18, 21],
                bestDays: ['Monday', 'Wednesday', 'Friday'],
                timezone: 'UTC',
                confidence: 0.85
            }
        };
    }
}

/**
 * Create a mock data provider instance
 * Should only be used in tests or development
 */
export const createMockDataProvider = (customMockData = null) => {
    return new MockDataProvider(customMockData);
};