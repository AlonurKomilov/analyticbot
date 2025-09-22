/**
 * AI Services API Client
 * Provides methods to interact with AI-powered services including
 * content optimization, churn prediction, and security monitoring.
 */

import { apiClient } from './apiClient';
import { aiServicesStatsMock } from '../__mocks__/aiServices/statsService.js';

const AI_SERVICES_BASE = '/ai-services';

// =====================================
// Content Optimizer Service
// =====================================

export const ContentOptimizerAPI = {
    async analyzeContent(content, options = {}) {
        try {
            const response = await apiClient.post(`${AI_SERVICES_BASE}/content-optimizer/analyze`, {
                content,
                channel_id: options.channelId || 'demo',
                target_audience: options.targetAudience || 'general'
            });
            return response.data;
        } catch (error) {
            console.error('Content optimization failed:', error);
            throw new Error(error.response?.data?.detail || 'Content optimization failed');
        }
    },

    async getStats() {
        try {
            const response = await apiClient.get(`${AI_SERVICES_BASE}/content-optimizer/stats`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch content optimizer stats:', error);
            throw new Error('Failed to fetch stats');
        }
    }
};

// =====================================
// Churn Predictor Service
// =====================================

export const ChurnPredictorAPI = {
    async predictChurn(userId, options = {}) {
        try {
            const response = await apiClient.post(`${AI_SERVICES_BASE}/churn-predictor/analyze`, {
                user_id: userId,
                channel_id: options.channelId || 'demo',
                include_recommendations: options.includeRecommendations !== false
            });
            return response.data;
        } catch (error) {
            console.error('Churn prediction failed:', error);
            throw new Error(error.response?.data?.detail || 'Churn prediction failed');
        }
    },

    async getStats() {
        try {
            const response = await apiClient.get(`${AI_SERVICES_BASE}/churn-predictor/stats`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch churn predictor stats:', error);
            throw new Error('Failed to fetch stats');
        }
    }
};

// =====================================
// Security Monitor Service
// =====================================

export const SecurityMonitorAPI = {
    async analyzeContent(content, options = {}) {
        try {
            const response = await apiClient.post(`${AI_SERVICES_BASE}/security-monitor/analyze`, {
                content,
                user_id: options.userId,
                channel_id: options.channelId || 'demo'
            });
            return response.data;
        } catch (error) {
            console.error('Security analysis failed:', error);
            throw new Error(error.response?.data?.detail || 'Security analysis failed');
        }
    },

    async getStats() {
        try {
            const response = await apiClient.get(`${AI_SERVICES_BASE}/security-monitor/stats`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch security monitor stats:', error);
            throw new Error('Failed to fetch stats');
        }
    }
};

// =====================================
// Predictive Analytics Service
// =====================================

export const PredictiveAnalyticsAPI = {
    async generateForecast(channelId, options = {}) {
        try {
            const response = await apiClient.post('/analytics/predictions/forecast', {
                channel_id: channelId,
                model_type: options.modelType || 'engagement',
                timeframe: options.timeframe || '7d',
                confidence_threshold: options.confidenceThreshold || 0.8
            });
            return response.data;
        } catch (error) {
            console.error('Forecast generation failed:', error);
            throw new Error(error.response?.data?.detail || 'Forecast generation failed');
        }
    },

    async getInsights(channelId) {
        try {
            const response = await apiClient.get(`/analytics/insights/${channelId}`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch insights:', error);
            throw new Error('Failed to fetch insights');
        }
    }
};

// =====================================
// AI Services General
// =====================================

export const AIServicesAPI = {
    async healthCheck() {
        try {
            const response = await apiClient.get(`${AI_SERVICES_BASE}/health`);
            return response.data;
        } catch (error) {
            console.error('AI services health check failed:', error);
            throw new Error('Health check failed');
        }
    },

    async getAllStats() {
        try {
            const response = await apiClient.get(`${AI_SERVICES_BASE}/stats`);
            return response.data;
        } catch (error) {
            console.error('Failed to fetch AI services stats:', error);
            // Return centralized mock data as fallback
            return aiServicesStatsMock;
        }
    }
};

// =====================================
// Utility Functions
// =====================================

export const AIServiceUtils = {
    formatServiceStats(stats) {
        return {
            totalOptimized: stats.content_optimizer?.total_optimized || 0,
            todayCount: stats.content_optimizer?.today_count || 0,
            avgImprovement: stats.content_optimizer?.avg_improvement || '+0%',
            accuracy: stats.predictive_analytics?.accuracy || '0%',
            predictions: stats.predictive_analytics?.predictions || 0,
            usersAnalyzed: stats.churn_predictor?.users_analyzed || 0,
            highRiskUsers: stats.churn_predictor?.high_risk_users || 0,
            securityScore: stats.security_monitor?.security_score || '0%',
            threatsDetected: stats.security_monitor?.threats_detected || 0
        };
    },

    getServiceStatus(serviceName, stats) {
        const serviceData = stats[serviceName.toLowerCase().replace(/\s+/g, '_')];
        return serviceData?.status || 'inactive';
    },

    formatChurnRiskLevel(probability) {
        if (probability >= 0.7) return { level: 'High', color: 'error' };
        if (probability >= 0.4) return { level: 'Medium', color: 'warning' };
        return { level: 'Low', color: 'success' };
    },

    formatSecurityThreatLevel(threatLevel) {
        const levels = {
            low: { color: 'success', severity: 'Low Risk' },
            medium: { color: 'warning', severity: 'Medium Risk' },
            high: { color: 'error', severity: 'High Risk' },
            critical: { color: 'error', severity: 'Critical' }
        };
        return levels[threatLevel] || levels.low;
    }
};

export default {
    ContentOptimizerAPI,
    ChurnPredictorAPI,
    SecurityMonitorAPI,
    PredictiveAnalyticsAPI,
    AIServicesAPI,
    AIServiceUtils
};