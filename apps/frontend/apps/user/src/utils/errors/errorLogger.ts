/**
 * Error Logging Service
 *
 * Centralized error logging with support for:
 * - Console logging (development)
 * - Sentry integration (production)
 * - Custom error tracking
 */

import type { AppError, ErrorContext } from './errorTypes';
import { ErrorSeverity } from './errorTypes';

export interface ErrorLoggerConfig {
  enabled: boolean;
  sentryDsn?: string;
  environment: 'development' | 'production' | 'staging';
  debug: boolean;
}

class ErrorLogger {
  private config: ErrorLoggerConfig;
  private sentryInitialized = false;

  constructor() {
    this.config = {
      enabled: true,
      environment: (import.meta.env.MODE || 'development') as 'development' | 'production' | 'staging',
      debug: import.meta.env.DEV === true,
      sentryDsn: import.meta.env.VITE_SENTRY_DSN as string | undefined,
    };

    this.initialize();
  }

  private initialize(): void {
    if (this.config.sentryDsn && this.config.environment === 'production') {
      // Initialize Sentry when available
      // import('@sentry/react').then((Sentry) => {
      //   Sentry.init({
      //     dsn: this.config.sentryDsn,
      //     environment: this.config.environment,
      //     beforeSend(event) {
      //       // Filter sensitive data
      //       return event;
      //     },
      //   });
      //   this.sentryInitialized = true;
      // });
    }
  }

  /**
   * Log an error with context
   */
  log(error: AppError, context?: ErrorContext): void {
    if (!this.config.enabled) return;

    // Console logging
    this.logToConsole(error, context);

    // Sentry logging (production only)
    if (this.config.environment === 'production') {
      this.logToSentry(error, context);
    }

    // Custom analytics (optional)
    this.logToAnalytics(error, context);
  }

  /**
   * Log error to console with formatting
   */
  private logToConsole(error: AppError, context?: ErrorContext): void {
    const style = this.getConsoleStyle(error.severity);

    console.group(`%c[${error.severity.toUpperCase()}] ${error.type}`, style);
    console.error('Message:', error.message);

    if (error.code) {
      console.error('Code:', error.code);
    }

    if (context) {
      console.error('Context:', context);
    }

    if (error.details) {
      console.error('Details:', error.details);
    }

    if (error.stack) {
      console.error('Stack:', error.stack);
    }

    console.error('Timestamp:', error.timestamp.toISOString());
    console.groupEnd();
  }

  /**
   * Log error to Sentry
   */
  private logToSentry(_error: AppError, _context?: ErrorContext): void {
    if (!this.sentryInitialized) return;

    // Future Sentry integration
    // import('@sentry/react').then((Sentry) => {
    //   Sentry.captureException(new Error(_error.message), {
    //     level: this.getSentryLevel(_error.severity),
    //     tags: {
    //       errorType: _error.type,
    //       retryable: _error.retryable ? 'yes' : 'no',
    //     },
    //     contexts: {
    //       error: {
    //         details: _error.details,
    //         code: _error.code,
    //       },
    //       custom: _context,
    //     },
    //   });
    // });
  }

  /**
   * Log error to analytics
   */
  private logToAnalytics(_error: AppError, _context?: ErrorContext): void {
    if (!this.config.debug) {
      // Track error in analytics
      // window.gtag?.('event', 'exception', {
      //   description: _error.message,
      //   fatal: _error.severity === ErrorSeverity.CRITICAL,
      //   error_type: _error.type,
      // });
    }
  }

  /**
   * Get console style based on severity
   */
  private getConsoleStyle(severity: ErrorSeverity): string {
    const styles: Record<ErrorSeverity, string> = {
      [ErrorSeverity.LOW]: 'color: #2196F3; font-weight: bold;',
      [ErrorSeverity.MEDIUM]: 'color: #FF9800; font-weight: bold;',
      [ErrorSeverity.HIGH]: 'color: #F44336; font-weight: bold;',
      [ErrorSeverity.CRITICAL]: 'color: #D32F2F; font-weight: bold; font-size: 14px;',
    };

    return styles[severity];
  }

  /**
   * Get Sentry severity level (for future use when Sentry is integrated)
   * Uncomment when implementing Sentry integration
   */
  /*
  private getSentryLevel(severity: ErrorSeverity): 'info' | 'warning' | 'error' | 'fatal' {
    const levels: Record<ErrorSeverity, 'info' | 'warning' | 'error' | 'fatal'> = {
      [ErrorSeverity.LOW]: 'info',
      [ErrorSeverity.MEDIUM]: 'warning',
      [ErrorSeverity.HIGH]: 'error',
      [ErrorSeverity.CRITICAL]: 'fatal',
    };

    return levels[severity];
  }
  */

  /**
   * Log React error boundary errors
   */
  logReactError(error: Error, errorInfo: { componentStack?: string }): void {
    const appError: AppError = {
      type: 'runtime_error' as any,
      severity: ErrorSeverity.HIGH,
      message: error.message,
      stack: error.stack,
      details: { componentStack: errorInfo.componentStack },
      timestamp: new Date(),
      retryable: false,
    };

    this.log(appError, { component: 'ErrorBoundary' });
  }
}

// Singleton instance
export const errorLogger = new ErrorLogger();
