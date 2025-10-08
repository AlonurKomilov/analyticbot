/**
 * Mock System Configuration
 * Centralized configuration for mock behavior and data source control
 */

// Environment-based configuration
export const MOCK_CONFIG = {
    // Data source preferences - Always use real API
    // Mock data is now controlled by backend demo user authentication
    USE_REAL_API: true,

    // API configuration
    API_TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT) || 5000,
    API_RETRY_COUNT: parseInt(import.meta.env.VITE_API_RETRY_COUNT) || 3,
    API_RETRY_DELAY: parseInt(import.meta.env.VITE_API_RETRY_DELAY) || 1000,

    // Mock behavior configuration - Disabled auto-fallbacks
    MOCK_DELAY: parseInt(import.meta.env.VITE_MOCK_API_DELAY) || 300,
    FALLBACK_TO_MOCK: false, // Disabled - no auto-fallback to frontend mocks
    ENABLE_MOCK_SWITCHING: false, // Disabled - mock data controlled by backend auth

    // Development features
    ENABLE_CONSOLE_LOGS: import.meta.env.DEV && import.meta.env.VITE_ENABLE_MOCK_LOGS !== 'false',
    ENABLE_PERFORMANCE_LOGS: import.meta.env.DEV && import.meta.env.VITE_ENABLE_PERF_LOGS === 'true',

    // Mock data quality settings
    REALISTIC_DELAYS: import.meta.env.VITE_REALISTIC_DELAYS !== 'false',
    MOCK_ERROR_RATE: parseFloat(import.meta.env.VITE_MOCK_ERROR_RATE) || 0,

    // Cache settings
    ENABLE_MOCK_CACHE: import.meta.env.VITE_ENABLE_MOCK_CACHE !== 'false',
    MOCK_CACHE_TTL: parseInt(import.meta.env.VITE_MOCK_CACHE_TTL) || 300000, // 5 minutes
};

// API endpoints configuration
export const API_CONFIG = {
    BASE_URL: import.meta.env.VITE_API_BASE_URL ||
              import.meta.env.VITE_API_URL ||
              'https://84dp9jc9-11400.euw.devtunnels.ms',

    ENDPOINTS: {
        HEALTH: '/health',
        INITIAL_DATA: '/initial-data',
        ANALYTICS_OVERVIEW: '/api/analytics/overview',
        ANALYTICS_GROWTH: '/api/analytics/growth',
        ANALYTICS_REACH: '/api/analytics/reach',
        ANALYTICS_TOP_POSTS: '/api/analytics/top-posts',
        POST_DYNAMICS: '/api/analytics/v2/post-dynamics',
        BEST_TIME: '/api/analytics/v2/best-time',
        ENGAGEMENT_METRICS: '/api/analytics/v2/engagement-metrics',
    }
};

// Mock data configuration
export const MOCK_DATA_CONFIG = {
    // Analytics data settings
    ANALYTICS: {
        TOTAL_VIEWS: 35340,
        TOTAL_POSTS: 156,
        AVG_ENGAGEMENT: 5.8,
        ACTIVE_USERS: 2847,
        GROWTH_RATE: 12.5,

        // Time-based data
        PEAK_HOURS: [18, 19, 20], // 6-8 PM
        ACTIVE_DAYS: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],

        // Geographic distribution
        TOP_COUNTRIES: ['US', 'UK', 'DE', 'FR', 'IT'],

        // Content categories
        CATEGORIES: ['tech', 'business', 'marketing', 'analytics', 'ai'],
    },

    // Channel data settings
    CHANNELS: {
        DEFAULT_COUNT: 3,
        MEMBER_COUNT_RANGE: [5000, 25000],
        ENGAGEMENT_RATE_RANGE: [3.5, 8.2],
        ACTIVITY_PROBABILITY: 0.85,
    },

    // Posts data settings
    POSTS: {
        DEFAULT_COUNT: 20,
        VIEW_COUNT_RANGE: [1000, 15000],
        REACTION_RATE_RANGE: [2, 8], // percentage of views
        FORWARD_RATE_RANGE: [0.5, 3], // percentage of views
        TIME_SPREAD_DAYS: 30,
    },

    // User data settings
    USER: {
        PLAN_FEATURES: ['analytics', 'scheduling', 'media_upload', 'best_time_recommendations'],
        MAX_CHANNELS: 10,
        MAX_SCHEDULED_POSTS: 100,
    }
};

