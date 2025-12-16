/**
 * Marketplace Items API
 * 
 * API client functions for one-time purchase items (themes, widgets, bundles).
 * 
 * @module features/marketplace/api/items
 */

import { apiClient } from '@/api/client';
import type { 
  MarketplaceItem, 
  MarketplaceCategory,
  UserPurchase,
  BundleItem,
} from '../types';

// Local type aliases for backward compatibility
type ItemPurchase = UserPurchase;
type Bundle = BundleItem;

// Review type definition (not in main types yet)
interface ItemReview {
  id: number;
  user_id: number;
  item_id: number;
  rating: number;
  review_text?: string;
  created_at: string;
}

// =============================================================================
// TYPES
// =============================================================================

export interface ItemsQueryParams {
  category?: MarketplaceCategory;
  search?: string;
  featured?: boolean;
  limit?: number;
  offset?: number;
}

export interface PurchaseItemRequest {
  item_id: number;
  quantity?: number;
}

export interface ReviewRequest {
  item_id: number;
  rating: number;
  review_text?: string;
}

// =============================================================================
// ITEMS API
// =============================================================================

/**
 * Get marketplace items with optional filtering
 */
export async function getMarketplaceItems(params?: ItemsQueryParams): Promise<MarketplaceItem[]> {
  const response = await apiClient.get<{ items: MarketplaceItem[] }>('/marketplace/items', { params });
  return response.items;
}

/**
 * Get a single item by slug
 */
export async function getItemBySlug(slug: string): Promise<MarketplaceItem> {
  return apiClient.get<MarketplaceItem>(`/marketplace/items/${slug}`);
}

/**
 * Get a single item by ID
 */
export async function getItemById(id: number): Promise<MarketplaceItem> {
  return apiClient.get<MarketplaceItem>(`/marketplace/items/by-id/${id}`);
}

/**
 * Get featured items
 */
export async function getFeaturedItems(limit: number = 5): Promise<MarketplaceItem[]> {
  const response = await apiClient.get<{ items: MarketplaceItem[] }>('/marketplace/items', {
    params: { featured: true, limit },
  });
  return response.items;
}

/**
 * Get item categories
 */
export async function getItemCategories(): Promise<{ id: string; name: string; count: number }[]> {
  const response = await apiClient.get<{ categories: { id: string; name: string; count: number }[] }>('/marketplace/categories');
  return response.categories;
}

// =============================================================================
// PURCHASES API
// =============================================================================

/**
 * Purchase an item
 */
export async function purchaseItem(request: PurchaseItemRequest): Promise<ItemPurchase> {
  return apiClient.post<ItemPurchase>('/marketplace/items/purchase', request);
}

/**
 * Get user's purchases
 */
export async function getUserPurchases(): Promise<ItemPurchase[]> {
  const response = await apiClient.get<{ purchases: ItemPurchase[] }>('/marketplace/purchases');
  return response.purchases;
}

/**
 * Check if user has purchased an item
 */
export async function hasUserPurchased(itemId: number): Promise<boolean> {
  const response = await apiClient.get<{ has_purchased: boolean }>(`/marketplace/purchases/${itemId}/check`);
  return response.has_purchased;
}

// =============================================================================
// REVIEWS API
// =============================================================================

/**
 * Add a review for an item
 */
export async function addItemReview(request: ReviewRequest): Promise<ItemReview> {
  return apiClient.post<ItemReview>('/marketplace/items/review', request);
}

/**
 * Get reviews for an item
 */
export async function getItemReviews(itemId: number): Promise<ItemReview[]> {
  const response = await apiClient.get<{ reviews: ItemReview[] }>(`/marketplace/items/${itemId}/reviews`);
  return response.reviews;
}

// =============================================================================
// BUNDLES API  
// =============================================================================

/**
 * Get available bundles
 */
export async function getBundles(): Promise<Bundle[]> {
  const response = await apiClient.get<{ bundles: Bundle[] }>('/marketplace/bundles');
  return response.bundles;
}

/**
 * Purchase a bundle
 */
export async function purchaseBundle(bundleId: number): Promise<{ success: boolean; message: string }> {
  return apiClient.post<{ success: boolean; message: string }>('/marketplace/bundles/purchase', { bundle_id: bundleId });
}

/**
 * Get user's purchased bundles
 */
export async function getUserBundles(): Promise<Bundle[]> {
  const response = await apiClient.get<{ bundles: Bundle[] }>('/marketplace/bundles/my');
  return response.bundles;
}
