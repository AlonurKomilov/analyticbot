/**
 * Unified Analytics Hook System
 * Consolidates all analytics data patterns into a single, powerful interface
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAppStore } from '../store/appStore';
import { apiClient } from '../api/client.js';

// Hook configuration presets for different use cases
export const ANALYTICS_PRESETS = {
    DASHBOARD: {
        realTime: true,
        interval: 30000,
        includeMetrics: ['overview', 'growth', 'engagement'],
        caching: true,
        retries: 3
    },
    ADMIN: {
        realTime: false,
        interval: 0,
        includeMetrics: ['users', 'system', 'performance'],
        caching: true,
        retries: 2
    },
    MOBILE: {
        realTime: true,
        interval: 60000,
        includeMetrics: ['overview', 'quick'],
        caching: true,
        retries: 1
    },
    PERFORMANCE: {
        realTime: true,
        interval: 60000,
        includeMetrics: ['performance', 'trends', 'alerts'],
        caching: false,
        retries: 2
    }
};

/**
 * Unified Analytics Hook
 * Single hook to handle all analytics needs across the application
 */
export const useUnifiedAnalytics = (channelId, preset = 'DASHBOARD', customConfig = {}) => {
    // Merge preset with custom configuration
    const config = { ...ANALYTICS_PRESETS[preset], ...customConfig };
    
    // State management
    const [data, setData] = useState({
        overview: null,
        growth: null,
        engagement: null,
        performance: null,
        trends: null,
        alerts: null,
        users: null,
        system: null,
        quick: null
    });
    
    const [loading, setLoading] = useState(true);
    const [errors, setErrors] = useState({});
    const [lastUpdated, setLastUpdated] = useState(null);
    const [connectionStatus, setConnectionStatus] = useState('connecting');
    
    // Refs for cleanup and retry logic
    const intervalRef = useRef(null);
    const retryCountRef = useRef(0);
    const mountedRef = useRef(true);
    
    // Store integration
    const { getCachedData, setCachedData, dataSource } = useAppStore();
    
    // Cleanup on unmount
    useEffect(() => {
        return () => {
            mountedRef.current = false;
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, []);
    
    /**
     * Core data fetching function with error handling and retry logic
     */
    const fetchAnalyticsData = useCallback(async (metrics = config.includeMetrics, isRetry = false) => {
        if (!mountedRef.current || !channelId) return;
        
        try {
            if (!isRetry) {
                setLoading(true);
                setConnectionStatus('fetching');
            }
            
            // Prepare API calls based on requested metrics
            const apiCalls = [];
            const metricKeys = [];
            
            if (metrics.includes('overview')) {
                apiCalls.push(apiClient.get(`/api/v2/analytics/channels/${channelId}/overview?period=30`));
                metricKeys.push('overview');
            }
            
            if (metrics.includes('growth')) {
                apiCalls.push(apiClient.get(`/api/v2/analytics/channels/${channelId}/growth?period=30`));
                metricKeys.push('growth');
            }
            
            if (metrics.includes('engagement')) {
                apiCalls.push(apiClient.get(`/api/v2/analytics/channels/${channelId}/engagement?period=30`));
                metricKeys.push('engagement');
            }
            
            if (metrics.includes('performance')) {
                apiCalls.push(apiClient.get(`/api/v2/analytics/channels/${channelId}/performance?period=30`));
                metricKeys.push('performance');
            }
            
            if (metrics.includes('trends')) {
                apiCalls.push(apiClient.get(`/api/v2/analytics/channels/${channelId}/trends?period=7`));
                metricKeys.push('trends');
            }
            
            if (metrics.includes('alerts')) {
                apiCalls.push(apiClient.get(`/api/v2/analytics/channels/${channelId}/alerts`));
                metricKeys.push('alerts');
            }
            
            if (metrics.includes('users')) {
                apiCalls.push(apiClient.get(`/api/v1/superadmin/users`));
                metricKeys.push('users');
            }
            
            if (metrics.includes('system')) {
                apiCalls.push(apiClient.get(`/api/v1/superadmin/system-status`));
                metricKeys.push('system');
            }
            
            if (metrics.includes('quick')) {
                apiCalls.push(apiClient.post('/api/mobile/v1/analytics/quick', {
                    channel_id: channelId,
                    include_real_time: config.realTime
                }));
                metricKeys.push('quick');
            }
            
            // Execute all API calls in parallel
            const results = await Promise.allSettled(apiCalls);
            
            if (!mountedRef.current) return;
            
            // Process results and update state
            const newData = { ...data };
            const newErrors = {};
            
            results.forEach((result, index) => {
                const metricKey = metricKeys[index];
                
                if (result.status === 'fulfilled') {
                    newData[metricKey] = result.value;
                    
                    // Cache successful results if caching is enabled
                    if (config.caching) {
                        setCachedData(`analytics_${metricKey}_${channelId}`, result.value);
                    }
                } else {
                    newErrors[metricKey] = result.reason?.message || 'Unknown error';
                    
                    // Try to use cached data on error
                    if (config.caching) {
                        const cachedData = getCachedData(`analytics_${metricKey}_${channelId}`);
                        if (cachedData) {
                            newData[metricKey] = {
                                ...cachedData,
                                cached: true,
                                cacheWarning: 'Using cached data due to API error'
                            };
                        }
                    }
                }
            });
            
            setData(newData);
            setErrors(newErrors);
            setLastUpdated(new Date());
            setConnectionStatus(Object.keys(newErrors).length === 0 ? 'connected' : 'partial');
            setLoading(false);
            retryCountRef.current = 0;
            
        } catch (error) {
            console.error('Unified analytics fetch failed:', error);
            
            if (!mountedRef.current) return;
            
            retryCountRef.current += 1;
            setConnectionStatus('error');
            
            // Auto-retry logic with exponential backoff
            if (retryCountRef.current <= config.retries) {
                setTimeout(() => {
                    if (mountedRef.current) {
                        fetchAnalyticsData(metrics, true);
                    }
                }, Math.min(1000 * Math.pow(2, retryCountRef.current), 10000));
            } else {
                setLoading(false);
                setErrors(prev => ({
                    ...prev,
                    system: error.message || 'Failed to fetch analytics data'
                }));
            }
        }
    }, [channelId, config, data, getCachedData, setCachedData]);
    
    /**
     * Manual refresh function
     */
    const refresh = useCallback((specificMetrics = null) => {
        retryCountRef.current = 0;
        fetchAnalyticsData(specificMetrics || config.includeMetrics);
    }, [fetchAnalyticsData, config.includeMetrics]);
    
    /**
     * Pause real-time updates
     */
    const pause = useCallback(() => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
        setConnectionStatus('paused');
    }, []);
    
    /**
     * Resume real-time updates
     */
    const resume = useCallback(() => {
        if (!intervalRef.current && config.realTime && config.interval > 0) {
            fetchAnalyticsData();
            intervalRef.current = setInterval(() => fetchAnalyticsData(), config.interval);
            setConnectionStatus('connecting');
        }
    }, [config, fetchAnalyticsData]);
    
    /**
     * Get specific metric with fallback
     */
    const getMetric = useCallback((metricName, fallback = null) => {
        return data[metricName] || fallback;
    }, [data]);
    
    /**
     * Check if specific metric has error
     */
    const hasError = useCallback((metricName = null) => {
        if (metricName) {
            return !!errors[metricName];
        }
        return Object.keys(errors).length > 0;
    }, [errors]);
    
    // Initialize and set up real-time updates
    useEffect(() => {
        if (!channelId) return;
        
        // Initial fetch
        fetchAnalyticsData();
        
        // Set up real-time interval if enabled
        if (config.realTime && config.interval > 0) {
            intervalRef.current = setInterval(() => fetchAnalyticsData(), config.interval);
        }
        
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
        };
    }, [channelId, fetchAnalyticsData, config.realTime, config.interval]);
    
    // Return unified interface
    return {
        // Data access
        data,
        loading,
        errors,
        lastUpdated,
        connectionStatus,
        
        // Controls  
        refresh,
        pause,
        resume,
        
        // Utilities
        getMetric,
        hasError,
        
        // Status helpers
        isConnected: connectionStatus === 'connected',
        isPartiallyConnected: connectionStatus === 'partial',
        isPaused: connectionStatus === 'paused',
        isOffline: connectionStatus === 'cached',
        canRetry: retryCountRef.current <= config.retries,
        
        // Configuration
        currentPreset: preset,
        currentConfig: config
    };
};