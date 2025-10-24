/**
 * Invoice Management Microservice
 *
 * Single Responsibility: Manage invoices and billing only
 * Separated from: payments, subscriptions, payment methods
 */

import apiClient from '../apiClient';

export interface Invoice {
    id: string;
    subscription_id?: string;
    amount: number;
    currency: string;
    status: 'draft' | 'open' | 'paid' | 'void';
    created_at: string;
    due_date?: string;
    paid_at?: string;
    invoice_url?: string;
}

/**
 * Invoice Service
 * Focused on: Invoice and billing document management
 */
class InvoiceService {
    private baseURL = '/payments/invoices';

    /**
     * Get user's invoices
     */
    async getUserInvoices(userId: number, limit: number = 50): Promise<Invoice[]> {
        try {
            const response = await apiClient.get<{ invoices: Invoice[] }>(
                `${this.baseURL}/${userId}`,
                { params: { limit } }
            );
            return response.data.invoices || [];
        } catch (error) {
            console.error('Failed to get invoices:', error);
            throw error;
        }
    }

    /**
     * Get invoice details
     */
    async getInvoice(invoiceId: string): Promise<Invoice> {
        try {
            const response = await apiClient.get<Invoice>(
                `${this.baseURL}/detail/${invoiceId}`
            );
            return response.data;
        } catch (error) {
            console.error('Failed to get invoice:', error);
            throw error;
        }
    }

    /**
     * Download invoice PDF
     */
    async download(invoiceId: string): Promise<Blob> {
        try {
            const response = await apiClient.get<Blob>(
                `${this.baseURL}/${invoiceId}/download`,
                { responseType: 'blob' }
            );
            return response.data;
        } catch (error) {
            console.error('Failed to download invoice:', error);
            throw error;
        }
    }

    /**
     * Get invoices for a subscription
     */
    async getSubscriptionInvoices(subscriptionId: string): Promise<Invoice[]> {
        try {
            const response = await apiClient.get<{ invoices: Invoice[] }>(
                `${this.baseURL}/subscription/${subscriptionId}`
            );
            return response.data.invoices || [];
        } catch (error) {
            console.error('Failed to get subscription invoices:', error);
            throw error;
        }
    }

    /**
     * Helper: Download and save invoice
     */
    async downloadAndSave(invoiceId: string, filename?: string): Promise<void> {
        try {
            const blob = await this.download(invoiceId);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename || `invoice-${invoiceId}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Failed to download and save invoice:', error);
            throw error;
        }
    }
}

export const invoiceService = new InvoiceService();
export default invoiceService;
