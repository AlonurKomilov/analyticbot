import { ErrorHandler } from './errorHandler.js';
import { dataSourceManager } from './dataSourceManager.js';
import { dataServiceFactory } from '../services/dataService.js';

const VITE_API_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '';
const REQUEST_TIMEOUT = 30000; // 30 seconds
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

/**
 * Enhanced API client with retry logic, timeout, and comprehensive error handling
 * Now integrated with mock/real data source management
 */
class ApiClient {
    constructor() {
        // Use relative URLs if VITE_API_URL is empty
        this.baseURL = VITE_API_URL ? VITE_API_URL : '';
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
        
        // Debug logging for API configuration
        if (import.meta.env.VITE_DEBUG === 'true') {
            console.log('🔧 API Client Configuration:', {
                baseURL: this.baseURL,
                timeout: REQUEST_TIMEOUT,
                maxRetries: MAX_RETRIES,
                dataSourceIntegration: 'enabled'
            });
        }
    }

    /**
     * Check if we should use the data service (for routes handled by our mock/real system)
     */
    isDataServiceRoute(url) {
        const dataServiceRoutes = [
            '/api/analytics/',
            '/api/v2/analytics/',
            '/initial-data',
            '/health'
        ];
        return dataServiceRoutes.some(route => url.includes(route));
    }

