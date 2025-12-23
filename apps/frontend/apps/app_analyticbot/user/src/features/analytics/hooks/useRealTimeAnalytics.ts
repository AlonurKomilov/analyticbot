import { useState, useEffect, useRef, useCallback } from 'react';
import { apiClient } from '@/api/client';

/**
 * Real-time analytics options
 */
export interface RealTimeAnalyticsOptions {
    interval?: number;
    enableRealTime?: boolean;
    maxRetries?: number;
    fallbackToCache?: boolean;
}

/**
 * Real-time data error
 */
export interface RealTimeError {
    message: string;
    retryCount: number;
    timestamp: Date;
    canRetry: boolean;
}

/**
 * Connection status type
 */
export type ConnectionStatus = 'connecting' | 'fetching' | 'connected' | 'error' | 'paused' | 'cached';

/**
 * Real-time analytics return type
 */
export interface UseRealTimeAnalyticsReturn {
    data: any | null;
    loading: boolean;
    error: RealTimeError | null;
    lastUpdated: Date | null;
    connectionStatus: ConnectionStatus;
    refresh: () => void;
    pauseRealTime: () => void;
    resumeRealTime: () => void;
    isConnected: boolean;
    isOffline: boolean;
    hasError: boolean;
    canRetry: boolean;
}

/**
 * Custom hook for real-time analytics data
 * Provides live data updates with configurable intervals and error handling
 */
export const useRealTimeAnalytics = (
    channelId: string,
    options: RealTimeAnalyticsOptions = {}
): UseRealTimeAnalyticsReturn => {
    const {
        interval = 30000,        // 30 seconds default
        enableRealTime = true,   // Enable real-time updates
        maxRetries = 3,         // Max retry attempts
        fallbackToCache = true, // Use cached data on error
    } = options;

    const [data, setData] = useState<any | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<RealTimeError | null>(null);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting');

    const intervalRef = useRef<NodeJS.Timeout | null>(null);
    const retryCountRef = useRef<number>(0);
    const mountedRef = useRef<boolean>(true);

    // Cache implementation (placeholder - could be moved to a cache store)
    const cacheRef = useRef<Record<string, any>>({});
    const getCachedData = useCallback((key: string): any => cacheRef.current[key], []);
    const setCachedData = useCallback((key: string, value: any): void => {
        cacheRef.current[key] = value;
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            mountedRef.current = false;
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, []);

    // Fetch real-time analytics data
    const fetchRealTimeData = useCallback(async (isRetry: boolean = false) => {
        if (!mountedRef.current) return;

        try {
            if (!isRetry) {
                setLoading(true);
                setError(null);
            }

            setConnectionStatus('fetching');

            // Make API call for real-time data
            const response = await apiClient.post('/analytics/channel-data', {
                channel_id: channelId,
                include_real_time: true,
                format: 'detailed'
            });

            if (!mountedRef.current) return;

            // Process and set the data
            const processedData = {
                ...(typeof response === 'object' && response !== null ? response : {}),
                timestamp: new Date().toISOString(),
                realTime: true,
                connectionStatus: 'connected'
            };

            setData(processedData);
            setLastUpdated(new Date());
            setConnectionStatus('connected');
            setLoading(false);
            setError(null);
            retryCountRef.current = 0;

            // Cache the data for offline usage
            if (fallbackToCache) {
                setCachedData(`realtime_${channelId}`, processedData);
            }

        } catch (err) {
            console.error('Real-time analytics fetch failed:', err);

            if (!mountedRef.current) return;

            retryCountRef.current += 1;
            setConnectionStatus('error');

            // Try fallback to cached data
            if (fallbackToCache && retryCountRef.current <= maxRetries) {
                const cachedData = getCachedData(`realtime_${channelId}`);
                if (cachedData) {
                    setData({
                        ...cachedData,
                        realTime: false,
                        connectionStatus: 'cached',
                        cacheWarning: 'Using cached data due to connection issues'
                    });
                    setConnectionStatus('cached');
                }
            }

            // Set error state
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch real-time data';
            setError({
                message: errorMessage,
                retryCount: retryCountRef.current,
                timestamp: new Date(),
                canRetry: retryCountRef.current < maxRetries
            });

            setLoading(false);

            // Auto-retry logic
            if (retryCountRef.current < maxRetries) {
                setTimeout(() => {
                    if (mountedRef.current) {
                        fetchRealTimeData(true);
                    }
                }, Math.min(1000 * Math.pow(2, retryCountRef.current), 10000)); // Exponential backoff
            }
        }
    }, [channelId, fallbackToCache, maxRetries, getCachedData, setCachedData]);

    // Manual refresh function
    const refresh = useCallback(() => {
        retryCountRef.current = 0;
        fetchRealTimeData();
    }, [fetchRealTimeData]);

    // Pause/resume real-time updates
    const pauseRealTime = useCallback(() => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
        setConnectionStatus('paused');
    }, []);

    const resumeRealTime = useCallback(() => {
        if (!intervalRef.current && enableRealTime) {
            fetchRealTimeData();
            intervalRef.current = setInterval(fetchRealTimeData, interval);
            setConnectionStatus('connecting');
        }
    }, [enableRealTime, interval, fetchRealTimeData]);

    // Initialize and set up interval
    useEffect(() => {
        if (!channelId || !enableRealTime) return;

        // Initial fetch
        fetchRealTimeData();

        // Set up interval for real-time updates
        intervalRef.current = setInterval(fetchRealTimeData, interval);

        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        };
    }, [channelId, enableRealTime, interval, fetchRealTimeData]);

    // Return hook interface
    return {
        // Data
        data,
        loading,
        error,
        lastUpdated,
        connectionStatus,

        // Controls
        refresh,
        pauseRealTime,
        resumeRealTime,

        // Status helpers
        isConnected: connectionStatus === 'connected',
        isOffline: connectionStatus === 'cached',
        hasError: !!error,
        canRetry: error?.canRetry || false,
    };
};

