// Route paths for Admin Panel
export const ROUTES = {
  // Auth
  LOGIN: '/login',

  // Dashboard
  DASHBOARD: '/',

  // User Management
  USERS: '/users',
  USER_DETAILS: '/users/:id',

  // Channel Management
  CHANNELS: '/channels',
  CHANNEL_DETAILS: '/channels/:id',

  // Bot Management
  BOTS: '/bots',
  BOT_DETAILS: '/bots/:id',

  // MTProto Management
  MTPROTO: '/mtproto',

  // Plans Management
  PLANS: '/plans',

  // System
  SYSTEM_HEALTH: '/system/health',
  SYSTEM_AUDIT: '/system/audit',
  SYSTEM_RATE_LIMITS: '/system/rate-limits',

  // System AI
  AI_DASHBOARD: '/ai',
  AI_WORKERS: '/ai/workers',
  AI_DECISIONS: '/ai/decisions',
  AI_CONFIG: '/ai/config',

  // Settings
  SETTINGS: '/settings',
};
