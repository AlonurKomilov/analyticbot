/**
 * Services Index - Updated for Analytics Consolidation
 * Exports unified analytics service and maintains backward compatibility
 */

// Import unified analytics service (replaces multiple duplicate services)
import { analyticsService } from './analyticsService.js';

// Import other non-analytics services
import { apiClient } from '../api/client.js';
import { dataSourceManager } from '../utils/dataSourceManager.js';

// Export unified analytics service as primary interface
export { analyticsService };

// Backward compatibility exports (deprecated - use analyticsService instead)
export const unifiedAnalyticsService = analyticsService;
export const mockAnalyticsService = analyticsService;
export const demoAnalyticsService = analyticsService;

// Export individual adapters for advanced use cases
export {
    RealAnalyticsAdapter,
    MockAnalyticsAdapter,
    AnalyticsCacheManager
} from './analyticsService.js';

// Export API client and data source manager
export { apiClient, dataSourceManager };

// Legacy service exports for gradual migration
export const legacyApiClient = apiClient;

// Service registry for dependency injection
export const serviceRegistry = {
    analytics: analyticsService,
    api: apiClient,
    dataSource: dataSourceManager
};

export default analyticsService;
