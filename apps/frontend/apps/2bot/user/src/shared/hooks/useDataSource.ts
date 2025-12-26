/**
 * Clean Data Source Hook - Production Code
 * Uses dependency injection to avoid mixed mock/production logic
 * Now supports optional AuthContext integration for JWT authentication
 *
 * @module useDataSource
 * @example
 * ```tsx
 * const { isAvailable, getAnalytics } = useDataSource();
 * const analytics = await getAnalytics('my_channel');
 * ```
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { productionDataProvider } from '@/providers/DataProvider';
import { DEFAULT_CHANNEL_ID } from '@config/constants';
import type {
    AnalyticsOverview,
    TopPost,
    EngagementMetrics
} from '@/types';

/**
 * Data Provider interface
 */
export interface DataProvider {
    getProviderName: () => string;
    isAvailable: () => Promise<boolean>;
    getAnalytics: (channelId: string) => Promise<AnalyticsOverview>;
    getTopPosts: (channelId: string, options?: Record<string, any>) => Promise<TopPost[]>;
    getEngagementMetrics: (channelId: string, options?: Record<string, any>) => Promise<EngagementMetrics>;
    getRecommendations: (channelId: string) => Promise<any>;
}

/**
 * useDataSource hook options
 */
export interface UseDataSourceOptions {
    /** Callback when provider changes */
    onProviderChange?: ((info: { provider: string; timestamp: string }) => void) | null;
    /** Enable automatic status polling */
    enableStatusPolling?: boolean;
    /** Polling interval in milliseconds */
    pollingInterval?: number;
    /** Auto-check availability on mount */
    autoCheckAvailability?: boolean;
}

/**
 * useDataSource hook return type
 */
export interface UseDataSourceReturn {
    /** Provider availability status */
    isAvailable: boolean | null;
    /** Loading state */
    isLoading: boolean;
    /** Error message if any */
    error: string | null;
    /** Timestamp of last availability check */
    lastCheck: number | null;
    /** Provider name */
    providerName: string;
    /** Fetch analytics data */
    getAnalytics: (channelId: string) => Promise<AnalyticsOverview>;
    /** Fetch top posts */
    getTopPosts: (channelId: string, options?: Record<string, any>) => Promise<TopPost[]>;
    /** Fetch engagement metrics */
    getEngagementMetrics: (channelId: string, options?: Record<string, any>) => Promise<EngagementMetrics>;
    /** Fetch recommendations */
    getRecommendations: (channelId: string) => Promise<any>;
    /** Check provider availability */
    checkAvailability: (force?: boolean) => Promise<boolean>;
    /** Whether provider is online */
    isOnline: boolean;
    /** Whether provider is offline */
    isOffline: boolean;
    /** Clear error state */
    clearError: () => void;
}

/**
 * Clean hook for data management using dependency injection
 * NO mock switching logic - uses provider pattern instead
 */
