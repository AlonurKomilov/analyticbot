// API Configuration for Moderator Panel
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
    ME: '/auth/me',
    CSRF_TOKEN: '/auth/csrf-token',
  },
  // Catalog Management
  CATALOG: {
    LIST: '/moderator/catalog',
    ADD: '/moderator/catalog/add',
    ENTRY: (id: number) => `/moderator/catalog/${id}`,
    FEATURE: (id: number) => `/moderator/catalog/${id}/feature`,
    VERIFY: (id: number) => `/moderator/catalog/${id}/verify`,
    SYNC: (id: number) => `/moderator/catalog/${id}/sync`,
    STATS: '/moderator/catalog/stats',
    LOOKUP: '/moderator/catalog/lookup',
  },
  // Categories
  CATEGORIES: {
    LIST: '/public/categories',
    MODERATOR_LIST: '/moderator/catalog/categories',
    CREATE: '/moderator/catalog/categories',
    UPDATE: (id: number) => `/moderator/catalog/categories/${id}`,
    DELETE: (id: number) => `/moderator/catalog/categories/${id}`,
  },
  // Public (for reference data)
  PUBLIC: {
    CATEGORIES: '/public/categories',
    STATS: '/public/stats',
  },
};
