/**
 * Analytics Service
 * 
 * Refactored from 656 lines to 6 files:
 * - types.ts: Type definitions
 * - CacheManager.ts: Analytics caching with TTL and LRU
 * - RealAnalyticsAdapter.ts: Real API adapter
 * - MockAnalyticsAdapter.ts: Mock/demo data adapter
 * - UnifiedAnalyticsService.ts: Main service with adapter pattern
 * - index.ts: Barrel exports
 */

// Main service export
export { analyticsService, UnifiedAnalyticsService } from './UnifiedAnalyticsService';
export { default } from './UnifiedAnalyticsService';

// Adapters for direct access if needed
export { RealAnalyticsAdapter } from './RealAnalyticsAdapter';
export { MockAnalyticsAdapter } from './MockAnalyticsAdapter';
export { AnalyticsCacheManager } from './CacheManager';

// Types
export * from './types';
