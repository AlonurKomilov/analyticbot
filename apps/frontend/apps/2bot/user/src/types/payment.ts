/**
 * Payment & Subscription Type Definitions
 * Aligned with backend enums (October 2025)
 *
 * Backend sources:
 * - apps/bot/models/payment.py (PaymentStatus, SubscriptionStatus)
 * - core/domain/payment/models.py
 *
 * Phase 1 Implementation - Critical Payment & Subscription Fixes
 */

// ============================================================================
// Payment Status Types
// ============================================================================

/**
 * Payment status values matching backend PaymentStatus enum
 * CHANGED: 'completed' → 'succeeded' (Stripe standard)
 */
export type PaymentStatus =
  | 'pending'      // Payment initiated, awaiting processing
  | 'processing'   // Payment being processed by provider
  | 'succeeded'    // ✅ CHANGED: was 'completed'
  | 'failed'       // Payment failed
  | 'canceled'     // Payment canceled before completion
  | 'refunded';    // Payment refunded after success

/**
 * Legacy payment status type for backward compatibility
 * @deprecated Use PaymentStatus instead
 */
export type LegacyPaymentStatus = PaymentStatus | 'completed';

/**
 * Map legacy status values to current standard
 * Handles backward compatibility with old 'completed' status
 */
export function normalizePaymentStatus(status: LegacyPaymentStatus): PaymentStatus {
  if (status === 'completed') {
    console.warn('PaymentStatus "completed" is deprecated, use "succeeded" instead');
    return 'succeeded';
  }
  return status as PaymentStatus;
}

/**
 * Check if payment was successful
 */
export function isPaymentSuccessful(status: PaymentStatus): boolean {
  return status === 'succeeded';
}

/**
 * Check if payment is in terminal state (completed processing)
 */
export function isPaymentTerminal(status: PaymentStatus): boolean {
  return ['succeeded', 'failed', 'canceled', 'refunded'].includes(status);
}

// ============================================================================
// Subscription Status Types
// ============================================================================

/**
 * Subscription status values matching backend SubscriptionStatus enum
 * CHANGED: Standardized to American English spelling (canceled, not cancelled)
 * ADDED: trialing, incomplete, unpaid (missing from some frontend files)
 */
export type SubscriptionStatus =
  | 'active'       // Subscription is active and current
  | 'canceled'     // ✅ CHANGED: was 'cancelled' (British spelling)
  | 'past_due'     // Payment failed, in grace period
  | 'unpaid'       // ✅ ADDED: Payment failed, suspended
  | 'trialing'     // ✅ ADDED: In trial period
  | 'incomplete';  // ✅ ADDED: Initial payment incomplete

/**
 * Legacy subscription status type accepting both spellings
 * @deprecated Use SubscriptionStatus
 */
export type LegacySubscriptionStatus = SubscriptionStatus | 'cancelled' | 'inactive';

/**
 * Normalize subscription status to current standard
 * Handles backward compatibility with old spellings and removed statuses
 */
export function normalizeSubscriptionStatus(
  status: LegacySubscriptionStatus
): SubscriptionStatus {
  // Handle spelling variants
  if (status === 'cancelled') {
    console.warn('SubscriptionStatus "cancelled" is deprecated, use "canceled"');
    return 'canceled';
  }

  // Handle removed statuses
  if (status === 'inactive') {
    console.warn('SubscriptionStatus "inactive" is deprecated, mapping to "canceled"');
    return 'canceled';
  }

  return status as SubscriptionStatus;
}

/**
 * Check if subscription is active
 */
export function isSubscriptionActive(status: SubscriptionStatus): boolean {
  return status === 'active' || status === 'trialing';
}

/**
 * Check if subscription requires payment action
 */
export function requiresPaymentAction(status: SubscriptionStatus): boolean {
  return ['past_due', 'unpaid', 'incomplete'].includes(status);
}

/**
 * Check if subscription is in grace period
 */
export function isInGracePeriod(status: SubscriptionStatus): boolean {
  return status === 'past_due';
}

// ============================================================================
// Shared Payment Types
// ============================================================================

/**
 * Payment provider types
 */
export type PaymentProvider = 'stripe' | 'paypal' | 'crypto';

/**
 * Billing cycle options
 */
export type BillingCycle = 'monthly' | 'yearly';

/**
 * Currency codes (ISO 4217)
 */
export type Currency = 'USD' | 'EUR' | 'GBP' | 'JPY' | 'CNY';

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard for PaymentStatus
 */
export function isPaymentStatus(value: unknown): value is PaymentStatus {
  return typeof value === 'string' &&
    ['pending', 'processing', 'succeeded', 'failed', 'canceled', 'refunded'].includes(value);
}

/**
 * Type guard for SubscriptionStatus
 */
export function isSubscriptionStatus(value: unknown): value is SubscriptionStatus {
  return typeof value === 'string' &&
    ['active', 'canceled', 'past_due', 'unpaid', 'trialing', 'incomplete'].includes(value);
}
