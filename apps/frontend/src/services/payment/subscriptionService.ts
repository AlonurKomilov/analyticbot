/**
 * Subscription Management Microservice
 * 
 * Single Responsibility: Manage subscriptions only
 * Separated from: payments, payment methods, invoicing
 */

import apiClient from '../apiClient';

export type SubscriptionStatus = 'active' | 'inactive' | 'cancelled' | 'past_due';

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
            return response.data.plans || [];
        } catch (error) {
            console.error('Failed to get subscription plans:', error);
            throw error;
        }
    }

    /**
     * Create subscription
     */
    async create(userId: number, subscriptionData: SubscriptionData): Promise<Subscription> {
        try {
            const response = await apiClient.post<Subscription>(
                this.baseURL,
                { ...subscriptionData, user_id: userId }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to create subscription:', error);
            throw error;
        }
    }

    /**
     * Get user's subscriptions
     */
    async getUserSubscriptions(userId: number): Promise<Subscription[]> {
        try {
            const response = await apiClient.get<{ subscriptions: Subscription[] }>(
                `${this.baseURL}/${userId}`
            );
            return response.data.subscriptions || [];
        } catch (error) {
            console.error('Failed to get subscriptions:', error);
            throw error;
        }
    }

    /**
     * Get subscription details
     */
    async getSubscription(subscriptionId: string): Promise<Subscription> {
        try {
            const response = await apiClient.get<Subscription>(
                `${this.baseURL}/detail/${subscriptionId}`
            );
            return response.data;
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
            return response.data;
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
            return response.data;
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
            return response.data;
        } catch (error) {
            console.error('Failed to update subscription:', error);
            throw error;
        }
    }
}

export const subscriptionService = new SubscriptionService();
export default subscriptionService;
