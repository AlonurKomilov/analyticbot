/**
 * React Hooks for Data Source Management
 * Clean hooks to replace scattered event listeners and provide centralized data source control
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { dataSourceManager } from '../utils/dataSourceManager.js';
import { mockService } from '../services/mockService.js';
import { configUtils } from '../config/mockConfig.js';

/**
 * Main hook for data source management
 * Replaces scattered event listeners with clean React patterns
 */
export const useDataSource = (options = {}) => {
    const {
        autoCheckApi = true,
        onSourceChange = null,
        enableApiStatusPolling = false,
        pollingInterval = 30000 // 30 seconds
    } = options;
    
    const [dataSource, setDataSource] = useState(dataSourceManager.getDataSource());
    const [apiStatus, setApiStatus] = useState(dataSourceManager.getApiStatus());
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const logger = configUtils.createLogger('useDataSource');
    const pollingRef = useRef(null);
    
    // Handle data source changes
    const handleDataSourceChange = useCallback((eventData) => {
        setDataSource(eventData.source);
        setError(null);
        
        if (onSourceChange) {
            onSourceChange(eventData);
        }
        
        logger.info('Data source changed:', eventData);
    }, [onSourceChange, logger]);
    
    // Handle API status changes
    const handleApiStatusChange = useCallback((eventData) => {
        if (eventData.type === 'api_status_changed') {
            setApiStatus(eventData.status);
            logger.info('API status changed:', eventData.status);
        }
    }, [logger]);
    
    // Switch data source
    const switchDataSource = useCallback(async (newSource, reason = 'user_choice') => {
        setIsLoading(true);
        setError(null);
        
        try {
            let success = false;
            
            if (newSource === 'api') {
                success = await dataSourceManager.switchToApi(reason);
            } else if (newSource === 'mock') {
                success = await dataSourceManager.switchToMock(reason);
            }
            
            if (!success) {
                throw new Error(`Failed to switch to ${newSource}`);
            }
            
            return true;
        } catch (err) {
            setError(err.message);
            logger.error('Failed to switch data source:', err);
            return false;
        } finally {
            setIsLoading(false);
        }
    }, [logger]);
    
    // Check API status
    const checkApiStatus = useCallback(async (force = false) => {
        setIsLoading(true);
        
        try {
            const status = await dataSourceManager.checkApiStatus(force);
            setApiStatus(status);
            return status;
        } catch (err) {
            setError(err.message);
            logger.error('API status check failed:', err);
            return 'offline';
        } finally {
            setIsLoading(false);
        }
    }, [logger]);
    
    // Setup event listeners and polling
    useEffect(() => {
        // Subscribe to data source manager events
        const unsubscribeSource = dataSourceManager.subscribe(handleDataSourceChange);
        const unsubscribeStatus = dataSourceManager.subscribe(handleApiStatusChange, {
            eventType: 'api_status_changed'
        });
        
        // Initial API check if enabled
        if (autoCheckApi) {
            checkApiStatus(true);
        }
        
        // Setup API status polling if enabled
        if (enableApiStatusPolling) {
            pollingRef.current = setInterval(() => {
                checkApiStatus(false);
            }, pollingInterval);
        }
        
        return () => {
            unsubscribeSource();
            unsubscribeStatus();
            
            if (pollingRef.current) {
                clearInterval(pollingRef.current);
                pollingRef.current = null;
            }
        };
    }, [autoCheckApi, enableApiStatusPolling, pollingInterval, checkApiStatus, handleDataSourceChange, handleApiStatusChange]);
    
    return {
        // State
        dataSource,
        apiStatus,
        isLoading,
        error,
        
        // Actions
        switchDataSource,
        checkApiStatus,
        switchToMock: (reason) => switchDataSource('mock', reason),
        switchToApi: (reason) => switchDataSource('api', reason),
        
        // Utilities
        isUsingRealAPI: dataSource === 'api',
        isApiOnline: apiStatus === 'online',
        canUseApi: apiStatus === 'online',
        
        // Clear error
        clearError: () => setError(null),
    };
};

/**
 * Hook for analytics data with automatic source switching
 */
