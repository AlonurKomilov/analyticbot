// Main Components Export
// Core Analytics Components - MIGRATED TO @features/dashboard
// export { AnalyticsDashboard } from './dashboard/AnalyticsDashboard';
export { default as TopPostsTable } from './analytics/TopPostsTable';
// MIGRATED TO @features/analytics
// export { default as BestTimeRecommender } from './analytics/BestTimeRecommender';
export { default as DataSourceSettings } from './DataSourceSettings';

// Channel Management
export { default as AddChannel } from './AddChannel';

// Content Creation - MIGRATED TO @features/posts
// export { default as PostCreator } from './PostCreator';
export { default as ButtonConstructor } from './ButtonConstructor';
export { default as EnhancedMediaUploader } from './EnhancedMediaUploader';
export { default as MediaPreview } from './MediaPreview';

// Scheduling - MIGRATED TO @features/posts
// export { default as ScheduledPostsList } from './ScheduledPostsList';

// Admin & Diagnostic
export { default as DiagnosticPanel } from './DiagnosticPanel';
export { default as StorageFileBrowser } from './StorageFileBrowser';

// Advanced Analytics - MIGRATED TO @features/analytics
// export { AdvancedAnalyticsDashboard } from './analytics/AdvancedAnalyticsDashboard';
// export { MetricsCard } from './analytics/MetricsCard';

// Alert System Components
export { RealTimeAlertsSystem } from '@features/alerts';

// Chart Components
export { PostViewDynamicsChart } from './charts';
export { TrendsChart } from './charts/TrendsChart';

// Common Components (Barrel Export) - NOW IN @shared
// export {
//     AccessibleFormField,
//     ErrorBoundary,
//     ExportButton,
//     ShareButton,
//     ToastNotification,
//     Button  // New consolidated button component (UnifiedButton)
// } from '@shared/components';

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
} from '@features/payment';

// Domain Components (Clean Architecture)
export {
    SuperAdminDashboard,
    ServicesOverview,
    NavigationBar
    // Sidebar // TODO: Create Sidebar component
} from './domains';
