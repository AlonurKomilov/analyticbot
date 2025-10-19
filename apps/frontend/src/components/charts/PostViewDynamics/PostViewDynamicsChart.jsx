import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import {
    Paper,
    Box,
    Typography,
    Alert
} from '@mui/material';
import { BarChart as ChartIcon } from '@mui/icons-material';
import { useAnalyticsStore } from '@/stores';

// Import extracted components
import TimeRangeControls from './TimeRangeControls.jsx';
import MetricsSummary from './MetricsSummary.jsx';
import ChartVisualization from './ChartVisualization.tsx';
import ChartErrorBoundary from './ChartErrorBoundary.jsx';
import { LoadingState, ChartEmptyState, StatusFooter } from './StatusComponents.jsx';

/**
 * PostViewDynamicsChart - Main orchestrator for post view dynamics analytics
 *
 * Refactored from 623-line monolithic component to modular architecture.
 * Manages state, data fetching, and coordinates between extracted components.
 * Optimized for multi-user dashboard performance with reduced re-renders.
 */
const PostViewDynamicsChart = () => {
    // Main component state
    const [timeRange, setTimeRange] = useState('24h');
    const [error, setError] = useState(null);
    const [data, setData] = useState([]);
    const [autoRefresh] = useState(true);
    const [refreshInterval, setRefreshInterval] = useState('30s');

    // Get store function and state
    const { fetchPostDynamics, postDynamics, isLoadingPostDynamics } = useAnalyticsStore();
    const fetchPostDynamicsFromStore = useAnalyticsStore.getState().fetchPostDynamics;

    // Use refs to track state and prevent unnecessary re-renders
    const isMountedRef = useRef(true);
    const dataRef = useRef([]);
    const timeRangeRef = useRef(timeRange);
    const isLoadingRef = useRef(false);
    const dataVersionRef = useRef(0);

    // Stable load data function with debouncing
    const loadData = useCallback(async () => {
        if (isLoadingRef.current) {
            return; // Already loading, skip duplicate request
        }

        isLoadingRef.current = true;
        setError(null);

        try {
            const currentTimeRange = timeRangeRef.current;
            await fetchPostDynamicsFromStore(1, currentTimeRange); // Channel ID 1 as default

            if (isMountedRef.current && postDynamics) {
                dataRef.current = postDynamics || {};
                setData(postDynamics || {});
                dataVersionRef.current += 1;
            }
        } catch (err) {
            console.error('PostViewDynamicsChart: Error loading data:', err);
            if (isMountedRef.current) {
                setError(err.message || 'Failed to load analytics data');
            }
        } finally {
            isLoadingRef.current = false;
        }
    }, [fetchPostDynamicsFromStore, postDynamics]); // Include dependencies

    // Handle time range changes with debouncing
    const handleTimeRangeChange = useCallback((event) => {
        const newTimeRange = event.target.value;
        timeRangeRef.current = newTimeRange;
        setTimeRange(newTimeRange);

        // Debounce time range changes to prevent rapid API calls
        setTimeout(() => {
            if (isMountedRef.current && timeRangeRef.current === newTimeRange) {
                loadData();
            }
        }, 300);
    }, []); // Removed loadData dependency - using stable callback via refs

    // Handle refresh interval changes
    const handleRefreshIntervalChange = useCallback((event) => {
        const newInterval = event.target.value;
        setRefreshInterval(newInterval);
    }, []);

    // Initial load (only once)
    useEffect(() => {
        let mounted = true;

        const initialLoad = async () => {
            // Small delay to avoid race conditions
            await new Promise(resolve => setTimeout(resolve, 100));
            if (mounted && isMountedRef.current) {
                loadData();
            }
        };

        initialLoad();

        return () => {
            mounted = false;
        };
    }, []); // Empty dependency array for initial load only

    // Auto-refresh logic
    useEffect(() => {
        if (!autoRefresh || refreshInterval === 'disabled') {
            return;
        }

        const intervalMap = {
            '30s': 30000,
            '1m': 60000,
            '5m': 300000
        };

        const intervalMs = intervalMap[refreshInterval] || 60000;

        if (process.env.NODE_ENV === 'development') {
            console.log('PostViewDynamicsChart: Setting up auto-refresh every', intervalMs, 'ms');
        }

        const interval = setInterval(() => {
            if (isMountedRef.current && !isLoadingRef.current) {
                if (process.env.NODE_ENV === 'development') {
                    console.log('PostViewDynamicsChart: Auto-refresh triggered');
                }
                loadData();
            }
        }, intervalMs);

        return () => {
            if (process.env.NODE_ENV === 'development') {
                console.log('PostViewDynamicsChart: Clearing auto-refresh interval');
            }
            clearInterval(interval);
        };
    }, [autoRefresh, refreshInterval]); // Removed loadData from dependencies - using refs for stability

    // Cleanup when component unmounts
    useEffect(() => {
        return () => {
            isMountedRef.current = false;
        };
    }, []);

    // Chart data transformation with enhanced validation and memoization
    const chartData = useMemo(() => {
        if (!data || !Array.isArray(data) || data.length === 0) {
            return [];
        }

        try {
            const transformedData = data.map((point, index) => {
                if (!point || typeof point !== 'object') {
                    return null;
                }

                return {
                    time: point.timestamp ?
                        new Date(point.timestamp).toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit'
                        }) :
                        point.time || `Point ${index + 1}`,
                    views: Math.max(0, Number(point.views) || 0),
                    likes: Math.max(0, Number(point.likes || point.reactions) || 0),
                    shares: Math.max(0, Number(point.shares || point.forwards) || 0),
                    comments: Math.max(0, Number(point.comments) || 0),
                    timestamp: point.timestamp || new Date().toISOString()
                };
            }).filter(Boolean);

            return transformedData;
        } catch (error) {
            console.error('Error transforming chart data:', error);
            return [];
        }
    }, [data]);

    // Summary statistics with memoization
    const summaryStats = useMemo(() => {
        if (!chartData || chartData.length === 0) return null;

        try {
            const latest = chartData[chartData.length - 1] || {};
            const previous = chartData[chartData.length - 2] || {};

            const total = chartData.reduce((sum, item) => sum + (item.views || 0), 0);
            const avgViews = Math.round(total / chartData.length) || 0;
            const currentViews = latest.views || 0;
            const previousViews = previous.views || 0;
            const growth = previousViews > 0 ? ((currentViews - previousViews) / previousViews * 100) : 0;

            return {
                totalViews: total,
                currentViews,
                averageViews: avgViews,
                growthRate: Number(growth.toFixed(1)),
                peakViews: Math.max(...chartData.map(d => d.views || 0)),
                dataPoints: chartData.length
            };
        } catch (error) {
            console.error('Error calculating summary stats:', error);
            return null;
        }
    }, [chartData]);

    // Error state
    if (error) {
        return (
            <Paper variant="card">
                <Alert severity="error" variant="spaced">
                    Error loading data: {error}
                </Alert>
            </Paper>
        );
    }

    return (
        <Paper variant="card">
            {/* Header */}
            <Box variant="headerControls">
                <Box variant="flexRow">
                    <ChartIcon color="primary" />
                    <Typography variant="h6">
                        Post View Dynamics
                    </Typography>
                </Box>

                <TimeRangeControls
                    timeRange={timeRange}
                    refreshInterval={refreshInterval}
                    onTimeRangeChange={handleTimeRangeChange}
                    onRefreshIntervalChange={handleRefreshIntervalChange}
                />
            </Box>

            {/* Summary Stats Cards */}
            {summaryStats && (
                <MetricsSummary summaryStats={summaryStats} />
            )}

            {/* Loading State */}
            {isLoadingPostDynamics && <LoadingState />}

            {/* Chart */}
            {!isLoadingPostDynamics && chartData.length > 0 && (
                <ChartVisualization data={chartData} timeRange={timeRange} />
            )}

            {/* Empty State */}
            {!isLoadingPostDynamics && chartData.length === 0 && <ChartEmptyState />}

            {/* Status Footer */}
            <StatusFooter
                autoRefresh={autoRefresh}
                refreshInterval={refreshInterval}
                summaryStats={summaryStats}
            />
        </Paper>
    );
};

// Memoize the component to prevent unnecessary re-renders from parent
const MemoizedPostViewDynamicsChart = React.memo(PostViewDynamicsChart);

/**
 * PostViewDynamicsChartWrapper - Error boundary wrapper component
 */
export default function PostViewDynamicsChartWrapper() {
    return (
        <ChartErrorBoundary>
            <MemoizedPostViewDynamicsChart />
        </ChartErrorBoundary>
    );
}
