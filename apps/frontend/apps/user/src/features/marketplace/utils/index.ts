/**
 * Marketplace Utils - Index
 * 
 * Central export for all marketplace utilities.
 * 
 * @module features/marketplace/utils
 */

// Category configuration
export {
  CATEGORY_CONFIGS,
  getCategoryConfig,
  getCategoryKeys,
  mapBackendCategory,
  SERVICE_SUBCATEGORY_CONFIGS,
  getServiceSubcategoryConfig,
  mapBackendToServiceSubcategory,
  USE_CASE_CONFIGS,
  getUseCaseConfig,
  SERVICE_USE_CASE_MAP,
} from './categoryConfig';

// Price formatting
export {
  formatCredits,
  getPrice,
  getPriceDisplay,
  calculateYearlySavings,
  getSavingsDisplay,
  canAfford,
  getRemainingBalance,
} from './priceFormatter';
