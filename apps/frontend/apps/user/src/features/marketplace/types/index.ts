/**
 * Marketplace Item Type Definitions
 * 
 * This file defines the standardized interfaces for all marketplace items.
 * Developers creating new items should implement these interfaces.
 * 
 * @module marketplace/types
 */

// =============================================================================
// BASE TYPES
// =============================================================================

/**
 * All possible marketplace item categories
 */
export type MarketplaceCategory = 
  | 'themes' 
  | 'widgets' 
  | 'ai_models' 
  | 'bot_service' 
  | 'mtproto_services' 
  | 'ai_services'
  | 'bundles';

/**
 * Pricing model for items
 */
export type PricingModel = 'one_time' | 'subscription';

/**
 * Billing cycle for subscriptions
 */
export type BillingCycle = 'monthly' | 'yearly';

/**
 * Item status
 */
export type ItemStatus = 'active' | 'inactive' | 'deprecated' | 'coming_soon';

// =============================================================================
// MARKETPLACE ITEM INTERFACES
// =============================================================================

/**
 * Base interface for ALL marketplace items
 * Every item type extends this
 */
export interface MarketplaceItemBase {
  /** Unique identifier (auto-generated) */
  id: number;
  
  /** Unique key for programmatic access (e.g., 'bot_anti_spam', 'theme_dark_pro') */
  unique_key: string;
  
  /** Display name shown to users */
  name: string;
  
  /** URL-friendly slug */
  slug: string;
  
  /** Short description for cards (max 100 chars) */
  short_description: string;
  
  /** Full description (supports markdown) */
  description: string;
  
  /** Category classification */
  category: MarketplaceCategory;
  
  /** Icon identifier (MUI icon name or URL) */
  icon: string;
  
  /** Primary color for theming (hex) */
  color: string;
  
  /** Version string */
  version: string;
  
  /** Whether item is active in marketplace */
  is_active: boolean;
  
  /** Show in featured section */
  is_featured: boolean;
  
  /** Show "Popular" badge */
  is_popular: boolean;
  
  /** Display order in listings */
  sort_order: number;
  
  /** Creation timestamp */
  created_at: string;
  
  /** Last update timestamp */
  updated_at: string;
}

/**
 * One-time purchase item (themes, widgets, AI models)
 */
export interface OneTimePurchaseItem extends MarketplaceItemBase {
  pricing_model: 'one_time';
  
  /** Price in credits */
  price_credits: number;
  
  /** Preview images */
  preview_images: string[];
  
  /** Download URL (for downloadable items) */
  download_url?: string;
  
  /** Tags for search/filtering */
  tags: string[];
  
  /** Author name */
  author: string;
  
  /** Author profile URL */
  author_url?: string;
}

/**
 * Subscription service (bot services, MTProto services)
 */
export interface SubscriptionService extends MarketplaceItemBase {
  pricing_model: 'subscription';
  
  /** Service key for feature gating */
  service_key: string;
  
  /** Monthly price in credits */
  price_credits_monthly: number;
  
  /** Yearly price in credits (optional discount) */
  price_credits_yearly?: number;
  
  /** Daily usage quota (null = unlimited) */
  usage_quota_daily: number | null;
  
  /** Monthly usage quota (null = unlimited) */
  usage_quota_monthly: number | null;
  
  /** List of features for marketing */
  features: string[];
  
  /** Requires per-chat configuration */
  requires_chat_config: boolean;
  
  /** Has usage tracking */
  tracks_usage: boolean;
}

// =============================================================================
// THEME TYPES
// =============================================================================

/**
 * Theme marketplace item
 */
export interface ThemeItem extends OneTimePurchaseItem {
  category: 'themes';
  
  /** Theme mode */
  mode: 'light' | 'dark' | 'system';
  
  /** Color palette preview */
  palette_preview: {
    primary: string;
    secondary: string;
    background: string;
    paper: string;
    text: string;
  };
}

/**
 * Theme definition for MUI
 */
export interface ThemeDefinition {
  id: string;
  name: string;
  mode: 'light' | 'dark';
  palette: {
    primary: { main: string; light?: string; dark?: string };
    secondary: { main: string; light?: string; dark?: string };
    background: { default: string; paper: string };
    text: { primary: string; secondary: string };
    divider: string;
    error?: { main: string };
    warning?: { main: string };
    info?: { main: string };
    success?: { main: string };
  };
  typography?: {
    fontFamily?: string;
    h1?: object;
    h2?: object;
    h3?: object;
    body1?: object;
    body2?: object;
  };
  shape?: {
    borderRadius: number;
  };
  components?: Record<string, object>;
}

// =============================================================================
// WIDGET TYPES
// =============================================================================

/**
 * Widget size options
 */
export type WidgetSize = 'small' | 'medium' | 'large' | 'full';

/**
 * Widget category
 */
export type WidgetCategory = 'analytics' | 'social' | 'tools' | 'monitoring';

/**
 * Widget marketplace item
 */
