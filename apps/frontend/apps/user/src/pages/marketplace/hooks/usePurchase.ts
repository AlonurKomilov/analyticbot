/**
 * 🛒 Purchase Hook
 *
 * Handles purchasing marketplace items and services
 */

import { useState, useCallback } from 'react';
import { apiClient } from '@/api/client';
import { MarketplaceItem, BillingCycle, PurchaseResponse } from '../types';

export const usePurchase = () => {
    const [purchasing, setPurchasing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const purchaseItem = useCallback(async (
        item: MarketplaceItem,
        billingCycle: BillingCycle = 'monthly'
    ): Promise<PurchaseResponse> => {
        setPurchasing(true);
        setError(null);

        try {
            let response: any;

            if (item.pricing_model === 'one_time') {
                // Purchase one-time item
                response = await apiClient.post('/marketplace/purchase', {
                    item_id: item.id,
                });
            } else {
                // Purchase subscription service
                const serviceKey = item.service_key || item.slug || `service-${item.id}`;
                response = await apiClient.post(`/services/${serviceKey}/purchase`, {
                    billing_cycle: billingCycle,
                });
            }

            // Normalize response format
            return {
                success: true,
                message: response.message || `Successfully purchased ${item.name}!`,
                new_balance: response.new_balance || response.credits_spent, // Backend may not return new balance
                purchase_id: response.purchase_id,
                subscription_id: response.subscription_id,
            };
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || 'Failed to complete purchase';
            setError(errorMessage);
            throw new Error(errorMessage);
        } finally {
            setPurchasing(false);
        }
    }, []);

    return {
        purchaseItem,
        purchasing,
        error,
        clearError: () => setError(null),
    };
};
