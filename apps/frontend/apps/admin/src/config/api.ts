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
    STATS: '/admin/system/stats',  // Correct endpoint
    USERS: '/admin/users',
    CHANNELS: '/admin/channels',
    AUDIT_LOG: '/admin/system/audit-logs',  // Correct endpoint
    HEALTH: '/admin/system/health',  // Correct endpoint
  },
  // Bot Management
  BOTS: {
    LIST: '/admin/bots',
    DETAILS: (id: string) => `/admin/bots/${id}`,
    ACTIONS: '/admin/bots/actions',
  },
};
