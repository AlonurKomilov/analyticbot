/**
 * Main API service
 * Exports all API modules for easy importing
 */

// Import API clients
import { apiClient } from './apiClient';
import { paymentAPI } from './paymentAPI';

// Export individual API modules
export { apiClient, paymentAPI };

// Export all APIs as a single object for convenience
export const api = {
  client: apiClient,
  payment: paymentAPI,
};

export default api;
