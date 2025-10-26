// Optimized Barrel Export Strategy
// Performance-focused exports with lazy loading support

// =================
// HIGH-FREQUENCY IMPORTS (Always loaded)
// =================

// Common utilities and frequently used components - NOW IN @shared
// export {
//     AccessibleButton,
//     AccessibleFormField,
//     ErrorBoundary,
//     ExportButton,
//     LoadingButton,
//     ShareButton,
//     ToastNotification
// } from '@shared/components';

// =================
// DOMAIN-SPECIFIC EXPORTS (Lazy loaded)
// =================

// Use dynamic imports for large components to improve initial bundle size
export const LazyAdminDashboard = () => import('./domains/admin/SuperAdminDashboard');
export const LazyServicesOverview = () => import('./domains/services/ServicesOverview');
export const LazyAnalyticsDashboard = () => import('../features/analytics/advanced-dashboard');

// =================
// DIRECT EXPORTS (For compatibility)
// =================

// Keep direct exports for smaller components
export { default as DiagnosticPanel } from './DiagnosticPanel';
export { default as StorageFileBrowser } from './StorageFileBrowser';
export { default as NavigationBar } from './domains/navigation/NavigationBar';

// =================
// ANALYTICS BARREL
// =================
// MIGRATED TO @features/analytics
// export * from './analytics';

// =================
// CHARTS BARREL
// =================
export * from './charts';
