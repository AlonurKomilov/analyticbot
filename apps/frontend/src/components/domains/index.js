// Domain-Driven Component Exports
// This file provides clean imports from all domain areas

// Admin Domain
export { default as SuperAdminDashboard } from './domains/admin/SuperAdminDashboard';

// Services Domain
export { default as ServicesOverview } from './domains/services/ServicesOverview';

// Navigation Domain
export { default as NavigationBar } from './domains/navigation/NavigationBar';
export { default as Sidebar } from './domains/navigation/Sidebar';

// Re-export domain index for convenience
export * as AdminDomain from './domains/admin';
export * as ServicesDomain from './domains/services';
export * as NavigationDomain from './domains/navigation';
