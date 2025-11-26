/**
 * Advanced Lazy Loading System with Preloading
 * TypeScript version with enhanced type safety and performance optimizations
 */

import { lazy, ComponentType, LazyExoticComponent } from 'react';

// Preloading cache for faster subsequent loads
const preloadCache = new Map<() => Promise<any>, Promise<any>>();

export interface PreloadConditions {
  /** Preload after specified milliseconds (0 for immediate) */
  preloadAfter?: number;
  /** Enable preload on hover */
  preloadOnHover?: boolean;
  /** Enable preload when browser is idle */
  preloadOnIdle?: boolean;
}

export interface PreloadableComponent<T extends ComponentType<any>> extends LazyExoticComponent<T> {
  preload: () => Promise<{ default: T }>;
}

/**
 * Enhanced lazy loading with preloading support
 */
export function lazyWithPreload<T extends ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  preloadConditions: PreloadConditions = {}
): PreloadableComponent<T> {
  const {
    preloadAfter = 2000,
    preloadOnIdle = true,
  } = preloadConditions;

  const LazyComponent = lazy(importFn);

  // Preload function
  const preload = (): Promise<{ default: T }> => {
    if (!preloadCache.has(importFn)) {
      const promise = importFn();
      preloadCache.set(importFn, promise);
      return promise;
    }
    return preloadCache.get(importFn)!;
  };

  // Auto-preload after delay
  if (preloadAfter >= 0) {
    setTimeout(preload, preloadAfter);
  }

  // Preload when browser is idle
  if (preloadOnIdle && 'requestIdleCallback' in window) {
    window.requestIdleCallback(() => preload());
  }

  // Add preload method to component
  (LazyComponent as PreloadableComponent<T>).preload = preload;

  return LazyComponent as PreloadableComponent<T>;
}

/**
 * Critical route components with immediate preloading
 */
export const CriticalComponents = {
  MainDashboard: lazyWithPreload(
    () => import('../MainDashboard.jsx'),
    { preloadAfter: 0 }
  ),

  AnalyticsDashboard: lazyWithPreload(
    () => import('../features/dashboard/analytics-dashboard/AnalyticsDashboard'),
    { preloadAfter: 2000 }
  ),
};

/**
 * Page components with optimized loading
 */
export const PageComponents = {
  DashboardPage: lazyWithPreload(
    () => import('../pages/DashboardPage.jsx'),
    { preloadAfter: 0 } // Critical page
  ),

  CreatePostPage: lazyWithPreload(
    () => import('../pages/posts/create'),
    { preloadAfter: 2000 }
  ),

  AnalyticsPage: lazyWithPreload(
    () => import('../pages/AnalyticsPage.jsx'),
    { preloadAfter: 1500 }
  ),

  AuthPage: lazyWithPreload(
    () => import('../pages/AuthPage.jsx'),
    { preloadAfter: 0 } // Critical for login flow
  ),

  ProfilePage: lazyWithPreload(
    () => import('../pages/ProfilePage.jsx'),
    { preloadAfter: 3000 }
  ),

  AdminDashboard: lazyWithPreload(
    () => import('../pages/AdminDashboard.jsx'),
    { preloadAfter: 5000 }
  ),

  ResetPasswordForm: lazyWithPreload(
    () => import('../features/auth/login/ResetPasswordForm'),
    { preloadOnHover: true }
  ),
};

/**
 * Admin components with hover preloading
 */
export const AdminComponents = {
  // SuperAdminDashboard archived - use @features/admin instead
  // SuperAdminDashboard: lazyWithPreload(
  //   () => import('../components/domains/admin/SuperAdminDashboard.jsx'),
  //   { preloadAfter: 3000, preloadOnHover: true }
  // ),
};

/**
 * Service components with lazy preloading
 */
export const ServiceComponents = {
  ServicesLayout: lazyWithPreload(
    () => import('../services/ServicesLayout.jsx'),
    { preloadAfter: 4000 }
  ),

  ContentOptimizerService: lazyWithPreload(
    () => import('../features/ai-services/ContentOptimizer').then(m => ({ default: m.ContentOptimizerPage })),
    { preloadAfter: 6000 }
  ),

  PredictiveAnalyticsService: lazyWithPreload(
    () => import('../services/PredictiveAnalyticsService.jsx'),
    { preloadAfter: 8000 }
  ),

  ChurnPredictorService: lazyWithPreload(
    () => import('../services/ChurnPredictorService.jsx'),
    { preloadAfter: 10000 }
  ),

  SecurityMonitoringService: lazyWithPreload(
    () => import('../features/ai-services/SecurityMonitoring').then(m => ({ default: m.SecurityMonitoringPage })),
    { preloadAfter: 12000 }
  ),
};

/**
 * Utility components with on-demand loading
 */