export interface WidgetItem extends OneTimePurchaseItem {
  category: 'widgets';
  
  /** Available sizes */
  available_sizes: WidgetSize[];
  
  /** Default size */
  default_size: WidgetSize;
  
  /** Widget subcategory */
  widget_category: WidgetCategory;
  
  /** Data source endpoint */
  data_source: string;
  
  /** Supports auto-refresh */
  refreshable: boolean;
  
  /** Default refresh interval (ms) */
  refresh_interval?: number;
  
  /** Has configuration options */
  configurable: boolean;
}

/**
 * Widget component props
 */
export interface WidgetProps {
  size: WidgetSize;
  refreshInterval?: number;
  config?: Record<string, unknown>;
}

/**
 * Widget metadata for registration
 */
export interface WidgetMetadata {
  id: string;
  name: string;
  description: string;
  sizes: readonly WidgetSize[];
  defaultSize: WidgetSize;
  category: WidgetCategory;
  dataSource: string;
  refreshable: boolean;
  configurable: boolean;
}

// =============================================================================
// SERVICE CONFIGURATION TYPES
// =============================================================================

/**
 * Base service settings that all services share
 */
export interface BaseServiceSettings {
  /** Service enabled for this chat */
  enabled: boolean;
}

/**
 * Service config component props
 */
export interface ServiceConfigProps {
  /** Chat ID to configure */
  chatId: number;
}

/**
 * Service metadata for registration
 */
export interface ServiceMetadata {
  /** Service key (e.g., 'bot_anti_spam') */
  service_key: string;
  
  /** Display name */
  name: string;
  
  /** Description for config page */
  description: string;
  
  /** Features list */
  features: string[];
  
  /** MUI icon name */
  icon: string;
  
  /** Theme color */
  color: string;
  
  /** Has per-chat settings */
  per_chat_config: boolean;
  
  /** Has usage quotas */
  has_quotas: boolean;
}

/**
 * Service registration entry
 */
export interface ServiceRegistration {
  metadata: ServiceMetadata;
  configComponent: React.ComponentType<ServiceConfigProps>;
}

// =============================================================================
// BUNDLE TYPES
// =============================================================================

/**
 * Bundle marketplace item
 */
export interface BundleItem extends MarketplaceItemBase {
  category: 'bundles';
  pricing_model: 'one_time';
  
  /** Total price for bundle */
  price_credits: number;
  
  /** Original price (sum of items) */
  original_price: number;
  
  /** Discount percentage */
  discount_percent: number;
  
  /** Items included in bundle */
  included_items: BundleIncludedItem[];
}

/**
 * Item reference in a bundle
 */
export interface BundleIncludedItem {
  item_type: 'item' | 'service';
  item_key: string;
  item_name: string;
}

// =============================================================================
// USER OWNERSHIP TYPES
// =============================================================================

/**
 * User's purchased item
 */
export interface UserPurchase {
  id: number;
  user_id: number;
  item_key: string;
  item_name: string;
  item_type: 'item' | 'service';
  purchased_at: string;
  price_paid: number;
}

/**
 * User's active subscription
 */
export interface UserSubscription {
  id: number;
  user_id: number;
  service_key: string;
  service_name: string;
  status: 'active' | 'expired' | 'cancelled';
  started_at: string;
  expires_at: string;
  auto_renew: boolean;
  usage_count_daily: number;
  usage_count_monthly: number;
  usage_quota_daily: number | null;
  usage_quota_monthly: number | null;
}

// =============================================================================
// API RESPONSE TYPES
// =============================================================================

/**
 * Marketplace listing response
 */
export interface MarketplaceListResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

/**
 * Purchase response
 */
export interface PurchaseResponse {
  success: boolean;
  purchase_id?: number;
  subscription_id?: number;
  new_balance: number;
  message: string;
}

/**
 * Service access check response
 */
export interface ServiceAccessResponse {
  has_access: boolean;
  subscription?: UserSubscription;
  quota_remaining?: {
    daily: number | null;
    monthly: number | null;
  };
}

// =============================================================================
// DEVELOPER REGISTRATION
// =============================================================================

/**
 * Complete marketplace item registration
 * Developers must provide this when creating new items
 */
export interface MarketplaceItemRegistration {
  /** Database seed data */
  seed: OneTimePurchaseItem | SubscriptionService;
  
  /** Frontend component (for widgets/themes) */
  component?: React.ComponentType<any>;
  
  /** Config component (for services) */
  configComponent?: React.ComponentType<ServiceConfigProps>;
  
  /** Metadata for UI */
  metadata: ServiceMetadata | WidgetMetadata;
  
  /** Backend handler class name (for services) */
  handlerClass?: string;
  
  /** Required database migrations */
  migrations?: string[];
}

// =============================================================================
// EXPORTS
// =============================================================================

export type MarketplaceItem = 
  | ThemeItem 
  | WidgetItem 
  | SubscriptionService 
  | BundleItem;

