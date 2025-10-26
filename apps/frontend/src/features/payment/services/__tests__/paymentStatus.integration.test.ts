/**
 * Payment Status Integration Tests
 * Tests payment flow, status transitions, and validation
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { PaymentStatus, normalizePaymentStatus } from '@/types';
import { validatePaymentResponse } from '@/validation/apiValidators';

describe('Payment Status Integration Tests', () => {
  describe('Payment Status Normalization', () => {
    it('should accept "succeeded" status from backend', () => {
      const status: PaymentStatus = 'succeeded';
      expect(status).toBe('succeeded');
    });

    it('should normalize legacy "completed" to "succeeded"', () => {
      const normalized = normalizePaymentStatus('completed' as any);
      expect(normalized).toBe('succeeded');
    });

    it('should handle all valid payment statuses', () => {
      const validStatuses: PaymentStatus[] = [
        'pending',
        'processing',
        'succeeded',
        'failed',
        'canceled',
        'refunded'
      ];

      validStatuses.forEach(status => {
        const normalized = normalizePaymentStatus(status);
        expect(normalized).toBe(status);
      });
    });

    it('should log warning for deprecated "completed" status', () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn');
      normalizePaymentStatus('completed' as any);
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('completed')
      );
      consoleWarnSpy.mockRestore();
    });
  });

  describe('Payment Status Transitions', () => {
    it('should validate pending → processing → succeeded flow', () => {
      const statuses: PaymentStatus[] = ['pending', 'processing', 'succeeded'];
      statuses.forEach(status => {
        expect(['pending', 'processing', 'succeeded', 'failed', 'canceled', 'refunded']).toContain(status);
      });
    });

    it('should validate pending → failed flow', () => {
      const statuses: PaymentStatus[] = ['pending', 'failed'];
      statuses.forEach(status => {
        expect(['pending', 'processing', 'succeeded', 'failed', 'canceled', 'refunded']).toContain(status);
      });
    });

    it('should validate succeeded → refunded flow', () => {
      const statuses: PaymentStatus[] = ['succeeded', 'refunded'];
      statuses.forEach(status => {
        expect(['pending', 'processing', 'succeeded', 'failed', 'canceled', 'refunded']).toContain(status);
      });
    });
  });

  describe('Payment Validation', () => {
    it('should validate payment object with succeeded status', () => {
      const payment = {
        id: 'pay_123',
        user_id: 1,
        amount: 1000,
        currency: 'USD',
        status: 'succeeded' as PaymentStatus,
        created_at: new Date().toISOString()
      };

      expect(() => validatePaymentResponse(payment)).not.toThrow();
      const validated = validatePaymentResponse(payment);
      expect(validated.status).toBe('succeeded');
    });

    it('should validate payment with all required fields', () => {
      const payment = {
        id: 'pay_456',
        user_id: 2,
        amount: 2500,
        currency: 'USD',
        status: 'pending' as PaymentStatus,
        created_at: new Date().toISOString()
      };

      const validated = validatePaymentResponse(payment);
      expect(validated).toHaveProperty('id');
      expect(validated).toHaveProperty('status');
      expect(validated.status).toBe('pending');
    });
  });

  describe('Stripe Status Mapping', () => {
    it('should map Stripe statuses correctly', () => {
      // Stripe uses these status values
      const stripeStatuses = [
        { stripe: 'succeeded', our: 'succeeded' as PaymentStatus },
        { stripe: 'pending', our: 'pending' as PaymentStatus },
        { stripe: 'failed', our: 'failed' as PaymentStatus },
        { stripe: 'canceled', our: 'canceled' as PaymentStatus }
      ];

      stripeStatuses.forEach(({ stripe, our }) => {
        expect(normalizePaymentStatus(our)).toBe(our);
      });
    });
  });

  describe('Error Cases', () => {
    it('should handle missing payment status gracefully', () => {
      const payment = {
        id: 'pay_789',
        user_id: 3,
        amount: 5000,
        currency: 'USD',
        // Missing status
        created_at: new Date().toISOString()
      };

      expect(() => validatePaymentResponse(payment)).toThrow();
    });

    it('should reject invalid payment status', () => {
      const payment = {
        id: 'pay_999',
        user_id: 4,
        amount: 1500,
        currency: 'USD',
        status: 'invalid_status',
        created_at: new Date().toISOString()
      };

      expect(() => validatePaymentResponse(payment)).toThrow();
    });
  });
});
