/**
 * Authentication-Aware API Service
 * Clean API service that works with backend demo user system
 * No frontend mock switching - all demo data served by backend
 */

import { apiClient } from '../api/client.js';

class AuthAwareAPIService {
    constructor() {
        this.isInitialized = false;
        this.userInfo = null;
    }

    /**
     * Initialize the service by checking current user authentication
     */
    async initialize() {
        if (this.isInitialized) return;

        try {
            // Try to get current user info from backend
            const response = await apiClient.get('/system/initial-data');
            this.userInfo = response.data || response;
            this.isInitialized = true;
        } catch (error) {
            console.warn('Could not initialize user info:', error);
            this.userInfo = null;
            this.isInitialized = true;
        }
    }

    /**
     * Check if current user is a demo user based on backend response
     */
    isDemoUser() {
        if (!this.userInfo) return false;

        // Check if user data indicates demo user
        const demoUsernames = ['Demo User', 'Demo Viewer', 'Demo Guest', 'Demo Admin'];
        return demoUsernames.includes(this.userInfo.user?.username);
    }

    /**
     * Get demo user type if applicable
     */
    getDemoUserType() {
        if (!this.isDemoUser()) return null;

        const username = this.userInfo.user?.username;
        const typeMap = {
            'Demo User': 'full_featured',
            'Demo Viewer': 'read_only',
            'Demo Guest': 'limited',
            'Demo Admin': 'admin'
        };

        return typeMap[username] || 'limited';
    }

    /**
     * Make authenticated API call
     */
    async makeRequest(endpoint, options = {}) {
        // Ensure we're initialized
        await this.initialize();

        try {
            const response = await apiClient.request({
                url: endpoint,
                method: 'GET',
                ...options
            });

            return response.data;
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);

            // Don't fallback to frontend mocks - let the error bubble up
            throw new Error(`API call failed: ${error.message}`);
        }
    }

    /**
     * Analytics API methods - all go through backend
     */
    async getInitialData() {
        return this.makeRequest('/system/initial-data');
    }

    async getAnalyticsOverview(channelId) {
        return this.makeRequest(`/analytics/overview/${channelId}`);
    }

    async getPostDynamics(channelId, period = '24h') {
        return this.makeRequest(`/analytics/v2/post-dynamics/${channelId}?period=${period}`);
    }

    async getTopPosts(channelId, options = {}) {
        const queryParams = new URLSearchParams(options).toString();
        const url = `/analytics/v2/top-posts/${channelId}${queryParams ? `?${queryParams}` : ''}`;
        return this.makeRequest(url);
    }

    async getBestTime(channelId, timeframe = 'week') {
        return this.makeRequest(`/analytics/v2/best-time/${channelId}?timeframe=${timeframe}`);
    }

    async getEngagementMetrics(channelId, period = '7d') {
        return this.makeRequest(`/analytics/v2/engagement-metrics/${channelId}?period=${period}`);
    }

    /**
     * AI Services API methods
     */
    async analyzeContentSecurity(content) {
        return this.makeRequest('/ai/security/analyze', {
            method: 'POST',
            data: { content }
        });
    }

    async predictChurn(channelId) {
        return this.makeRequest('/ai/churn/predict', {
            method: 'POST',
            data: { channel_id: channelId }
        });
    }

    async optimizeContent(content, options = {}) {
        return this.makeRequest('/ai/content/optimize', {
            method: 'POST',
            data: { content, ...options }
        });
    }

    /**
     * Authentication methods
     */
    async login(credentials) {
        try {
            const response = await apiClient.post('/auth/login', credentials);

            if (response.data.access_token) {
                // Store token
                localStorage.setItem('authToken', response.data.access_token);

                // Reinitialize to get user info
                this.isInitialized = false;
                await this.initialize();

                return {
                    success: true,
                    token: response.data.access_token,
                    user: this.userInfo,
                    isDemoUser: this.isDemoUser(),
                    demoType: this.getDemoUserType()
                };
            }

            throw new Error('No access token received');
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async logout() {
        try {
            // Clear tokens
            localStorage.removeItem('authToken');
            sessionStorage.removeItem('authToken');

            // Reset service state
            this.isInitialized = false;
            this.userInfo = null;

            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    /**
     * Get current service status
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            authenticated: !!this.userInfo,
            demoUser: this.isDemoUser(),
            demoType: this.getDemoUserType(),
            dataSource: 'backend-controlled'
        };
    }

    /**
     * Refresh user info from backend
     */
    async refresh() {
        this.isInitialized = false;
        await this.initialize();
        return this.getStatus();
    }
}

// Create singleton instance
export const authAwareAPI = new AuthAwareAPIService();

// Export for testing
export { AuthAwareAPIService };

// Default export
export default authAwareAPI;
