/**
 * Validation Schemas
 *
 * Zod schemas for runtime validation of API responses and user input
 * Ensures type safety at runtime and catches invalid data early
 *
 * Created: October 25, 2025
 *
 * Note: Using manual validation instead of Zod to avoid adding dependencies
 * This provides runtime type checking without external libraries
 */

import {
  PaymentStatus,
  SubscriptionStatus
} from '@/types';
import { UserTier } from '@/types';
import { UserStatus, PostStatus } from '@/types';

// ============================================================================
// Payment & Subscription Schemas
// ============================================================================

/**
 * Valid PaymentStatus values
 */
const VALID_PAYMENT_STATUSES: readonly PaymentStatus[] = [
  'pending',
  'processing',
  'succeeded',
  'failed',
  'canceled',
  'refunded'
] as const;

/**
 * Valid SubscriptionStatus values
 */
const VALID_SUBSCRIPTION_STATUSES: readonly SubscriptionStatus[] = [
  'active',
  'canceled',
  'past_due',
  'unpaid',
  'trialing',
  'incomplete'
] as const;

/**
 * Validate PaymentStatus
 * @throws Error if status is invalid
 */
export function validatePaymentStatus(status: unknown): PaymentStatus {
  if (typeof status !== 'string') {
    throw new Error(`Invalid payment status type: expected string, got ${typeof status}`);
  }

  if (!VALID_PAYMENT_STATUSES.includes(status as PaymentStatus)) {
    throw new Error(
      `Invalid payment status: "${status}". Valid values: ${VALID_PAYMENT_STATUSES.join(', ')}`
    );
  }

  return status as PaymentStatus;
}

/**
 * Validate SubscriptionStatus
 * @throws Error if status is invalid
 */
export function validateSubscriptionStatus(status: unknown): SubscriptionStatus {
  if (typeof status !== 'string') {
    throw new Error(`Invalid subscription status type: expected string, got ${typeof status}`);
  }

  if (!VALID_SUBSCRIPTION_STATUSES.includes(status as SubscriptionStatus)) {
    throw new Error(
      `Invalid subscription status: "${status}". Valid values: ${VALID_SUBSCRIPTION_STATUSES.join(', ')}`
    );
  }

  return status as SubscriptionStatus;
}

/**
 * Safe PaymentStatus validation (returns null instead of throwing)
 */
export function safeValidatePaymentStatus(status: unknown): PaymentStatus | null {
  try {
    return validatePaymentStatus(status);
  } catch {
    return null;
  }
}

/**
 * Safe SubscriptionStatus validation (returns null instead of throwing)
 */
export function safeValidateSubscriptionStatus(status: unknown): SubscriptionStatus | null {
  try {
    return validateSubscriptionStatus(status);
  } catch {
    return null;
  }
}

// ============================================================================
// User Tier Schema
// ============================================================================

/**
 * Valid UserTier values
 */
const VALID_USER_TIERS: readonly UserTier[] = [
  'free',
  'start',
  'pro',
  'premium'
] as const;

/**
 * Validate UserTier
 * @throws Error if tier is invalid
 */
export function validateUserTier(tier: unknown): UserTier {
  if (typeof tier !== 'string') {
    throw new Error(`Invalid user tier type: expected string, got ${typeof tier}`);
  }

  if (!VALID_USER_TIERS.includes(tier as UserTier)) {
    throw new Error(
      `Invalid user tier: "${tier}". Valid values: ${VALID_USER_TIERS.join(', ')}`
    );
  }

  return tier as UserTier;
}

/**
 * Safe UserTier validation (returns default 'free' instead of throwing)
 */
export function safeValidateUserTier(tier: unknown): UserTier {
  try {
    return validateUserTier(tier);
  } catch {
    console.warn(`Invalid user tier "${tier}", defaulting to "free"`);
    return 'free';
  }
}

// ============================================================================
// User Status Schema
// ============================================================================

/**
 * Valid UserStatus values
 */
const VALID_USER_STATUSES: readonly UserStatus[] = [
  'active',
  'inactive',
  'suspended',
  'pending',
  'deleted'
] as const;

/**
 * Validate UserStatus
 * @throws Error if status is invalid
 */
export function validateUserStatus(status: unknown): UserStatus {
  if (typeof status !== 'string') {
    throw new Error(`Invalid user status type: expected string, got ${typeof status}`);
  }

  if (!VALID_USER_STATUSES.includes(status as UserStatus)) {
    throw new Error(
      `Invalid user status: "${status}". Valid values: ${VALID_USER_STATUSES.join(', ')}`
    );
  }

  return status as UserStatus;
}

/**
 * Safe UserStatus validation (returns 'inactive' instead of throwing)
 */
export function safeValidateUserStatus(status: unknown): UserStatus {
  try {
    return validateUserStatus(status);
  } catch {
    console.warn(`Invalid user status "${status}", defaulting to "inactive"`);
    return 'inactive';
  }
}

// ============================================================================
// Post Status Schema
// ============================================================================

/**
 * Valid PostStatus values
 */
const VALID_POST_STATUSES: readonly PostStatus[] = [
  'draft',
  'scheduled',
  'publishing',
  'published',
  'failed',
  'cancelled'
] as const;

/**
 * Validate PostStatus
 * @throws Error if status is invalid
 */
