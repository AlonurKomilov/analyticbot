/**
 * Error Handling System - Central Export
 *
 * Unified error handling for the entire application
 */

// Error types and classification
export {
  ErrorSeverity,
  ErrorType,
  classifyError,
  isRetryableError,
  getUserFriendlyMessage,
  type AppError,
  type ErrorContext,
} from './errorTypes';

// Error logging
export { errorLogger } from './errorLogger';

// Error handling
export {
  errorHandler,
  handleError,
  handleAsync,
  handleValidationError,
  handleAuthError,
  type ErrorHandlerOptions,
} from './errorHandler';

// React error boundary
export { ErrorBoundary } from './ErrorBoundary';
