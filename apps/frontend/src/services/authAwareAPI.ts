/**
 * Authentication-Aware API Service
 * Clean API service that works with backend demo user system
 * No frontend mock switching - all demo data served by backend
 */

import { apiClient } from '../api/client';

export interface UserInfo {
    user?: {
        username?: string;
        email?: string;
        [key: string]: any;
    };
    [key: string]: any;
}

export interface LoginCredentials {
    email?: string;
    username?: string;
    password: string;
}

export interface LoginResponse {
    success: boolean;
    token?: string;
    user?: UserInfo;
    isDemoUser?: boolean;
    demoType?: string | null;
    error?: string;
}

export interface ServiceStatus {
    initialized: boolean;
    authenticated: boolean;
    demoUser: boolean;
    demoType: string | null;
    dataSource: string;
}

export type DemoUserType = 'full_featured' | 'read_only' | 'limited' | 'admin';

class AuthAwareAPIService {
    private isInitialized: boolean = false;
    private userInfo: UserInfo | null = null;

    /**
     * Initialize the service by checking current user authentication
     */
    async initialize(): Promise<void> {
        if (this.isInitialized) return;

        try {
            // Try to get current user info from backend
            const response: any = await apiClient.get('/system/initial-data');
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
    isDemoUser(): boolean {
        if (!this.userInfo) return false;

        // Check if user data indicates demo user
        const demoUsernames = ['Demo User', 'Demo Viewer', 'Demo Guest', 'Demo Admin'];
        return demoUsernames.includes(this.userInfo.user?.username || '');
    }

    /**
     * Get demo user type if applicable
     */
    getDemoUserType(): DemoUserType | null {
        if (!this.isDemoUser()) return null;

        const username = this.userInfo?.user?.username;
        const typeMap: Record<string, DemoUserType> = {
            'Demo User': 'full_featured',
            'Demo Viewer': 'read_only',
            'Demo Guest': 'limited',
            'Demo Admin': 'admin'
        };

        return (username && typeMap[username]) || 'limited';
    }

    /**
     * Make authenticated API call
     */
    async makeRequest(endpoint: string, options: { method?: string; data?: any; params?: any } = {}): Promise<any> {
        // Ensure we're initialized
        await this.initialize();

        try {
            const method = options.method || 'GET';
            let response: any;

            if (method === 'POST' || method === 'PUT') {
                response = await apiClient[method.toLowerCase() as 'post' | 'put'](endpoint, options.data);
            } else if (method === 'DELETE') {
                response = await apiClient.delete(endpoint);
            } else {
                response = await apiClient.get(endpoint, options.params ? { params: options.params } : undefined);
            }

            return response.data;
        } catch (error: any) {
            console.error(`API request failed for ${endpoint}:`, error);

            // Don't fallback to frontend mocks - let the error bubble up
            throw new Error(`API call failed: ${error.message}`);
        }
    }

    /**
     * Analytics API methods - all go through backend
     */
    async getInitialData(): Promise<any> {
        return this.makeRequest('/system/initial-data');
    }

    async getAnalyticsOverview(channelId: string): Promise<any> {
        return this.makeRequest(`/analytics/historical/overview/${channelId}`);
    }

    async getPostDynamics(channelId: string, period: string = '24h'): Promise<any> {
        return this.makeRequest(`/analytics/posts/dynamics/post-dynamics/${channelId}?period=${period}`);
    }

    async getTopPosts(channelId: string, options: Record<string, any> = {}): Promise<any> {
        const queryParams = new URLSearchParams(options).toString();
        const url = `/analytics/posts/dynamics/top-posts/${channelId}${queryParams ? `?${queryParams}` : ''}`;
        return this.makeRequest(url);
    }

    async getBestTime(channelId: string, timeframe: string = 'week'): Promise<any> {
        return this.makeRequest(`/analytics/predictive/best-times/${channelId}?timeframe=${timeframe}`);
    }

    async getEngagementMetrics(channelId: string, period: string = '7d'): Promise<any> {
        return this.makeRequest(`/analytics/channels/${channelId}/engagement?period=${period}`);
    }

    /**
     * AI Services API methods
     */
    async analyzeContentSecurity(content: string): Promise<any> {
        return this.makeRequest('/ai/security/analyze', {
            method: 'POST',
            data: { content }
        });
    }

    async predictChurn(channelId: string): Promise<any> {
        return this.makeRequest('/ai/churn/predict', {
            method: 'POST',
            data: { channel_id: channelId }
        });
    }

    async optimizeContent(content: string, options: Record<string, any> = {}): Promise<any> {
        return this.makeRequest('/ai/content/optimize', {
            method: 'POST',
            data: { content, ...options }
        });
    }

    /**
     * Authentication methods
     */
    async login(credentials: LoginCredentials): Promise<LoginResponse> {
        try {
            const response: any = await apiClient.post('/auth/login', credentials);

            if (response.data?.access_token) {
                // Store token
                localStorage.setItem('authToken', response.data.access_token);

                // Reinitialize to get user info
                this.isInitialized = false;
                await this.initialize();

                return {
                    success: true,
                    token: response.data.access_token,
                    user: this.userInfo || undefined,
                    isDemoUser: this.isDemoUser(),
                    demoType: this.getDemoUserType()
                };
            }

            throw new Error('No access token received');
        } catch (error: any) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async logout(): Promise<{ success: boolean; error?: string }> {
        try {
            // Clear tokens
            localStorage.removeItem('authToken');
            sessionStorage.removeItem('authToken');

            // Reset service state
            this.isInitialized = false;
            this.userInfo = null;

            return { success: true };
        } catch (error: any) {
            return { success: false, error: error.message };
        }
    }

    /**
     * Get current service status
     */
    getStatus(): ServiceStatus {
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
    async refresh(): Promise<ServiceStatus> {
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
