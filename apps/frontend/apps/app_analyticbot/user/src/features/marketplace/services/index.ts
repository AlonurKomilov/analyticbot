/**
 * Marketplace Services - Index
 * 
 * Central export for service registry and config components.
 * 
 * @module features/marketplace/services
 */

// Service registry
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
} from './registry';

export type { ServiceRegistryEntry } from './registry';
