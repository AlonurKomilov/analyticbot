import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';
import { useLocation, useNavigate, NavigateOptions } from 'react-router-dom';

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

/**
 * Type definitions
 */
export interface PageView {
    id: number;
    path: string;
    title: string;
    timestamp: number;
    duration: number;
}

export interface RecentPage {
    path: string;
    title: string;
    timestamp: number;
}

export interface Bookmark {
    path: string;
    title: string;
    timestamp: number;
}

export interface SearchHistoryItem {
    query: string;
    timestamp: number;
}

export interface Notification {
    id?: number;
    title: string;
    message: string;
    type?: 'info' | 'success' | 'warning' | 'error';
    persistent?: boolean;
    timestamp?: number;
    read?: boolean;
}

export interface UserPreferences {
    theme: 'light' | 'dark';
    sidebarCollapsed: boolean;
    quickActions: any[];
    recentPages: RecentPage[];
    bookmarks: Bookmark[];
    searchHistory: SearchHistoryItem[];
}

export interface NavigationPerformance {
    [path: string]: {
        duration: number;
        timestamp: number;
    };
}

export interface RouteInfo {
    path: string;
    title: string;
    level: number;
}

export interface NavigateWithTrackingOptions extends NavigateOptions {
    title?: string;
}

export interface NavigationContextValue {
    currentPath: string;
    pageTitle: string;
    setPageTitle: (title: string) => void;
    isDarkMode: boolean;
    toggleTheme: () => void;
    preferences: UserPreferences;
    updatePreferences: (updates: Partial<UserPreferences>) => void;
    navigate: (path: string, options?: NavigateWithTrackingOptions) => void;
    recentPages: RecentPage[];
    bookmarks: Bookmark[];
    addBookmark: (bookmark: Bookmark) => void;
    removeBookmark: (path: string) => void;
    isBookmarked: (path: string) => boolean;
    searchHistory: SearchHistoryItem[];
    addSearchHistory: (query: string) => void;
    clearSearchHistory: () => void;
    notifications: Notification[];
    unreadCount: number;
    addNotification: (notification: Notification) => void;
    markAsRead: (id: number) => void;
    removeNotification: (id: number) => void;
    clearAllNotifications: () => void;
    pageViews: PageView[];
    navigationPerformance: NavigationPerformance;
    trackNavigationTiming: (path: string, startTime: number) => void;
    formatPath: (path: string) => string;
    getRouteInfo: (path: string) => RouteInfo;
}

export interface NavigationProviderProps {
    children: ReactNode;
}

const NavigationContext = createContext<NavigationContextValue | undefined>(undefined);

// Navigation analytics and tracking
const useNavigationAnalytics = () => {
    const [pageViews, setPageViews] = useState<PageView[]>([]);
    const [sessionStart] = useState(Date.now());

    const trackPageView = useCallback((path: string, title: string) => {
        const view: PageView = {
            id: Date.now(),
            path,
            title,
            timestamp: Date.now(),
            duration: 0
        };

        setPageViews(prev => {
            // Update duration of previous page
            const updated = [...prev];
            if (updated.length > 0) {
                const lastView = updated[updated.length - 1];
                lastView.duration = Date.now() - lastView.timestamp;
            }

            return [...updated, view].slice(-50); // Keep last 50 views
        });

        // Analytics tracking (could integrate with Google Analytics, etc.)
        // Disabled verbose logging - enable only when debugging navigation
        if (process.env.NODE_ENV === 'development' && process.env.VITE_DEBUG_NAVIGATION === 'true') {
            console.debug('[Navigation]', {
                path,
                title,
                sessionTime: Date.now() - sessionStart
            });
        }
    }, []); // Remove sessionStart dependency since it never changes

    return {
        pageViews,
        trackPageView,
        sessionStart
    };
};

// User preferences management
const useUserPreferences = () => {
    const [preferences, setPreferences] = useState<UserPreferences>(() => {
        try {
            const saved = localStorage.getItem('navigationPreferences');
            return saved ? JSON.parse(saved) : {
                theme: 'light' as const,
                sidebarCollapsed: false,
                quickActions: [],
                recentPages: [],
                bookmarks: [],
                searchHistory: []
            };
        } catch {
            return {
                theme: 'light' as const,
                sidebarCollapsed: false,
                quickActions: [],
                recentPages: [],
                bookmarks: [],
                searchHistory: []
            };
        }
    });

    const updatePreferences = useCallback((updates: Partial<UserPreferences> | ((prev: UserPreferences) => Partial<UserPreferences>)) => {
        setPreferences(prev => {
            const updateValues = typeof updates === 'function' ? updates(prev) : updates;
            const updated = { ...prev, ...updateValues };
            try {
                localStorage.setItem('navigationPreferences', JSON.stringify(updated));
            } catch (error) {
                console.warn('Failed to save navigation preferences:', error);
            }
            return updated;
        });
    }, []);

    return {
        preferences,
        updatePreferences
    };
};

