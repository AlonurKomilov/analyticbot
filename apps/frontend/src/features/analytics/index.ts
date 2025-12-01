/**
 * Analytics Feature Module
 * Barrel export for all analytics features
 */

// Analytics Overview Dashboard (existing)
export * from './analytics-overview';

// TGStat-style Overview (new)
export * from './overview';

// Special Times Recommender
export * from './special-times';

// Metrics Cards
export * from './metrics';

// Sub-feature specific exports (for direct access)
export { default as AnalyticsOverview } from './analytics-overview/AnalyticsOverview';
// Backward compatibility alias
export { default as AdvancedAnalyticsDashboard } from './analytics-overview/AnalyticsOverview';
export { default as SpecialTimesRecommender } from './special-times/SpecialTimesRecommender';
export { default as MetricsCard } from './metrics/MetricsCard';

// TGStat-style Overview Page
export { OverviewPage } from './overview';
