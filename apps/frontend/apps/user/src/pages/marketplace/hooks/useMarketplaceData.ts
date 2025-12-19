/**
 * 📦 Marketplace Data Hook
 *
 * Fetches marketplace items and services with filtering support
 */

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/api/client';
import { MarketplaceItem, MarketplaceCategory, MarketplaceListResponse } from '../types';
import { mapBackendCategory, SERVICE_USE_CASE_MAP } from '../utils/categoryConfig';

interface UseMarketplaceDataOptions {
    category: MarketplaceCategory;
    searchQuery?: string;
    showFeaturedOnly?: boolean;
    showPremiumOnly?: boolean;
}

export const useMarketplaceData = (options: UseMarketplaceDataOptions) => {
    const { category, searchQuery, showFeaturedOnly, showPremiumOnly } = options;
    
    const [items, setItems] = useState<MarketplaceItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [userPurchases, setUserPurchases] = useState<number[]>([]);
    const [userSubscriptions, setUserSubscriptions] = useState<string[]>([]);

    // Fetch marketplace data
    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const requests: Promise<any>[] = [];

            // Fetch items based on category
            if (category === 'themes' || category === 'widgets' || category === 'bundles') {
                // Note: Currently filtering out items as they're mock data
                // Backend has items seeded but they're placeholders until real implementation
                // When ready to show items, uncomment this:
                /*
                requests.push(
                    apiClient.get<MarketplaceListResponse>('/marketplace/items', {
                        params: {
                            category: category,
                            is_featured: showFeaturedOnly || undefined,
                            is_premium: showPremiumOnly || undefined,
                            search: searchQuery || undefined,
                        }
                    })
                );
                */
            }

            // Fetch services
            if (category === 'services') {
                requests.push(
                    apiClient.get<MarketplaceListResponse>('/services', {
                        params: {
                            featured: showFeaturedOnly || undefined,
                            search: searchQuery || undefined,
                        }
                    })
                );
            }

            // Fetch user purchases
            requests.push(
                apiClient.get<{ purchases: { item_id: number }[] }>('/marketplace/purchases')
            );

            // Fetch user's service subscriptions to mark as owned
            requests.push(
                apiClient.get<{ subscriptions: { service_key: string }[] }>('/services/user/active').catch(() => ({ subscriptions: [] }))
            );

            const responses = await Promise.all(requests);
            
            // Combine items and services
            const allItems: MarketplaceItem[] = [];
            
            responses.forEach(response => {
                if (response.items) {
                    // Normalize marketplace items
                    const normalizedItems = response.items.map((item: any) => ({
                        ...item,
                        unique_key: `item-${item.id}`, // Add unique key to prevent React key collision
                        pricing_model: 'one_time' as const,
                        price_credits: item.price_credits,
                        category: mapBackendCategory(item.category),
                        user_owned: false, // Will be set based on purchases
                    }));
                    allItems.push(...normalizedItems);
                }
                
                if (response.services) {
                    // Normalize services
                    const normalizedServices = response.services.map((service: any) => ({
                        ...service,
                        unique_key: `service-${service.id}`, // Add unique key to prevent React key collision
                        pricing_model: 'subscription' as const,
                        price_credits: service.price_credits_monthly || service.price_monthly,
                        price_monthly: service.price_credits_monthly || service.price_monthly,
                        price_yearly: service.price_credits_yearly || service.price_yearly,
                        // Keep original backend category for subcategory filtering (bot_service, mtproto_services, etc.)
                        category: service.category,
                        user_owned: service.user_subscribed || false,
                        // Add goal-oriented use cases for discovery
                        use_cases: SERVICE_USE_CASE_MAP[service.service_key] || [],
                    }));
                    allItems.push(...normalizedServices);
                }

                if (response.purchases) {
                    setUserPurchases(response.purchases.map((p: any) => p.item_id));
                }

                // Handle user subscriptions from /services/user/active
                if (response.subscriptions) {
                    setUserSubscriptions(response.subscriptions.map((s: any) => s.service_key));
                }
            });

            setItems(allItems);
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to load marketplace');
            console.error('Failed to fetch marketplace data:', err);
        } finally {
            setLoading(false);
        }
    }, [category, searchQuery, showFeaturedOnly, showPremiumOnly]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Mark items as owned based on purchases and subscriptions
    const itemsWithOwnership = items.map(item => ({
        ...item,
        user_owned: !!(item.user_owned || 
                    userPurchases.includes(item.id) || 
                    (item.service_key && userSubscriptions.includes(item.service_key))),
    }));

    return {
        items: itemsWithOwnership,
        loading,
        error,
        refetch: fetchData,
        userPurchases,
        userSubscriptions,
    };
};
