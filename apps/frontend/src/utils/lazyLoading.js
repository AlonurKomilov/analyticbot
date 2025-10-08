/**
 * Advanced Lazy Loading System with Preloading
 * Optimized for performance with smart component loading strategies
 */

import { lazy, ComponentType } from 'react';

// Preloading cache for faster subsequent loads
const preloadCache = new Map();

/**
 * Enhanced lazy loading with preloading support
 */
export const lazyWithPreload = (importFn, preloadConditions = {}) => {
    const {
        preloadAfter = 2000, // Preload after 2 seconds
        preloadOnHover = true, // Preload on hover
        preloadOnIdle = true   // Preload when browser is idle
    } = preloadConditions;

    const LazyComponent = lazy(importFn);

    // Preload function
    const preload = () => {
        if (!preloadCache.has(importFn)) {
            const promise = importFn();
            preloadCache.set(importFn, promise);
            return promise;
        }
        return preloadCache.get(importFn);
    };

    // Auto-preload after delay
    if (preloadAfter > 0) {
        setTimeout(preload, preloadAfter);
    }

    // Preload when browser is idle
    if (preloadOnIdle && 'requestIdleCallback' in window) {
        requestIdleCallback(preload);
    }

    // Add preload method to component
    LazyComponent.preload = preload;

    return LazyComponent;
};

/**
 * Critical route components with immediate preloading
 */
export const CriticalComponents = {
    MainDashboard: lazyWithPreload(
        () => import('../MainDashboard.jsx'),
        { preloadAfter: 0 } // Immediate preload
    ),

    AnalyticsDashboard: lazyWithPreload(
        () => import('../components/dashboard/AnalyticsDashboard/AnalyticsDashboard'),
        { preloadAfter: 1000 }
    )
};

/**
 * Admin components with hover preloading
 */
export const AdminComponents = {
    SuperAdminDashboard: lazyWithPreload(
        () => import('../components/domains/admin/SuperAdminDashboard.jsx'),
        { preloadAfter: 3000, preloadOnHover: true }
    )
};

/**
 * Service components with lazy preloading
 */
export const ServiceComponents = {
    ServicesLayout: lazyWithPreload(
        () => import('../services/ServicesLayout.jsx'),
        { preloadAfter: 5000 }
    ),

    ContentOptimizerService: lazyWithPreload(
        () => import('../services/ContentOptimizerService.jsx'),
        { preloadAfter: 8000 }
    ),

    PredictiveAnalyticsService: lazyWithPreload(
        () => import('../services/PredictiveAnalyticsService.jsx'),
        { preloadAfter: 10000 }
    ),

    ChurnPredictorService: lazyWithPreload(
        () => import('../services/ChurnPredictorService.jsx'),
        { preloadAfter: 12000 }
    ),

    SecurityMonitoringService: lazyWithPreload(
        () => import('../services/SecurityMonitoringService.jsx'),
        { preloadAfter: 15000 }
    )
};

/**
 * Utility components with on-demand loading
 */
export const UtilityComponents = {
    DataTablesShowcase: lazyWithPreload(
        () => import('../components/DataTablesShowcase.jsx'),
        { preloadAfter: 5000 }
    ),

    SettingsPage: lazyWithPreload(
        () => import('../components/pages/SettingsPage.jsx'),
        { preloadOnHover: true }
    ),

    HelpPage: lazyWithPreload(
        () => import('../components/pages/HelpPage.jsx'),
        { preloadOnHover: true }
    ),

    ServicesOverview: lazyWithPreload(
        () => import('../components/domains/services/ServicesOverview.jsx'),
        { preloadAfter: 7000 }
    )
};

/**
 * Preload critical components for better UX
 */
export const preloadCriticalComponents = () => {
    // Preload main dashboard immediately
    CriticalComponents.MainDashboard.preload();

    // Preload analytics dashboard after short delay
    setTimeout(() => {
        CriticalComponents.AnalyticsDashboard.preload();
    }, 1000);
};

/**
 * Preload components based on user interaction patterns
 */
export const preloadByUserBehavior = (userRole = 'user') => {
    if (userRole === 'admin') {
        // Preload admin components for admin users
        AdminComponents.SuperAdminDashboard.preload();
    }

    // Preload most commonly used service components
    setTimeout(() => {
        ServiceComponents.ServicesLayout.preload();
    }, 3000);
};

/**
 * Smart preloading based on route patterns
 */
export const preloadByRoute = (currentPath) => {
    if (currentPath.includes('/analytics')) {
        CriticalComponents.AnalyticsDashboard.preload();
    }

    if (currentPath.includes('/admin')) {
        AdminComponents.SuperAdminDashboard.preload();
    }

    if (currentPath.includes('/services')) {
        ServiceComponents.ServicesLayout.preload();
        ServiceComponents.ContentOptimizerService.preload();
    }
};

/**
 * Initialize performance optimizations
 */
export const initializePerformanceOptimizations = () => {
    // Preload critical components
    preloadCriticalComponents();

    // Setup intersection observer for hover preloading
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const preloadTarget = element.getAttribute('data-preload');

                    if (preloadTarget && window[preloadTarget]) {
                        window[preloadTarget]();
                    }
                }
            });
        }, { threshold: 0.1 });

        // Observe elements with preload attributes
        document.querySelectorAll('[data-preload]').forEach((el) => {
            observer.observe(el);
        });
    }

    // Preload on network idle
    if ('navigator' in window && 'connection' in navigator) {
        const connection = navigator.connection;

        // Only preload aggressively on fast connections
        if (connection.effectiveType === '4g' || connection.downlink > 2) {
            setTimeout(() => {
                Object.values(ServiceComponents).forEach((component) => {
                    if (component.preload) component.preload();
                });
            }, 10000);
        }
    }
};
