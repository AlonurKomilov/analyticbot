// Main Components Export
// Core Analytics Components
export { AnalyticsDashboard } from './dashboard/AnalyticsDashboard';
export { default as TopPostsTable } from './analytics/TopPostsTable';
export { default as BestTimeRecommender } from './analytics/BestTimeRecommender';
export { default as DataSourceSettings } from './DataSourceSettings';

// Channel Management
export { default as AddChannel } from './AddChannel';

// Content Creation
export { default as PostCreator } from './PostCreator';
export { default as ButtonConstructor } from './ButtonConstructor';
export { default as EnhancedMediaUploader } from './EnhancedMediaUploader';
export { default as MediaPreview } from './MediaPreview';

// Scheduling
export { default as ScheduledPostsList } from './ScheduledPostsList';

// Admin & Diagnostic
export { default as DiagnosticPanel } from './DiagnosticPanel';
export { default as StorageFileBrowser } from './StorageFileBrowser';

// Advanced Analytics (Week 3-4)
export { default as AdvancedAnalyticsDashboard } from './analytics/AdvancedAnalyticsDashboard';
export { default as MetricsCard } from './analytics/MetricsCard';

// Alert System Components
export { RealTimeAlertsSystem } from './alerts';

// Chart Components
export { PostViewDynamicsChart } from './charts';
export { TrendsChart } from './charts/TrendsChart';

// Common Components (Barrel Export)
export {
    AccessibleFormField,
    ErrorBoundary,
    ExportButton,
    ShareButton,
    ToastNotification,
    UnifiedButton  // New consolidated button component
} from './common';

// Layout Components (Enhanced Visual Hierarchy)
export {
    EnhancedDashboardLayout,
    EnhancedSection,
    EnhancedCard
} from './layout';

// Showcase Components (Decomposed from DataTablesShowcase)
export {
    TablesShowcase,
    ShowcaseNavigation
} from './showcase';

// Payment Components (Refactored SubscriptionDashboard)
export {
    SubscriptionCard,
    UsageMetrics,
    PaymentHistory
} from './payment';

// Domain Components (Clean Architecture)
export {
    SuperAdminDashboard,
    ServicesOverview,
    NavigationBar,
    Sidebar
} from './domains';
