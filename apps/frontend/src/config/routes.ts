/**
 * Route Configuration
 * Centralized route definitions for the application
 */

/**
 * Application routes
 */
export const ROUTES = {
  // Auth Routes
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  RESET_PASSWORD: '/reset-password',
  VERIFY_EMAIL: '/verify-email',

  // Dashboard Routes
  DASHBOARD: '/dashboard',
  ANALYTICS: '/analytics',
  ADVANCED_ANALYTICS: '/analytics/advanced',

  // Admin Routes
  ADMIN: '/admin',
  ADMIN_USERS: '/admin/users',
  ADMIN_CHANNELS: '/admin/channels',
  ADMIN_SETTINGS: '/admin/settings',
  SYSTEM_HEALTH: '/admin/health',

  // Content Routes
  POSTS: '/posts',
  CREATE_POST: '/posts/create',
  EDIT_POST: '/posts/:id/edit',
  POST_DETAILS: '/posts/:id',
  SCHEDULED_POSTS: '/posts/scheduled',

  // Channel Routes
  CHANNELS: '/channels',
  CHANNEL_DETAILS: '/channels/:id',
  ADD_CHANNEL: '/channels/add',

  // AI Services Routes
  AI_SERVICES: '/ai-services',
  CONTENT_OPTIMIZER: '/ai-services/optimizer',
  PREDICTIVE_ANALYTICS: '/ai-services/predictive',
  SECURITY_MONITORING: '/ai-services/security',

  // Protection Routes
  CONTENT_PROTECTION: '/protection',

  // Payment Routes
  PAYMENT: '/payment',
  SUBSCRIPTION: '/payment/subscription',
  PAYMENT_HISTORY: '/payment/history',
  INVOICES: '/payment/invoices',

  // User Routes
  PROFILE: '/profile',
  SETTINGS: '/settings',
  HELP: '/help',

  // Error Routes
  NOT_FOUND: '/404',
  UNAUTHORIZED: '/401',
  SERVER_ERROR: '/500',
} as const;

export type AppRoutes = typeof ROUTES;
export type RoutePath = (typeof ROUTES)[keyof typeof ROUTES];

/**
 * Route metadata for navigation and breadcrumbs
 */
export interface RouteMetadata {
  path: RoutePath;
  title: string;
  description?: string;
  requiresAuth?: boolean;
  minTier?: string;
  icon?: string;
  breadcrumbs?: string[];
}

/**
 * Route metadata definitions
 */
export const ROUTE_METADATA: Record<string, RouteMetadata> = {
  HOME: {
    path: ROUTES.HOME,
    title: 'Home',
    description: 'Welcome to AnalyticBot',
  },
  
  DASHBOARD: {
    path: ROUTES.DASHBOARD,
    title: 'Dashboard',
    description: 'Overview of your analytics',
    requiresAuth: true,
    icon: 'dashboard',
  },
  
  ANALYTICS: {
    path: ROUTES.ANALYTICS,
    title: 'Analytics',
    description: 'Detailed analytics and insights',
    requiresAuth: true,
    icon: 'analytics',
    breadcrumbs: ['Dashboard', 'Analytics'],
  },
  
  ADMIN: {
    path: ROUTES.ADMIN,
    title: 'Admin Panel',
    description: 'System administration',
    requiresAuth: true,
    icon: 'admin_panel_settings',
    breadcrumbs: ['Dashboard', 'Admin'],
  },
  
  POSTS: {
    path: ROUTES.POSTS,
    title: 'Posts',
    description: 'Manage your posts',
    requiresAuth: true,
    icon: 'article',
    breadcrumbs: ['Dashboard', 'Posts'],
  },
  
  CREATE_POST: {
    path: ROUTES.CREATE_POST,
    title: 'Create Post',
    description: 'Create a new post',
    requiresAuth: true,
    icon: 'add',
    breadcrumbs: ['Dashboard', 'Posts', 'Create'],
  },
  
  AI_SERVICES: {
    path: ROUTES.AI_SERVICES,
    title: 'AI Services',
    description: 'AI-powered tools and insights',
    requiresAuth: true,
    minTier: 'premium',
    icon: 'psychology',
    breadcrumbs: ['Dashboard', 'AI Services'],
  },
  
  PAYMENT: {
    path: ROUTES.PAYMENT,
    title: 'Payment',
    description: 'Manage your subscription',
    requiresAuth: true,
    icon: 'payment',
    breadcrumbs: ['Dashboard', 'Payment'],
  },
  
  PROFILE: {
    path: ROUTES.PROFILE,
    title: 'Profile',
    description: 'Your profile settings',
    requiresAuth: true,
    icon: 'person',
    breadcrumbs: ['Dashboard', 'Profile'],
  },
  
  SETTINGS: {
    path: ROUTES.SETTINGS,
    title: 'Settings',
    description: 'Application settings',
    requiresAuth: true,
    icon: 'settings',
    breadcrumbs: ['Dashboard', 'Settings'],
  },
};

/**
 * Get route metadata
 */
export function getRouteMetadata(path: RoutePath): RouteMetadata | undefined {
  const key = Object.keys(ROUTES).find(k => ROUTES[k as keyof typeof ROUTES] === path);
  return key ? ROUTE_METADATA[key] : undefined;
}

/**
 * Build dynamic route path with parameters
 */
export function buildRoute(route: RoutePath, params?: Record<string, string | number>): string {
  if (!params) return route;
  
  let path: string = route;
  Object.entries(params).forEach(([key, value]) => {
    path = path.replace(`:${key}`, String(value));
  });
  
  return path;
}

/**
 * Check if a route requires authentication
 */
export function requiresAuth(path: RoutePath): boolean {
  const metadata = getRouteMetadata(path);
  return metadata?.requiresAuth ?? false;
}
