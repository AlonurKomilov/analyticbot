/**
 * Environment Configuration
 * Single source of truth for all environment variables
 */

export const ENV = {
  // API Configuration
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'https://b2qz1m0n-11400.euw.devtunnels.ms',
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:11400',
  
  // Timeouts
  API_TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT || '30000'),
  
  // Environment
  NODE_ENV: import.meta.env.MODE,
  IS_DEV: import.meta.env.DEV,
  IS_PROD: import.meta.env.PROD,
  
  // Analytics & Monitoring
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  ENABLE_DEBUG: import.meta.env.DEV,
  ENABLE_SENTRY: import.meta.env.VITE_ENABLE_SENTRY === 'true',
  
  // Telegram
  TELEGRAM_BOT_TOKEN: import.meta.env.VITE_TELEGRAM_BOT_TOKEN || '',
  TELEGRAM_BOT_USERNAME: import.meta.env.VITE_TELEGRAM_BOT_USERNAME || '',
  
  // Feature Flags
  FEATURES: {
    AI_SERVICES: import.meta.env.VITE_FEATURE_AI === 'true',
    PAYMENT: import.meta.env.VITE_FEATURE_PAYMENT === 'true',
    ANALYTICS: import.meta.env.VITE_FEATURE_ANALYTICS === 'true',
    CONTENT_PROTECTION: import.meta.env.VITE_FEATURE_PROTECTION === 'true',
    ADVANCED_ANALYTICS: import.meta.env.VITE_FEATURE_ADVANCED === 'true',
  },
  
  // Build Info
  BUILD_VERSION: import.meta.env.VITE_BUILD_VERSION || '1.0.0',
  BUILD_TIMESTAMP: import.meta.env.VITE_BUILD_TIMESTAMP || new Date().toISOString(),
} as const;

export type EnvConfig = typeof ENV;

/**
 * Validate required environment variables
 */
export function validateEnv(): void {
  const required: Array<keyof typeof ENV> = ['API_BASE_URL'];
  
  for (const key of required) {
    if (!ENV[key]) {
      console.warn(`Missing required environment variable: ${key}`);
    }
  }
}

/**
 * Get feature flag status
 */
export function isFeatureEnabled(feature: keyof typeof ENV.FEATURES): boolean {
  return ENV.FEATURES[feature] === true;
}

/**
 * Check if running in development mode
 */
export function isDevelopment(): boolean {
  return ENV.IS_DEV;
}

/**
 * Check if running in production mode
 */
export function isProduction(): boolean {
  return ENV.IS_PROD;
}
