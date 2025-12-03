/**
 * Services Index - Updated for Feature-First Architecture
 *
 * NOTE: AI Service PAGES have been moved to pages/ai-services/
 * This folder now only contains:
 * - Re-exports for backward compatibility
 * - userBotApi.ts - Bot API utilities
 *
 * New structure:
 * - pages/ai-services/ - AI service PAGE components
 * - features/analytics/services/ - Analytics service logic
 * - features/admin/services/ - Admin services (users, channels)
 * - features/ai-services/services/ - AI service LOGIC (not pages)
 * - features/payment/services/ - Payment services
 * - features/protection/services/ - Content protection
 * - features/posts/services/ - Sharing services
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
