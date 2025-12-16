/**
 * Marketplace Services API
 * 
 * API client functions for subscription services.
 * 
 * @module features/marketplace/api/services
 */

import { apiClient } from '@/api/client';
import type { 
  SubscriptionService,
  UserSubscription,
  BillingCycle,
} from '../types';

// Local type aliases for better readability
type MarketplaceService = SubscriptionService;
type ServiceSubscription = UserSubscription;

// =============================================================================
// TYPES
// =============================================================================

export interface ServicesQueryParams {
  category?: string;
  featured?: boolean;
  limit?: number;
}

export interface SubscribeRequest {
  service_key: string;
  billing_cycle: BillingCycle;
}

export interface CancelSubscriptionRequest {
  subscription_id: number;
  reason?: string;
}

// =============================================================================
// SERVICES CATALOG API
// =============================================================================

/**
 * Get service catalog
 */
export async function getServiceCatalog(params?: ServicesQueryParams): Promise<MarketplaceService[]> {
  const response = await apiClient.get<{ services: MarketplaceService[] }>('/marketplace/services', { params });
  return response.services;
}

/**
 * Get featured services
 */
export async function getFeaturedServices(limit: number = 5): Promise<MarketplaceService[]> {
  return apiClient.get<MarketplaceService[]>('/marketplace/services/featured', {
    params: { limit },
  });
}

/**
 * Get service details by key
 */
export async function getServiceByKey(serviceKey: string): Promise<MarketplaceService> {
  return apiClient.get<MarketplaceService>(`/marketplace/services/${serviceKey}`);
}

// =============================================================================
// SUBSCRIPTIONS API
// =============================================================================

/**
 * Subscribe to a service
 */
export async function subscribeToService(request: SubscribeRequest): Promise<ServiceSubscription> {
  return apiClient.post<ServiceSubscription>('/marketplace/services/subscribe', request);
}

/**
 * Get user's subscriptions
 */
export async function getUserSubscriptions(includeExpired: boolean = false): Promise<ServiceSubscription[]> {
  const response = await apiClient.get<{ subscriptions: ServiceSubscription[] }>('/marketplace/subscriptions', {
    params: { include_expired: includeExpired },
  });
  return response.subscriptions;
}

/**
 * Get user's active subscriptions
 */
export async function getActiveSubscriptions(): Promise<ServiceSubscription[]> {
  const response = await apiClient.get<{ subscriptions: ServiceSubscription[] }>('/marketplace/subscriptions/active');
  return response.subscriptions;
}

/**
 * Cancel a subscription
 */
export async function cancelSubscription(request: CancelSubscriptionRequest): Promise<{ success: boolean; message: string }> {
  return apiClient.post<{ success: boolean; message: string }>('/marketplace/subscriptions/cancel', request);
}

/**
 * Toggle auto-renew for a subscription
 */
export async function toggleAutoRenew(
  subscriptionId: number, 
  autoRenew: boolean
): Promise<{ success: boolean; message: string }> {
  return apiClient.post<{ success: boolean; message: string }>('/marketplace/subscriptions/auto-renew', {
    subscription_id: subscriptionId,
    auto_renew: autoRenew,
  });
}

// =============================================================================
// FEATURE ACCESS API
// =============================================================================

/**
 * Check if user has access to a service
 */
export async function checkServiceAccess(serviceKey: string): Promise<{ 
  service_key: string; 
  has_access: boolean; 
}> {
  return apiClient.get<{ service_key: string; has_access: boolean }>(`/marketplace/access/${serviceKey}`);
}

/**
 * Check quota for a service
 */
export async function checkServiceQuota(
  serviceKey: string, 
  checkType: 'daily' | 'monthly' = 'daily'
): Promise<{
  service_key: string;
  limit: number | null;
  used: number;
  remaining: number | null;
  exceeded: boolean;
}> {
  return apiClient.get<{
    service_key: string;
    limit: number | null;
    used: number;
    remaining: number | null;
    exceeded: boolean;
  }>(`/marketplace/access/${serviceKey}/quota`, {
    params: { check_type: checkType },
  });
}

/**
 * Get all services user has access to
 */
export async function getUserFeatures(): Promise<{ features: string[] }> {
  return apiClient.get<{ features: string[] }>('/marketplace/features');
}

// =============================================================================
// USAGE TRACKING API
// =============================================================================

/**
 * Get usage statistics for a subscription
 */
export async function getSubscriptionUsage(
  subscriptionId: number, 
  days: number = 30
): Promise<{
  subscription_id: number;
  total_usage: number;
  daily_breakdown: { date: string; count: number }[];
}> {
  return apiClient.get<{
    subscription_id: number;
    total_usage: number;
    daily_breakdown: { date: string; count: number }[];
  }>(`/marketplace/subscriptions/${subscriptionId}/usage`, {
    params: { days },
  });
}