    /**
     * Route request through data service if applicable
     */
    async routeThroughDataService(method, url, data = null) {
        const currentSource = dataSourceManager.getDataSource();
        const dataService = dataServiceFactory.getService(currentSource);
        
        // Map common API endpoints to data service methods
        if (url.includes('/initial-data')) {
            return await dataService.getInitialData();
        }
        if (url.includes('/health')) {
            return await dataService.healthCheck();
        }
        if (url.includes('/analytics/overview')) {
            const channelId = this.extractChannelId(url) || 'demo_channel';
            return await dataService.getAnalyticsOverview(channelId);
        }
        if (url.includes('/analytics/growth')) {
            const channelId = this.extractChannelId(url) || 'demo_channel';
            return await dataService.getAnalyticsGrowth(channelId);
        }
        if (url.includes('/post-dynamics')) {
            const channelId = this.extractChannelId(url) || 'demo_channel';
            return await dataService.getPostDynamics(channelId);
        }
        
        // Fallback to original fetch for unhandled routes
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
     * Get authentication headers with TWA data
     */
    getAuthHeaders() {
        const twaInitData = window.Telegram?.WebApp?.initData || '';
        return {
            ...this.defaultHeaders,
            'Authorization': `TWA ${twaInitData}`
        };
    }

    /**
     * Sleep utility for retry delays
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Check if error is retryable
     */
    isRetryableError(error) {
        if (!error.response) return true; // Network errors are retryable
        const status = error.response.status;
        return status === 408 || status === 429 || status >= 500;
    }

    /**
     * Make HTTP request with timeout and retry logic
     * Now with data source management integration
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
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

        try {
            // Use relative URL if baseURL is empty
            const url = this.baseURL ? `${this.baseURL}${endpoint}` : endpoint;
            const config = {
                ...options,
                headers: {
                    ...this.getAuthHeaders(),
                    ...options.headers
                },
                signal: controller.signal
            };

            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            // Check content type before trying to parse JSON
            const contentType = response.headers.get('content-type');
            let responseData;
            
            if (contentType && contentType.includes('application/json')) {
                try {
                    responseData = await response.json();
                } catch (parseError) {
                    // If JSON parsing fails, throw a more helpful error
                    const error = new Error(`Invalid JSON response from API: ${parseError.message}`);
                    error.response = {
                        status: response.status,
                        statusText: response.statusText,
                        data: null
                    };
                    throw error;
                }
            } else {
                // If not JSON, likely an error page or wrong endpoint
                const textContent = await response.text();
                const error = new Error(`API returned non-JSON response. Expected JSON but got: ${contentType || 'unknown content type'}`);
                error.response = {
                    status: response.status,
                    statusText: response.statusText,
                    data: textContent.substring(0, 200) // First 200 chars for debugging
                };
                throw error;
            }

            if (!response.ok) {
                const error = new Error(responseData.detail || 'API request failed');
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

            // Handle connection refused - auto-switch to demo mode
            if (error.message.includes('ERR_CONNECTION_REFUSED') || 
                error.message.includes('Failed to fetch') ||
                error.message.includes('Network request failed')) {
                
                // Only log in development mode
                if (import.meta.env.DEV) {
                    console.warn('API connection failed, auto-switching to demo mode');
                }
                
                // Automatically switch to demo mode
                localStorage.setItem('useRealAPI', 'false');
                window.dispatchEvent(new CustomEvent('dataSourceChanged', { 
                    detail: { source: 'mock', reason: 'api_unavailable' }
                }));
                
                // Create a user-friendly error
                const connectionError = new Error('API is currently unavailable. Switched to demo mode automatically.');
                connectionError.response = { status: 503, autoSwitched: true };
                throw connectionError;
            }

            // Retry logic
            if (this.isRetryableError(error) && attempt < MAX_RETRIES) {
                console.warn(`API request failed (attempt ${attempt}/${MAX_RETRIES}), retrying...`, {
                    endpoint,
                    error: error.message
                });
                
                await this.sleep(RETRY_DELAY * attempt);
                return this.request(endpoint, options, attempt + 1);
            }

            // Final error handling
            throw ErrorHandler.handleApiError(error, endpoint, {
                component: 'ApiClient',
                action: 'request',
                attempt
            });
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        const searchParams = new URLSearchParams(params);
        const url = searchParams.toString() ? `${endpoint}?${searchParams}` : endpoint;
        return this.request(url, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data = null) {
        return this.request(endpoint, {
            method: 'POST',
            body: data ? JSON.stringify(data) : null
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data = null) {
        return this.request(endpoint, {
            method: 'PUT',
            body: data ? JSON.stringify(data) : null
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    /**
     * Upload file with progress tracking
     */
    async uploadFile(endpoint, file, onProgress = null) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            const formData = new FormData();
            formData.append('file', file);

            // Progress tracking
            if (onProgress) {
                xhr.upload.addEventListener('progress', (event) => {
                    if (event.lengthComputable) {
                        const progress = (event.loaded / event.total) * 100;
                        onProgress(progress);
                    }
                });
            }

            // Success handler
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch {
                        reject(new Error('Invalid JSON response'));
                    }
                } else {
                    const error = new Error(`Upload failed: ${xhr.statusText}`);
                    error.response = {
                        status: xhr.status,
                        statusText: xhr.statusText
                    };
                    reject(ErrorHandler.handleApiError(error, endpoint, {
                        component: 'ApiClient',
                        action: 'uploadFile'
                    }));
                }
            });

            // Error handler
            xhr.addEventListener('error', () => {
                const error = new Error('Upload failed');
                reject(ErrorHandler.handleApiError(error, endpoint, {
                    component: 'ApiClient',
                    action: 'uploadFile'
                }));
            });

            // Timeout handler
            xhr.addEventListener('timeout', () => {
                const error = new Error('Upload timeout');
                error.response = { status: 408 };
                reject(ErrorHandler.handleApiError(error, endpoint, {
                    component: 'ApiClient',
                    action: 'uploadFile'
                }));
            });

            // Set timeout first
            xhr.timeout = REQUEST_TIMEOUT;
            
            // Open the request
            xhr.open('POST', `${this.baseURL}${endpoint}`);
            
            // Set auth header after opening the request
            const twaInitData = window.Telegram?.WebApp?.initData || '';
            try {
                xhr.setRequestHeader('Authorization', `TWA ${twaInitData}`);
            } catch (error) {
                console.warn('Failed to set Authorization header:', error);
            }

            // Start upload
            xhr.send(formData);
        });
    }

    /**
     * Enhanced direct upload with channel targeting (NEW for TWA Phase 2.1)
     */
    async uploadFileDirect(file, channelId = null, onProgress = null) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            const formData = new FormData();
            formData.append('file', file);
            
            // Add channel_id if provided
            if (channelId) {
                formData.append('channel_id', channelId.toString());
            }

            const startTime = Date.now();

            // Progress tracking with enhanced metadata
            if (onProgress) {
                xhr.upload.addEventListener('progress', (event) => {
                    if (event.lengthComputable) {
                        const progress = (event.loaded / event.total) * 100;
                        const speed = event.loaded / ((Date.now() - startTime) / 1000); // bytes per second
                        onProgress({
                            progress,
                            loaded: event.loaded,
                            total: event.total,
                            speed: speed || 0
                        });
                    }
                });
            }

            // Success handler with enhanced response
            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        // Enhanced response with upload metadata
                        resolve({
                            ...response,
                            upload_duration: Date.now() - startTime,
                            upload_speed: file.size / ((Date.now() - startTime) / 1000)
                        });
                    } catch {
                        reject(new Error('Invalid JSON response'));
                    }
                } else {
                    const error = new Error(`Direct upload failed: ${xhr.statusText}`);
                    error.response = {
                        status: xhr.status,
                        statusText: xhr.statusText
                    };
                    reject(ErrorHandler.handleApiError(error, '/api/v1/media/upload-direct', {
                        component: 'ApiClient',
                        action: 'uploadFileDirect',
                        channelId
                    }));
                }
            });

            // Error handler
            xhr.addEventListener('error', () => {
                const error = new Error('Direct upload failed');
                reject(ErrorHandler.handleApiError(error, '/api/v1/media/upload-direct', {
                    component: 'ApiClient',
                    action: 'uploadFileDirect',
                    channelId
                }));
            });

            // Timeout handler
            xhr.addEventListener('timeout', () => {
                const error = new Error('Direct upload timeout');
                error.response = { status: 408 };
                reject(ErrorHandler.handleApiError(error, '/api/v1/media/upload-direct', {
                    component: 'ApiClient',
                    action: 'uploadFileDirect',
                    channelId
                }));
            });

            // Set timeout first
            xhr.timeout = REQUEST_TIMEOUT;
            
            // Open the request
            xhr.open('POST', `${this.baseURL}/api/v1/media/upload-direct`);
            
            // Set auth header after opening the request
            const twaInitData = window.Telegram?.WebApp?.initData || '';
            try {
                xhr.setRequestHeader('Authorization', `TWA ${twaInitData}`);
            } catch (error) {
                console.warn('Failed to set Authorization header:', error);
            }

            // Start upload
            xhr.send(formData);
        });
    }

    /**
     * Get storage files for media browser (NEW for TWA Phase 2.1)
     */
    async getStorageFiles(limit = 20, offset = 0) {
        return this.get(`/api/v1/media/storage-files?limit=${limit}&offset=${offset}`);
    }

    /**
     * Export Analytics to CSV (Week 1-2 Quick Win)
     */
    async exportToCsv(type, channelId, period = '7d') {
        const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
        const periodDays = parseInt(period.replace('d', '')) || 7;
        const { from, to } = this.getPeriodDateRange(periodDays);
        return this.get(`/api/v2/exports/csv/${type}/${numericChannelId}?from=${from}&to=${to}`);
    }

    /**
     * Export Analytics to PNG (Week 1-2 Quick Win)
     */
    async exportToPng(type, channelId, period = '7d') {
        const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
        const periodDays = parseInt(period.replace('d', '')) || 7;
        const { from, to } = this.getPeriodDateRange(periodDays);
        return this.get(`/api/v2/exports/png/${type}/${numericChannelId}?from=${from}&to=${to}`);
    }

    /**
     * Get Export System Status (Week 1-2 Quick Win)
     */
    async getExportStatus() {
        return this.get('/api/v2/exports/status');
    }

    /**
     * Create Share Link (Week 1-2 Quick Win)
     */
    async createShareLink(type, channelId, ttl = '24h') {
        const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
        return this.post(`/api/v2/share/create/${type}/${numericChannelId}`, { ttl });
    }

    /**
     * Get Shared Report (Week 1-2 Quick Win)
     */
    async getSharedReport(token) {
        return this.get(`/api/v2/share/report/${token}`);
    }

    /**
     * Get Share Link Info (Week 1-2 Quick Win)
     */
    async getShareInfo(token) {
        return this.get(`/api/v2/share/info/${token}`);
    }

    /**
     * Revoke Share Link (Week 1-2 Quick Win)
     */
    async revokeShareLink(token) {
        return this.delete(`/api/v2/share/revoke/${token}`);
    }

    // ==========================================
    // WEEK 3-4 ADVANCED ANALYTICS METHODS
    // ==========================================

    /**
     * Get Advanced Analytics Dashboard (Week 3-4)
     */
    async getAdvancedDashboard(channelId, period = 30, includeAlerts = true, includeRecommendations = true) {
        const params = new URLSearchParams({
            period: period.toString(),
            include_alerts: includeAlerts.toString(),
            include_recommendations: includeRecommendations.toString()
        });
        return this.get(`/api/v2/analytics/advanced/dashboard/${channelId}?${params}`);
    }

    /**
     * Get Real-time Metrics (Week 3-4)
     */
    async getRealTimeMetrics(channelId) {
        const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
        return this.get(`/api/v2/analytics/advanced/metrics/real-time/${numericChannelId}`);
    }

    /**
     * Check Active Alerts (Week 3-4)
     */
    async checkAlerts(channelId) {
        const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
        return this.get(`/api/v2/analytics/advanced/alerts/check/${numericChannelId}`);
    }

    /**
     * Get AI Recommendations (Week 3-4)
     */
    async getRecommendations(channelId) {
        const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
        return this.get(`/api/v2/analytics/advanced/recommendations/${numericChannelId}`);
    }

    /**
     * Get Performance Score (Week 3-4)
     */
    async getPerformanceScore(channelId, period = 30) {
        const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
        const { from, to } = this.getPeriodDateRange(period);
        return this.get(`/api/v2/analytics/advanced/performance/score/${numericChannelId}?from=${from}&to=${to}`);
    }

    /**
     * Advanced Trending Analysis (Week 3-4)
     */
    async getAdvancedTrends(channelId, period = 7) {
        const numericChannelId = channelId === 'demo_channel' ? 1 : parseInt(channelId);
        const { from, to } = this.getPeriodDateRange(period);
        
        return Promise.all([
            this.get(`/api/v2/analytics/channels/${numericChannelId}/trending?from=${from}&to=${to}`),
            this.getRealTimeMetrics(numericChannelId),
            this.getPerformanceScore(channelId, period)
        ]).then(([trends, realTime, performance]) => ({
            trends,
            realTime,
            performance
        }));
    }

    /**
     * Helper function to convert period to datetime range
     */
    getPeriodDateRange(periodDays = 30) {
        const to = new Date();
        const from = new Date();
        from.setDate(from.getDate() - periodDays);
        
        return {
            from: from.toISOString(),
            to: to.toISOString()
        };
    }

    /**
     * Batch Analytics Data (Week 3-4) - Optimized for dashboard
     */
    async getBatchAnalytics(channelId, period = 30) {
        // Convert string channel ID to integer and period to date range
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
}

// Create singleton instance
export const apiClient = new ApiClient();

// Backward compatibility function
export const apiFetch = async (endpoint, options = {}) => {
    const method = options.method || 'GET';
    const data = options.body ? JSON.parse(options.body) : null;

    switch (method.toUpperCase()) {
        case 'GET':
            return apiClient.get(endpoint);
        case 'POST':
            return apiClient.post(endpoint, data);
        case 'PUT':
            return apiClient.put(endpoint, data);
        case 'DELETE':
            return apiClient.delete(endpoint);
        default:
            throw new Error(`Unsupported method: ${method}`);
    }
};
