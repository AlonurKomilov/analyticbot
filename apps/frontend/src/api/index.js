/**
 * API Module Index
 * Unified API exports for the frontend application
 * 
 * This module consolidates all API client functionality that was previously
 * scattered across multiple files:
 * - services/apiClient.js (axios-based)
 * - utils/apiClient.js (fetch-based with complex features)
 * - services/dataService.js (adapter pattern)
 */

// Import unified client
import { apiClient, UnifiedApiClient, AuthStrategies, apiFetch } from './client.js';

// Re-export everything for easy access
export {
    // Main client instance
    apiClient,
    
    // Class for custom instances
    UnifiedApiClient,
    
    // Authentication strategies
    AuthStrategies,
    
    // Backward compatibility
    apiFetch
};

// Default export (main client instance)
export default apiClient;

/**
 * Migration Guide:
 * 
 * BEFORE (multiple imports):
 * import { apiClient } from '../services/apiClient.js';          // Axios-based
 * import { apiClient } from '../utils/apiClient.js';             // Fetch-based
 * import { dataServiceFactory } from '../services/dataService.js'; // Adapter
 * 
 * AFTER (single import):
 * import { apiClient } from '../api/client.js';  // OR
 * import apiClient from '../api/client.js';      // OR
 * import { apiClient } from '../api/index.js';   // OR
 * import apiClient from '../api/index.js';
 * 
 * API remains the same:
 * - apiClient.get(url, config)
 * - apiClient.post(url, data, config)  
 * - apiClient.put(url, data, config)
 * - apiClient.delete(url, config)
 * - apiClient.uploadFile(url, file, onProgress)
 * - apiClient.uploadFileDirect(file, onProgress)
 * - apiClient.getBatchAnalytics(channelId, period)
 * 
 * New features:
 * - apiClient.setAuthStrategy(AuthStrategies.JWT | AuthStrategies.TWA | AuthStrategies.NONE)
 * - apiClient.healthCheck()
 * - apiClient.initialize()
 * - apiClient.isDemoUser()
 */