/**
 * Analytics Feature Module
 * Barrel export for all analytics features
 */

// Advanced Analytics Dashboard
export * from './advanced-dashboard';

// Special Times Recommender
export * from './special-times';

// Metrics Cards
export * from './metrics';

// Sub-feature specific exports (for direct access)
export { default as AdvancedAnalyticsDashboard } from './advanced-dashboard/AdvancedAnalyticsDashboard';
export { default as SpecialTimesRecommender } from './special-times/SpecialTimesRecommender';
export { default as MetricsCard } from './metrics/MetricsCard';
