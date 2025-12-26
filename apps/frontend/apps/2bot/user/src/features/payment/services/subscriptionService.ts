/**
 * Subscription Management Microservice
 *
 * Single Responsibility: Manage subscriptions only
 * Separated from: payments, payment methods, invoicing
 *
 * Phase 1 Update: Using centralized subscription types
 * - Fixed 'cancelled' → 'canceled' (American spelling)
 * - Added missing statuses: trialing, incomplete, unpaid
 *
 * Phase 4 Update: Added runtime validation
 * - Validate API responses to catch invalid data early
 */

import { apiClient } from '@/api/client';
import {
    SubscriptionStatus
} from '@/types/payment';
import {
    validateSubscriptionResponse,
    safeValidateSubscriptionsArray
} from '@/validation/apiValidators';

export interface SubscriptionData {
    plan_id: string;
    payment_method_id: string;
    trial_days?: number;
    metadata?: Record<string, any>;
}

export interface Subscription {
    id: string;
    user_id: number;
    plan_id: string;
    status: SubscriptionStatus;
    current_period_start: string;
    current_period_end: string;
    cancel_at?: string;
    trial_end?: string;           // ✅ ADDED: for trialing status support
    created_at: string;
}

export interface SubscriptionPlan {
    id: string;
    name: string;
    description: string;
    price: number;
    currency: string;
    interval: 'day' | 'week' | 'month' | 'year';
    features: string[];
}

/**
 * Subscription Service
 * Focused on: Subscription lifecycle management
 */
class SubscriptionService {
    private baseURL = '/payments/subscriptions';

    /**
     * Get available subscription plans
     */
    async getPlans(): Promise<SubscriptionPlan[]> {
        try {
            const response = await apiClient.get<{ plans: SubscriptionPlan[] }>(
                `${this.baseURL}/plans`
            );
            return response.plans || [];
        } catch (error) {
            console.error('Failed to get subscription plans:', error);
            throw error;
        }
    }

    /**
     * Create subscription
     * Returns subscription with validated and normalized status
     */
    async create(userId: number, subscriptionData: SubscriptionData): Promise<Subscription> {
        try {
            const response = await apiClient.post<Subscription>(
                this.baseURL,
                { ...subscriptionData, user_id: userId }
            );
            // Validate and normalize response
            return validateSubscriptionResponse(response) as Subscription;
        } catch (error) {
            console.error('Failed to create subscription:', error);
            throw error;
        }
    }

    /**
     * Get user subscriptions
     * Returns array of subscriptions with validated and normalized statuses
     */
    async getUserSubscriptions(userId: number): Promise<Subscription[]> {
        try {
            const response = await apiClient.get<Subscription[]>(`${this.baseURL}/user/${userId}`);
            // Safely validate array, filtering out any invalid subscriptions
            return safeValidateSubscriptionsArray(response) as Subscription[];
        } catch (error) {
            console.error('Failed to fetch user subscriptions:', error);
            throw error;
        }
    }

    /**
     * Get subscription details
     * Returns subscription with validated and normalized status
     */
    async getSubscription(subscriptionId: string): Promise<Subscription> {
        try {
            const response = await apiClient.get<Subscription>(
                `${this.baseURL}/detail/${subscriptionId}`
            );
            // Validate and normalize response
            return validateSubscriptionResponse(response) as Subscription;
        } catch (error) {
            console.error('Failed to get subscription:', error);
            throw error;
        }
    }

    /**
     * Cancel subscription
     */
    async cancel(subscriptionId: string, immediate: boolean = false): Promise<Subscription> {
        try {
            const response = await apiClient.post<Subscription>(
                `${this.baseURL}/${subscriptionId}/cancel`,
                { immediate }
            );
            return response;
        } catch (error) {
            console.error('Failed to cancel subscription:', error);
            throw error;
        }
    }

    /**
     * Resume cancelled subscription
     */
    async resume(subscriptionId: string): Promise<Subscription> {
        try {
            const response = await apiClient.post<Subscription>(
                `${this.baseURL}/${subscriptionId}/resume`
            );
            return response;
        } catch (error) {
            console.error('Failed to resume subscription:', error);
            throw error;
        }
    }

    /**
     * Update subscription (change plan)
     */
    async updatePlan(subscriptionId: string, newPlanId: string): Promise<Subscription> {
        try {
            const response = await apiClient.patch<Subscription>(
                `${this.baseURL}/${subscriptionId}`,
                { plan_id: newPlanId }
            );
            return response;
        } catch (error) {
            console.error('Failed to update subscription:', error);
            throw error;
        }
    }
}

export const subscriptionService = new SubscriptionService();
export default subscriptionService;
