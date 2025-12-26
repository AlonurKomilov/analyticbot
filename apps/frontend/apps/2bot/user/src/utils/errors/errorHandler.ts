/**
 * Central Error Handler
 *
 * Provides unified error handling across the application with:
 * - Error classification
 * - Logging
 * - User notifications
 * - Retry logic
 */

import { toast } from 'react-hot-toast';
import { classifyError, getUserFriendlyMessage, isRetryableError, type AppError, type ErrorContext } from './errorTypes';
import { errorLogger } from './errorLogger';

export interface ErrorHandlerOptions {
  /** Show toast notification to user */
  showNotification?: boolean;
  /** Custom error message to display */
  customMessage?: string;
  /** Callback after error is handled */
  onError?: (error: AppError) => void;
  /** Enable automatic retry for retryable errors */
  enableRetry?: boolean;
  /** Maximum retry attempts */
  maxRetries?: number;
  /** Retry delay in milliseconds */
  retryDelay?: number;
}

class ErrorHandler {
  /**
   * Handle an error with full pipeline:
   * 1. Classify error
   * 2. Log error
   * 3. Show notification (optional)
   * 4. Execute callback (optional)
   */
  handle(error: unknown, context?: ErrorContext, options: ErrorHandlerOptions = {}): AppError {
    const {
      showNotification = true,
      customMessage,
      onError,
    } = options;

    // Classify the error
    const appError = classifyError(error, context);

    // Log the error
    errorLogger.log(appError, context);

    // Show user notification
    if (showNotification) {
      this.showNotification(appError, customMessage);
    }

    // Execute callback
    if (onError) {
      onError(appError);
    }

    return appError;
  }

  /**
   * Handle async operations with automatic error handling
   */
  async handleAsync<T>(
    operation: () => Promise<T>,
    context?: ErrorContext,
    options: ErrorHandlerOptions = {}
  ): Promise<T> {
    const {
      enableRetry = false,
      maxRetries = 3,
      retryDelay = 1000,
    } = options;

    let lastError: unknown;
    let attempts = 0;

    while (attempts <= (enableRetry ? maxRetries : 0)) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        attempts++;

        const appError = classifyError(error, context);

        // Only retry if error is retryable and we haven't exceeded max retries
        if (enableRetry && isRetryableError(appError) && attempts <= maxRetries) {
          // Log retry attempt
          console.warn(`Retry attempt ${attempts}/${maxRetries} for ${appError.type}`);

          // Wait before retrying (exponential backoff)
          await this.delay(retryDelay * Math.pow(2, attempts - 1));
          continue;
        }

        // Handle the error if no more retries
        throw this.handle(error, context, options);
      }
    }

    // This should never be reached, but TypeScript needs it
    throw this.handle(lastError, context, options);
  }

  /**
   * Show user notification based on error severity
   */
  private showNotification(error: AppError, customMessage?: string): void {
    const message = customMessage || getUserFriendlyMessage(error);

    switch (error.severity) {
      case 'critical':
      case 'high':
        toast.error(message, {
          duration: 5000,
          position: 'top-right',
          icon: '🚨',
        });
        break;

      case 'medium':
        toast.error(message, {
          duration: 4000,
          position: 'top-right',
        });
        break;

      case 'low':
        toast(message, {
          duration: 3000,
          position: 'top-right',
          icon: 'ℹ️',
        });
        break;
    }
  }

  /**
   * Delay helper for retry logic
   */
  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Handle validation errors specifically
   */
  handleValidationError(errors: Record<string, string[]>, context?: ErrorContext): void {
    const firstError = Object.values(errors)[0]?.[0];

    if (firstError) {
      toast.error(firstError, {
        duration: 4000,
        position: 'top-right',
      });
    }

    errorLogger.log(
      {
        type: 'validation_error' as any,
        severity: 'low' as any,
        message: 'Validation failed',
        details: errors,
        timestamp: new Date(),
        retryable: false,
      },
      context
    );
  }

  /**
   * Handle authentication errors specifically
   */
  handleAuthError(error: unknown, context?: ErrorContext): void {
    const appError = this.handle(error, {
      ...context,
      action: 'authentication',
    }, {
      customMessage: 'Your session has expired. Please log in again.',
      showNotification: true,
    });

    // Redirect to login if needed
    if (appError.type === 'auth_error' || appError.type === 'session_expired') {
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    }
  }
}

// Singleton instance
export const errorHandler = new ErrorHandler();

// Convenience exports for common use cases
export const handleError = errorHandler.handle.bind(errorHandler);
export const handleAsync = errorHandler.handleAsync.bind(errorHandler);
export const handleValidationError = errorHandler.handleValidationError.bind(errorHandler);
export const handleAuthError = errorHandler.handleAuthError.bind(errorHandler);
