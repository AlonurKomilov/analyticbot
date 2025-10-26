/**
 * Analytics Feature Module
 * Barrel export for all analytics features
 */

// Advanced Analytics Dashboard
export * from './advanced-dashboard';

// Best Time Recommender
export * from './best-time';

// Metrics Cards
export * from './metrics';

// Sub-feature specific exports (for direct access)
export { default as AdvancedAnalyticsDashboard } from './advanced-dashboard/AdvancedAnalyticsDashboard';
export { default as BestTimeRecommender } from './best-time/BestTimeRecommender';
export { default as MetricsCard } from './metrics/MetricsCard';
