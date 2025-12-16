/**
 * Marketplace Components - Index
 * 
 * Central export for all marketplace components.
 * Re-exports from pages/marketplace for components that haven't been migrated.
 * 
 * @module features/marketplace/components
 */

// Common components
export { CreditBalance } from './common/CreditBalance';
export { SearchBar } from './common/SearchBar';
export { PurchaseDialog } from './common/PurchaseDialog';
export { CategoryFilter } from './common/CategoryFilter';

// Re-export from pages/marketplace for now
export { ItemDetailModal } from '@/pages/marketplace/components/ItemDetailModal';

// Card components
export { MarketplaceCard } from './cards/MarketplaceCard';
