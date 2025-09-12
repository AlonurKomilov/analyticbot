import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

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

const NavigationContext = createContext({});

// Navigation analytics and tracking
const useNavigationAnalytics = () => {
    const [pageViews, setPageViews] = useState([]);
    const [sessionStart] = useState(Date.now());

    const trackPageView = useCallback((path, title) => {
        const view = {
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
        console.log('Navigation Analytics:', {
            path,
            title,
            sessionTime: Date.now() - sessionStart
        });
    }, [sessionStart]);

    return {
        pageViews,
        trackPageView,
        sessionStart
    };
};

// User preferences management
const useUserPreferences = () => {
    const [preferences, setPreferences] = useState(() => {
        try {
            const saved = localStorage.getItem('navigationPreferences');
            return saved ? JSON.parse(saved) : {
                theme: 'light',
                sidebarCollapsed: false,
                quickActions: [],
                recentPages: [],
                bookmarks: [],
                searchHistory: []
            };
        } catch {
            return {
                theme: 'light',
                sidebarCollapsed: false,
                quickActions: [],
                recentPages: [],
                bookmarks: [],
                searchHistory: []
            };
        }
    });

    const updatePreferences = useCallback((updates) => {
        setPreferences(prev => {
            const updated = { ...prev, ...updates };
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

    const addToRecentPages = useCallback((page) => {
        const recent = preferences.recentPages || [];
        const filtered = recent.filter(p => p.path !== page.path);
        const updated = [page, ...filtered].slice(0, 10); // Keep last 10

        updatePreferences({ recentPages: updated });
    }, [preferences.recentPages, updatePreferences]);

    const addBookmark = useCallback((bookmark) => {
        const bookmarks = preferences.bookmarks || [];
        const exists = bookmarks.find(b => b.path === bookmark.path);
        
        if (!exists) {
            const updated = [bookmark, ...bookmarks].slice(0, 20); // Max 20 bookmarks
            updatePreferences({ bookmarks: updated });
        }
    }, [preferences.bookmarks, updatePreferences]);

    const removeBookmark = useCallback((path) => {
        const bookmarks = preferences.bookmarks || [];
        const updated = bookmarks.filter(b => b.path !== path);
        updatePreferences({ bookmarks: updated });
    }, [preferences.bookmarks, updatePreferences]);

    const isBookmarked = useCallback((path) => {
        const bookmarks = preferences.bookmarks || [];
        return bookmarks.some(b => b.path === path);
    }, [preferences.bookmarks]);

    // Track current page
    useEffect(() => {
        const pathSegments = location.pathname.split('/').filter(Boolean);
        const title = pathSegments.length > 0 
            ? pathSegments[pathSegments.length - 1]
                .split('-')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ')
            : 'Dashboard';

        addToRecentPages({
            path: location.pathname,
            title,
            timestamp: Date.now()
        });
    }, [location.pathname, addToRecentPages]);

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

    const addSearchHistory = useCallback((query) => {
        if (!query.trim()) return;

        const history = preferences.searchHistory || [];
        const filtered = history.filter(h => h.query !== query);
        const updated = [
            { query, timestamp: Date.now() },
            ...filtered
        ].slice(0, 20); // Keep last 20 searches

        updatePreferences({ searchHistory: updated });
    }, [preferences.searchHistory, updatePreferences]);

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
    const [notifications, setNotifications] = useState([]);

    const addNotification = useCallback((notification) => {
        const id = Date.now();
        const newNotification = {
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

    const markAsRead = useCallback((id) => {
        setNotifications(prev => 
            prev.map(n => n.id === id ? { ...n, read: true } : n)
        );
    }, []);

    const removeNotification = useCallback((id) => {
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
export const NavigationProvider = ({ children }) => {
    const location = useLocation();
    const navigate = useNavigate();
    
    // Hooks
    const { pageViews, trackPageView } = useNavigationAnalytics();
    const { preferences, updatePreferences } = useUserPreferences();
    const navigationHistory = useNavigationHistoryInternal();
    const navigationSearch = useNavigationSearchInternal();
    const notificationSystem = useNotificationsInternal();

    // Theme management
    const [isDarkMode, setIsDarkMode] = useState(() => 
        preferences.theme === 'dark'
    );

    const toggleTheme = useCallback(() => {
        const newTheme = isDarkMode ? 'light' : 'dark';
        setIsDarkMode(!isDarkMode);
        updatePreferences({ theme: newTheme });
    }, [isDarkMode, updatePreferences]);

    // Navigation helpers
    const navigateWithTracking = useCallback((path, options = {}) => {
        navigate(path, options);
        
        // Track navigation
        if (options.title) {
            trackPageView(path, options.title);
        }
    }, [navigate, trackPageView]);

    // Page title management
    const [pageTitle, setPageTitle] = useState('Dashboard');

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
    const [navigationPerformance, setNavigationPerformance] = useState({});

    const trackNavigationTiming = useCallback((path, startTime) => {
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
    const contextValue = {
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
        formatPath: (path) => {
            return path.split('/').filter(Boolean).join(' > ') || 'Dashboard';
        },
        
        getRouteInfo: (path) => {
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
export const useNavigation = () => {
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