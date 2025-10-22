// Domain-Driven Component Exports
// This file provides clean imports from all domain areas

// Admin Domain
export { default as SuperAdminDashboard } from './admin/SuperAdminDashboard';

// Services Domain
export { default as ServicesOverview } from './services/ServicesOverview';

// Navigation Domain
export { default as NavigationBar } from './navigation/NavigationBar';
// export { default as Sidebar } from './navigation/Sidebar'; // TODO: Create Sidebar component

// Re-export domain index for convenience
export * as AdminDomain from './admin';
export * as ServicesDomain from './services';
export * as NavigationDomain from './navigation';
