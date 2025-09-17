/**
 * 🔐 Authenticated Data Source Hooks
 * 
 * Enhanced data source hooks that integrate with AuthContext for JWT authentication.
 * These hooks automatically handle token-based API requests and authentication errors.
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { createAuthenticatedDataProvider } from '../providers/DataProvider.js';

/**
 * Hook to create an authenticated data provider instance
 * @param {string} baseUrl - Optional API base URL override
 * @returns {Object} Authenticated data provider with token management
 */
export const useAuthenticatedDataProvider = (baseUrl = null) => {
    const authContext = useAuth();
    
    const dataProvider = useMemo(() => {
        const provider = createAuthenticatedDataProvider(authContext, baseUrl);
        return provider;
    }, [authContext, baseUrl]);

    return dataProvider;
};

/**
 * Enhanced analytics hook with authentication
 * @param {string} channelId - Channel identifier
 * @param {Object} options - Additional options
 * @returns {Object} Analytics data with auth-aware loading states
 */
export const useAuthenticatedAnalytics = (channelId = 'demo_channel', options = {}) => {
    const { user, isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastFetch, setLastFetch] = useState(null);

    const fetchAnalytics = useCallback(async () => {
        if (!isAuthenticated) {
            setError('Authentication required');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const analyticsData = await dataProvider.getAnalytics(channelId);
            setData(analyticsData);
            setLastFetch(new Date().toISOString());
        } catch (err) {
            console.error('Failed to fetch analytics:', err);
            setError(err.message || 'Failed to fetch analytics data');
        } finally {
            setLoading(false);
        }
    }, [channelId, dataProvider, isAuthenticated]);

    // Auto-fetch when authenticated and channelId changes
    useEffect(() => {
        if (isAuthenticated && channelId) {
            fetchAnalytics();
        }
    }, [isAuthenticated, channelId, fetchAnalytics]);

    return {
        data,
        loading,
        error,
        lastFetch,
        refetch: fetchAnalytics,
        user,
        isAuthenticated
    };
};

/**
 * Enhanced top posts hook with authentication
 * @param {string} channelId - Channel identifier
 * @param {Object} queryOptions - Query parameters for filtering
 * @param {Object} options - Hook options
 * @returns {Object} Top posts data with auth-aware loading states
 */
export const useAuthenticatedTopPosts = (channelId = 'demo_channel', queryOptions = {}, options = {}) => {
    const { user, isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastFetch, setLastFetch] = useState(null);

    const fetchTopPosts = useCallback(async () => {
        if (!isAuthenticated) {
            setError('Authentication required');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const postsData = await dataProvider.getTopPosts(channelId, queryOptions);
            setData(postsData);
            setLastFetch(new Date().toISOString());
        } catch (err) {
            console.error('Failed to fetch top posts:', err);
            setError(err.message || 'Failed to fetch top posts data');
        } finally {
            setLoading(false);
        }
    }, [channelId, queryOptions, dataProvider, isAuthenticated]);

    // Auto-fetch when authenticated and parameters change
    useEffect(() => {
        if (isAuthenticated && channelId) {
            fetchTopPosts();
        }
    }, [isAuthenticated, channelId, queryOptions, fetchTopPosts]);

    return {
        data,
        loading,
        error,
        lastFetch,
        refetch: fetchTopPosts,
        user,
        isAuthenticated
    };
};

/**
 * Enhanced engagement metrics hook with authentication
 * @param {string} channelId - Channel identifier
 * @param {Object} queryOptions - Query parameters for filtering
 * @param {Object} options - Hook options
 * @returns {Object} Engagement metrics with auth-aware loading states
 */
export const useAuthenticatedEngagementMetrics = (channelId = 'demo_channel', queryOptions = {}, options = {}) => {
    const { user, isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastFetch, setLastFetch] = useState(null);

    const fetchEngagementMetrics = useCallback(async () => {
        if (!isAuthenticated) {
            setError('Authentication required');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const metricsData = await dataProvider.getEngagementMetrics(channelId, queryOptions);
            setData(metricsData);
            setLastFetch(new Date().toISOString());
        } catch (err) {
            console.error('Failed to fetch engagement metrics:', err);
            setError(err.message || 'Failed to fetch engagement metrics');
        } finally {
            setLoading(false);
        }
    }, [channelId, queryOptions, dataProvider, isAuthenticated]);

    // Auto-fetch when authenticated and parameters change
    useEffect(() => {
        if (isAuthenticated && channelId) {
            fetchEngagementMetrics();
        }
    }, [isAuthenticated, channelId, queryOptions, fetchEngagementMetrics]);

    return {
        data,
        loading,
        error,
        lastFetch,
        refetch: fetchEngagementMetrics,
        user,
        isAuthenticated
    };
};