export const UtilityComponents = {
  // DataTablesShowcase and ServicesOverview archived
  // DataTablesShowcase: lazyWithPreload(
  //   () => import('../components/DataTablesShowcase.jsx'),
  //   { preloadAfter: 5000 }
  // ),

  SettingsPage: lazyWithPreload(
    () => import('../pages/SettingsPage.jsx'),
    { preloadOnHover: true }
  ),

  HelpPage: lazyWithPreload(
    () => import('../pages/HelpPage.jsx'),
    { preloadOnHover: true }
  ),

  // ServicesOverview: lazyWithPreload(
  //   () => import('../components/domains/services/ServicesOverview.jsx'),
  //   { preloadAfter: 7000 }
  // ),
};

/**
 * Preload critical components for better UX
 */
export const preloadCriticalComponents = (): void => {
  // Preload main pages immediately
  PageComponents.DashboardPage.preload();
  PageComponents.AuthPage.preload();

  // Preload main dashboard
  CriticalComponents.MainDashboard.preload();

  // Preload analytics dashboard after short delay
  setTimeout(() => {
    CriticalComponents.AnalyticsDashboard.preload();
    PageComponents.AnalyticsPage.preload();
  }, 1000);

  // Preload create post page
  setTimeout(() => {
    PageComponents.CreatePostPage.preload();
  }, 2000);
};

/**
 * Preload components based on user interaction patterns
 */
export const preloadByUserBehavior = (userRole: string = 'user'): void => {
  if (userRole === 'admin' || userRole === 'owner') {
    // Preload admin components for admin/owner users
    // AdminComponents.SuperAdminDashboard.preload(); // Archived
    PageComponents.AdminDashboard.preload();
  }

  // Preload most commonly used service components
  setTimeout(() => {
    ServiceComponents.ServicesLayout.preload();
  }, 3000);
};

/**
 * Smart preloading based on route patterns
 */
export const preloadByRoute = (currentPath: string): void => {
  if (currentPath.includes('/analytics')) {
    CriticalComponents.AnalyticsDashboard.preload();
    PageComponents.AnalyticsPage.preload();
  }

  if (currentPath.includes('/admin')) {
    // AdminComponents.SuperAdminDashboard.preload(); // Archived
    PageComponents.AdminDashboard.preload();
  }

  if (currentPath.includes('/services')) {
    ServiceComponents.ServicesLayout.preload();
    ServiceComponents.ContentOptimizerService.preload();
  }

  if (currentPath.includes('/create')) {
    PageComponents.CreatePostPage.preload();
  }

  if (currentPath.includes('/profile')) {
    PageComponents.ProfilePage.preload();
  }

  if (currentPath === '/' || currentPath.includes('/dashboard')) {
    PageComponents.DashboardPage.preload();
  }
};

/**
 * Initialize performance optimizations
 */
export const initializePerformanceOptimizations = (): void => {
  // Preload critical components
  preloadCriticalComponents();

  // Setup intersection observer for hover preloading
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const element = entry.target;
            const preloadTarget = element.getAttribute('data-preload');

            if (preloadTarget) {
              // Find and preload the target component
              const componentMap: Record<string, any> = {
                ...CriticalComponents,
                ...PageComponents,
                ...AdminComponents,
                ...ServiceComponents,
                ...UtilityComponents,
              };

              const targetComponent = componentMap[preloadTarget];
              if (targetComponent && targetComponent.preload) {
                targetComponent.preload();
              }
            }
          }
        });
      },
      { threshold: 0.1 }
    );

    // Observe elements with preload attributes
    setTimeout(() => {
      document.querySelectorAll('[data-preload]').forEach((el) => {
        observer.observe(el);
      });
    }, 1000);
  }

  // Preload on network idle (only on fast connections)
  if ('connection' in navigator) {
    const connection = (navigator as any).connection;

    // Only preload aggressively on fast connections
    if (connection && (connection.effectiveType === '4g' || connection.downlink > 2)) {
      setTimeout(() => {
        // Preload service components
        Object.values(ServiceComponents).forEach((component) => {
          if (component.preload) component.preload();
        });

        // Preload utility components
        Object.values(UtilityComponents).forEach((component) => {
          if (component.preload) component.preload();
        });
      }, 10000);
    }
  }
};

/**
 * Preload all components (use sparingly, e.g., after user interaction)
 */
export const preloadAll = (): void => {
  const allComponents = {
    ...CriticalComponents,
    ...PageComponents,
    ...AdminComponents,
    ...ServiceComponents,
    ...UtilityComponents,
  };

  Object.values(allComponents).forEach((component) => {
    if (component.preload) {
      component.preload();
    }
  });
};

/**
 * Clear preload cache (useful for memory management)
 */
export const clearPreloadCache = (): void => {
  preloadCache.clear();
};

/**
 * Get cache statistics
 */
export const getCacheStats = () => {
  return {
    cachedComponents: preloadCache.size,
    cacheKeys: Array.from(preloadCache.keys()).map((fn) => fn.toString()),
  };
};
