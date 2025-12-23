/**
 * Application Constants
 * Shared constants used across the application
 */

/**
 * Application Metadata
 */
export const APP = {
  NAME: 'AnalyticBot',
  VERSION: '1.0.0',
  DESCRIPTION: 'Advanced Telegram Analytics and Management Platform',
  AUTHOR: 'AnalyticBot Team',
  HOMEPAGE: 'https://analyticbot.com',
} as const;

/**
 * Local Storage Keys
 */
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_PREFERENCES: 'user_preferences',
  THEME: 'theme',
  DATA_SOURCE: 'data_source',
  LAST_CHANNEL: 'last_selected_channel',
  SIDEBAR_STATE: 'sidebar_collapsed',
  TOUR_COMPLETED: 'onboarding_tour_completed',
} as const;

/**
 * Session Storage Keys
 */
export const SESSION_KEYS = {
  REDIRECT_URL: 'redirect_url',
  FORM_DATA: 'temp_form_data',
  UPLOAD_PROGRESS: 'upload_progress',
} as const;

/**
 * API Configuration
 */
export const API = {
  TIMEOUT: {
    DEFAULT: 30000,        // 30 seconds
    UPLOAD: 120000,        // 2 minutes
    LONG_RUNNING: 300000,  // 5 minutes
    WEBSOCKET: 5000,       // 5 seconds
  },
  RETRY: {
    MAX_ATTEMPTS: 3,
    DELAY: 1000,           // 1 second
    BACKOFF_FACTOR: 2,
  },
  RATE_LIMIT: {
    MAX_REQUESTS: 100,
    WINDOW_MS: 60000,      // 1 minute
  },
} as const;

/**
 * Pagination Settings
 */
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [10, 25, 50, 100],
  MAX_PAGE_SIZE: 100,
} as const;

/**
 * Date & Time Formats
 */
export const DATE_FORMATS = {
  DISPLAY: 'MMM DD, YYYY',
  DISPLAY_LONG: 'MMMM DD, YYYY',
  DISPLAY_TIME: 'MMM DD, YYYY HH:mm',
  API: 'YYYY-MM-DD',
  API_DATETIME: 'YYYY-MM-DDTHH:mm:ss',
  TIME_ONLY: 'HH:mm',
  TIME_12H: 'hh:mm A',
} as const;

/**
 * File Upload Limits
 */
export const UPLOAD = {
  MAX_FILE_SIZE: 10 * 1024 * 1024,  // 10 MB
  MAX_IMAGE_SIZE: 5 * 1024 * 1024,   // 5 MB
  MAX_VIDEO_SIZE: 50 * 1024 * 1024,  // 50 MB
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  ALLOWED_VIDEO_TYPES: ['video/mp4', 'video/webm', 'video/ogg'],
  ALLOWED_DOCUMENT_TYPES: ['application/pdf', 'application/msword', 'text/plain'],
} as const;

/**
 * Chart & Analytics Settings
 */
export const ANALYTICS = {
  DEFAULT_PERIOD: '7d',
  PERIODS: ['24h', '7d', '30d', '90d', 'all'] as const,
  CHART_COLORS: {
    PRIMARY: '#1976d2',
    SECONDARY: '#dc004e',
    SUCCESS: '#4caf50',
    WARNING: '#ff9800',
    ERROR: '#f44336',
    INFO: '#2196f3',
  },
  REFRESH_INTERVAL: 60000,  // 1 minute
} as const;

/**
 * UI Constants
 */
export const UI = {
  DEBOUNCE_DELAY: 300,      // 300ms
  TOAST_DURATION: 3000,     // 3 seconds
  LOADING_DELAY: 200,       // Show loader after 200ms
  ANIMATION_DURATION: 200,  // 200ms for transitions
  SIDEBAR_WIDTH: 240,       // pixels
  SIDEBAR_WIDTH_COLLAPSED: 60,
  HEADER_HEIGHT: 64,
  MOBILE_BREAKPOINT: 768,
} as const;

/**
 * Validation Rules
 */
export const VALIDATION = {
  USERNAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 30,
    PATTERN: /^[a-zA-Z0-9_]+$/,
  },
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  PASSWORD: {
    MIN_LENGTH: 8,
    MAX_LENGTH: 128,
    REQUIRE_UPPERCASE: true,
    REQUIRE_LOWERCASE: true,
    REQUIRE_NUMBER: true,
    REQUIRE_SPECIAL: false,
  },
  POST: {
    MIN_LENGTH: 1,
    MAX_LENGTH: 4096,
  },
  CHANNEL_NAME: {
    MIN_LENGTH: 1,
    MAX_LENGTH: 255,
  },
} as const;

/**
 * Error Messages
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'Unauthorized. Please log in again.',
  FORBIDDEN: 'You do not have permission to access this resource.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  UPLOAD_ERROR: 'Failed to upload file. Please try again.',
  GENERIC_ERROR: 'An error occurred. Please try again.',
} as const;

/**
 * Success Messages
 */
export const SUCCESS_MESSAGES = {
  LOGIN: 'Successfully logged in!',
  LOGOUT: 'Successfully logged out!',
  SAVE: 'Changes saved successfully!',
  DELETE: 'Deleted successfully!',
  UPLOAD: 'File uploaded successfully!',
  COPY: 'Copied to clipboard!',
} as const;

/**
 * WebSocket Events
 */
export const WS_EVENTS = {
  CONNECT: 'connect',
  DISCONNECT: 'disconnect',
  ERROR: 'error',
  ANALYTICS_UPDATE: 'analytics:update',
  POST_UPDATE: 'post:update',
  CHANNEL_UPDATE: 'channel:update',
  NOTIFICATION: 'notification',
} as const;

/**
 * Feature Limits by Tier
 */
export const TIER_LIMITS = {
  free: {
    channels: 1,
    posts_per_day: 10,
    storage_mb: 100,
    analytics_days: 7,
  },
  basic: {
    channels: 5,
    posts_per_day: 50,
    storage_mb: 1000,
    analytics_days: 30,
  },
  premium: {
    channels: 25,
    posts_per_day: 200,
    storage_mb: 5000,
    analytics_days: 90,
  },
  enterprise: {
    channels: -1,  // unlimited
    posts_per_day: -1,
    storage_mb: -1,
    analytics_days: -1,
  },
} as const;

/**
 * Export all constants
 */
export const CONSTANTS = {
  APP,
  STORAGE_KEYS,
  SESSION_KEYS,
  API,
  PAGINATION,
  DATE_FORMATS,
  UPLOAD,
  ANALYTICS,
  UI,
  VALIDATION,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  WS_EVENTS,
  TIER_LIMITS,
} as const;
