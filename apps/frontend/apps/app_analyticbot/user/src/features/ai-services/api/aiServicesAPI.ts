/**
 * AI Services API Client
 * Provides methods to interact with AI-powered services including
 * content optimization, churn prediction, and security monitoring.
 */

import { apiClient } from '@/api/client';
import { apiLogger } from '@/utils/logger';

// Mock data removed - should only be loaded dynamically in demo mode
// See ContentOptimizerService.tsx for proper dynamic import pattern

const AI_SERVICES_BASE = '/ai/services';

// =====================================
// Types
// =====================================

interface ContentAnalysisOptions {
    channelId?: string;
    targetAudience?: string;
}

interface ChurnPredictionOptions {
    channelId?: string;
    includeRecommendations?: boolean;
}

interface SecurityAnalysisOptions {
    userId?: string;
    channelId?: string;
}

interface ForecastOptions {
    modelType?: string;
    timeframe?: string;
    confidenceThreshold?: number;
}

interface ServiceStats {
    content_optimizer?: {
        total_optimized?: number;
        today_count?: number;
        avg_improvement?: string;
    };
    predictive_analytics?: {
        accuracy?: string;
        predictions?: number;
    };
    churn_predictor?: {
        users_analyzed?: number;
        high_risk_users?: number;
    };
    security_monitor?: {
        security_score?: string;
        threats_detected?: number;
    };
    [key: string]: any;
}

interface FormattedServiceStats {
    totalOptimized: number;
    todayCount: number;
    avgImprovement: string;
    accuracy: string;
    predictions: number;
    usersAnalyzed: number;
    highRiskUsers: number;
    securityScore: string;
    threatsDetected: number;
}

interface RiskLevel {
    level: 'High' | 'Medium' | 'Low';
    color: 'error' | 'warning' | 'success';
}

interface ThreatLevel {
    color: 'success' | 'warning' | 'error';
    severity: string;
}

// =====================================
// Content Optimizer Service
// =====================================

export const ContentOptimizerAPI = {
    async analyzeContent(content: string, options: ContentAnalysisOptions = {}): Promise<any> {
        try {
            const response: any = await apiClient.post(`${AI_SERVICES_BASE}/content-optimizer/analyze`, {
                content,
                channel_id: options.channelId || 'demo',
                target_audience: options.targetAudience || 'general'
            });
            return response.data;
        } catch (error: any) {
            apiLogger.error('Content optimization failed', { error });
            throw new Error(error.response?.data?.detail || 'Content optimization failed');
        }
    },

    async getStats(): Promise<any> {
        try {
            const response: any = await apiClient.get(`${AI_SERVICES_BASE}/content-optimizer/stats`);
            return response.data;
        } catch (error) {
            apiLogger.error('Failed to fetch content optimizer stats', { error });
            throw new Error('Failed to fetch stats');
        }
    }
};

// =====================================
// Churn Predictor Service
// =====================================

export const ChurnPredictorAPI = {
    async predictChurn(userId: string, options: ChurnPredictionOptions = {}): Promise<any> {
        try {
            const response: any = await apiClient.post(`${AI_SERVICES_BASE}/churn-predictor/analyze`, {
                user_id: userId,
                channel_id: options.channelId || 'demo',
                include_recommendations: options.includeRecommendations !== false
            });
            return response.data;
        } catch (error: any) {
            apiLogger.error('Churn prediction failed', { error });
            throw new Error(error.response?.data?.detail || 'Churn prediction failed');
        }
    },

    async getStats(): Promise<any> {
        try {
            const response: any = await apiClient.get(`${AI_SERVICES_BASE}/churn-predictor/stats`);
            return response.data;
        } catch (error) {
            apiLogger.error('Failed to fetch churn predictor stats', { error });
            throw new Error('Failed to fetch stats');
        }
    }
};

// =====================================
// Security Monitor Service
// =====================================

export const SecurityMonitorAPI = {
    async analyzeContent(content: string, options: SecurityAnalysisOptions = {}): Promise<any> {
        try {
            const response: any = await apiClient.post(`${AI_SERVICES_BASE}/security-monitor/analyze`, {
                content,
                user_id: options.userId,
                channel_id: options.channelId || 'demo'
            });
            return response.data;
        } catch (error: any) {
            apiLogger.error('Security analysis failed', { error });
            throw new Error(error.response?.data?.detail || 'Security analysis failed');
        }
    },

    async getStats(): Promise<any> {
        try {
            const response: any = await apiClient.get(`${AI_SERVICES_BASE}/security-monitor/stats`);
            return response.data;
        } catch (error) {
            apiLogger.error('Failed to fetch security monitor stats', { error });
            throw new Error('Failed to fetch stats');
        }
    }
};

// =====================================
// Predictive Analytics Service
// ✅ UPDATED (Oct 22, 2025): Now uses PredictiveOrchestratorService endpoints
// =====================================

