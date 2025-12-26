/**
 * API Response Validators
 *
 * Utilities for validating and normalizing API responses
 * Ensures data integrity and type safety at runtime
 *
 * Created: October 25, 2025
 */

import {
  validatePaymentStatus,
  validateSubscriptionStatus,
  validateUserStatus,
  validateUserTier,
  validatePostStatus,
  ValidationError,
  createValidationError
} from './schemas';

import { normalizePaymentStatus, normalizeSubscriptionStatus } from '@/types';
import { normalizeUser } from '@shared/utils/userMigration';
import { normalizePost } from '@shared/utils/postStatus';
import { logger } from '@/utils/logger';

// ============================================================================
// API Response Validators
// ============================================================================

/**
 * Validate and normalize payment API response
 *
 * @param response - Raw API response
 * @returns Validated and normalized payment object
 * @throws ValidationError if response is invalid
 */
export function validatePaymentResponse(response: any): any {
  if (!response || typeof response !== 'object') {
    throw new ValidationError('Payment response must be an object');
  }

  // Validate required fields
  if (!response.id) {
    throw createValidationError('payment.id', 'string', response.id);
  }

  if (typeof response.amount !== 'number') {
    throw createValidationError('payment.amount', 'number', response.amount);
  }

  // Validate and normalize status
  const validatedStatus = validatePaymentStatus(response.status);
  const normalizedStatus = normalizePaymentStatus(validatedStatus as any);

  return {
    ...response,
    status: normalizedStatus
  };
}

/**
 * Safe payment response validation (logs errors instead of throwing)
 */
export function safeValidatePaymentResponse(response: any): any | null {
  try {
    return validatePaymentResponse(response);
  } catch (error) {
    logger.error('Payment validation failed', { error });
    return null;
  }
}

/**
 * Validate and normalize subscription API response
 *
 * @param response - Raw API response
 * @returns Validated and normalized subscription object
 * @throws ValidationError if response is invalid
 */
export function validateSubscriptionResponse(response: any): any {
  if (!response || typeof response !== 'object') {
    throw new ValidationError('Subscription response must be an object');
  }

  // Validate required fields
  if (!response.id) {
    throw createValidationError('subscription.id', 'string', response.id);
  }

  if (!response.user_id && response.user_id !== 0) {
    throw createValidationError('subscription.user_id', 'number', response.user_id);
  }

  if (!response.plan_id) {
    throw createValidationError('subscription.plan_id', 'string', response.plan_id);
  }

  // Validate and normalize status
  const validatedStatus = validateSubscriptionStatus(response.status);
  const normalizedStatus = normalizeSubscriptionStatus(validatedStatus as any);

  return {
    ...response,
    status: normalizedStatus
  };
}

/**
 * Safe subscription response validation
 */
export function safeValidateSubscriptionResponse(response: any): any | null {
  try {
    return validateSubscriptionResponse(response);
  } catch (error) {
    logger.error('Subscription validation failed', { error });
    return null;
  }
}

/**
 * Validate and normalize user API response
 *
 * @param response - Raw API response
 * @returns Validated and normalized user object
 * @throws ValidationError if response is invalid
 */
export function validateUserResponse(response: any): any {
  if (!response || typeof response !== 'object') {
    throw new ValidationError('User response must be an object');
  }

  // Validate required fields
  if (!response.id) {
    throw createValidationError('user.id', 'string', response.id);
  }

  if (!response.email) {
    throw createValidationError('user.email', 'string', response.email);
  }

  // Validate status if present
  if (response.status) {
    validateUserStatus(response.status);
  }

  // Validate tier if present
  if (response.tier) {
    validateUserTier(response.tier);
  }

  // Normalize user (handles isActive -> status conversion)
  return normalizeUser(response);
}

/**
 * Safe user response validation
 */
export function safeValidateUserResponse(response: any): any | null {
  try {
    return validateUserResponse(response);
  } catch (error) {
    logger.error('User validation failed', { error });
    return null;
  }
}

/**
 * Validate and normalize post API response
 *
 * @param response - Raw API response
 * @returns Validated and normalized post object
 * @throws ValidationError if response is invalid
 */
export function validatePostResponse(response: any): any {
  if (!response || typeof response !== 'object') {
    throw new ValidationError('Post response must be an object');
  }

  // Validate required fields
  if (!response.id) {
    throw createValidationError('post.id', 'string', response.id);
  }

  if (!response.channelId) {
    throw createValidationError('post.channelId', 'string', response.channelId);
  }

  if (response.content === undefined || response.content === null) {
    throw createValidationError('post.content', 'string', response.content);
  }

  // Validate status
  validatePostStatus(response.status);

  // Normalize post (handles backend status -> frontend status)
  return normalizePost(response);
}