export function validatePostStatus(status: unknown): PostStatus {
  if (typeof status !== 'string') {
    throw new Error(`Invalid post status type: expected string, got ${typeof status}`);
  }

  if (!VALID_POST_STATUSES.includes(status as PostStatus)) {
    throw new Error(
      `Invalid post status: "${status}". Valid values: ${VALID_POST_STATUSES.join(', ')}`
    );
  }

  return status as PostStatus;
}

/**
 * Safe PostStatus validation (returns 'draft' instead of throwing)
 */
export function safeValidatePostStatus(status: unknown): PostStatus {
  try {
    return validatePostStatus(status);
  } catch {
    console.warn(`Invalid post status "${status}", defaulting to "draft"`);
    return 'draft';
  }
}

// ============================================================================
// Composite Validation
// ============================================================================

/**
 * Validate payment object from API
 */
export function validatePaymentObject(data: any): {
  valid: boolean;
  errors: string[];
  data?: any;
} {
  const errors: string[] = [];

  if (!data || typeof data !== 'object') {
    return { valid: false, errors: ['Payment data must be an object'] };
  }

  // Validate required fields
  if (!data.id) errors.push('Missing required field: id');
  if (!data.amount && data.amount !== 0) errors.push('Missing required field: amount');

  // Validate status
  try {
    validatePaymentStatus(data.status);
  } catch (error) {
    errors.push((error as Error).message);
  }

  return {
    valid: errors.length === 0,
    errors,
    data: errors.length === 0 ? data : undefined
  };
}

/**
 * Validate subscription object from API
 */
export function validateSubscriptionObject(data: any): {
  valid: boolean;
  errors: string[];
  data?: any;
} {
  const errors: string[] = [];

  if (!data || typeof data !== 'object') {
    return { valid: false, errors: ['Subscription data must be an object'] };
  }

  // Validate required fields
  if (!data.id) errors.push('Missing required field: id');
  if (!data.user_id && data.user_id !== 0) errors.push('Missing required field: user_id');
  if (!data.plan_id) errors.push('Missing required field: plan_id');

  // Validate status
  try {
    validateSubscriptionStatus(data.status);
  } catch (error) {
    errors.push((error as Error).message);
  }

  return {
    valid: errors.length === 0,
    errors,
    data: errors.length === 0 ? data : undefined
  };
}

/**
 * Validate user object from API
 */
export function validateUserObject(data: any): {
  valid: boolean;
  errors: string[];
  data?: any;
} {
  const errors: string[] = [];

  if (!data || typeof data !== 'object') {
    return { valid: false, errors: ['User data must be an object'] };
  }

  // Validate required fields
  if (!data.id) errors.push('Missing required field: id');
  if (!data.email) errors.push('Missing required field: email');

  // Validate status
  if (data.status) {
    try {
      validateUserStatus(data.status);
    } catch (error) {
      errors.push((error as Error).message);
    }
  }

  // Validate tier if present
  if (data.tier) {
    try {
      validateUserTier(data.tier);
    } catch (error) {
      errors.push((error as Error).message);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    data: errors.length === 0 ? data : undefined
  };
}

/**
 * Validate post object from API
 */
export function validatePostObject(data: any): {
  valid: boolean;
  errors: string[];
  data?: any;
} {
  const errors: string[] = [];

  if (!data || typeof data !== 'object') {
    return { valid: false, errors: ['Post data must be an object'] };
  }

  // Validate required fields
  if (!data.id) errors.push('Missing required field: id');
  if (!data.channelId) errors.push('Missing required field: channelId');
  if (!data.content && data.content !== '') errors.push('Missing required field: content');

  // Validate status
  try {
    validatePostStatus(data.status);
  } catch (error) {
    errors.push((error as Error).message);
  }

  return {
    valid: errors.length === 0,
    errors,
    data: errors.length === 0 ? data : undefined
  };
}

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard for PaymentStatus
 */
export function isPaymentStatus(value: unknown): value is PaymentStatus {
  return typeof value === 'string' && VALID_PAYMENT_STATUSES.includes(value as PaymentStatus);
}

/**
 * Type guard for SubscriptionStatus
 */
export function isSubscriptionStatus(value: unknown): value is SubscriptionStatus {
  return typeof value === 'string' && VALID_SUBSCRIPTION_STATUSES.includes(value as SubscriptionStatus);
}

/**
 * Type guard for UserTier
 */
export function isUserTier(value: unknown): value is UserTier {
  return typeof value === 'string' && VALID_USER_TIERS.includes(value as UserTier);
}

/**
 * Type guard for UserStatus
 */
export function isUserStatus(value: unknown): value is UserStatus {
  return typeof value === 'string' && VALID_USER_STATUSES.includes(value as UserStatus);
}

/**
 * Type guard for PostStatus
 */
export function isPostStatus(value: unknown): value is PostStatus {
  return typeof value === 'string' && VALID_POST_STATUSES.includes(value as PostStatus);
}

// ============================================================================
// Validation Error Class
// ============================================================================

/**
 * Custom error class for validation failures
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public field?: string,
    public receivedValue?: unknown
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Create validation error with context
 */
export function createValidationError(
  field: string,
  expectedType: string,
  receivedValue: unknown
): ValidationError {
  return new ValidationError(
    `Invalid ${field}: expected ${expectedType}, received ${JSON.stringify(receivedValue)}`,
    field,
    receivedValue
  );
}
