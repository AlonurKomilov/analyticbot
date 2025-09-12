/**
 * Payment API service
 * Handles all payment-related API calls
 */

import { apiClient } from './apiClient';

class PaymentAPI {
  constructor(baseURL = '/api/payments') {
    this.baseURL = baseURL;
  }

  /**
   * Create a new subscription
   */
  async createSubscription(data) {
    const response = await apiClient.post(`${this.baseURL}/create-subscription`, data);
    return response.data;
  }

  /**
   * Get user's current subscription
   */
  async getUserSubscription(userId) {
    const response = await apiClient.get(`${this.baseURL}/user/${userId}/subscription`);
    return response.data;
  }

  /**
   * Cancel user's subscription
   */
  async cancelSubscription(data) {
    const response = await apiClient.post(`${this.baseURL}/cancel-subscription`, data);
    return response.data;
  }

  /**
   * Get available subscription plans
   */
  async getAvailablePlans() {
    const response = await apiClient.get(`${this.baseURL}/plans`);
    return response.data;
  }

  /**
   * Get user's payment history
   */
  async getPaymentHistory(userId, limit = 50, offset = 0) {
    const response = await apiClient.get(`${this.baseURL}/user/${userId}/history`, {
      params: { limit, offset }
    });
    return response.data;
  }

  /**
   * Get payment statistics
   */
  async getPaymentStats() {
    const response = await apiClient.get(`${this.baseURL}/stats/payments`);
    return response.data;
  }

  /**
   * Get subscription statistics
   */
  async getSubscriptionStats() {
    const response = await apiClient.get(`${this.baseURL}/stats/subscriptions`);
    return response.data;
  }

  /**
   * Get payment system status
   */
  async getPaymentStatus() {
    const response = await apiClient.get(`${this.baseURL}/status`);
    return response.data;
  }

  /**
   * Process Stripe webhook (usually called by backend)
   */
  async processStripeWebhook(payload, signature) {
    const response = await apiClient.post(`${this.baseURL}/webhook/stripe`, payload, {
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
  async updatePaymentMethod(userId, paymentMethodId) {
    const response = await apiClient.post(`${this.baseURL}/user/${userId}/payment-method`, {
      payment_method_id: paymentMethodId
    });
    return response.data;
  }

  /**
   * Get billing portal URL (for Stripe Customer Portal)
   */
  async getBillingPortalUrl(userId, returnUrl = window.location.href) {
    const response = await apiClient.post(`${this.baseURL}/user/${userId}/billing-portal`, {
      return_url: returnUrl
    });
    return response.data;
  }

  /**
   * Preview subscription changes
   */
  async previewSubscriptionChange(userId, newPlanId) {
    const response = await apiClient.post(`${this.baseURL}/user/${userId}/preview-change`, {
      plan_id: newPlanId
    });
    return response.data;
  }

  /**
   * Change subscription plan
   */
  async changeSubscriptionPlan(userId, newPlanId, prorated = true) {
    const response = await apiClient.post(`${this.baseURL}/user/${userId}/change-plan`, {
      plan_id: newPlanId,
      prorated: prorated
    });
    return response.data;
  }

  /**
   * Retry failed payment
   */
  async retryPayment(paymentId) {
    const response = await apiClient.post(`${this.baseURL}/payments/${paymentId}/retry`);
    return response.data;
  }

  /**
   * Get invoice details
   */
  async getInvoice(invoiceId) {
    const response = await apiClient.get(`${this.baseURL}/invoices/${invoiceId}`);
    return response.data;
  }

  /**
   * Download invoice PDF
   */
  async downloadInvoice(invoiceId) {
    const response = await apiClient.get(`${this.baseURL}/invoices/${invoiceId}/pdf`, {
      responseType: 'blob'
    });
    return response.data;
  }

  /**
   * Get upcoming invoice
   */
  async getUpcomingInvoice(userId) {
    const response = await apiClient.get(`${this.baseURL}/user/${userId}/upcoming-invoice`);
    return response.data;
  }

  /**
   * Apply coupon to subscription
   */
  async applyCoupon(userId, couponCode) {
    const response = await apiClient.post(`${this.baseURL}/user/${userId}/apply-coupon`, {
      coupon_code: couponCode
    });
    return response.data;
  }

  /**
   * Remove coupon from subscription
   */
  async removeCoupon(userId) {
    const response = await apiClient.post(`${this.baseURL}/user/${userId}/remove-coupon`);
    return response.data;
  }

  /**
   * Get tax rates for location
   */
  async getTaxRates(country, state = null, postalCode = null) {
    const response = await apiClient.get(`${this.baseURL}/tax-rates`, {
      params: { country, state, postal_code: postalCode }
    });
    return response.data;
  }

  /**
   * Validate coupon code
   */
  async validateCoupon(couponCode) {
    const response = await apiClient.post(`${this.baseURL}/validate-coupon`, {
      coupon_code: couponCode
    });
    return response.data;
  }

  /**
   * Get payment methods for user
   */
  async getPaymentMethods(userId) {
    const response = await apiClient.get(`${this.baseURL}/user/${userId}/payment-methods`);
    return response.data;
  }

  /**
   * Delete payment method
   */
  async deletePaymentMethod(userId, paymentMethodId) {
    const response = await apiClient.delete(`${this.baseURL}/user/${userId}/payment-methods/${paymentMethodId}`);
    return response.data;
  }

  /**
   * Set default payment method
   */
  async setDefaultPaymentMethod(userId, paymentMethodId) {
    const response = await apiClient.post(`${this.baseURL}/user/${userId}/payment-methods/${paymentMethodId}/default`);
    return response.data;
  }
}

// Create and export singleton instance
export const paymentAPI = new PaymentAPI();
export default PaymentAPI;
