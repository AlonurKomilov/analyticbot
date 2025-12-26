/**
 * Validation Error Handler
 *
 * Centralized error handling for validation failures
 * Provides user-friendly error messages and logging
 *
 * Created: October 25, 2025
 */

import { ValidationError } from './schemas';

/**
 * Error severity levels
 */
export type ErrorSeverity = 'error' | 'warning' | 'info';

/**
 * Formatted validation error for UI display
 */
export interface FormattedValidationError {
  message: string;
  field?: string;
  severity: ErrorSeverity;
  technicalDetails?: string;
}

/**
 * Format validation error for user display
 *
 * @param error - Validation error
 * @returns User-friendly error object
 */
export function formatValidationError(error: ValidationError): FormattedValidationError {
  return {
    message: getUserFriendlyMessage(error),
    field: error.field,
    severity: 'error',
    technicalDetails: error.message
  };
}

/**
 * Get user-friendly error message
 *
 * @param error - Validation error
 * @returns Human-readable error message
 */
function getUserFriendlyMessage(error: ValidationError): string {
  const field = error.field || 'data';

  // Common error patterns
  if (error.message.includes('status')) {
    return 'Invalid status received from server. Please refresh and try again.';
  }

  if (error.message.includes('tier')) {
    return 'Invalid subscription tier. Please contact support.';
  }

  if (error.message.includes('must be an object')) {
    return 'Invalid data format received from server. Please try again.';
  }

  if (error.message.includes('Missing required field')) {
    return `Required information is missing (${field}). Please try again.`;
  }

  // Generic fallback
  return `Invalid ${field} received from server. Please try again or contact support.`;
}

/**
 * Handle validation error with logging and user notification
 *
 * @param error - Validation error
 * @param context - Context where error occurred (e.g., 'payment processing')
 * @param showToUser - Whether to show error to user
 * @returns Formatted error
 */
export function handleValidationError(
  error: ValidationError,
  context: string,
  showToUser: boolean = true
): FormattedValidationError {
  const formatted = formatValidationError(error);

  // Log technical details
  console.error(`[Validation Error] ${context}:`, {
    message: error.message,
    field: error.field,
    receivedValue: error.receivedValue,
    stack: error.stack
  });

  // Optionally show to user (would integrate with toast/notification system)
  if (showToUser) {
    console.warn('User should see:', formatted.message);
    // In real app: toast.error(formatted.message);
  }

  return formatted;
}

/**
 * Handle array of validation errors
 *
 * @param errors - Array of validation errors
 * @param context - Context where errors occurred
 * @returns Array of formatted errors
 */
export function handleValidationErrors(
  errors: ValidationError[],
  context: string
): FormattedValidationError[] {
  return errors.map(error => handleValidationError(error, context, false));
}

/**
 * Check if error is a validation error
 *
 * @param error - Any error object
 * @returns True if error is ValidationError
 */
export function isValidationError(error: any): error is ValidationError {
  return error instanceof ValidationError || error?.name === 'ValidationError';
}

/**
 * Safely handle any error, converting to validation error if applicable
 *
 * @param error - Any error
 * @param context - Context where error occurred
 * @returns Formatted error
 */
export function handleAnyError(error: any, context: string): FormattedValidationError {
  if (isValidationError(error)) {
    return handleValidationError(error, context);
  }

  // Handle other error types
  console.error(`[Error] ${context}:`, error);

  return {
    message: 'An unexpected error occurred. Please try again.',
    severity: 'error',
    technicalDetails: error?.message || String(error)
  };
}

/**
 * Create validation error summary for multiple errors
 *
 * @param errors - Array of formatted errors
 * @returns Summary message
 */
export function createErrorSummary(errors: FormattedValidationError[]): string {
  if (errors.length === 0) {
    return '';
  }

  if (errors.length === 1) {
    return errors[0].message;
  }

  return `${errors.length} validation errors occurred. Please check the form and try again.`;
}

/**
 * Log validation warning (non-critical issues)
 *
 * @param field - Field with issue
 * @param message - Warning message
 * @param value - The problematic value
 */
export function logValidationWarning(field: string, message: string, value?: unknown): void {
  console.warn(`[Validation Warning] ${field}:`, {
    message,
    value,
    timestamp: new Date().toISOString()
  });
}

/**
 * Log validation info (informational messages)
 *
 * @param field - Field being validated
 * @param message - Info message
 */
export function logValidationInfo(field: string, message: string): void {
  console.info(`[Validation Info] ${field}:`, message);
}

/**
 * Track validation errors for analytics/monitoring
 *
 * @param error - Validation error
 * @param context - Context where error occurred
 */
export function trackValidationError(error: ValidationError, context: string): void {
  // In production, this would send to analytics service
  const trackingData = {
    error_type: 'validation_error',
    field: error.field,
    context,
    message: error.message,
    timestamp: new Date().toISOString()
  };

  console.debug('[Analytics] Validation error tracked:', trackingData);

  // Example: analytics.track('validation_error', trackingData);
}

/**
 * Retry handler for validation failures
 * Useful for transient network issues
 *
 * @param fn - Function to retry
 * @param maxRetries - Maximum number of retries
 * @param delay - Delay between retries in ms
 * @returns Result from function
 */
export async function retryOnValidationError<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: any;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (!isValidationError(error)) {
        throw error; // Don't retry non-validation errors
      }

      if (i < maxRetries - 1) {
        console.log(`Retry ${i + 1}/${maxRetries - 1} after validation error`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError;
}

/**
 * Validation error recovery strategies
 */
export const RecoveryStrategies = {
  /**
   * Use default value when validation fails
   */
  useDefault<T>(value: unknown, defaultValue: T, validator: (v: unknown) => T): T {
    try {
      return validator(value);
    } catch (error) {
      if (isValidationError(error)) {
        logValidationWarning('recovery', `Using default value due to validation error: ${error.message}`);
      }
      return defaultValue;
    }
  },

  /**
   * Attempt to coerce value to valid type
   */
  coerce(value: unknown, expectedType: 'string' | 'number' | 'boolean'): any {
    try {
      switch (expectedType) {
        case 'string':
          return String(value);
        case 'number':
          return Number(value);
        case 'boolean':
          return Boolean(value);
      }
    } catch {
      return undefined;
    }
  },

  /**
   * Sanitize object by removing invalid fields
   */
  sanitize(obj: any, validKeys: string[]): any {
    const sanitized: any = {};
    validKeys.forEach(key => {
      if (key in obj) {
        sanitized[key] = obj[key];
      }
    });
    return sanitized;
  }
};