export const useAnalytics = (channelId = 'demo_channel', options = {}) => {
    const { dataSource, isUsingRealAPI } = useDataSource();
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const logger = configUtils.createLogger('useAnalytics');
    
    const fetchAnalytics = useCallback(async (forceRefresh = false) => {
        if (!forceRefresh && data) return data;
        
        setIsLoading(true);
        setError(null);
        
        try {
            let analyticsData;
            
            if (isUsingRealAPI) {
                // Use real API (would be imported from apiClient or store)
                logger.info('Fetching analytics from real API');
                // This would call the real API method
                // analyticsData = await apiClient.getAnalytics(channelId);
                throw new Error('Real API not implemented in this hook yet');
            } else {
                // Use mock service
                logger.info('Fetching analytics from mock service');
                analyticsData = await mockService.getAnalyticsOverview(channelId);
            }
            
            setData(analyticsData);
            return analyticsData;
        } catch (err) {
            setError(err.message);
            logger.error('Analytics fetch failed:', err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [channelId, isUsingRealAPI, data, logger]);
    
    // Auto-fetch on mount and data source change
    useEffect(() => {
        fetchAnalytics();
    }, [dataSource]); // Re-fetch when data source changes
    
    return {
        data,
        isLoading,
        error,
        refetch: fetchAnalytics,
        clearError: () => setError(null),
    };
};

/**
 * Hook for post dynamics data
 */
export const usePostDynamics = (channelId = 'demo_channel', period = '24h') => {
    const { dataSource, isUsingRealAPI } = useDataSource();
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const logger = configUtils.createLogger('usePostDynamics');
    
    const fetchPostDynamics = useCallback(async (forceRefresh = false) => {
        if (!forceRefresh && data) return data;
        
        setIsLoading(true);
        setError(null);
        
        try {
            let dynamicsData;
            
            if (isUsingRealAPI) {
                logger.info('Fetching post dynamics from real API');
                // Real API call would go here
                throw new Error('Real API not implemented in this hook yet');
            } else {
                logger.info('Fetching post dynamics from mock service');
                dynamicsData = await mockService.getPostDynamics(channelId, period);
            }
            
            setData(dynamicsData);
            return dynamicsData;
        } catch (err) {
            setError(err.message);
            logger.error('Post dynamics fetch failed:', err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [channelId, period, isUsingRealAPI, data, logger]);
    
    useEffect(() => {
        fetchPostDynamics();
    }, [dataSource, period]);
    
    return {
        data,
        isLoading,
        error,
        refetch: fetchPostDynamics,
        clearError: () => setError(null),
    };
};

/**
 * Hook for top posts data
 */
export const useTopPosts = (channelId = 'demo_channel', period = 'today', sortBy = 'views') => {
    const { dataSource, isUsingRealAPI } = useDataSource();
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const logger = configUtils.createLogger('useTopPosts');
    
    const fetchTopPosts = useCallback(async (forceRefresh = false) => {
        if (!forceRefresh && data) return data;
        
        setIsLoading(true);
        setError(null);
        
        try {
            let postsData;
            
            if (isUsingRealAPI) {
                logger.info('Fetching top posts from real API');
                // Real API call would go here
                throw new Error('Real API not implemented in this hook yet');
            } else {
                logger.info('Fetching top posts from mock service');
                postsData = await mockService.getTopPosts(channelId, period, sortBy);
            }
            
            setData(postsData);
            return postsData;
        } catch (err) {
            setError(err.message);
            logger.error('Top posts fetch failed:', err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [channelId, period, sortBy, isUsingRealAPI, data, logger]);
    
    useEffect(() => {
        fetchTopPosts();
    }, [dataSource, period, sortBy]);
    
    return {
        data,
        isLoading,
        error,
        refetch: fetchTopPosts,
        clearError: () => setError(null),
    };
};

/**
 * Hook for best time recommendations
 */
export const useBestTime = (channelId = 'demo_channel', timeframe = 'week') => {
    const { dataSource, isUsingRealAPI } = useDataSource();
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    
    const logger = configUtils.createLogger('useBestTime');
    
    const fetchBestTime = useCallback(async (forceRefresh = false) => {
        if (!forceRefresh && data) return data;
        
        setIsLoading(true);
        setError(null);
        
        try {
            let bestTimeData;
            
            if (isUsingRealAPI) {
                logger.info('Fetching best time from real API');
                // Real API call would go here
                throw new Error('Real API not implemented in this hook yet');
            } else {
                logger.info('Fetching best time from mock service');
                bestTimeData = await mockService.getBestTime(channelId, timeframe);
            }
            
            setData(bestTimeData);
            return bestTimeData;
        } catch (err) {
            setError(err.message);
            logger.error('Best time fetch failed:', err);
            return null;
        } finally {
            setIsLoading(false);
        }
    }, [channelId, timeframe, isUsingRealAPI, data, logger]);
    
    useEffect(() => {
        fetchBestTime();
    }, [dataSource, timeframe]);
    
    return {
        data,
        isLoading,
        error,
        refetch: fetchBestTime,
        clearError: () => setError(null),
    };
};

/**
 * Composite hook for all analytics data
 */
export const useAllAnalytics = (channelId = 'demo_channel') => {
    const overview = useAnalytics(channelId);
    const postDynamics = usePostDynamics(channelId);
    const topPosts = useTopPosts(channelId);
    const bestTime = useBestTime(channelId);
    
    const isLoading = overview.isLoading || postDynamics.isLoading || topPosts.isLoading || bestTime.isLoading;
    const hasError = overview.error || postDynamics.error || topPosts.error || bestTime.error;
    
    const refetchAll = useCallback(() => {
        overview.refetch(true);
        postDynamics.refetch(true);
        topPosts.refetch(true);
        bestTime.refetch(true);
    }, [overview, postDynamics, topPosts, bestTime]);
    
    const clearAllErrors = useCallback(() => {
        overview.clearError();
        postDynamics.clearError();
        topPosts.clearError();
        bestTime.clearError();
    }, [overview, postDynamics, topPosts, bestTime]);
    
    return {
        overview: overview.data,
        postDynamics: postDynamics.data,
        topPosts: topPosts.data,
        bestTime: bestTime.data,
        isLoading,
        hasError,
        errors: {
            overview: overview.error,
            postDynamics: postDynamics.error,
            topPosts: topPosts.error,
            bestTime: bestTime.error,
        },
        actions: {
            refetchAll,
            clearAllErrors,
        }
    };
};