/**
 * Safe post response validation
 */
export function safeValidatePostResponse(response: any): any | null {
  try {
    return validatePostResponse(response);
  } catch (error) {
    logger.error('Post validation failed', { error });
    return null;
  }
}

// ============================================================================
// Array Response Validators
// ============================================================================

/**
 * Validate array of payments
 */
export function validatePaymentsArray(response: any): any[] {
  if (!Array.isArray(response)) {
    throw new ValidationError('Expected array of payments');
  }

  return response.map((item, index) => {
    try {
      return validatePaymentResponse(item);
    } catch (error) {
      logger.error('Payment validation failed at index', { index, error });
      throw error;
    }
  });
}

/**
 * Validate array of subscriptions
 */
export function validateSubscriptionsArray(response: any): any[] {
  if (!Array.isArray(response)) {
    throw new ValidationError('Expected array of subscriptions');
  }

  return response.map((item, index) => {
    try {
      return validateSubscriptionResponse(item);
    } catch (error) {
      logger.error('Subscription validation failed at index', { index, error });
      throw error;
    }
  });
}

/**
 * Validate array of users
 */
export function validateUsersArray(response: any): any[] {
  if (!Array.isArray(response)) {
    throw new ValidationError('Expected array of users');
  }

  return response.map((item, index) => {
    try {
      return validateUserResponse(item);
    } catch (error) {
      logger.error('User validation failed at index', { index, error });
      throw error;
    }
  });
}

/**
 * Validate array of posts
 */
export function validatePostsArray(response: any): any[] {
  if (!Array.isArray(response)) {
    throw new ValidationError('Expected array of posts');
  }

  return response.map((item, index) => {
    try {
      return validatePostResponse(item);
    } catch (error) {
      logger.error('Post validation failed at index', { index, error });
      throw error;
    }
  });
}

// ============================================================================
// Safe Array Validators (filter out invalid items)
// ============================================================================

/**
 * Safely validate array of payments (filters out invalid items)
 */
export function safeValidatePaymentsArray(response: any): any[] {
  if (!Array.isArray(response)) {
    logger.error('Expected array of payments', { responseType: typeof response });
    return [];
  }

  return response
    .map((item, index) => {
      const validated = safeValidatePaymentResponse(item);
      if (!validated) {
        logger.warn('Skipping invalid payment at index', { index });
      }
      return validated;
    })
    .filter(Boolean);
}

/**
 * Safely validate array of subscriptions (filters out invalid items)
 */
export function safeValidateSubscriptionsArray(response: any): any[] {
  if (!Array.isArray(response)) {
    logger.error('Expected array of subscriptions', { responseType: typeof response });
    return [];
  }

  return response
    .map((item, index) => {
      const validated = safeValidateSubscriptionResponse(item);
      if (!validated) {
        logger.warn('Skipping invalid subscription at index', { index });
      }
      return validated;
    })
    .filter(Boolean);
}

/**
 * Safely validate array of users (filters out invalid items)
 */
export function safeValidateUsersArray(response: any): any[] {
  if (!Array.isArray(response)) {
    logger.error('Expected array of users', { responseType: typeof response });
    return [];
  }

  return response
    .map((item, index) => {
      const validated = safeValidateUserResponse(item);
      if (!validated) {
        logger.warn('Skipping invalid user at index', { index });
      }
      return validated;
    })
    .filter(Boolean);
}

/**
 * Safely validate array of posts (filters out invalid items)
 */
export function safeValidatePostsArray(response: any): any[] {
  if (!Array.isArray(response)) {
    logger.error('Expected array of posts', { responseType: typeof response });
    return [];
  }

  return response
    .map((item, index) => {
      const validated = safeValidatePostResponse(item);
      if (!validated) {
        logger.warn('Skipping invalid post at index', { index });
      }
      return validated;
    })
    .filter(Boolean);
}

// ============================================================================
// Generic Validator
// ============================================================================

/**
 * Generic API response validator with logging
 */
export function validateApiResponse<T>(
  response: any,
  validator: (data: any) => T,
  context: string
): T {
  try {
    return validator(response);
  } catch (error) {
    logger.error('API validation failed', { context, error });
    throw error;
  }
}

/**
 * Safe generic API response validator
 */
export function safeValidateApiResponse<T>(
  response: any,
  validator: (data: any) => T | null,
  context: string,
  fallback: T
): T {
  try {
    const result = validator(response);
    return result !== null ? result : fallback;
  } catch (error) {
    logger.error('API validation failed', { context, error });
    return fallback;
  }
}