export const PredictiveAnalyticsAPI = {
    /**
     * Generate predictive forecasts using PredictiveOrchestratorService
     * Uses /insights/predictive/forecast endpoint with orchestrator
     */
    async generateForecast(channelId: string, options: ForecastOptions = {}): Promise<any> {
        try {
            const response: any = await apiClient.post('/analytics/predictive/forecast', {
                channel_ids: [parseInt(channelId)],
                prediction_type: options.modelType || 'engagement',
                forecast_days: options.timeframe === '7d' ? 7 : options.timeframe === '30d' ? 30 : 7,
                confidence_level: options.confidenceThreshold || 0.95
            });
            return response.data || response;
        } catch (error: any) {
            apiLogger.error('Forecast generation failed', { error });
            throw new Error(error.response?.data?.detail || 'Forecast generation failed');
        }
    },

    /**
     * Get contextual intelligence insights using PredictiveOrchestratorService
     * Uses /insights/predictive/intelligence/contextual endpoint
     */
    async getInsights(channelId: string): Promise<any> {
        try {
            const response: any = await apiClient.post('/analytics/predictive/intelligence/contextual', {
                channel_id: parseInt(channelId),
                intelligence_context: ['temporal', 'environmental', 'behavioral'],
                analysis_period_days: 30,
                prediction_horizon_days: 7,
                include_explanations: true
            });
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to fetch insights', { error });
            throw new Error('Failed to fetch insights');
        }
    },

    /**
     * Get temporal intelligence patterns
     * Uses /insights/predictive/intelligence/temporal endpoint
     */
    async getTemporalPatterns(channelId: string, days: number = 90): Promise<any> {
        try {
            const response: any = await apiClient.get(
                `/analytics/predictive/intelligence/temporal/${channelId}?analysis_depth_days=${days}`
            );
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to fetch temporal patterns', { error });
            throw new Error('Failed to fetch temporal patterns');
        }
    },

    /**
     * Get cross-channel intelligence
     * Uses /insights/predictive/intelligence/cross-channel endpoint
     */
    async getCrossChannelIntelligence(channelIds: string[], options: any = {}): Promise<any> {
        try {
            const response: any = await apiClient.post('/analytics/predictive/intelligence/cross-channel', {
                channel_ids: channelIds.map(id => parseInt(id)),
                correlation_depth_days: options.correlationDepth || 60,
                include_competitive_intelligence: options.includeCompetitive !== false
            });
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to fetch cross-channel intelligence', { error });
            throw new Error('Failed to fetch cross-channel intelligence');
        }
    },

    /**
     * Health check for predictive orchestrator
     * Uses /insights/predictive/intelligence/health endpoint
     */
    async healthCheck(): Promise<any> {
        try {
            const response: any = await apiClient.get('/analytics/predictive/intelligence/health');
            return response.data || response;
        } catch (error) {
            apiLogger.error('Predictive service health check failed', { error });
            throw new Error('Health check failed');
        }
    }
};

// =====================================
// Alerts Orchestrator Service
// ✅ NEW (Oct 22, 2025): AlertsOrchestratorService endpoints
// =====================================

