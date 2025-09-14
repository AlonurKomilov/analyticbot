// Optimized Barrel Export Strategy
// Performance-focused exports with lazy loading support

// =================
// HIGH-FREQUENCY IMPORTS (Always loaded)
// =================

// Common utilities and frequently used components
export { 
    AccessibleButton, 
    AccessibleFormField, 
    ErrorBoundary, 
    ExportButton, 
    LoadingButton, 
    ShareButton, 
    ToastNotification 
} from './common';

// =================
// DOMAIN-SPECIFIC EXPORTS (Lazy loaded)
// =================

// Use dynamic imports for large components to improve initial bundle size
export const LazyAdminDashboard = () => import('./domains/admin/SuperAdminDashboard');
export const LazyServicesOverview = () => import('./domains/services/ServicesOverview');
export const LazyAnalyticsDashboard = () => import('./analytics/AdvancedAnalyticsDashboard');

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
export * from './analytics';

// =================
// CHARTS BARREL  
// =================
export * from './charts';