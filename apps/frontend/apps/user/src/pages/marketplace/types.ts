/**
 * 🏪 Unified Marketplace Type System
 *
 * Defines types for all marketplace items: AI Models, Themes, Services, Widgets, Bundles
 */

/**
 * Category types for marketplace items
 */
export type MarketplaceCategory = 'themes' | 'services' | 'widgets' | 'bundles';

/**
 * Service subcategories (technical grouping for filtering)
 */
export type ServiceSubcategory = 'all' | 'bot' | 'mtproto' | 'ai';

/**
 * Goal-oriented use cases (for discovery and "what's this good for?")
 */
export type ServiceUseCase = 
  | 'grow_community'
  | 'protect_chat'
  | 'keep_clean'
  | 'understand_audience'
  | 'power_tools';

/**
 * Pricing model for items
 */
export type PricingModel = 'one_time' | 'subscription';

/**
 * Billing cycle for subscriptions
 */
export type BillingCycle = 'monthly' | 'yearly';

/**
 * Base interface for all marketplace items
 * This unified type works for both marketplace_items and marketplace_services
 */
export interface MarketplaceItem {
    // Core identification
    id: number;
    unique_key?: string; // Combined key to prevent React key collision (item-1, service-1)
    name: string;
    slug?: string;
    service_key?: string; // For services

    // Description
    description: string;
    short_description?: string;

    // Categorization
    category: string;
    subcategory?: string;
    
    // Goal-oriented use cases (what is this good for?)
    use_cases?: ServiceUseCase[];

    // Pricing
    pricing_model: PricingModel;
    price_credits: number; // For one-time purchases or monthly price
    price_monthly?: number; // Alternative field name from services
    price_yearly?: number;

    // Features & Metadata
    features?: string[];
    metadata?: Record<string, any>;

    // Visual
    icon?: string;
    icon_url?: string;
    color?: string;
    preview_url?: string;

    // Status flags
    is_featured: boolean;
    is_premium?: boolean;
    is_popular?: boolean;
    is_new?: boolean;
    is_beta?: boolean;
    active: boolean;

    // User-specific
    user_owned?: boolean;
    user_subscribed?: boolean;

    // Stats
    download_count?: number;
    rating?: number;
    rating_count?: number;
    active_subscriptions?: number;
    total_subscriptions?: number;

    // Service-specific (for backwards compatibility)
    requires_bot?: boolean;
    requires_mtproto?: boolean;
    usage_quota_daily?: number;
    usage_quota_monthly?: number;
    rate_limit_per_minute?: number;
    min_tier?: string;

    // Documentation
    documentation_url?: string;
    demo_video_url?: string;
}

/**
 * API response for marketplace items list
 */
export interface MarketplaceListResponse {
    items?: MarketplaceItem[];
    services?: MarketplaceItem[];
    total: number;
    categories?: string[];
}

/**
 * Purchase request payload
 */
export interface PurchaseRequest {
    item_id?: number;
    service_id?: number;
    billing_cycle?: BillingCycle;
}

/**
 * Purchase response
 */
export interface PurchaseResponse {
    success: boolean;
    message: string;
    new_balance: number;
    purchase_id?: number;
    subscription_id?: number;
}

/**
 * Category configuration for UI
 */
export interface CategoryConfig {
    key: MarketplaceCategory;
    label: string;
    icon: string; // Icon name from MUI
    color: string;
    description: string;
    pricingModel: PricingModel;
}

/**
 * Service subcategory configuration (technical grouping)
 */
export interface ServiceSubcategoryConfig {
    key: ServiceSubcategory;
    label: string;
    icon: string;
    color: string;
    description: string;
    backendCategories: string[]; // Maps backend category to frontend subcategory
}

/**
 * Use case configuration (goal-oriented marketing)
 */
export interface UseCaseConfig {
    key: ServiceUseCase;
    label: string;
    icon: string;
    color: string;
    description: string;
}

/**
 * Filter options for marketplace
 */
export interface MarketplaceFilters {
    category: MarketplaceCategory;
    searchQuery: string;
    showFeaturedOnly: boolean;
    showPremiumOnly: boolean;
    billingCycle: BillingCycle;
}
