/**
 * Marketplace Pages - Index
 * 
 * Re-exports marketplace pages from their original locations
 * for backward compatibility during migration.
 * 
 * Eventually these will be moved into this directory.
 * 
 * @module features/marketplace/pages
 */

// Re-export from original locations for now
// TODO: Move actual page components here during full migration
export { default as MarketplacePage } from '@/pages/MarketplacePage';
export { default as MyServicesPage } from '@/pages/MyServicesPage';
export { default as ServiceConfigPage } from '@/pages/services/ServiceConfigPage';
