/**
 * Clean Data Source Hook - Production Code
 * Uses dependency injection to avoid mixed mock/production logic
 * Now supports optional AuthContext integration for JWT authentication
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { productionDataProvider } from '../providers/DataProvider.js';

/**
 * Clean hook for data management using dependency injection
 * NO mock switching logic - uses provider pattern instead
 */
export const useDataSource = (dataProvider = productionDataProvider, options = {}) => {
    const {
        onProviderChange = null,
        enableStatusPolling = false,
        pollingInterval = 30000, // 30 seconds
        autoCheckAvailability = true
    } = options;

    const [isAvailable, setIsAvailable] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [lastCheck, setLastCheck] = useState(null);

    const pollingRef = useRef(null);
    const providerRef = useRef(dataProvider);

    // Update provider reference when it changes
    useEffect(() => {
        providerRef.current = dataProvider;

        if (onProviderChange) {
            onProviderChange({
                provider: dataProvider.getProviderName(),
                timestamp: new Date().toISOString()
            });
        }
    }, [dataProvider, onProviderChange]);

    // Check provider availability
    const checkAvailability = useCallback(async (force = false) => {
        // Don't check too frequently unless forced
        if (!force && lastCheck && (Date.now() - lastCheck) < 10000) {
            return isAvailable;
        }

        setIsLoading(true);
        setError(null);

        try {
            const available = await providerRef.current.isAvailable();
            setIsAvailable(available);
            setLastCheck(Date.now());
            return available;
        } catch (err) {
            setError(`Availability check failed: ${err.message}`);
            setIsAvailable(false);
            console.error('Provider availability check failed:', err);
            return false;
        } finally {
            setIsLoading(false);
        }
    }, [isAvailable, lastCheck]);

    // Get analytics data
    const getAnalytics = useCallback(async (channelId) => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await providerRef.current.getAnalytics(channelId);
            return data;
        } catch (err) {
            setError(`Failed to get analytics: ${err.message}`);
            console.error('Analytics fetch failed:', err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Get top posts
    const getTopPosts = useCallback(async (channelId, options = {}) => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await providerRef.current.getTopPosts(channelId, options);
            return data;
        } catch (err) {
            setError(`Failed to get top posts: ${err.message}`);
            console.error('Top posts fetch failed:', err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Get engagement metrics
    const getEngagementMetrics = useCallback(async (channelId, options = {}) => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await providerRef.current.getEngagementMetrics(channelId, options);
            return data;
        } catch (err) {
            setError(`Failed to get engagement metrics: ${err.message}`);
            console.error('Engagement metrics fetch failed:', err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Get recommendations
    const getRecommendations = useCallback(async (channelId) => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await providerRef.current.getRecommendations(channelId);
            return data;
        } catch (err) {
            setError(`Failed to get recommendations: ${err.message}`);
            console.error('Recommendations fetch failed:', err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Setup availability polling and initial check
    useEffect(() => {
        // Initial availability check if enabled
        if (autoCheckAvailability) {
            checkAvailability(true);
        }

        // Setup availability polling if enabled
        if (enableStatusPolling) {
            pollingRef.current = setInterval(() => {
                checkAvailability(false);
            }, pollingInterval);
        }

        return () => {
            if (pollingRef.current) {
                clearInterval(pollingRef.current);
                pollingRef.current = null;
            }
        };
    }, [autoCheckAvailability, enableStatusPolling, pollingInterval, checkAvailability]);

    return {
        // State
        isAvailable,
        isLoading,
        error,
        lastCheck,
        providerName: dataProvider.getProviderName(),

        // Data fetching methods
        getAnalytics,
        getTopPosts,
        getEngagementMetrics,
        getRecommendations,

        // Utilities
        checkAvailability,
        isOnline: isAvailable === true,
        isOffline: isAvailable === false,

        // Clear error
        clearError: () => setError(null),
    };
};

/**
 * Clean analytics hook using data provider
 */
import { DEFAULT_CHANNEL_ID } from '../config/constants.js';

export const useAnalytics = (channelId = DEFAULT_CHANNEL_ID, dataProvider = productionDataProvider) => {
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchAnalytics = useCallback(async (forceRefresh = false) => {
        if (!forceRefresh && data) return data;

        setIsLoading(true);
        setError(null);

        try {
            const analyticsData = await dataProvider.getAnalytics(channelId);
            setData(analyticsData);
            return analyticsData;
        } catch (err) {
            setError(err.message);
            console.error('Analytics fetch failed:', err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [channelId, dataProvider, data]);

    // Auto-fetch on mount and provider change
    useEffect(() => {
        fetchAnalytics();
    }, [dataProvider, channelId]);

    return {
        data,
        isLoading,
        error,
        refetch: fetchAnalytics,
        clearError: () => setError(null),
    };
};

/**
 * Clean top posts hook using data provider
 */
export const useTopPosts = (channelId = DEFAULT_CHANNEL_ID, options = {}, dataProvider = productionDataProvider) => {
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchTopPosts = useCallback(async (forceRefresh = false) => {
        if (!forceRefresh && data) return data;

        setIsLoading(true);
        setError(null);

        try {
            const postsData = await dataProvider.getTopPosts(channelId, options);
            setData(postsData);
            return postsData;
        } catch (err) {
            setError(err.message);
            console.error('Top posts fetch failed:', err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [channelId, options, dataProvider, data]);

    useEffect(() => {
        fetchTopPosts();
    }, [dataProvider, channelId, options]);

    return {
        data,
        isLoading,
        error,
        refetch: fetchTopPosts,
        clearError: () => setError(null),
    };
};

/**
 * Clean engagement metrics hook using data provider
 */
export const useEngagementMetrics = (channelId = DEFAULT_CHANNEL_ID, options = {}, dataProvider = productionDataProvider) => {
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchEngagementMetrics = useCallback(async (forceRefresh = false) => {
        if (!forceRefresh && data) return data;

        setIsLoading(true);
        setError(null);

        try {
            const metricsData = await dataProvider.getEngagementMetrics(channelId, options);
            setData(metricsData);
            return metricsData;
        } catch (err) {
            setError(err.message);
            console.error('Engagement metrics fetch failed:', err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [channelId, options, dataProvider, data]);

    useEffect(() => {
        fetchEngagementMetrics();
    }, [dataProvider, channelId, options]);

    return {
        data,
        isLoading,
        error,
        refetch: fetchEngagementMetrics,
        clearError: () => setError(null),
    };
};

/**
 * Clean recommendations hook using data provider
 */
export const useRecommendations = (channelId = DEFAULT_CHANNEL_ID, dataProvider = productionDataProvider) => {
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchRecommendations = useCallback(async (forceRefresh = false) => {
        if (!forceRefresh && data) return data;

        setIsLoading(true);
        setError(null);

        try {
            const recommendationsData = await dataProvider.getRecommendations(channelId);
            setData(recommendationsData);
            return recommendationsData;
        } catch (err) {
            setError(err.message);
            console.error('Recommendations fetch failed:', err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [channelId, dataProvider, data]);

    useEffect(() => {
        fetchRecommendations();
    }, [dataProvider, channelId]);

    return {
        data,
        isLoading,
        error,
        refetch: fetchRecommendations,
        clearError: () => setError(null),
    };
};

/**
 * Composite hook for all analytics data using dependency injection
 */
export const useAllAnalytics = (channelId = DEFAULT_CHANNEL_ID, dataProvider = productionDataProvider) => {
    const analytics = useAnalytics(channelId, dataProvider);
    const topPosts = useTopPosts(channelId, {}, dataProvider);
    const engagementMetrics = useEngagementMetrics(channelId, {}, dataProvider);
    const recommendations = useRecommendations(channelId, dataProvider);

    const isLoading = analytics.isLoading || topPosts.isLoading || engagementMetrics.isLoading || recommendations.isLoading;
    const hasError = analytics.error || topPosts.error || engagementMetrics.error || recommendations.error;

    const refetchAll = useCallback(() => {
        analytics.refetch(true);
        topPosts.refetch(true);
        engagementMetrics.refetch(true);
        recommendations.refetch(true);
    }, [analytics, topPosts, engagementMetrics, recommendations]);

    const clearAllErrors = useCallback(() => {
        analytics.clearError();
        topPosts.clearError();
        engagementMetrics.clearError();
        recommendations.clearError();
    }, [analytics, topPosts, engagementMetrics, recommendations]);

    return {
        analytics: analytics.data,
        topPosts: topPosts.data,
        engagementMetrics: engagementMetrics.data,
        recommendations: recommendations.data,
        isLoading,
        hasError,
        errors: {
            analytics: analytics.error,
            topPosts: topPosts.error,
            engagementMetrics: engagementMetrics.error,
            recommendations: recommendations.error,
        },
        actions: {
            refetchAll,
            clearAllErrors,
        }
    };
};
