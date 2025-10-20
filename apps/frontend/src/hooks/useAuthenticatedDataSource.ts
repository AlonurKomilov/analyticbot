/**
 * 🔐 Authenticated Data Source Hooks
 *
 * Enhanced data source hooks that integrate with AuthContext for JWT authentication.
 * These hooks automatically handle token-based API requests and authentication errors.
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { createAuthenticatedDataProvider } from '../providers/DataProvider.js';
import { DEFAULT_CHANNEL_ID } from '../config/constants.js';
import type {
    AnalyticsOverview,
    Post,
    EngagementMetrics
} from '@/types';
import type { DataProvider } from './useDataSource';

/**
 * User type from AuthContext
 */
interface User {
    id: string;
    username: string;
    email?: string;
    role?: string;
}

/**
 * Hook to create an authenticated data provider instance
 * @param baseUrl - Optional API base URL override
 * @returns Authenticated data provider with token management
 */
export const useAuthenticatedDataProvider = (baseUrl: string | null = null): DataProvider => {
    const authContext = useAuth();

    const dataProvider = useMemo(() => {
        const provider = createAuthenticatedDataProvider(authContext, baseUrl ?? undefined);
        return provider;
    }, [authContext, baseUrl]);

    return dataProvider;
};

/**
 * Enhanced analytics hook return type with authentication
 */
export interface UseAuthenticatedAnalyticsReturn {
    data: AnalyticsOverview | null;
    loading: boolean;
    error: string | null;
    lastFetch: string | null;
    refetch: () => Promise<void>;
    user: User | null;
    isAuthenticated: boolean;
}

/**
 * Enhanced analytics hook with authentication
 * @param channelId - Channel identifier
 * @param options - Additional options
 * @returns Analytics data with auth-aware loading states
 */
