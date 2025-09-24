/**
 * Main API service
 * Clean API-first approach using authentication-aware service
 * All demo data controlled by backend demo user authentication
 */

// Import services
import { apiClient } from '../api/client.js';
import { paymentAPI } from './paymentAPI';
import { authAwareAPI } from './authAwareAPI';

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
      getOverview: (channelId) => authAwareAPI.getAnalyticsOverview(channelId),
      getPostDynamics: (channelId, period = '24h') => authAwareAPI.getPostDynamics(channelId, period),
      getTopPosts: (channelId, options = {}) => authAwareAPI.getTopPosts(channelId, options),
      getBestTime: (channelId, timeframe = 'week') => authAwareAPI.getBestTime(channelId, timeframe),
      getEngagementMetrics: (channelId, period = '7d') => authAwareAPI.getEngagementMetrics(channelId, period)
    },
    
    // AI Services methods
    ai: {
      analyzeSecurity: (content) => authAwareAPI.analyzeContentSecurity(content),
      predictChurn: (channelId) => authAwareAPI.predictChurn(channelId),
      optimizeContent: (content, options = {}) => authAwareAPI.optimizeContent(content, options)
    },
    
    // Authentication methods
    login: (credentials) => authAwareAPI.login(credentials),
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