// Recent pages and bookmarks functionality
const useNavigationHistoryInternal = () => {
    const location = useLocation();
    const { preferences, updatePreferences } = useUserPreferences();

    const addBookmark = useCallback((bookmark: Bookmark) => {
        updatePreferences(prev => {
            const bookmarks = prev.bookmarks || [];
            const exists = bookmarks.find(b => b.path === bookmark.path);

            if (!exists) {
                const updated = [bookmark, ...bookmarks].slice(0, 20); // Max 20 bookmarks
                return { bookmarks: updated };
            }
            return {};
        });
    }, [updatePreferences]);

    const removeBookmark = useCallback((path: string) => {
        updatePreferences(prev => {
            const bookmarks = prev.bookmarks || [];
            const updated = bookmarks.filter(b => b.path !== path);
            return { bookmarks: updated };
        });
    }, [updatePreferences]);

    const isBookmarked = useCallback((path: string): boolean => {
        const bookmarks = preferences.bookmarks || [];
        return bookmarks.some(b => b.path === path);
    }, [preferences]);

    // Track current page
    useEffect(() => {
        const pathSegments = location.pathname.split('/').filter(Boolean);
        const title = pathSegments.length > 0
            ? pathSegments[pathSegments.length - 1]
                .split('-')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ')
            : 'Dashboard';

        const page: RecentPage = {
            path: location.pathname,
            title,
            timestamp: Date.now()
        };

        // Use updatePreferences directly to avoid dependency loop
        updatePreferences(prev => {
            const recent = prev.recentPages || [];
            const filtered = recent.filter(p => p.path !== page.path);
            const updated = [page, ...filtered].slice(0, 10);
            return { recentPages: updated };
        });
    }, [location.pathname, updatePreferences]);

    return {
        recentPages: preferences.recentPages || [],
        bookmarks: preferences.bookmarks || [],
        addBookmark,
        removeBookmark,
        isBookmarked
    };
};

// Search functionality
const useNavigationSearchInternal = () => {
    const { preferences, updatePreferences } = useUserPreferences();

    const addSearchHistory = useCallback((query: string) => {
        if (!query.trim()) return;

        updatePreferences(prev => {
            const history = prev.searchHistory || [];
            const filtered = history.filter(h => h.query !== query);
            const updated: SearchHistoryItem[] = [
                { query, timestamp: Date.now() },
                ...filtered
            ].slice(0, 20); // Keep last 20 searches
            return { searchHistory: updated };
        });
    }, [updatePreferences]);

    const clearSearchHistory = useCallback(() => {
        updatePreferences({ searchHistory: [] });
    }, [updatePreferences]);

    return {
        searchHistory: preferences.searchHistory || [],
        addSearchHistory,
        clearSearchHistory
    };
};

// Notification management
const useNotificationsInternal = () => {
    const [notifications, setNotifications] = useState<Notification[]>([]);

    const addNotification = useCallback((notification: Notification) => {
        const id = Date.now();
        const newNotification: Notification = {
            id,
            timestamp: Date.now(),
            read: false,
            ...notification
        };

        setNotifications(prev => [newNotification, ...prev]);

        // Auto-remove after 5 minutes if not persistent
        if (!notification.persistent) {
            setTimeout(() => {
                setNotifications(prev => prev.filter(n => n.id !== id));
            }, 5 * 60 * 1000);
        }
    }, []);

    const markAsRead = useCallback((id: number) => {
        setNotifications(prev =>
            prev.map(n => n.id === id ? { ...n, read: true } : n)
        );
    }, []);

    const removeNotification = useCallback((id: number) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    }, []);

    const clearAllNotifications = useCallback(() => {
        setNotifications([]);
    }, []);

    const unreadCount = notifications.filter(n => !n.read).length;

    return {
        notifications,
        unreadCount,
        addNotification,
        markAsRead,
        removeNotification,
        clearAllNotifications
    };
};

// Main Navigation Provider
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
    const navigateWithTracking = useCallback((path: string, options: NavigateWithTrackingOptions = {}) => {
        navigate(path, options);

        // Track navigation
        if (options.title) {
            trackPageView(path, options.title);
        }
    }, [navigate, trackPageView]);

    // Page title management
    const [pageTitle, setPageTitle] = useState<string>('Dashboard');

    useEffect(() => {
        // Update page title based on current route
        const pathSegments = location.pathname.split('/').filter(Boolean);
        const title = pathSegments.length > 0
            ? pathSegments[pathSegments.length - 1]
                .split('-')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ')
            : 'Dashboard';

        setPageTitle(title);
        document.title = `${title} - AnalyticBot`;
        trackPageView(location.pathname, title);
    }, [location.pathname, trackPageView]);

    // Performance monitoring
    const [navigationPerformance, setNavigationPerformance] = useState<NavigationPerformance>({});

    const trackNavigationTiming = useCallback((path: string, startTime: number) => {
        const endTime = performance.now();
        const duration = endTime - startTime;

        setNavigationPerformance(prev => ({
            ...prev,
            [path]: {
                duration,
                timestamp: Date.now()
            }
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
            // Route metadata could be enhanced here
            return {
                path,
                title: path.split('/').pop() || 'Dashboard',
                level: path.split('/').length - 1
            };
        }
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
    const { recentPages, bookmarks, addBookmark, removeBookmark, isBookmarked } = useNavigation();
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
        clearAllNotifications
    } = useNavigation();

    return {
        notifications,
        unreadCount,
        addNotification,
        markAsRead,
        removeNotification,
        clearAllNotifications
    };
};

export default NavigationProvider;
