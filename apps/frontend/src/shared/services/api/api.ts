/**
 * Main API service
 * Clean API-first approach using authentication-aware service
 * All demo data controlled by backend demo user authentication
 */

// Import services
import { apiClient } from '@/api/client';
import { paymentAPI } from '@features/payment/api';
import { authAwareAPI } from './authAwareAPI';

interface AnalyticsOptions {
  [key: string]: any;
}

interface ContentOptions {
  [key: string]: any;
}

interface Credentials {
  email?: string;
  username?: string;
  password: string;
}

// Create clean API that uses authentication-aware service
const createCleanAPI = () => {
  return {
    // Core API methods
    client: apiClient,
    payment: paymentAPI,
    auth: authAwareAPI,

    // Analytics methods - all go through authentication-aware API
    analytics: {
      getInitialData: () => authAwareAPI.getInitialData(),
      getOverview: (channelId: string) => authAwareAPI.getAnalyticsOverview(channelId),
      getPostDynamics: (channelId: string, period: string = '24h') => authAwareAPI.getPostDynamics(channelId, period),
      getTopPosts: (channelId: string, options: AnalyticsOptions = {}) => authAwareAPI.getTopPosts(channelId, options),
      getBestTime: (channelId: string, timeframe: string = 'week') => authAwareAPI.getBestTime(channelId, timeframe),
      getEngagementMetrics: (channelId: string, period: string = '7d') => authAwareAPI.getEngagementMetrics(channelId, period)
    },

    // AI Services methods
    ai: {
      analyzeSecurity: (content: string) => authAwareAPI.analyzeContentSecurity(content),
      predictChurn: (channelId: string) => authAwareAPI.predictChurn(channelId),
      optimizeContent: (content: string, options: ContentOptions = {}) => authAwareAPI.optimizeContent(content, options)
    },

    // Authentication methods
    login: (credentials: Credentials) => authAwareAPI.login(credentials),
    logout: () => authAwareAPI.logout(),

    // Utility methods
    isDemoUser: () => authAwareAPI.isDemoUser(),
    getDemoType: () => authAwareAPI.getDemoUserType(),
    getStatus: () => authAwareAPI.getStatus(),
    refresh: () => authAwareAPI.refresh(),

    // Initialize service
    initialize: () => authAwareAPI.initialize()
  };
};

// Export individual API modules
export { apiClient, paymentAPI };

// Export authentication-aware API service
export { authAwareAPI };

// Export clean API as default
export const api = createCleanAPI();

export default api;
