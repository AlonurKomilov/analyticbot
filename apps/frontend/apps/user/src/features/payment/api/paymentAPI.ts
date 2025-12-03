/**
 * Payment API service
 * Handles all payment-related API calls
 */

import { apiClient } from '@/api/client';

interface SubscriptionData {
  plan_id: string;
  user_id: string;
  payment_method_id?: string;
  [key: string]: any;
}

interface CancelSubscriptionData {
  subscription_id: string;
  immediate?: boolean;
  reason?: string;
}

interface PaymentMethod {
  id: string;
  type: string;
  last4?: string;
  brand?: string;
  exp_month?: number;
  exp_year?: number;
}

interface Invoice {
  id: string;
  amount: number;
  currency: string;
  status: string;
  created_at: string;
  due_date?: string;
}

class PaymentAPI {
  private baseURL: string;

  constructor(baseURL: string = '/payments') {
    this.baseURL = baseURL;
  }

  /**
   * Create a new subscription
   */
  async createSubscription(data: SubscriptionData): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/create-subscription`, data);
    return response.data;
  }

  /**
   * Get user's current subscription
   */
  async getUserSubscription(userId: string): Promise<any> {
    const response: any = await apiClient.get(`${this.baseURL}/user/${userId}/subscription`);
    return response.data;
  }

  /**
   * Cancel user's subscription
   */
  async cancelSubscription(data: CancelSubscriptionData): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/cancel-subscription`, data);
    return response.data;
  }

  /**
   * Get available subscription plans
   */
  async getAvailablePlans(): Promise<any[]> {
    const response: any = await apiClient.get(`${this.baseURL}/plans`);
    return response.data;
  }

  /**
   * Get user's payment history
   */
  async getPaymentHistory(userId: string, limit: number = 50, offset: number = 0): Promise<any[]> {
    const response: any = await apiClient.get(`${this.baseURL}/user/${userId}/history`, {
      params: { limit, offset }
    });
    return response.data;
  }

  /**
   * Get payment statistics
   */
  async getPaymentStats(): Promise<any> {
    const response: any = await apiClient.get(`${this.baseURL}/stats/payments`);
    return response.data;
  }

  /**
   * Get subscription statistics
   */
  async getSubscriptionStats(): Promise<any> {
    const response: any = await apiClient.get(`${this.baseURL}/stats/subscriptions`);
    return response.data;
  }

  /**
   * Get payment system status
   */
  async getPaymentStatus(): Promise<any> {
    const response: any = await apiClient.get(`${this.baseURL}/status`);
    return response.data;
  }

  /**
   * Process Stripe webhook (usually called by backend)
   */
  async processStripeWebhook(payload: any, signature: string): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/webhook/stripe`, payload, {
      headers: {
        'Content-Type': 'application/json',
        'Stripe-Signature': signature
      }
    });
    return response.data;
  }

  /**
   * Update payment method
   */
  async updatePaymentMethod(userId: string, paymentMethodId: string): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/user/${userId}/payment-method`, {
      payment_method_id: paymentMethodId
    });
    return response.data;
  }

  /**
   * Get billing portal URL (for Stripe Customer Portal)
   */
  async getBillingPortalUrl(userId: string, returnUrl: string = window.location.href): Promise<{ url: string }> {
    const response: any = await apiClient.post(`${this.baseURL}/user/${userId}/billing-portal`, {
      return_url: returnUrl
    });
    return response.data;
  }

  /**
   * Preview subscription changes
   */
  async previewSubscriptionChange(userId: string, newPlanId: string): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/user/${userId}/preview-change`, {
      plan_id: newPlanId
    });
    return response.data;
  }

  /**
   * Change subscription plan
   */
  async changeSubscriptionPlan(userId: string, newPlanId: string, prorated: boolean = true): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/user/${userId}/change-plan`, {
      plan_id: newPlanId,
      prorated: prorated
    });
    return response.data;
  }

  /**
   * Retry failed payment
   */
  async retryPayment(paymentId: string): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/payments/${paymentId}/retry`);
    return response.data;
  }

  /**
   * Get invoice details
   */
  async getInvoice(invoiceId: string): Promise<Invoice> {
    const response: any = await apiClient.get(`${this.baseURL}/invoices/${invoiceId}`);
    return response.data;
  }

  /**
   * Download invoice PDF
   */
  async downloadInvoice(invoiceId: string): Promise<Blob> {
    const response: any = await apiClient.get(`${this.baseURL}/invoices/${invoiceId}/pdf`, {
      responseType: 'blob'
    } as any);
    return response.data;
  }

  /**
   * Get upcoming invoice
   */
  async getUpcomingInvoice(userId: string): Promise<Invoice> {
    const response: any = await apiClient.get(`${this.baseURL}/user/${userId}/upcoming-invoice`);
    return response.data;
  }

  /**
   * Apply coupon to subscription
   */
  async applyCoupon(userId: string, couponCode: string): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/user/${userId}/apply-coupon`, {
      coupon_code: couponCode
    });
    return response.data;
  }

  /**
   * Remove coupon from subscription
   */
  async removeCoupon(userId: string): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/user/${userId}/remove-coupon`);
    return response.data;
  }

  /**
   * Get tax rates for location
   */
  async getTaxRates(country: string, state: string | null = null, postalCode: string | null = null): Promise<any> {
    const response: any = await apiClient.get(`${this.baseURL}/tax-rates`, {
      params: {
        country,
        ...(state && { state }),
        ...(postalCode && { postal_code: postalCode })
      }
    });
    return response.data;
  }

  /**
   * Validate coupon code
   */
  async validateCoupon(couponCode: string): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/validate-coupon`, {
      coupon_code: couponCode
    });
    return response.data;
  }

  /**
   * Get payment methods for user
   */
  async getPaymentMethods(userId: string): Promise<PaymentMethod[]> {
    const response: any = await apiClient.get(`${this.baseURL}/user/${userId}/payment-methods`);
    return response.data;
  }

  /**
   * Delete payment method
   */
  async deletePaymentMethod(userId: string, paymentMethodId: string): Promise<any> {
    const response: any = await apiClient.delete(`${this.baseURL}/user/${userId}/payment-methods/${paymentMethodId}`);
    return response.data;
  }

  /**
   * Set default payment method
   */
  async setDefaultPaymentMethod(userId: string, paymentMethodId: string): Promise<any> {
    const response: any = await apiClient.post(`${this.baseURL}/user/${userId}/payment-methods/${paymentMethodId}/default`);
    return response.data;
  }
}

// Create and export singleton instance
export const paymentAPI = new PaymentAPI();
export default PaymentAPI;
