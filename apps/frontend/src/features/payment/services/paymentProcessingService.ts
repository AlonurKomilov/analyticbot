/**
 * Payment Processing Microservice
 *
 * Single Responsibility: Process individual payments only
 * Separated from: payment methods, subscriptions, invoicing
 *
 * Phase 1 Update: Using centralized payment types
 * - Changed 'completed' → 'succeeded' to match backend
 *
 * Phase 4 Update: Added runtime validation
 * - Validate API responses to catch invalid data early
 */

import { apiClient } from '@shared/services/api/apiClient';
import {
    PaymentStatus,
    PaymentProvider
} from '@/types/payment';
import {
    validatePaymentResponse,
    safeValidatePaymentsArray
} from '@/validation/apiValidators';

export interface PaymentData {
    amount: number;
    currency: string;
    payment_method_id: string;
    description?: string;
    metadata?: Record<string, any>;
}

export interface Payment {
    id: string;
    user_id: number;
    amount: number;
    currency: string;
    status: PaymentStatus;
    provider: PaymentProvider;
    description?: string;
    created_at: string;
    completed_at?: string;
}

/**
 * Payment Processing Service
 * Focused on: Payment transactions only
 */
class PaymentProcessingService {
    private baseURL = '/payments';

    /**
     * Process a payment
     * Returns payment with normalized and validated status
     */
    async process(userId: number, paymentData: PaymentData): Promise<Payment> {
        try {
            const response = await apiClient.post<Payment>(
                `${this.baseURL}/process`,
                { ...paymentData, user_id: userId }
            );
            // Validate and normalize response
            return validatePaymentResponse(response.data) as Payment;
        } catch (error) {
            console.error('Failed to process payment:', error);
            throw error;
        }
    }

    /**
     * Get payment status
     * Validates and normalizes status from backend for backward compatibility
     */
    async getStatus(paymentId: string): Promise<Payment> {
        try {
            const response = await apiClient.get<Payment>(
                `${this.baseURL}/status/${paymentId}`
            );
            // Validate and normalize response
            return validatePaymentResponse(response.data) as Payment;
        } catch (error) {
            console.error('Failed to get payment status:', error);
            throw error;
        }
    }

    /**
     * Get user's payment history
     * Safely validates all payments in response
     */
    async getHistory(userId: number, limit: number = 50): Promise<Payment[]> {
        try {
            const response = await apiClient.get<{ payments: Payment[] }>(
                `${this.baseURL}/history/${userId}`,
                { params: { limit } }
            );
            // Safely validate array, filtering out any invalid payments
            return safeValidatePaymentsArray(response.data.payments || []) as Payment[];
        } catch (error) {
            console.error('Failed to get payment history:', error);
            throw error;
        }
    }

    /**
     * Request refund
     */
    async refund(paymentId: string, reason?: string): Promise<Payment> {
        try {
            const response = await apiClient.post<Payment>(
                `${this.baseURL}/refund/${paymentId}`,
                { reason }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to refund payment:', error);
            throw error;
        }
    }
}

export const paymentProcessingService = new PaymentProcessingService();
export default paymentProcessingService;
