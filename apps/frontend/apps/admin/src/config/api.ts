// API Configuration for Admin Panel
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'https://api.analyticbot.org',
  TIMEOUT: 30000,
};

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',  // Use /auth/me to verify token and get user info
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
  },
  // Bot Management
  BOTS: {
    LIST: '/admin/bots',
    DETAILS: (id: string) => `/admin/bots/${id}`,
    ACTIONS: '/admin/bots/actions',
  },
};