export const useAuthenticatedAnalytics = (
    channelId: string = DEFAULT_CHANNEL_ID,
    _options: Record<string, any> = {}
): UseAuthenticatedAnalyticsReturn => {
    const { user, isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();
    const [data, setData] = useState<AnalyticsOverview | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [lastFetch, setLastFetch] = useState<string | null>(null);

    const fetchAnalytics = useCallback(async (): Promise<void> => {
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
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch analytics data';
            setError(errorMessage);
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
 * Enhanced top posts hook return type with authentication
 */
export interface UseAuthenticatedTopPostsReturn {
    data: Post[] | null;
    loading: boolean;
    error: string | null;
    lastFetch: string | null;
    refetch: () => Promise<void>;
    user: User | null;
    isAuthenticated: boolean;
}

/**
 * Enhanced top posts hook with authentication
 * @param channelId - Channel identifier
 * @param queryOptions - Query parameters for filtering
 * @param options - Hook options
 * @returns Top posts data with auth-aware loading states
 */
export const useAuthenticatedTopPosts = (
    channelId: string = DEFAULT_CHANNEL_ID,
    queryOptions: Record<string, any> = {},
    _options: Record<string, any> = {}
): UseAuthenticatedTopPostsReturn => {
    const { user, isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();
    const [data, setData] = useState<Post[] | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [lastFetch, setLastFetch] = useState<string | null>(null);

    const fetchTopPosts = useCallback(async (): Promise<void> => {
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
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch top posts data';
            setError(errorMessage);
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
 * Enhanced engagement metrics hook return type with authentication
 */
export interface UseAuthenticatedEngagementMetricsReturn {
    data: EngagementMetrics | null;
    loading: boolean;
    error: string | null;
    lastFetch: string | null;
    refetch: () => Promise<void>;
    user: User | null;
    isAuthenticated: boolean;
}

/**
 * Enhanced engagement metrics hook with authentication
 * @param channelId - Channel identifier
 * @param queryOptions - Query parameters for filtering
 * @param options - Hook options
 * @returns Engagement metrics with auth-aware loading states
 */
export const useAuthenticatedEngagementMetrics = (
    channelId: string = DEFAULT_CHANNEL_ID,
    queryOptions: Record<string, any> = {},
    _options: Record<string, any> = {}
): UseAuthenticatedEngagementMetricsReturn => {
    const { user, isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();
    const [data, setData] = useState<EngagementMetrics | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [lastFetch, setLastFetch] = useState<string | null>(null);

    const fetchEngagementMetrics = useCallback(async (): Promise<void> => {
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
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch engagement metrics';
            setError(errorMessage);
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
 * Enhanced recommendations hook return type with authentication
 */
export interface UseAuthenticatedRecommendationsReturn {
    data: any | null;
    loading: boolean;
    error: string | null;
    lastFetch: string | null;
    refetch: () => Promise<void>;
    user: User | null;
    isAuthenticated: boolean;
}

/**
 * Enhanced recommendations hook with authentication
 * @param channelId - Channel identifier
 * @param options - Hook options
 * @returns Recommendations data with auth-aware loading states
 */
export const useAuthenticatedRecommendations = (
    channelId: string = DEFAULT_CHANNEL_ID,
    _options: Record<string, any> = {}
): UseAuthenticatedRecommendationsReturn => {
    const { user, isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();
    const [data, setData] = useState<any | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [lastFetch, setLastFetch] = useState<string | null>(null);

    const fetchRecommendations = useCallback(async (): Promise<void> => {
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
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch recommendations';
            setError(errorMessage);
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
 * Enhanced data source availability checker return type with authentication
 */
export interface UseAuthenticatedDataSourceStatusReturn {
    isAvailable: boolean | null;
    loading: boolean;
    error: string | null;
    lastCheck: string | null;
    refetch: () => Promise<void>;
    isAuthenticated: boolean;
}

/**
 * Enhanced data source availability checker with authentication
 * @param options - Hook options
 * @returns Availability status with auth context
 */
export const useAuthenticatedDataSourceStatus = (
    options: { enablePolling?: boolean; pollingInterval?: number } = {}
): UseAuthenticatedDataSourceStatusReturn => {
    const { enablePolling = false, pollingInterval = 30000 } = options;
    const { isAuthenticated } = useAuth();
    const dataProvider = useAuthenticatedDataProvider();
    const [isAvailable, setIsAvailable] = useState<boolean | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [lastCheck, setLastCheck] = useState<string | null>(null);

    const checkAvailability = useCallback(async (): Promise<void> => {
        setLoading(true);
        setError(null);

        try {
            const available = await dataProvider.isAvailable();
            setIsAvailable(available);
            setLastCheck(new Date().toISOString());
        } catch (err) {
            console.error('Failed to check data source availability:', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to check availability';
            setError(errorMessage);
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
        return undefined;
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
 * Combined hook return type that provides all authenticated data operations
 */
export interface UseAuthenticatedDataSourceReturn {
    analytics: UseAuthenticatedAnalyticsReturn;
    topPosts: UseAuthenticatedTopPostsReturn;
    engagement: UseAuthenticatedEngagementMetricsReturn;
    recommendations: UseAuthenticatedRecommendationsReturn;
    status: UseAuthenticatedDataSourceStatusReturn;
    refetchAll: () => Promise<void>;
    isLoading: boolean;
    hasError: boolean;
    isAuthenticated: boolean;
    user: User | null;
}

/**
 * Combined hook that provides all authenticated data operations
 * @param channelId - Channel identifier
 * @param options - Combined options for all data operations
 * @returns All data operations with shared auth state
 */
export const useAuthenticatedDataSource = (
    channelId: string = DEFAULT_CHANNEL_ID,
    options: {
        topPostsOptions?: Record<string, any>;
        engagementOptions?: Record<string, any>;
        enablePolling?: boolean;
        pollingInterval?: number;
    } = {}
): UseAuthenticatedDataSourceReturn => {
    const analytics = useAuthenticatedAnalytics(channelId, options);
    const topPosts = useAuthenticatedTopPosts(channelId, options.topPostsOptions || {}, options);
    const engagement = useAuthenticatedEngagementMetrics(channelId, options.engagementOptions || {}, options);
    const recommendations = useAuthenticatedRecommendations(channelId, options);
    const status = useAuthenticatedDataSourceStatus(options);

    const refetchAll = useCallback(async (): Promise<void> => {
        await Promise.all([
            analytics.refetch(),
            topPosts.refetch(),
            engagement.refetch(),
            recommendations.refetch(),
            status.refetch()
        ]);
    }, [analytics, topPosts, engagement, recommendations, status]);

    const isLoading = analytics.loading || topPosts.loading || engagement.loading || recommendations.loading || status.loading;
    const hasError = !!(analytics.error || topPosts.error || engagement.error || recommendations.error || status.error);

    return {
        analytics,
        topPosts,
        engagement,
        recommendations,
        status,
        refetchAll,
        isLoading,
        hasError,
        isAuthenticated: analytics.isAuthenticated,
        user: analytics.user
    };
};
