/**
 * Navigation Context Provider
 *
 * Manages global navigation state including:
 * - Navigation history and analytics
 * - User preferences (theme, layout)
 * - Recent pages and bookmarks
 * - Search history
 * - Quick action configurations
 */

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import {
  NavigationContextValue,
  NavigationProviderProps,
  NavigateWithTrackingOptions,
  NavigationPerformance,
  RouteInfo,
} from './types';
import { useNavigationAnalytics } from './useNavigationAnalytics';
import { useUserPreferences } from './useUserPreferences';
import { useNavigationHistoryInternal } from './useNavigationHistory';
import { useNavigationSearchInternal } from './useNavigationSearch';
import { useNotificationsInternal } from './useNotifications';

const NavigationContext = createContext<NavigationContextValue | undefined>(undefined);

export const NavigationProvider: React.FC<NavigationProviderProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();

  // Hooks
  const { pageViews, trackPageView } = useNavigationAnalytics();
  const { preferences, updatePreferences } = useUserPreferences();
  const navigationHistory = useNavigationHistoryInternal();
  const navigationSearch = useNavigationSearchInternal();
  const notificationSystem = useNotificationsInternal();

  // Theme management
  const isDarkMode = preferences.theme === 'dark';

  const toggleTheme = useCallback(() => {
    const newTheme = preferences.theme === 'dark' ? 'light' : 'dark';
    updatePreferences({ theme: newTheme });
  }, [preferences.theme, updatePreferences]);

  // Navigation helpers
  const navigateWithTracking = useCallback(
    (path: string, options: NavigateWithTrackingOptions = {}) => {
      navigate(path, options);

      // Track navigation
      if (options.title) {
        trackPageView(path, options.title);
      }
    },
    [navigate, trackPageView]
  );

  // Page title management
  const [pageTitle, setPageTitle] = useState<string>('Dashboard');

  useEffect(() => {
    // Update page title based on current route
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const title =
      pathSegments.length > 0
        ? pathSegments[pathSegments.length - 1]
            .split('-')
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ')
        : 'Dashboard';

    setPageTitle(title);
    document.title = `${title} - AnalyticBot`;
    trackPageView(location.pathname, title);
  }, [location.pathname, trackPageView]);

  // Performance monitoring
  const [navigationPerformance, setNavigationPerformance] =
    useState<NavigationPerformance>({});

  const trackNavigationTiming = useCallback((path: string, startTime: number) => {
    const endTime = performance.now();
    const duration = endTime - startTime;

    setNavigationPerformance((prev) => ({
      ...prev,
      [path]: {
        duration,
        timestamp: Date.now(),
      },
    }));
  }, []);

  // Context value
  const contextValue: NavigationContextValue = {
    // Current state
    currentPath: location.pathname,
    pageTitle,
    setPageTitle,

    // Theme
    isDarkMode,
    toggleTheme,

    // Preferences
    preferences,
    updatePreferences,

    // Navigation
    navigate: navigateWithTracking,
    ...navigationHistory,

    // Search
    ...navigationSearch,

    // Notifications
    ...notificationSystem,

    // Analytics
    pageViews,
    navigationPerformance,
    trackNavigationTiming,

    // Utility functions
    formatPath: (path: string) => {
      return path.split('/').filter(Boolean).join(' > ') || 'Dashboard';
    },

    getRouteInfo: (path: string): RouteInfo => {
      return {
        path,
        title: path.split('/').pop() || 'Dashboard',
        level: path.split('/').length - 1,
      };
    },
  };

  return (
    <NavigationContext.Provider value={contextValue}>
      {children}
    </NavigationContext.Provider>
  );
};

// Hook to use navigation context
export const useNavigation = (): NavigationContextValue => {
  const context = useContext(NavigationContext);

  if (context === undefined) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }

  return context;
};

// Specialized hooks for specific functionality
export const useNavigationPreferences = () => {
  const { preferences, updatePreferences } = useNavigation();
  return { preferences, updatePreferences };
};

export const useNavigationHistory = () => {
  const { recentPages, bookmarks, addBookmark, removeBookmark, isBookmarked } =
    useNavigation();
  return { recentPages, bookmarks, addBookmark, removeBookmark, isBookmarked };
};

export const useNavigationSearch = () => {
  const { searchHistory, addSearchHistory, clearSearchHistory } = useNavigation();
  return { searchHistory, addSearchHistory, clearSearchHistory };
};

export const useNotifications = () => {
  const {
    notifications,
    unreadCount,
    addNotification,
    markAsRead,
    removeNotification,
    clearAllNotifications,
  } = useNavigation();

  return {
    notifications,
    unreadCount,
    addNotification,
    markAsRead,
    removeNotification,
    clearAllNotifications,
  };
};

export default NavigationProvider;
