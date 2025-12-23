/**
 * Payment Methods Microservice
 *
 * Single Responsibility: Manage user payment methods only
 * Separated from: payment processing, subscriptions, invoicing
 */

import { apiClient } from '@/api/client';

export type PaymentProvider = 'stripe' | 'paypal' | 'crypto';

export interface PaymentMethodData {
    method_type: string;
    provider: PaymentProvider;
    last_four?: string;
    brand?: string;
    metadata?: Record<string, any>;
}

export interface PaymentMethod {
    id: string;
    user_id: number;
    method_type: string;
    provider: PaymentProvider;
    last_four?: string;
    brand?: string;
    is_default: boolean;
    created_at: string;
}

/**
 * Payment Methods Service
 * Focused on: CRUD operations for payment methods
 */
class PaymentMethodsService {
    private baseURL = '/payments/methods';

    /**
     * Create new payment method
     */
    async create(userId: number, methodData: PaymentMethodData): Promise<PaymentMethod> {
        try {
            const response = await apiClient.post<PaymentMethod>(
                this.baseURL,
                methodData,
                { params: { user_id: userId } }
            );
            return response;
        } catch (error) {
            console.error('Failed to create payment method:', error);
            throw error;
        }
    }

    /**
     * Get user's payment methods
     */
    async getUserMethods(userId: number): Promise<PaymentMethod[]> {
        try {
            const response = await apiClient.get<{ methods: PaymentMethod[] }>(
                `${this.baseURL}/${userId}`
            );
            return response.methods || [];
        } catch (error) {
            console.error('Failed to get payment methods:', error);
            throw error;
        }
    }

    /**
     * Get single payment method details
     */
    async getMethod(methodId: string): Promise<PaymentMethod> {
        try {
            const response = await apiClient.get<PaymentMethod>(
                `${this.baseURL}/detail/${methodId}`
            );
            return response;
        } catch (error) {
            console.error('Failed to get payment method:', error);
            throw error;
        }
    }

    /**
     * Set default payment method
     */
    async setDefault(methodId: string): Promise<{ success: boolean }> {
        try {
            const response = await apiClient.patch<{ success: boolean }>(
                `${this.baseURL}/${methodId}/default`
            );
            return response;
        } catch (error) {
            console.error('Failed to set default method:', error);
            throw error;
        }
    }

    /**
     * Delete payment method
     */
    async delete(methodId: string): Promise<{ success: boolean }> {
        try {
            const response = await apiClient.delete<{ success: boolean }>(
                `${this.baseURL}/${methodId}`
            );
            return response;
        } catch (error) {
            console.error('Failed to delete payment method:', error);
            throw error;
        }
    }
}

export const paymentMethodsService = new PaymentMethodsService();
export default paymentMethodsService;
