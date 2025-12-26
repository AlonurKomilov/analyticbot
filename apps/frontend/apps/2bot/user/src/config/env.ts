/**
 * Environment Configuration
 * Single source of truth for all environment variables
 */

// Dynamic API URL detection based on current domain
const getApiBaseUrl = (): string => {
  // Allow override via environment variables
  if (import.meta.env.VITE_API_BASE_URL) return import.meta.env.VITE_API_BASE_URL;
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL;
  
  // Auto-detect based on current domain
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    console.log('[ENV] Detecting API URL for hostname:', hostname);
    
    // If on 2bot.org domain, use api.2bot.org
    if (hostname.endsWith('.2bot.org') || hostname === '2bot.org') {
      console.log('[ENV] Using api.2bot.org');
      return 'https://api.2bot.org';
    }
    // If on analyticbot.org domain, use api.analyticbot.org
    if (hostname.endsWith('.analyticbot.org') || hostname === 'analyticbot.org') {
      console.log('[ENV] Using api.analyticbot.org');
      return 'https://api.analyticbot.org';
    }
  }
  
  // Default fallback
  console.log('[ENV] Using default api.analyticbot.org');
  return 'https://api.analyticbot.org';
};

// Create a getter that evaluates at runtime
export const ENV = {
  // API Configuration - use getter to evaluate at access time
  get API_BASE_URL() {
    return getApiBaseUrl();
  },
  WS_URL: import.meta.env.VITE_WS_URL || (typeof window !== 'undefined' ? `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/ws` : 'wss://api.analyticbot.org'),

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
