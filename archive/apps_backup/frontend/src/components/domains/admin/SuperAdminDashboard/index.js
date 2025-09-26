/**
 * SuperAdminDashboard - Refactored modular components
 * 
 * Main Component:
 * - SuperAdminDashboard: Core admin dashboard with tab-based interface
 * 
 * Tab Components:
 * - OverviewTab: System overview with recent activity and health status
 * - UserManagementTab: User management with suspend/reactivate functionality
 * - AuditLogsTab: Administrative audit trail with action logs
 * - SystemConfigTab: System configuration interface
 * 
 * UI Components:
 * - AdminStatsCards: System statistics display cards
 * - AdminTabNavigation: Tab navigation for dashboard sections
 * - SuspendUserDialog: Modal dialog for user suspension
 * - TabPanel: Utility component for tab content rendering
 * 
 * Hooks:
 * - useAdminDashboardState: State management for tabs, dialogs, notifications
 * 
 * Utils:
 * - adminUtils: Formatting and helper functions for admin dashboard
 */

// Main component export
export { default as SuperAdminDashboard } from './SuperAdminDashboard.jsx';

// Tab component exports
export { default as OverviewTab } from './components/OverviewTab.jsx';
export { default as UserManagementTab } from './components/UserManagementTab.jsx';
export { default as AuditLogsTab } from './components/AuditLogsTab.jsx';
export { default as SystemConfigTab } from './components/SystemConfigTab.jsx';

// UI component exports
export { default as AdminStatsCards } from './components/AdminStatsCards.jsx';
export { default as AdminTabNavigation } from './components/AdminTabNavigation.jsx';
export { default as SuspendUserDialog } from './components/SuspendUserDialog.jsx';
export { default as TabPanel } from './components/TabPanel.jsx';

// Hook exports
export { useAdminDashboardState } from './hooks/useAdminDashboardState.js';

// Utility exports
export * from './utils/adminUtils.js';

// Default export for backward compatibility
export { default } from './SuperAdminDashboard.jsx';