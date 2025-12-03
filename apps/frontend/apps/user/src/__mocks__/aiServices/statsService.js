/**
 * AI Services Statistics Mock Data
 * Centralized mock data for AI services stats, moved from aiServicesAPI.js
 */

export const aiServicesStatsMock = {
    content_optimizer: {
        total_optimized: 1247,
        today_count: 23,
        avg_improvement: '+34%',
        status: 'active'
    },
    predictive_analytics: {
        accuracy: '94.2%',
        predictions: 156,
        trends: 8,
        status: 'active'
    },
    churn_predictor: {
        users_analyzed: 892,
        high_risk_users: 47,
        retention_success: '78%',
        status: 'beta'
    },
    security_monitor: {
        threats_detected: 12,
        security_score: '92.5%',
        monitoring_active: true,
        status: 'active'
    }
};

/**
 * Health Check Mock Data
 */
export const aiServicesHealthMock = {
    status: 'healthy',
    services: {
        content_optimizer: { status: 'active', uptime: '99.8%' },
        predictive_analytics: { status: 'active', uptime: '99.5%' },
        churn_predictor: { status: 'beta', uptime: '97.2%' },
        security_monitor: { status: 'active', uptime: '99.9%' }
    },
    last_updated: new Date().toISOString()
};

/**
 * Service Capabilities Mock Data
 */
export const aiServicesCapabilitiesMock = {
    content_optimizer: {
        features: ['content_analysis', 'tone_optimization', 'engagement_prediction'],
        max_content_length: 5000,
        supported_languages: ['en', 'es', 'fr', 'de'],
        response_time_avg: '250ms'
    },
    predictive_analytics: {
        features: ['trend_forecasting', 'engagement_prediction', 'growth_analysis'],
        prediction_accuracy: 0.942,
        max_timeframe: '90d',
        supported_metrics: ['views', 'engagement', 'growth']
    },
    churn_predictor: {
        features: ['risk_assessment', 'retention_strategies', 'behavior_analysis'],
        accuracy: 0.834,
        risk_categories: ['low', 'medium', 'high', 'critical'],
        update_frequency: 'hourly'
    },
    security_monitor: {
        features: ['threat_detection', 'content_scanning', 'risk_assessment'],
        detection_types: ['spam', 'malicious_content', 'policy_violation'],
        monitoring_coverage: '24/7',
        response_time: '< 100ms'
    }
};

/**
 * Error Scenarios Mock Data (for testing error handling)
 */
export const aiServicesErrorsMock = {
    service_unavailable: {
        error: 'Service temporarily unavailable',
        code: 503,
        retry_after: 30
    },
    rate_limit_exceeded: {
        error: 'Rate limit exceeded',
        code: 429,
        reset_time: Date.now() + 3600000 // 1 hour from now
    },
    invalid_request: {
        error: 'Invalid request parameters',
        code: 400,
        details: 'Missing required field: content'
    },
    authentication_failed: {
        error: 'Authentication failed',
        code: 401,
        message: 'Invalid or expired API key'
    }
};

export default {
    aiServicesStatsMock,
    aiServicesHealthMock,
    aiServicesCapabilitiesMock,
    aiServicesErrorsMock
};