// Logging configuration
export const LOG_CONFIG = {
    ENABLED: MOCK_CONFIG.ENABLE_CONSOLE_LOGS,

    PREFIXES: {
        DATA_SOURCE: '🔄',
        API_CALL: '📡',
        MOCK_DATA: '📊',
        ERROR: '❌',
        SUCCESS: '✅',
        WARNING: '⚠️',
        INFO: 'ℹ️',
    },

    LEVELS: {
        ERROR: 0,
        WARN: 1,
        INFO: 2,
        DEBUG: 3,
    },

    CURRENT_LEVEL: import.meta.env.DEV ? 3 : 1,
};

// Utility functions for configuration
export const configUtils = {
    // Check if feature is enabled
    isFeatureEnabled(feature) {
        const envVar = `VITE_ENABLE_${feature.toUpperCase()}`;
        return import.meta.env[envVar] !== 'false';
    },

    // Get timeout for operation type
    getTimeout(operation) {
        const timeouts = {
            api_health: 3000,
            api_data: MOCK_CONFIG.API_TIMEOUT,
            mock_delay: MOCK_CONFIG.MOCK_DELAY,
        };
        return timeouts[operation] || MOCK_CONFIG.API_TIMEOUT;
    },

    // Get retry configuration
    getRetryConfig() {
        return {
            count: MOCK_CONFIG.API_RETRY_COUNT,
            delay: MOCK_CONFIG.API_RETRY_DELAY,
        };
    },

    // Check if should log
    shouldLog(level) {
        const levels = LOG_CONFIG.LEVELS;
        return LOG_CONFIG.ENABLED && levels[level.toUpperCase()] <= LOG_CONFIG.CURRENT_LEVEL;
    },

    // Create logger function
    createLogger(prefix) {
        return {
            error: (msg, ...args) => configUtils.shouldLog('error') &&
                   console.error(`${LOG_CONFIG.PREFIXES.ERROR} ${prefix}:`, msg, ...args),
            warn: (msg, ...args) => configUtils.shouldLog('warn') &&
                  console.warn(`${LOG_CONFIG.PREFIXES.WARNING} ${prefix}:`, msg, ...args),
            info: (msg, ...args) => configUtils.shouldLog('info') &&
                  console.log(`${LOG_CONFIG.PREFIXES.INFO} ${prefix}:`, msg, ...args),
            debug: (msg, ...args) => configUtils.shouldLog('debug') &&
                   console.log(`${LOG_CONFIG.PREFIXES.INFO} ${prefix}:`, msg, ...args),
        };
    }
};

// Performance monitoring
export const PERFORMANCE_CONFIG = {
    ENABLED: MOCK_CONFIG.ENABLE_PERFORMANCE_LOGS,

    // Track these operations
    TRACK_OPERATIONS: [
        'data_source_switch',
        'api_call',
        'mock_data_generation',
        'component_render',
    ],

    // Performance thresholds (ms)
    THRESHOLDS: {
        data_source_switch: 100,
        api_call: 2000,
        mock_data_generation: 50,
        component_render: 16, // 60fps
    }
};

// Export environment check
export const ENV_INFO = {
    IS_DEVELOPMENT: import.meta.env.DEV,
    IS_PRODUCTION: import.meta.env.PROD,
    MODE: import.meta.env.MODE,
    BASE_URL: import.meta.env.BASE_URL,
};

// Validation functions
export const validateConfig = () => {
    const errors = [];

    if (MOCK_CONFIG.API_TIMEOUT < 1000) {
        errors.push('API_TIMEOUT should be at least 1000ms');
    }

    if (MOCK_CONFIG.MOCK_DELAY < 0) {
        errors.push('MOCK_DELAY should be non-negative');
    }

    if (!API_CONFIG.BASE_URL) {
        errors.push('API BASE_URL is required');
    }

    return errors;
};

// Initialize configuration validation in development
if (import.meta.env.DEV) {
    const configErrors = validateConfig();
    if (configErrors.length > 0) {
        console.warn('🔧 Mock Configuration Issues:', configErrors);
    }
}
