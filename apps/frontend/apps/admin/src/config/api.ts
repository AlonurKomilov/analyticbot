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
    VERIFY: '/auth/verify',
  },
  // Admin
  ADMIN: {
    STATS: '/admin/analytics/system-stats',
    USERS: '/admin/users',
    CHANNELS: '/admin/channels',
    AUDIT_LOG: '/admin/audit-log',
    HEALTH: '/admin/health',
  },
  // Bot Management
  BOTS: {
    LIST: '/admin/bots',
    DETAILS: (id: string) => `/admin/bots/${id}`,
    ACTIONS: '/admin/bot-actions',
  },
};
