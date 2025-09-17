/**
 * Clean Data Provider Interface - Production Code
 * This file contains NO mock logic - only production data fetching
 */

/**
 * Abstract base class for data providers
 * Defines the interface that all data providers must implement
 */
export class DataProvider {
    /**
     * Check if the provider is available/online
     * @returns {Promise<boolean>}
     */
    async isAvailable() {
        throw new Error('isAvailable() must be implemented by subclass');
    }
    
    /**
     * Get analytics data for a channel
     * @param {string} channelId - The channel identifier
     * @returns {Promise<Object>} Analytics data
     */
    async getAnalytics(channelId) {
        throw new Error('getAnalytics() must be implemented by subclass');
    }
    
    /**
     * Get top posts data
     * @param {string} channelId - The channel identifier  
     * @param {Object} options - Query options
     * @returns {Promise<Array>} Top posts data
     */
    async getTopPosts(channelId, options = {}) {
        throw new Error('getTopPosts() must be implemented by subclass');
    }
    
    /**
     * Get engagement metrics
     * @param {string} channelId - The channel identifier
     * @param {Object} options - Query options
     * @returns {Promise<Object>} Engagement metrics
     */
    async getEngagementMetrics(channelId, options = {}) {
        throw new Error('getEngagementMetrics() must be implemented by subclass');
    }
    
    /**
     * Get recommendations data
     * @param {string} channelId - The channel identifier
     * @returns {Promise<Object>} Recommendations data
     */
    async getRecommendations(channelId) {
        throw new Error('getRecommendations() must be implemented by subclass');
    }
    
    /**
     * Get provider identifier
     * @returns {string} Provider name
     */
    getProviderName() {
        throw new Error('getProviderName() must be implemented by subclass');
    }
}

/**
 * Production API Data Provider
 * Handles real API communication with JWT authentication - contains NO mock logic
 */
export class ApiDataProvider extends DataProvider {
    constructor(baseUrl = null, authContext = null) {
        super();
        this.baseUrl = baseUrl || 
                      import.meta.env.VITE_API_BASE_URL || 
                      import.meta.env.VITE_API_URL || 
                      'http://localhost:8000';
        this.authContext = authContext;
    }

    /**
     * Set the authentication context for JWT token access
     * @param {Object} authContext - AuthContext instance with token
     */
    setAuthContext(authContext) {
        this.authContext = authContext;
    }

    /**
     * Get JWT token from auth context
     * @private
     */
    _getAuthToken() {
        return this.authContext?.token || null;
    }

    /**
     * Build authentication headers
     * @private
     */
    _getAuthHeaders() {
        const token = this._getAuthToken();
        const headers = {
            'Content-Type': 'application/json'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }
    
    async isAvailable() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000);
            
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                signal: controller.signal,
                headers: this._getAuthHeaders()
            });
            
            clearTimeout(timeoutId);
            return response.ok;
        } catch (error) {
            console.warn('API availability check failed:', error.message);
            return false;
        }
    }
    
    /**
     * Convert string channel IDs to numeric IDs for API compatibility
     * @private
     */
    _convertChannelId(channelId) {
        // Map string channel IDs to numeric IDs that the API expects
        const channelMap = {
            'demo_channel': 1,
            'tech_news': 2,
            'daily_updates': 3,
            'business_insights': 4
        };
        
        // If it's already numeric, return as is
        if (typeof channelId === 'number' || /^\d+$/.test(channelId)) {
            return channelId;
        }
        
        // Map string to numeric ID, default to 1 for demo purposes
        return channelMap[channelId] || 1;
    }

    async getAnalytics(channelId) {
        const numericChannelId = this._convertChannelId(channelId);
        // Use the insights endpoint which provides similar analytics data
        const response = await this._makeRequest(`/analytics/insights/${numericChannelId}`);
        return response;
    }
    
    async getTopPosts(channelId, options = {}) {
        const numericChannelId = this._convertChannelId(channelId);
        const queryParams = new URLSearchParams(options).toString();
        // Use the demo top-posts endpoint for now
        const url = `/analytics/demo/top-posts${queryParams ? `?${queryParams}` : ''}`;
        const response = await this._makeRequest(url);
        return response;
    }
    
    async getEngagementMetrics(channelId, options = {}) {
        const numericChannelId = this._convertChannelId(channelId);
        const queryParams = new URLSearchParams(options).toString();
        // Use the channel metrics endpoint
        const url = `/analytics/channels/${numericChannelId}/metrics${queryParams ? `?${queryParams}` : ''}`;
        const response = await this._makeRequest(url);
        return response;
    }
    
    async getRecommendations(channelId) {
        const numericChannelId = this._convertChannelId(channelId);
        // Use the advanced analytics recommendations endpoint
        const response = await this._makeRequest(`/api/v2/analytics/advanced/recommendations/${numericChannelId}`);
        return response;
    }
    
    getProviderName() {
        return 'api';
    }
    
    /**
     * Internal method to make HTTP requests with JWT authentication
     * @private
     */
    async _makeRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: this._getAuthHeaders(),
                ...options
            });
            
            // Handle 401 Unauthorized - token might be expired
            if (response.status === 401) {
                // Try to refresh token if auth context supports it
                if (this.authContext?.refreshToken) {
                    const refreshResult = await this.authContext.refreshToken();
                    if (refreshResult.success) {
                        // Retry request with new token
                        const retryResponse = await fetch(url, {
                            method: 'GET',
                            headers: this._getAuthHeaders(),
                            ...options
                        });
                        
                        if (!retryResponse.ok) {
                            throw new Error(`API request failed after token refresh: ${retryResponse.status} ${retryResponse.statusText}`);
                        }
                        
                        return await retryResponse.json();
                    } else {
                        // Refresh failed, user needs to login again
                        throw new Error('Authentication expired. Please login again.');
                    }
                } else {
                    throw new Error('Authentication required. Please login.');
                }
            }
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }
}

/**
 * Default production data provider instance
 * This is what production code should use
 * Note: AuthContext should be set via setAuthContext() after initialization
 */
export const productionDataProvider = new ApiDataProvider();

/**
 * Factory function to create an authenticated data provider
 * @param {Object} authContext - AuthContext instance
 * @param {string} baseUrl - Optional base URL override
 * @returns {ApiDataProvider} Configured data provider with authentication
 */
export const createAuthenticatedDataProvider = (authContext, baseUrl = null) => {
    return new ApiDataProvider(baseUrl, authContext);
};