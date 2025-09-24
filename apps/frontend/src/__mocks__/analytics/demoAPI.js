/**
 * Demo API Service
 * Provides API-like interface for demo data without backend dependency
 * Clean replacement for /analytics/demo/* endpoints
 */

import { analyticsService } from '../../services/analyticsService.js';
// demoAnalyticsService functionality moved to main analyticsService

/**
 * Demo API Client
 * Provides the same interface as real API but uses local mock data
 */
export class DemoAPIService {
    constructor() {
        this.baseURL = '/demo'; // Virtual base URL for consistency
        this.cache = new Map();
    }

    /**
     * Simulate API response format
     */
    _formatResponse(data, metadata = {}) {
        return {
            data,
            meta: {
                timestamp: new Date().toISOString(),
                source: 'demo',
                cached: metadata.cached || false,
                ...metadata
            }
        };
    }

    /**
     * Simulate network delay for realistic testing
     */
    async _simulateDelay(type = 'default') {
        const delays = {
            fast: 50,
            default: 150,
            slow: 300,
            ai_processing: 500
        };
        
        const delay = delays[type] || delays.default;
        await new Promise(resolve => setTimeout(resolve, delay));
    }

    /**
     * GET /analytics/demo/posts/dynamics
     * @param {Object} params - Query parameters
     * @param {number} params.hours - Hours to look back (1-168)
     */
    async getPostDynamics(params = {}) {
        const { hours = 24 } = params;
        
        // Validate parameters
        if (hours < 1 || hours > 168) {
            throw new Error('Hours parameter must be between 1 and 168');
        }

        await this._simulateDelay('default');
        
        try {
            const data = await analyticsService.getDemoPostDynamics(hours);
            return this._formatResponse(data, { 
                params: { hours },
                count: data.length
            });
        } catch (error) {
            throw new Error(`Failed to generate demo post dynamics: ${error.message}`);
        }
    }

    /**
     * GET /analytics/demo/posts/top
     * @param {Object} params - Query parameters  
     * @param {number} params.count - Number of posts (1-100)
     */
    async getTopPosts(params = {}) {
        const { count = 10 } = params;
        
        // Validate parameters
        if (count < 1 || count > 100) {
            throw new Error('Count parameter must be between 1 and 100');
        }

        await this._simulateDelay('default');
        
        try {
            const data = await analyticsService.getDemoTopPosts(count);
            return this._formatResponse(data, { 
                params: { count },
                total: data.length
            });
        } catch (error) {
            throw new Error(`Failed to generate demo top posts: ${error.message}`);
        }
    }

    /**
     * GET /analytics/demo/timing/best
     */
    async getBestTimes() {
        await this._simulateDelay('slow'); // AI processing takes longer
        
        try {
            const data = await analyticsService.getDemoBestTimes();
            return this._formatResponse(data, { 
                algorithm: 'engagement_optimization',
                confidence: 'high'
            });
        } catch (error) {
            throw new Error(`Failed to generate demo best times: ${error.message}`);
        }
    }

    /**
     * GET /analytics/demo/recommendations/ai
     */
    async getAIRecommendations() {
        await this._simulateDelay('ai_processing'); // AI processing simulation
        
        try {
            const data = await analyticsService.getDemoAIRecommendations();
            return this._formatResponse(data, { 
                model_version: 'v2.1.0',
                processing_time_ms: Math.floor(Math.random() * 300) + 200
            });
        } catch (error) {
            throw new Error(`Failed to generate demo AI recommendations: ${error.message}`);
        }
    }

    /**
     * Batch request multiple demo endpoints
     */
    async getBatchData(requests = []) {
        const results = {};
        
        for (const request of requests) {
            try {
                switch (request.endpoint) {
                    case 'post_dynamics':
                        results.postDynamics = await this.getPostDynamics(request.params);
                        break;
                    case 'top_posts':
                        results.topPosts = await this.getTopPosts(request.params);
                        break;
                    case 'best_times':
                        results.bestTimes = await this.getBestTimes();
                        break;
                    case 'ai_recommendations':
                        results.aiRecommendations = await this.getAIRecommendations();
                        break;
                    default:
                        results[request.endpoint] = { error: 'Unknown endpoint' };
                }
            } catch (error) {
                results[request.endpoint] = { error: error.message };
            }
        }
        
        return this._formatResponse(results, { 
            batch: true,
            requested: requests.length,
            successful: Object.keys(results).filter(k => !results[k].error).length
        });
    }

    /**
     * Get demo service health and statistics
     */
    async getHealth() {
        await this._simulateDelay('fast');
        
        return this._formatResponse({
            status: 'healthy',
            service: 'demo-analytics',
            version: '1.0.0',
            cache_stats: { hits: 0, misses: 0, size: 0 }, // Simplified cache stats
            endpoints: [
                '/demo/posts/dynamics',
                '/demo/posts/top', 
                '/demo/timing/best',
                '/demo/recommendations/ai'
            ]
        });
    }

    /**
     * Clear demo data cache
     */
    async clearCache() {
        // Cache clearing handled by main analyticsService
        analyticsService.clearCache('demo');
        
        return this._formatResponse({
            message: 'Demo cache cleared successfully',
            timestamp: new Date().toISOString()
        });
    }
}

// Create singleton instance
export const demoAPI = new DemoAPIService();

// Convenience wrapper functions that match the old API endpoints
export const demoEndpoints = {
    /**
     * GET /analytics/demo/posts/dynamics equivalent
     */
    getPostDynamics: (hours = 24) => demoAPI.getPostDynamics({ hours }),
    
    /**
     * GET /analytics/demo/posts/top equivalent  
     */
    getTopPosts: (count = 10) => demoAPI.getTopPosts({ count }),
    
    /**
     * GET /analytics/demo/timing/best equivalent
     */
    getBestTimes: () => demoAPI.getBestTimes(),
    
    /**
     * GET /analytics/demo/recommendations/ai equivalent
     */
    getAIRecommendations: () => demoAPI.getAIRecommendations()
};

export default demoAPI;