/**
 * Subscription Status Integration Tests
 * Tests subscription lifecycle, status transitions, and validation
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SubscriptionStatus, normalizeSubscriptionStatus } from '../../../types/payment';
import { validateSubscriptionResponse } from '../../../validation/apiValidators';
import { getSubscriptionStatusMessage } from '../../../utils/subscriptionMessages';

describe('Subscription Status Integration Tests', () => {
  describe('Subscription Status Normalization', () => {
    it('should use American spelling "canceled" (1 L)', () => {
      const status: SubscriptionStatus = 'canceled';
      expect(status).toBe('canceled');
    });

    it('should normalize British spelling "cancelled" to "canceled"', () => {
      const normalized = normalizeSubscriptionStatus('cancelled' as any);
      expect(normalized).toBe('canceled');
    });

    it('should handle all valid subscription statuses', () => {
      const validStatuses: SubscriptionStatus[] = [
        'active',
        'canceled',
        'past_due',
        'unpaid',
        'trialing',
        'incomplete'
      ];

      validStatuses.forEach(status => {
        const normalized = normalizeSubscriptionStatus(status);
        expect(normalized).toBe(status);
      });
    });

    it('should log warning for deprecated "cancelled" spelling', () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn');
      normalizeSubscriptionStatus('cancelled' as any);
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('cancelled')
      );
      consoleWarnSpy.mockRestore();
    });

    it('should handle legacy "inactive" status', () => {
      const consoleWarnSpy = vi.spyOn(console, 'warn');
      const normalized = normalizeSubscriptionStatus('inactive' as any);
      expect(normalized).toBe('canceled');
      expect(consoleWarnSpy).toHaveBeenCalledWith(
        expect.stringContaining('inactive')
      );
      consoleWarnSpy.mockRestore();
    });
  });

  describe('Subscription Lifecycle States', () => {
    it('should handle trial period state', () => {
      const subscription = {
        id: 'sub_trial_123',
        user_id: 1,
        plan_id: 'plan_pro',
        status: 'trialing' as SubscriptionStatus,
        current_period_start: new Date().toISOString(),
        current_period_end: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
        trial_end: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
        created_at: new Date().toISOString()
      };

      const validated = validateSubscriptionResponse(subscription);
      expect(validated.status).toBe('trialing');
    });

    it('should handle active subscription', () => {
      const subscription = {
        id: 'sub_active_456',
        user_id: 2,
        plan_id: 'plan_start',
        status: 'active' as SubscriptionStatus,
        current_period_start: new Date().toISOString(),
        current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        created_at: new Date().toISOString()
      };

      const validated = validateSubscriptionResponse(subscription);
      expect(validated.status).toBe('active');
    });

    it('should handle past_due subscription (payment failed)', () => {
      const subscription = {
        id: 'sub_pastdue_789',
        user_id: 3,
        plan_id: 'plan_premium',
        status: 'past_due' as SubscriptionStatus,
        current_period_start: new Date(Date.now() - 35 * 24 * 60 * 60 * 1000).toISOString(),
        current_period_end: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString()
      };

      const validated = validateSubscriptionResponse(subscription);
      expect(validated.status).toBe('past_due');
    });

    it('should handle unpaid subscription (suspended)', () => {
      const subscription = {
        id: 'sub_unpaid_101',
        user_id: 4,
        plan_id: 'plan_pro',
        status: 'unpaid' as SubscriptionStatus,
        current_period_start: new Date(Date.now() - 40 * 24 * 60 * 60 * 1000).toISOString(),
        current_period_end: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 200 * 24 * 60 * 60 * 1000).toISOString()
      };

      const validated = validateSubscriptionResponse(subscription);
      expect(validated.status).toBe('unpaid');
    });

    it('should handle incomplete subscription (payment pending)', () => {
      const subscription = {
        id: 'sub_incomplete_202',
        user_id: 5,
        plan_id: 'plan_start',
        status: 'incomplete' as SubscriptionStatus,
        current_period_start: new Date().toISOString(),
        current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        created_at: new Date().toISOString()
      };

      const validated = validateSubscriptionResponse(subscription);
      expect(validated.status).toBe('incomplete');
    });

    it('should handle canceled subscription', () => {
      const subscription = {
        id: 'sub_canceled_303',
        user_id: 6,
        plan_id: 'plan_premium',
        status: 'canceled' as SubscriptionStatus,
        current_period_start: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
        current_period_end: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        cancel_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString()
      };

      const validated = validateSubscriptionResponse(subscription);
      expect(validated.status).toBe('canceled');
    });
  });

  describe('Status Messages', () => {
    it('should provide appropriate message for active subscription', () => {
      const message = getSubscriptionStatusMessage('active');
      expect(message.title).toContain('Active');
      expect(message.severity).toBe('success');
    });

    it('should provide appropriate message for trialing subscription', () => {
      const message = getSubscriptionStatusMessage('trialing');
      expect(message.title).toContain('Trial');
      expect(message.severity).toBe('info');
      expect(message.action).toBeDefined();
    });

    it('should provide appropriate message for past_due subscription', () => {
      const message = getSubscriptionStatusMessage('past_due');
      expect(message.title).toContain('Past Due');
      expect(message.severity).toBe('warning');
      expect(message.action).toBeDefined();
    });

    it('should provide appropriate message for unpaid subscription', () => {
      const message = getSubscriptionStatusMessage('unpaid');
      expect(message.title).toContain('Payment Required');
      expect(message.severity).toBe('warning');
      expect(message.action).toBeDefined();
    });

    it('should provide appropriate message for incomplete subscription', () => {
      const message = getSubscriptionStatusMessage('incomplete');
      expect(message.title).toContain('Incomplete');
      expect(message.severity).toBe('error');
      expect(message.action).toBeDefined();
    });

    it('should provide appropriate message for canceled subscription', () => {
      const message = getSubscriptionStatusMessage('canceled');
      expect(message.title).toContain('Canceled');
      expect(message.severity).toBe('error');
      expect(message.action).toBeDefined();
    });
  });

  describe('Stripe Status Alignment', () => {
    it('should align with Stripe subscription statuses', () => {
      // Stripe subscription statuses
      const stripeStatuses: SubscriptionStatus[] = [
        'active',
        'canceled', // Stripe uses American spelling
        'incomplete',
        'past_due',
        'trialing',
        'unpaid'
      ];

      stripeStatuses.forEach(status => {
        expect(normalizeSubscriptionStatus(status)).toBe(status);
      });
    });
  });

  describe('Error Cases', () => {
    it('should reject invalid subscription status', () => {
      const subscription = {
        id: 'sub_invalid_999',
        user_id: 99,
        plan_id: 'plan_test',
        status: 'invalid_status',
        current_period_start: new Date().toISOString(),
        current_period_end: new Date().toISOString(),
        created_at: new Date().toISOString()
      };

      expect(() => validateSubscriptionResponse(subscription)).toThrow();
    });
  });
});
