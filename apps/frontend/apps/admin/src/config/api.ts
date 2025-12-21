// API Configuration for Admin Panel
// Use relative /api path which nginx proxies to the backend
// This avoids CORS issues and provides better security
export const API_CONFIG = {
  BASE_URL: '/api',
  TIMEOUT: 30000,
};

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',  // Use /auth/me to verify token and get user info
    CSRF_TOKEN: '/auth/csrf-token',  // Get CSRF token for state-changing requests
  },
  // Admin
  ADMIN: {
    STATS: '/admin/system/stats',
    USERS: '/admin/users',
    USER_DETAIL: (id: number) => `/admin/users/${id}`,
    USER_SUSPEND: (id: number) => `/admin/users/${id}/suspend`,
    USER_UNSUSPEND: (id: number) => `/admin/users/${id}/unsuspend`,
    USER_DELETE: (id: number) => `/admin/users/${id}`,
    USER_CREDITS: (id: number) => `/admin/users/${id}/credits`,
    USER_CREDITS_ADJUST: (id: number) => `/admin/users/${id}/credits/adjust`,
    ALL_USER_CREDITS: '/admin/users/credits/all',
    CHANNELS: '/admin/channels',
    AUDIT_LOG: '/admin/system/audit-logs',
    HEALTH: '/admin/system/health',
    // Settings
    SETTINGS: '/admin/system/settings',
    SETTING_DETAIL: (key: string) => `/admin/system/settings/${key}`,
    // Rate Limits
    RATE_LIMITS: {
      DASHBOARD: '/admin/rate-limits/dashboard',
      CONFIGS: '/admin/rate-limits/configs',
      CONFIG_DETAIL: (service: string) => `/admin/rate-limits/configs/${service}`,
      STATS: '/admin/rate-limits/stats',
      STAT_DETAIL: (service: string) => `/admin/rate-limits/stats/${service}`,
      HISTORY: (service: string) => `/admin/rate-limits/history/${service}`,
      TOP_USERS: (service: string) => `/admin/rate-limits/top-users/${service}`,
      RESET_USER: (userId: number) => `/admin/rate-limits/reset/user/${userId}`,
      RESET_IP: (ip: string) => `/admin/rate-limits/reset/ip/${ip}`,
      SERVICES: '/admin/rate-limits/services',
    },
  },
  // Bot Management
  BOTS: {
    LIST: '/admin/bots',
    DETAILS: (id: string) => `/admin/bots/${id}`,
    ACTIONS: '/admin/bots/actions',
  },
};
