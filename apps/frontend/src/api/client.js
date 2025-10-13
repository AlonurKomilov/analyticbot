/**
 * Unified API Client
 * Consolidates all API client functionality from:
 * - services/apiClient.js (axios-based, interceptors, file upload)
 * - utils/apiClient.js (fetch-based, retry logic, TWA auth, data source routing)
 * - services/dataService.js (adapter pattern, analytics switching)
 *
 * Features:
 * - Multiple authentication strategies (JWT, TWA)
 * - Retry logic with exponential backoff
 * - Mock/real data source switching
 * - File upload capabilities
 * - Comprehensive error handling
 * - Axios-style method interface
 */

import { ErrorHandler } from '../utils/errorHandler.js';
import { dataSourceManager } from '../utils/dataSourceManager.js';
import { analyticsService } from '../services/analyticsService.js';
// Import analytics service

// Configuration constants
const DEFAULT_CONFIG = {
    baseURL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://b2qz1m0n-11400.euw.devtunnels.ms',
    timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 60000, // Use env var or default 60 seconds (increased for devtunnel)
    maxRetries: 3,
    retryDelay: 1000, // 1 second
    retryMultiplier: 2
};

/**
 * Authentication strategies
 */
class AuthStrategies {
    static JWT = 'jwt';
    static TWA = 'twa';
    static NONE = 'none';
}

/**
 * Unified API Client Class
 */
class UnifiedApiClient {
    constructor(config = {}) {
        this.config = { ...DEFAULT_CONFIG, ...config };
        this.authStrategy = AuthStrategies.JWT; // Default to JWT
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };

