/**
 * Services Index - Updated for Feature-First Architecture (Phase 3 Task 1.5)
 * 
 * Services have been reorganized into feature-specific directories.
 * This file maintains backward compatibility by re-exporting from new locations.
 * 
 * New structure:
 * - features/analytics/services/ - Analytics service
 * - features/admin/services/ - Admin services (users, channels)
 * - features/ai-services/api/ - AI services API
 * - features/ai-services/services/ - AI service logic
 * - features/payment/api/ - Payment API
 * - features/payment/services/ - Payment services
 * - features/protection/services/ - Content protection
 * - features/posts/services/ - Sharing services
 * - shared/services/api/ - Shared API utilities
 * - shared/services/ - Shared service utilities
 */

// Import unified analytics service (replaces multiple duplicate services)
import { analyticsService } from '@features/analytics/services';

// Import other services from their new locations
import { apiClient } from '@/api/client';
import { dataSourceManager } from '@/utils/dataSourceManager';

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
} from '@features/analytics/services';

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
