/**
 * Marketplace Feature
 * ====================
 * 
 * Self-contained vertical slice for all marketplace functionality.
 * 
 * Structure
 * ---------
 * features/marketplace/
 * ├── index.ts                    # Main exports (this file)
 * ├── types/                      # TypeScript types
 * │   └── index.ts               # Item, service, and common types
 * ├── api/                        # API client functions
 * │   ├── items.ts               # One-time purchase items
 * │   ├── services.ts            # Subscription services
 * │   └── credits.ts             # Credit balance and gifting
 * ├── hooks/                      # React hooks
 * │   ├── useMarketplaceItems.ts
 * │   ├── useUserServices.ts
 * │   ├── useCreditBalance.ts
 * │   └── useServiceAccess.ts
 * ├── components/                 # Reusable components
 * │   ├── common/                # Shared (CreditBalance, SearchBar, etc.)
 * │   └── cards/                 # Card components
 * ├── pages/                      # Page components (re-exports)
 * ├── services/                   # Service config registry
 * │   └── registry.tsx           # Service registry
 * └── utils/                      # Utilities
 *     ├── categoryConfig.ts
 *     └── priceFormatter.ts
 * 
 * Usage
 * -----
 *   import { 
 *     useMarketplaceItems,
 *     useCreditBalance,
 *     SERVICE_REGISTRY,
 *     MarketplaceCard,
 *   } from '@/features/marketplace';
 * 
 * @module features/marketplace
 */

// =============================================================================
// TYPES
// =============================================================================

export * from './types';

// =============================================================================
// API
// =============================================================================

export * from './api';

// =============================================================================
// HOOKS
// =============================================================================

export * from './hooks';

// =============================================================================
// COMPONENTS
// =============================================================================

export * from './components';

// =============================================================================
// PAGES (re-exports for backward compatibility)
// =============================================================================

export * from './pages';

// =============================================================================
// SERVICE REGISTRY
// =============================================================================

export {
  SERVICE_REGISTRY,
  getServiceEntry,
  getServiceConfigComponent,
  getServiceMetadata,
  getServiceIcon,
  getAllServiceKeys,
  getServicesByCategory,
  isServiceRegistered,
  // Deprecated exports for backward compatibility
  SERVICE_CONFIG_MAP,
  SERVICE_ICON_MAP,
  SERVICE_DETAILS,
} from './services/registry';

export type { ServiceRegistryEntry } from './services/registry';

// =============================================================================
// UTILS
// =============================================================================

export * from './utils';

