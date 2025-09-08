import { useState, useEffect, useRef, useCallback } from 'react';
import { useAppStore } from '../store/appStore';
import apiClient from '../utils/apiClient';

/**
 * Custom hook for real-time analytics data
 * Provides live data updates with configurable intervals and error handling
 */
export const useRealTimeAnalytics = (channelId, options = {}) => {
    const {
        interval = 30000,        // 30 seconds default
        enableRealTime = true,   // Enable real-time updates
        maxRetries = 3,         // Max retry attempts
        fallbackToCache = true, // Use cached data on error
    } = options;

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);
    const [connectionStatus, setConnectionStatus] = useState('connecting');
    
    const intervalRef = useRef(null);
    const retryCountRef = useRef(0);
    const mountedRef = useRef(true);
    
    // Get store methods for fallback data
    const { getCachedData, setCachedData } = useAppStore();

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
    const fetchRealTimeData = useCallback(async (isRetry = false) => {
        if (!mountedRef.current) return;
        
        try {
            if (!isRetry) {
                setLoading(true);
                setError(null);
            }
            
            setConnectionStatus('fetching');

            // Make API call for real-time data
            const response = await apiClient.post('/api/v2/analytics/channel-data', {
                channel_id: channelId,
                include_real_time: true,
                format: 'detailed'
            });

            if (!mountedRef.current) return;

            // Process and set the data
            const processedData = {
                ...response,
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
            setError({
                message: err.message || 'Failed to fetch real-time data',
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
 * Custom hook for mobile-optimized quick analytics
 * Provides fast, lightweight data for mobile widgets
 */
export const useQuickAnalytics = (channelId, widgetType = 'dashboard') => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    const fetchQuickData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await apiClient.post('/api/mobile/v1/analytics/quick', {
                channel_id: channelId,
                widget_type: widgetType,
                include_real_time: true
            });

            setData(response);
            setLoading(false);
        } catch (err) {
            console.error('Quick analytics fetch failed:', err);
            setError(err.message);
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
 * Custom hook for performance metrics with real-time updates
 * Focuses on key performance indicators
 */
export const usePerformanceMetrics = (channelId, period = 30) => {
    const [metrics, setMetrics] = useState(null);
    const [trends, setTrends] = useState([]);
    const [score, setScore] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchPerformanceData = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const [metricsData, trendsData] = await Promise.all([
                apiClient.post('/api/v2/analytics/metrics/performance', {
                    channels: [channelId],
                    period: `${period}d`
                }),
                apiClient.get('/api/v2/analytics/trends/top-posts')
            ]);

            setMetrics(metricsData);
            setTrends(trendsData.trends || []);
            setScore(metricsData.performance_score || 0);
            setLoading(false);
        } catch (err) {
            console.error('Performance metrics fetch failed:', err);
            setError(err.message);
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
