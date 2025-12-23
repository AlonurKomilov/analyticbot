/**
 * Error Classification System
 *
 * Defines error types and severity levels for consistent error handling
 * across the application.
 */

export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum ErrorType {
  // Network errors
  NETWORK_ERROR = 'network_error',
  API_ERROR = 'api_error',
  TIMEOUT_ERROR = 'timeout_error',

  // Authentication errors
  AUTH_ERROR = 'auth_error',
  PERMISSION_ERROR = 'permission_error',
  SESSION_EXPIRED = 'session_expired',

  // Validation errors
  VALIDATION_ERROR = 'validation_error',
  INVALID_INPUT = 'invalid_input',

  // Business logic errors
  BUSINESS_LOGIC_ERROR = 'business_logic_error',
  CHANNEL_ERROR = 'channel_error',
  POST_ERROR = 'post_error',
  MEDIA_ERROR = 'media_error',

  // System errors
  UNKNOWN_ERROR = 'unknown_error',
  CONFIGURATION_ERROR = 'configuration_error',
  RUNTIME_ERROR = 'runtime_error',
}

export interface AppError {
  type: ErrorType;
  severity: ErrorSeverity;
  message: string;
  details?: unknown;
  timestamp: Date;
  stack?: string;
  code?: string | number;
  retryable?: boolean;
}

export interface ErrorContext {
  component?: string;
  action?: string;
  userId?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Create a classified error from a generic error
 */
export function classifyError(error: unknown, context?: ErrorContext): AppError {
  const timestamp = new Date();

  // Handle axios errors
  if (isAxiosError(error)) {
    const status = error.response?.status;

    if (status === 401 || status === 403) {
      return {
        type: ErrorType.AUTH_ERROR,
        severity: ErrorSeverity.HIGH,
        message: error.response?.data?.message || 'Authentication failed',
        details: { status, context },
        timestamp,
        code: status,
        retryable: false,
      };
    }

    if (status === 422) {
      return {
        type: ErrorType.VALIDATION_ERROR,
        severity: ErrorSeverity.LOW,
        message: error.response?.data?.message || 'Validation failed',
        details: { errors: error.response?.data?.errors, context },
        timestamp,
        code: status,
        retryable: false,
      };
    }

    if (status && status >= 500) {
      return {
        type: ErrorType.API_ERROR,
        severity: ErrorSeverity.CRITICAL,
        message: 'Server error occurred',
        details: { status, context },
        timestamp,
        code: status,
        retryable: true,
      };
    }

    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return {
        type: ErrorType.TIMEOUT_ERROR,
        severity: ErrorSeverity.MEDIUM,
        message: 'Request timed out',
        details: { context },
        timestamp,
        retryable: true,
      };
    }

    return {
      type: ErrorType.NETWORK_ERROR,
      severity: ErrorSeverity.HIGH,
      message: 'Network error occurred',
      details: { error, context },
      timestamp,
      retryable: true,
    };
  }

  // Handle Error objects
  if (error instanceof Error) {
    return {
      type: ErrorType.RUNTIME_ERROR,
      severity: ErrorSeverity.HIGH,
      message: error.message,
      details: { context },
      timestamp,
      stack: error.stack,
      retryable: false,
    };
  }

  // Handle string errors
  if (typeof error === 'string') {
    return {
      type: ErrorType.UNKNOWN_ERROR,
      severity: ErrorSeverity.MEDIUM,
      message: error,
      details: { context },
      timestamp,
      retryable: false,
    };
  }

  // Unknown error type
  return {
    type: ErrorType.UNKNOWN_ERROR,
    severity: ErrorSeverity.MEDIUM,
    message: 'An unexpected error occurred',
    details: { error, context },
    timestamp,
    retryable: false,
  };
}

/**
 * Type guard for axios errors
 */
function isAxiosError(error: unknown): error is {
  response?: { status: number; data?: { message?: string; errors?: unknown } };
  code?: string;
  message: string;
} {
  return (
    typeof error === 'object' &&
    error !== null &&
    'isAxiosError' in error &&
    error.isAxiosError === true
  );
}

/**
 * Check if an error is retryable based on its classification
 */
export function isRetryableError(error: AppError): boolean {
  return error.retryable === true;
}

/**
 * Get user-friendly error message
 */
export function getUserFriendlyMessage(error: AppError): string {
  const messages: Record<ErrorType, string> = {
    [ErrorType.NETWORK_ERROR]: 'Unable to connect. Please check your internet connection.',
    [ErrorType.API_ERROR]: 'Server error. Please try again later.',
    [ErrorType.TIMEOUT_ERROR]: 'Request timed out. Please try again.',
    [ErrorType.AUTH_ERROR]: 'Authentication failed. Please log in again.',
    [ErrorType.PERMISSION_ERROR]: 'You do not have permission to perform this action.',
    [ErrorType.SESSION_EXPIRED]: 'Your session has expired. Please log in again.',
    [ErrorType.VALIDATION_ERROR]: error.message,
    [ErrorType.INVALID_INPUT]: 'Invalid input. Please check your data.',
    [ErrorType.BUSINESS_LOGIC_ERROR]: error.message,
    [ErrorType.CHANNEL_ERROR]: 'Channel operation failed. Please try again.',
    [ErrorType.POST_ERROR]: 'Post operation failed. Please try again.',
    [ErrorType.MEDIA_ERROR]: 'Media upload failed. Please try again.',
    [ErrorType.UNKNOWN_ERROR]: 'An unexpected error occurred.',
    [ErrorType.CONFIGURATION_ERROR]: 'Configuration error. Please contact support.',
    [ErrorType.RUNTIME_ERROR]: error.message,
  };

  return messages[error.type] || error.message;
}