/**
 * Enhanced recommendations hook with authentication
 * @param {string} channelId - Channel identifier
 * @param {Object} options - Hook options
 * @returns {Object} Recommendations data with auth-aware loading states
 */
export const useAuthenticatedRecommendations = (channelId = 'demo_channel', options = {}) => {
    const { user, isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastFetch, setLastFetch] = useState(null);

    const fetchRecommendations = useCallback(async () => {
        if (!isAuthenticated) {
            setError('Authentication required');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const recommendationsData = await dataProvider.getRecommendations(channelId);
            setData(recommendationsData);
            setLastFetch(new Date().toISOString());
        } catch (err) {
            console.error('Failed to fetch recommendations:', err);
            setError(err.message || 'Failed to fetch recommendations');
        } finally {
            setLoading(false);
        }
    }, [channelId, dataProvider, isAuthenticated]);

    // Auto-fetch when authenticated and channelId changes
    useEffect(() => {
        if (isAuthenticated && channelId) {
            fetchRecommendations();
        }
    }, [isAuthenticated, channelId, fetchRecommendations]);

    return {
        data,
        loading,
        error,
        lastFetch,
        refetch: fetchRecommendations,
        user,
        isAuthenticated
    };
};

/**
 * Enhanced data source availability checker with authentication
 * @param {Object} options - Hook options
 * @returns {Object} Availability status with auth context
 */
export const useAuthenticatedDataSourceStatus = (options = {}) => {
    const { enablePolling = false, pollingInterval = 30000 } = options;
    const { isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();
    const [isAvailable, setIsAvailable] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastCheck, setLastCheck] = useState(null);

    const checkAvailability = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const available = await dataProvider.isAvailable();
            setIsAvailable(available);
            setLastCheck(new Date().toISOString());
        } catch (err) {
            console.error('Failed to check data source availability:', err);
            setError(err.message || 'Failed to check availability');
            setIsAvailable(false);
        } finally {
            setLoading(false);
        }
    }, [dataProvider]);

    // Initial availability check
    useEffect(() => {
        checkAvailability();
    }, [checkAvailability]);

    // Polling if enabled
    useEffect(() => {
        if (enablePolling && isAuthenticated) {
            const interval = setInterval(checkAvailability, pollingInterval);
            return () => clearInterval(interval);
        }
    }, [enablePolling, pollingInterval, isAuthenticated, checkAvailability]);

    return {
        isAvailable,
        loading,
        error,
        lastCheck,
        refetch: checkAvailability,
        isAuthenticated
    };
};

/**
 * Combined hook that provides all authenticated data operations
 * @param {string} channelId - Channel identifier
 * @param {Object} options - Combined options for all data operations
 * @returns {Object} All data operations with shared auth state
 */
export const useAuthenticatedDataSource = (channelId = 'demo_channel', options = {}) => {
    const analytics = useAuthenticatedAnalytics(channelId, options);
    const topPosts = useAuthenticatedTopPosts(channelId, options.topPostsOptions || {}, options);
    const engagement = useAuthenticatedEngagementMetrics(channelId, options.engagementOptions || {}, options);
    const recommendations = useAuthenticatedRecommendations(channelId, options);
    const status = useAuthenticatedDataSourceStatus(options);

    const refetchAll = useCallback(async () => {
        await Promise.all([
            analytics.refetch(),
            topPosts.refetch(),
            engagement.refetch(),
            recommendations.refetch(),
            status.refetch()
        ]);
    }, [analytics, topPosts, engagement, recommendations, status]);

    return {
        analytics,
        topPosts,
        engagement,
        recommendations,
        status,
        refetchAll,
        isAuthenticated: analytics.isAuthenticated,
        user: analytics.user
    };
};