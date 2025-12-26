// API Configuration for Public Catalog

export const API_CONFIG = {
  // API base URL - uses Vite proxy in development
  baseUrl: import.meta.env.VITE_API_URL || '/api',
  
  // Public endpoints base
  publicBase: '/public',
  
  // Timeouts
  timeout: 30000,
  
  // Retry configuration
  retryAttempts: 3,
  retryDelay: 1000,
}

// App domain configuration
export const DOMAIN_CONFIG = {
  public: 'analyticbot.org',
  app: '2bot.org',
  admin: 'admin.analyticbot.org',
  moderator: 'moderator.analyticbot.org',
  api: 'api.analyticbot.org',
}

// Feature flags
export const FEATURES = {
  enableSearch: true,
  enableTrending: true,
  enableCategories: true,
  enableChannelDetails: true,
  showPremiumBanner: true,
  enableSEO: true,
}

export default API_CONFIG
