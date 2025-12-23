/**
 * Dashboard Feature Module
 * Barrel export for all dashboard features
 */

// Analytics Dashboard
export * from './analytics-dashboard';

// Dashboard Widgets
export * from './widgets';

// Direct exports
export { default as AnalyticsDashboard } from './analytics-dashboard/AnalyticsDashboard';
export { default as SystemStatusWidget } from './widgets/SystemStatusWidget';
