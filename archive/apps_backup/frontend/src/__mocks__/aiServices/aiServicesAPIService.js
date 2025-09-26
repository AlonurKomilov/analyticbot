/**
 * AI Services API Service - Backend Integration
 * Replaces duplicate frontend mock data generation with backend API calls
 * 
 * This service now connects to backend mock endpoints instead of generating
 * data locally, creating a single source of truth for AI services mock data.
 */

import { API_CONFIG } from '../../config/mockConfig.js';

class AIServicesAPIService {
    constructor() {
        this.baseURL = API_CONFIG.API_BASE_URL || 'https://84dp9jc9-11400.euw.devtunnels.ms';
    }

    /**
     * Get content optimizer stats from backend
     */
    async getContentOptimizerStats() {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/ai-services/content-optimizer/stats`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.warn('Backend AI API unavailable, using fallback data:', error.message);
            return this._getFallbackContentOptimizerStats();
        }
    }

    /**
     * Get recent content optimizations from backend
     */
    async getRecentOptimizations(limit = 10) {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/ai-services/content-optimizer/recent?limit=${limit}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.warn('Backend AI API unavailable, using fallback data:', error.message);
            return this._getFallbackRecentOptimizations();
        }
    }

    /**
     * Get churn predictor stats from backend
     */
    async getChurnPredictorStats() {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/ai-services/churn-predictor/stats`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.warn('Backend AI API unavailable, using fallback data:', error.message);
            return this._getFallbackChurnPredictorStats();
        }
    }

    /**
     * Get churn predictions from backend
     */
    async getChurnPredictions(limit = 10) {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/ai-services/churn-predictor/predictions?limit=${limit}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.warn('Backend AI API unavailable, using fallback data:', error.message);
            return this._getFallbackChurnPredictions();
        }
    }

    /**
     * Get predictive analytics stats from backend
     */
    async getPredictiveAnalyticsStats() {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/ai-services/predictive-analytics/stats`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.warn('Backend AI API unavailable, using fallback data:', error.message);
            return this._getFallbackPredictiveAnalyticsStats();
        }
    }

    /**
     * Get security monitor stats from backend
     */
    async getSecurityMonitorStats() {
        try {
            const response = await fetch(`${this.baseURL}/api/mock/ai-services/security-monitor/stats`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.warn('Backend AI API unavailable, using fallback data:', error.message);
            return this._getFallbackSecurityMonitorStats();
        }
    }

    // Fallback data methods for when backend is unavailable
    _getFallbackContentOptimizerStats() {
        return {
            total_optimized: 1247,
            today_optimized: 23,
            avg_improvement: '+34%',
            status: 'active'
        };
    }

    _getFallbackRecentOptimizations() {
        return [{
            id: 1,
            content: 'Sample Content',
            improvement: '+25%',
            timestamp: '5 minutes ago',
            status: 'success',
            original_score: 68,
            optimized_score: 85
        }];
    }

    _getFallbackChurnPredictorStats() {
        return {
            users_analyzed: 892,
            high_risk_users: 47,
            retention_success: '78%',
            churn_rate: '12.3%',
            status: 'beta'
        };
    }

    _getFallbackChurnPredictions() {
        return [{
            user_id: 12345,
            user_name: 'demo_user',
            churn_probability: 0.75,
            risk_level: 'High',
            last_activity: '3 days ago',
            engagement_score: 0.45
        }];
    }

    _getFallbackPredictiveAnalyticsStats() {
        return {
            predictions_made: 15678,
            accuracy_rate: '87.3%',
            models_active: 12,
            status: 'operational'
        };
    }

    _getFallbackSecurityMonitorStats() {
        return {
            threats_detected: 156,
            threats_blocked: 147,
            security_score: 94.2,
            status: 'monitoring'
        };
    }
}

// Export singleton instance
export const aiServicesAPIService = new AIServicesAPIService();

// Backward compatibility exports for existing frontend code
export const contentOptimizerStats = aiServicesAPIService._getFallbackContentOptimizerStats();
export const churnPredictorStats = aiServicesAPIService._getFallbackChurnPredictorStats();
export const predictiveAnalyticsStats = aiServicesAPIService._getFallbackPredictiveAnalyticsStats();
export const securityMonitorStats = aiServicesAPIService._getFallbackSecurityMonitorStats();