export const AlertsAPI = {
    /**
     * Get live monitoring metrics for a channel
     * Uses /analytics/alerts/monitor/live endpoint
     */
    async getLiveMonitoring(channelId: string, hours: number = 6): Promise<any> {
        try {
            const response: any = await apiClient.get(
                `/analytics/alerts/monitor/live/${channelId}?hours=${hours}`
            );
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to fetch live monitoring', { error });
            throw new Error('Failed to fetch live monitoring');
        }
    },

    /**
     * Check channel alerts using orchestrated workflow
     * Uses /analytics/alerts/check endpoint
     */
    async checkAlerts(channelId: string, analysisType: string = 'comprehensive'): Promise<any> {
        try {
            const response: any = await apiClient.post(
                `/analytics/alerts/check/${channelId}?analysis_type=${analysisType}`,
                {}
            );
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to check alerts', { error });
            throw new Error('Failed to check alerts');
        }
    },

    /**
     * Monitor channel with competitive intelligence
     * Uses /analytics/alerts/competitive/monitor endpoint
     */
    async competitiveMonitoring(channelId: string, options: any = {}): Promise<any> {
        try {
            const response: any = await apiClient.post('/analytics/alerts/competitive/monitor', {
                channel_id: parseInt(channelId),
                monitoring_period_days: options.days || 7,
                include_competitor_analysis: options.includeCompetitors !== false,
                alert_thresholds: options.thresholds
            });
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to fetch competitive monitoring', { error });
            throw new Error('Failed to fetch competitive monitoring');
        }
    },

    /**
     * Execute comprehensive alerts workflow
     * Uses /analytics/alerts/workflow/comprehensive endpoint
     */
    async comprehensiveWorkflow(channelId: string, includeCompetitive: boolean = true): Promise<any> {
        try {
            const response: any = await apiClient.post(
                `/analytics/alerts/workflow/comprehensive/${channelId}?include_competitive=${includeCompetitive}`,
                {}
            );
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to execute comprehensive workflow', { error });
            throw new Error('Failed to execute comprehensive workflow');
        }
    },

    /**
     * Get alert rules for a channel (legacy endpoint)
     * Uses /analytics/alerts/rules endpoint
     * Note: This endpoint is not fully implemented on backend yet
     */
    async getAlertRules(channelId: string): Promise<any> {
        try {
            const response: any = await apiClient.get(`/analytics/alerts/rules/${channelId}`);
            return response.data || response;
        } catch (error) {
            // Silently handle - endpoint not yet implemented, return empty structure
            // This is expected behavior until get_channel_rules() is added to backend
            return {
                channel_id: channelId,
                rules: [],
                total_rules: 0,
                active_rules: 0
            };
        }
    },

    /**
     * Get smart personalized alert rules for a channel
     * Uses /analytics/alerts/rules/smart/{channel_id}
     * Analyzes channel and returns intelligent, size-appropriate rules
     */
    async getSmartAlertRules(channelId: string): Promise<any> {
        try {
            const response: any = await apiClient.get(`/analytics/alerts/rules/smart/${channelId}`);
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to fetch smart alert rules', { error });
            throw new Error('Failed to fetch smart alert rules');
        }
    },

    /**
     * Create a new alert rule for a channel
     * Uses POST /analytics/alerts/rules/{channel_id}
     */
    async createAlertRule(channelId: string, rule: {
        rule_name: string;
        metric_type: string;
        threshold_value: number;
        comparison: string;
        enabled: boolean;
        notification_channels?: string[];
    }): Promise<any> {
        try {
            const response: any = await apiClient.post(`/analytics/alerts/rules/${channelId}`, rule);
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to create alert rule', { error });
            throw new Error('Failed to create alert rule');
        }
    },

    /**
     * Update an alert rule (toggle enabled/disabled)
     * Uses PUT /analytics/alerts/rules/{channel_id}/{rule_id}
     */
    async updateAlertRule(channelId: string, ruleId: string, enabled: boolean): Promise<any> {
        try {
            const response: any = await apiClient.put(
                `/analytics/alerts/rules/${channelId}/${ruleId}?enabled=${enabled}`,
                {}
            );
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to update alert rule', { error });
            throw new Error('Failed to update alert rule');
        }
    },

    /**
     * Get alert history for a channel (legacy endpoint)
     * Uses /analytics/alerts/history endpoint
     */
    async getAlertHistory(channelId: string, days: number = 30): Promise<any> {
        try {
            const response: any = await apiClient.get(
                `/analytics/alerts/history/${channelId}?days=${days}`
            );
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to fetch alert history', { error });
            throw new Error('Failed to fetch alert history');
        }
    },

    /**
     * Health check for alerts orchestrator
     * Uses /analytics/alerts/health endpoint
     */
    async healthCheck(): Promise<any> {
        try {
            const response: any = await apiClient.get('/analytics/alerts/health');
            return response.data || response;
        } catch (error) {
            apiLogger.error('Alerts service health check failed', { error });
            throw new Error('Health check failed');
        }
    },

    /**
     * Get alerts service statistics
     * Uses /analytics/alerts/stats endpoint
     */
    async getStats(): Promise<any> {
        try {
            const response: any = await apiClient.get('/analytics/alerts/stats');
            return response.data || response;
        } catch (error) {
            apiLogger.error('Failed to fetch alerts stats', { error });
            throw new Error('Failed to fetch stats');
        }
    }
};

// =====================================
// AI Services General
// =====================================

export const AIServicesAPI = {
    async healthCheck(): Promise<any> {
        try {
            const response: any = await apiClient.get(`${AI_SERVICES_BASE}/health`);
            return response.data;
        } catch (error) {
            apiLogger.error('AI services health check failed', { error });
            throw new Error('Health check failed');
        }
    },

    async getAllStats(): Promise<any> {
        try {
            const response: any = await apiClient.get(`${AI_SERVICES_BASE}/stats`);
            return response.data;
        } catch (error) {
            apiLogger.error('Failed to fetch AI services stats', { error });
            // NEVER fallback to mock - throw error so UI can handle properly
            throw error;
        }
    }
};

// =====================================
// Utility Functions
// =====================================

export const AIServiceUtils = {
    formatServiceStats(stats: ServiceStats): FormattedServiceStats {
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

    getServiceStatus(serviceName: string, stats: ServiceStats): string {
        const serviceData = stats[serviceName.toLowerCase().replace(/\s+/g, '_')];
        return serviceData?.status || 'inactive';
    },

    formatChurnRiskLevel(probability: number): RiskLevel {
        if (probability >= 0.7) return { level: 'High', color: 'error' };
        if (probability >= 0.4) return { level: 'Medium', color: 'warning' };
        return { level: 'Low', color: 'success' };
    },

    formatSecurityThreatLevel(threatLevel: string): ThreatLevel {
        const levels: Record<string, ThreatLevel> = {
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
    AlertsAPI,
    AIServicesAPI,
    AIServiceUtils
};
