/**
 * 🪵 Production-Safe Logger
 * Only logs in development, silent in production
 *
 * Usage:
 *   import { logger, apiLogger, authLogger } from '@/utils/logger';
 *   logger.log('General message');
 *   apiLogger.log('API call', data);
 *   authLogger.error('Auth failed', error);
 *
 * Features:
 * - Environment-aware (DEV vs PROD)
 * - Errors always logged + sent to Sentry
 * - Structured logging with timestamps
 * - Multiple logger instances for different domains
 */

import { ENV } from '@/config/env';

type LogLevel = 'log' | 'info' | 'warn' | 'error' | 'debug';

interface LoggerConfig {
  enableInProduction: boolean;
  minLevel: LogLevel;
  prefix?: string;
  enableTimestamp?: boolean;
}

class Logger {
  private config: LoggerConfig;
  private isDev: boolean;

  constructor(configParam: Partial<LoggerConfig> = {}) {
    this.config = {
      enableInProduction: false,
      minLevel: 'log',
      enableTimestamp: true,
      ...configParam
    };
    this.isDev = ENV.IS_DEV;
  }

  /**
   * General logging - only in development
   */
  log(...args: any[]): void {
    if (this.shouldLog('log')) {
      logger.log(this.formatMessage('LOG'), ...args);
    }
  }

  /**
   * Informational messages - only in development
   */
  info(...args: any[]): void {
    if (this.shouldLog('info')) {
      logger.info(this.formatMessage('INFO'), ...args);
    }
  }

  /**
   * Warning messages - logged in production too
   */
  warn(...args: any[]): void {
    if (this.shouldLog('warn') || !this.isDev) {
      logger.warn(this.formatMessage('WARN'), ...args);
    }
  }

  /**
   * Error messages - always logged, sent to Sentry in production
   */
  error(...args: any[]): void {
    // Always log errors, even in production
    logger.error(this.formatMessage('ERROR'), ...args);

    // Send to Sentry in production
    if (!this.isDev && typeof window !== 'undefined') {
      const errorObj = args[0];
      if (errorObj instanceof Error) {
        // @ts-ignore - Sentry may not be loaded
        window.Sentry?.captureException(errorObj, {
          extra: {
            additionalArgs: args.slice(1),
            logger: this.config.prefix || 'default'
          }
        });
      } else {
        // @ts-ignore
        window.Sentry?.captureMessage(String(errorObj), {
          level: 'error',
          extra: { args }
        });
      }
    }
  }

  /**
   * Debug messages - only in development
   */
  debug(...args: any[]): void {
    if (this.shouldLog('debug') && this.isDev) {
      logger.log(this.formatMessage('DEBUG'), ...args);
    }
  }

  /**
   * Group logging - for related log entries
   */
  group(label: string, collapsed: boolean = false): void {
    if (this.isDev) {
      if (collapsed) {
        logger.log(this.formatMessage('GROUP'), label);
      } else {
        logger.log(this.formatMessage('GROUP'), label);
      }
    }
  }

  /**
   * End group logging
   */
  groupEnd(): void {
    if (this.isDev) {
      logger.log();
    }
  }

  /**
   * Table logging - for structured data
   */
  table(data: any): void {
    if (this.isDev) {
      logger.log(data);
    }
  }

  /**
   * Time tracking - for performance measurements
   */
  time(label: string): void {
    if (this.isDev) {
      logger.log(this.config.prefix ? `${this.config.prefix} ${label}` : label);
    }
  }

  /**
   * End time tracking
   */
  timeEnd(label: string): void {
    if (this.isDev) {
      logger.log(this.config.prefix ? `${this.config.prefix} ${label}` : label);
    }
  }

  /**
   * Check if should log at this level
   */
  private shouldLog(_level: LogLevel): boolean {
    if (this.isDev) return true;
    return this.config.enableInProduction;
  }

  /**
   * Format log message with timestamp and prefix
   */
  private formatMessage(level: string): string {
    const parts: string[] = [];

    if (this.config.enableTimestamp && this.isDev) {
      const now = new Date();
      const timestamp = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}.${now.getMilliseconds().toString().padStart(3, '0')}`;
      parts.push(`[${timestamp}]`);
    }

    if (this.config.prefix) {
      parts.push(`[${this.config.prefix}]`);
    }

    parts.push(`[${level}]`);

    return parts.join(' ');
  }
}

// Export singleton instances for different domains
export const logger = new Logger();

export const apiLogger = new Logger({
  prefix: '🌐 API',
  enableTimestamp: true
});

export const authLogger = new Logger({
  prefix: '🔐 Auth',
  enableTimestamp: true
});

export const storeLogger = new Logger({
  prefix: '📦 Store',
  enableTimestamp: true
});

export const routerLogger = new Logger({
  prefix: '🚦 Router',
  enableTimestamp: true
});

export const uiLogger = new Logger({
  prefix: '🎨 UI',
  enableTimestamp: true
});

// Default export
export default logger;