/**
 * Quick analytics return type
 */
export interface UseQuickAnalyticsReturn {
    data: any | null;
    loading: boolean;
    error: string | null;
    refresh: () => void;
}

/**
 * Custom hook for mobile-optimized quick analytics
 * Provides fast, lightweight data for mobile widgets
 */
export const useQuickAnalytics = (
    channelId: string,
    widgetType: string = 'dashboard'
): UseQuickAnalyticsReturn => {
    const [data, setData] = useState<any | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchQuickData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await apiClient.post('/mobile/analytics/quick', {
                channel_id: channelId,
                widget_type: widgetType,
                include_real_time: true
            });

            setData(response as any);
            setLoading(false);
        } catch (err) {
            console.error('Quick analytics fetch failed:', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch quick analytics';
            setError(errorMessage);
            setLoading(false);
        }
    }, [channelId, widgetType]);

    useEffect(() => {
        if (channelId) {
            fetchQuickData();
        }
    }, [channelId, fetchQuickData]);

    return {
        data,
        loading,
        error,
        refresh: fetchQuickData
    };
};

/**
 * Performance metrics return type
 */
export interface UsePerformanceMetricsReturn {
    metrics: any | null;
    trends: any[];
    score: number;
    loading: boolean;
    error: string | null;
    refresh: () => void;
    isGoodPerformance: boolean;
    isExcellentPerformance: boolean;
    needsAttention: boolean;
}

/**
 * Custom hook for performance metrics with real-time updates
 * Focuses on key performance indicators
 */
export const usePerformanceMetrics = (
    channelId: string,
    period: number = 30
): UsePerformanceMetricsReturn => {
    const [metrics, setMetrics] = useState<any | null>(null);
    const [trends, setTrends] = useState<any[]>([]);
    const [score, setScore] = useState<number>(0);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const fetchPerformanceData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const [metricsData, trendsData] = await Promise.all([
                apiClient.post('/analytics/metrics/performance', {
                    channels: [channelId],
                    period: `${period}d`
                }),
                apiClient.get('/analytics/trends/top-posts')
            ]);

            const metrics = metricsData as any;
            const trends = trendsData as any;

            setMetrics(metrics);
            setTrends(trends.trends || []);
            setScore(metrics.performance_score || 0);
            setLoading(false);
        } catch (err) {
            console.error('Performance metrics fetch failed:', err);
            const errorMessage = err instanceof Error ? err.message : 'Failed to fetch performance metrics';
            setError(errorMessage);
            setLoading(false);
        }
    }, [channelId, period]);

    useEffect(() => {
        if (channelId) {
            fetchPerformanceData();

            // Update every 60 seconds for performance metrics
            const interval = setInterval(fetchPerformanceData, 60000);
            return () => clearInterval(interval);
        }

        return undefined;
    }, [channelId, fetchPerformanceData]);

    return {
        metrics,
        trends,
        score,
        loading,
        error,
        refresh: fetchPerformanceData,

        // Performance helpers
        isGoodPerformance: score >= 70,
        isExcellentPerformance: score >= 85,
        needsAttention: score < 50
    };
};

export default useRealTimeAnalytics;