export const useDataSource = (
    dataProvider: DataProvider = productionDataProvider,
    options: UseDataSourceOptions = {}
): UseDataSourceReturn => {
    const {
        onProviderChange = null,
        enableStatusPolling = false,
        pollingInterval = 30000, // 30 seconds
        autoCheckAvailability = true
    } = options;

    const [isAvailable, setIsAvailable] = useState<boolean | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [lastCheck, setLastCheck] = useState<number | null>(null);

    const pollingRef = useRef<NodeJS.Timeout | null>(null);
    const providerRef = useRef<DataProvider>(dataProvider);

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
    const checkAvailability = useCallback(async (force: boolean = false): Promise<boolean> => {
        // Don't check too frequently unless forced
        if (!force && lastCheck && (Date.now() - lastCheck) < 10000) {
            return isAvailable || false;
        }

        setIsLoading(true);
        setError(null);

        try {
            const available = await providerRef.current.isAvailable();
            setIsAvailable(available);
            setLastCheck(Date.now());
            return available;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(`Availability check failed: ${errorMessage}`);
            setIsAvailable(false);
            console.error('Provider availability check failed:', err);
            return false;
        } finally {
            setIsLoading(false);
        }
    }, [isAvailable, lastCheck]);

    // Get analytics data
    const getAnalytics = useCallback(async (channelId: string): Promise<AnalyticsOverview> => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await providerRef.current.getAnalytics(channelId);
            return data;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(`Failed to get analytics: ${errorMessage}`);
            console.error('Analytics fetch failed:', err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Get top posts
    const getTopPosts = useCallback(async (channelId: string, options: Record<string, any> = {}): Promise<TopPost[]> => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await providerRef.current.getTopPosts(channelId, options);
            return data;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(`Failed to get top posts: ${errorMessage}`);
            console.error('Top posts fetch failed:', err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Get engagement metrics
    const getEngagementMetrics = useCallback(async (channelId: string, options: Record<string, any> = {}): Promise<EngagementMetrics> => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await providerRef.current.getEngagementMetrics(channelId, options);
            return data;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(`Failed to get engagement metrics: ${errorMessage}`);
            console.error('Engagement metrics fetch failed:', err);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Get recommendations
    const getRecommendations = useCallback(async (channelId: string): Promise<any> => {
        setIsLoading(true);
        setError(null);

        try {
            const data = await providerRef.current.getRecommendations(channelId);
            return data;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(`Failed to get recommendations: ${errorMessage}`);
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
export interface UseAnalyticsReturn {
    data: AnalyticsOverview | null;
    isLoading: boolean;
    error: string | null;
    refetch: (forceRefresh?: boolean) => Promise<AnalyticsOverview | null>;
    clearError: () => void;
}

export const useAnalytics = (
    channelId: string = DEFAULT_CHANNEL_ID,
    dataProvider: DataProvider = productionDataProvider
): UseAnalyticsReturn => {
    const [data, setData] = useState<AnalyticsOverview | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const fetchAnalytics = useCallback(async (forceRefresh: boolean = false): Promise<AnalyticsOverview | null> => {
        if (!forceRefresh && data) return data;

        setIsLoading(true);
        setError(null);

        try {
            const analyticsData = await dataProvider.getAnalytics(channelId);
            setData(analyticsData);
            return analyticsData;
        } catch (err) {
            // Analytics errors are expected when channel has no data yet
            // Don't set error state - just return null and let UI show empty state
            console.debug('Analytics not available:', err);
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
export interface UseTopPostsReturn {
    data: TopPost[] | null;
    isLoading: boolean;
    error: string | null;
    refetch: (forceRefresh?: boolean) => Promise<TopPost[] | null>;
    clearError: () => void;
}

export const useTopPosts = (
    channelId: string = DEFAULT_CHANNEL_ID,
    options: Record<string, any> = {},
    dataProvider: DataProvider = productionDataProvider
): UseTopPostsReturn => {
    const [data, setData] = useState<TopPost[] | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const fetchTopPosts = useCallback(async (forceRefresh: boolean = false): Promise<TopPost[] | null> => {
        if (!forceRefresh && data) return data;

        setIsLoading(true);
        setError(null);

        try {
            const postsData = await dataProvider.getTopPosts(channelId, options);
            setData(postsData);
            return postsData;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
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
export interface UseEngagementMetricsReturn {
    data: EngagementMetrics | null;
    isLoading: boolean;
    error: string | null;
    refetch: (forceRefresh?: boolean) => Promise<EngagementMetrics | null>;
    clearError: () => void;
}

export const useEngagementMetrics = (
    channelId: string = DEFAULT_CHANNEL_ID,
    options: Record<string, any> = {},
    dataProvider: DataProvider = productionDataProvider
): UseEngagementMetricsReturn => {
    const [data, setData] = useState<EngagementMetrics | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const fetchEngagementMetrics = useCallback(async (forceRefresh: boolean = false): Promise<EngagementMetrics | null> => {
        if (!forceRefresh && data) return data;

        setIsLoading(true);
        setError(null);

        try {
            const metricsData = await dataProvider.getEngagementMetrics(channelId, options);
            setData(metricsData);
            return metricsData;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
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
export interface UseRecommendationsReturn {
    data: any | null;
    isLoading: boolean;
    error: string | null;
    refetch: (forceRefresh?: boolean) => Promise<any | null>;
    clearError: () => void;
}

export const useRecommendations = (
    channelId: string = DEFAULT_CHANNEL_ID,
    dataProvider: DataProvider = productionDataProvider
): UseRecommendationsReturn => {
    const [data, setData] = useState<any | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    const fetchRecommendations = useCallback(async (forceRefresh: boolean = false): Promise<any | null> => {
        if (!forceRefresh && data) return data;

        setIsLoading(true);
        setError(null);

        try {
            const recommendationsData = await dataProvider.getRecommendations(channelId);
            setData(recommendationsData);
            return recommendationsData;
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Unknown error';
            setError(errorMessage);
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
export interface UseAllAnalyticsReturn {
    analytics: AnalyticsOverview | null;
    topPosts: TopPost[] | null;
    engagementMetrics: EngagementMetrics | null;
    recommendations: any | null;
    isLoading: boolean;
    hasError: string | null | false;
    errors: {
        analytics: string | null;
        topPosts: string | null;
        engagementMetrics: string | null;
        recommendations: string | null;
    };
    actions: {
        refetchAll: () => void;
        clearAllErrors: () => void;
    };
}

export const useAllAnalytics = (
    channelId: string = DEFAULT_CHANNEL_ID,
    dataProvider: DataProvider = productionDataProvider
): UseAllAnalyticsReturn => {
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