        // Debug logging with env var inspection
        console.log('🔧 Unified API Client Configuration:', {
            baseURL: this.config.baseURL,
            timeout: this.config.timeout,
            maxRetries: this.config.maxRetries,
            authStrategy: this.authStrategy,
            envTimeout: import.meta.env.VITE_API_TIMEOUT,
            envBaseURL: import.meta.env.VITE_API_BASE_URL
        });
    }

    /**
     * Set authentication strategy
     */
    setAuthStrategy(strategy) {
        if (!Object.values(AuthStrategies).includes(strategy)) {
            throw new Error(`Invalid auth strategy: ${strategy}`);
        }
        this.authStrategy = strategy;
        console.log(`🔐 Auth strategy set to: ${strategy}`);
    }

    /**
     * Get authentication headers based on current strategy
     */
    getAuthHeaders() {
        const headers = { ...this.defaultHeaders };

        switch (this.authStrategy) {
            case AuthStrategies.JWT:
                // Check all possible token storage keys
                const token = localStorage.getItem('access_token') ||
                             localStorage.getItem('token') ||
                             localStorage.getItem('accessToken') ||
                             sessionStorage.getItem('access_token');
                if (token) {
                    headers['Authorization'] = `Bearer ${token}`;
                }
                break;

            case AuthStrategies.TWA:
                const twaInitData = window.Telegram?.WebApp?.initData || '';
                if (twaInitData) {
                    headers['Authorization'] = `TWA ${twaInitData}`;
                }
                break;

            case AuthStrategies.NONE:
                // No authentication headers
                break;
        }

        return headers;
    }

    /**
     * Check if request should use data service routing
     */
    isDataServiceRoute(url) {
        const dataServiceRoutes = [
            '/api/analytics/',
            '/api/v2/analytics/',
            '/system/initial-data',
            '/initial-data',  // Keep for backwards compatibility
            '/health'
        ];
        return dataServiceRoutes.some(route => url.includes(route));
    }

    /**
     * Route request through data service if applicable
     * NOTE: Data service factory not implemented yet - all requests go directly to API
     */
    async routeThroughDataService(method, url, data = null) {
        // For now, always return null to use direct API calls
        // This will be implemented later when dataServiceFactory is created
        return null;
    }

    /**
     * Extract channel ID from URL
     */
    extractChannelId(url) {
        const match = url.match(/channels\/([^\/\?]+)/);
        return match ? match[1] : null;
    }

    /**
     * Check if error is retryable
     */
    isRetryableError(error) {
        if (!error.response) return true; // Network errors are retryable
        const status = error.response?.status;
        return status === 408 || status === 429 || status >= 500;
    }

    /**
     * Sleep utility for retry delays
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Core request method with retry logic and data source routing
     */
    async request(endpoint, options = {}, attempt = 1) {
        // Check if this request should go through the data service
        if (this.isDataServiceRoute(endpoint)) {
            try {
                const dataServiceResult = await this.routeThroughDataService(
                    options.method || 'GET',
                    endpoint,
                    options.body ? JSON.parse(options.body) : null
                );
                if (dataServiceResult !== null) {
                    return dataServiceResult;
                }
            } catch (error) {
                console.warn('Data service routing failed, falling back to direct API:', error);
                // Continue with direct API call as fallback
            }
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            console.warn(`⏱️ Request timeout after ${this.config.timeout}ms for ${endpoint}`);
            controller.abort();
        }, this.config.timeout);

        try {
            // Construct full URL
            const url = this.config.baseURL ? `${this.config.baseURL}${endpoint}` : endpoint;

            if (import.meta.env.DEV) {
                console.log(`🌐 API Request: ${options.method || 'GET'} ${url} (timeout: ${this.config.timeout}ms)`);
            }

            // Prepare request configuration
            const requestConfig = {
                method: options.method || 'GET',
                headers: {
                    ...this.getAuthHeaders(),
                    ...options.headers
                },
                signal: controller.signal,
                ...options
            };

            // Add body for non-GET requests
            if (options.body && requestConfig.method !== 'GET') {
                requestConfig.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
            }

            const response = await fetch(url, requestConfig);
            clearTimeout(timeoutId);

            // Handle response
            let responseData;
            const contentType = response.headers.get('content-type');

            if (contentType && contentType.includes('application/json')) {
                try {
                    responseData = await response.json();
                } catch (parseError) {
                    const error = new Error(`Invalid JSON response: ${parseError.message}`);
                    error.response = { status: response.status, statusText: response.statusText };
                    throw error;
                }
            } else {
                const textContent = await response.text();
                if (!response.ok) {
                    const error = new Error(`API returned non-JSON response: ${response.status} ${response.statusText}`);
                    error.response = {
                        status: response.status,
                        statusText: response.statusText,
                        data: textContent.substring(0, 200)
                    };
                    throw error;
                }
                responseData = { data: textContent };
            }

            if (!response.ok) {
                const error = new Error(responseData.detail || responseData.message || 'API request failed');
                error.response = {
                    status: response.status,
                    statusText: response.statusText,
                    data: responseData
                };
                throw error;
            }

            return responseData;

        } catch (error) {
            clearTimeout(timeoutId);

            // Handle timeout
            if (error.name === 'AbortError') {
                const timeoutError = new Error('Request timeout');
                timeoutError.response = { status: 408 };
                throw timeoutError;
            }

            // Handle connection errors
            if (error.message.includes('ERR_CONNECTION_REFUSED') ||
                error.message.includes('Failed to fetch') ||
                error.message.includes('Network request failed')) {

                if (import.meta.env.DEV) {
                    console.warn('API connection failed - consider using demo mode');
                }

                const connectionError = new Error('API is currently unavailable');
                connectionError.response = { status: 503 };
                throw connectionError;
            }

            // Retry logic
            if (this.isRetryableError(error) && attempt < this.config.maxRetries) {
                console.warn(`API request failed (attempt ${attempt}/${this.config.maxRetries}), retrying...`, {
                    endpoint,
                    error: error.message
                });

                const delay = this.config.retryDelay * Math.pow(this.config.retryMultiplier, attempt - 1);
                await this.sleep(delay);
                return this.request(endpoint, options, attempt + 1);
            }

            // Final error handling
            console.error('API request failed after all retries:', error);
            throw error;
        }
    }

    /**
     * Axios-style HTTP methods
     */
    async get(url, config = {}) {
        return this.request(url, { method: 'GET', ...config });
    }

    async post(url, data = null, config = {}) {
        return this.request(url, {
            method: 'POST',
            body: data,
            ...config
        });
    }

    async put(url, data = null, config = {}) {
        return this.request(url, {
            method: 'PUT',
            body: data,
            ...config
        });
    }

    async patch(url, data = null, config = {}) {
        return this.request(url, {
            method: 'PATCH',
            body: data,
            ...config
        });
    }

    async delete(url, config = {}) {
        return this.request(url, { method: 'DELETE', ...config });
    }

    /**
     * File upload method (consolidated from services/apiClient.js)
     */
    async uploadFile(url, file, onProgress = null, config = {}) {
        const formData = new FormData();
        formData.append('file', file);

        const uploadConfig = {
            method: 'POST',
            body: formData,
            headers: {
                // Don't set Content-Type for FormData - browser will set it with boundary
                ...this.getAuthHeaders(),
                ...config.headers
            }
        };

        // Remove Content-Type from default headers for file upload
        delete uploadConfig.headers['Content-Type'];

        return this.request(url, uploadConfig);
    }

    /**
     * Direct file upload method (from utils/apiClient.js)
     * Supports channel-specific uploads with progress tracking
     */
    async uploadFileDirect(file, channelId = null, onProgress = null) {
        const formData = new FormData();
        formData.append('file', file);

        // Add channel_id if provided (from utils version)
        if (channelId) {
            formData.append('channel_id', channelId.toString());
        }

        const uploadConfig = {
            method: 'POST',
            body: formData,
            headers: {
                // Don't set Content-Type for FormData - browser will set it with boundary
                ...this.getAuthHeaders()
            }
        };

        // Remove Content-Type from default headers for file upload
        delete uploadConfig.headers['Content-Type'];

        // Note: Fetch API doesn't support upload progress like XMLHttpRequest
        // For now, we'll do a basic upload and call onProgress with completion
        try {
            const result = await this.request('/upload', uploadConfig);

            // Call progress callback with completion if provided
            if (onProgress) {
                onProgress({
                    progress: 100,
                    loaded: file.size,
                    total: file.size,
                    speed: file.size // Approximate speed
                });
            }

            return result;
        } catch (error) {
            if (onProgress) {
                onProgress({
                    progress: 0,
                    loaded: 0,
                    total: file.size,
                    error: error.message
                });
            }
            throw error;
        }
    }

    /**
     * Batch analytics methods (from utils/apiClient.js)
     */
    async getBatchAnalytics(channelId, period = 30) {
        const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
        const { from, to } = this.getPeriodDateRange(period);

        return Promise.all([
            this.get(`/api/v2/analytics/channels/${numericChannelId}/overview?from=${from}&to=${to}`),
            this.get(`/api/v2/analytics/channels/${numericChannelId}/growth?from=${from}&to=${to}`),
            this.get(`/api/v2/analytics/channels/${numericChannelId}/reach?from=${from}&to=${to}`),
            this.get(`/api/v2/analytics/channels/${numericChannelId}/top-posts?from=${from}&to=${to}`),
            this.getRealTimeMetrics(numericChannelId),
            this.checkAlerts(numericChannelId)
        ]).then(([overview, growth, reach, topPosts, realTime, alerts]) => ({
            overview,
            growth,
            reach,
            topPosts,
            realTime,
            alerts,
            timestamp: new Date().toISOString()
        }));
    }

    /**
     * Get period date range helper
     */
    getPeriodDateRange(period) {
        const to = new Date();
        const from = new Date();
        from.setDate(to.getDate() - period);

        return {
            from: from.toISOString(),
            to: to.toISOString()
        };
    }

    /**
     * Real-time metrics helper
     */
    async getRealTimeMetrics(channelId) {
        try {
            return await this.get(`/api/v2/analytics/channels/${channelId}/real-time`);
        } catch (error) {
            console.warn('Real-time metrics unavailable:', error);
            return { metrics: [], timestamp: new Date().toISOString() };
        }
    }

    /**
     * Check alerts helper
     */
    async checkAlerts(channelId) {
        try {
            return await this.get(`/api/v2/analytics/channels/${channelId}/alerts`);
        } catch (error) {
            console.warn('Alerts unavailable:', error);
            return { alerts: [], timestamp: new Date().toISOString() };
        }
    }

    /**
     * Demo user utilities (backward compatibility)
     */
    isDemoUser() {
        return localStorage.getItem('is_demo_user') === 'true' ||
               window.location.search.includes('demo=true') ||
               window.location.hostname.includes('demo');
    }

    /**
     * Get storage files (from utils/apiClient.js)
     */
    async getStorageFiles(limit = 20, offset = 0) {
        return this.get(`/api/v1/media/storage-files?limit=${limit}&offset=${offset}`);
    }

    /**
     * Export analytics to CSV (from utils/apiClient.js)
     */
    async exportToCsv(type, channelId, period = '7d') {
        const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
        const periodDays = parseInt(period.replace('d', '')) || 7;
        const { from, to } = this.getPeriodDateRange(periodDays);

        return this.get(`/api/v2/analytics/channels/${numericChannelId}/export/${type}?from=${from}&to=${to}&format=csv`);
    }

    /**
     * Health check method
     */
    async healthCheck() {
        return this.get('/health');
    }

    /**
     * Initialize client (backward compatibility)
     */
    async initialize() {
        console.log('🚀 Unified API Client initialized');
        return Promise.resolve();
    }
}

// Create singleton instance
export const apiClient = new UnifiedApiClient();

// Export class for custom instances
export { UnifiedApiClient, AuthStrategies };

// Backward compatibility exports
export const apiFetch = async (endpoint, options = {}) => {
    const method = options.method || 'GET';
    const data = options.body ? JSON.parse(options.body) : null;

    switch (method.toUpperCase()) {
        case 'GET':
            return apiClient.get(endpoint, options);
        case 'POST':
            return apiClient.post(endpoint, data, options);
        case 'PUT':
            return apiClient.put(endpoint, data, options);
        case 'DELETE':
            return apiClient.delete(endpoint, options);
        default:
            throw new Error(`Unsupported method: ${method}`);
    }
};

// Default export
export default apiClient;
