import React, { useState, useEffect, useMemo, useCallback, useRef, ChangeEvent } from 'react';
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
import ChartVisualization from './ChartVisualization';
import ChartErrorBoundary from './ChartErrorBoundary.jsx';
import { LoadingState, ChartEmptyState, StatusFooter } from './StatusComponents.jsx';

// ============================================================================
// Type Definitions
// ============================================================================

export type TimeRange = '24h' | '7d' | '30d' | '90d';
export type RefreshInterval = '30s' | '1m' | '5m' | 'disabled';

interface DataPoint {
    timestamp?: string;
    time?: string;
    views?: number;
    likes?: number;
    reactions?: number;
    shares?: number;
    forwards?: number;
    comments?: number;
}

interface ChartDataPoint {
    time: string;
    views: number;
    likes: number;
    shares: number;
    comments: number;
    timestamp: string;
}

interface SummaryStats {
    totalViews: number;
    currentViews: number;
    averageViews: number;
    growthRate: number;
    peakViews: number;
    dataPoints: number;
}

// ============================================================================
// Main Component
// ============================================================================

/**
 * PostViewDynamicsChart - Main orchestrator for post view dynamics analytics
 *
 * Refactored from 623-line monolithic component to modular architecture.
 * Manages state, data fetching, and coordinates between extracted components.
 * Optimized for multi-user dashboard performance with reduced re-renders.
 */
const PostViewDynamicsChart: React.FC = () => {
    // Main component state
    const [timeRange, setTimeRange] = useState<TimeRange>('24h');
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<DataPoint[]>([]);
    const [autoRefresh] = useState<boolean>(true);
    const [refreshInterval, setRefreshInterval] = useState<RefreshInterval>('30s');

    // Get store function and state
    const { postDynamics, isLoadingPostDynamics } = useAnalyticsStore();
    const fetchPostDynamicsFromStore = useAnalyticsStore.getState().fetchPostDynamics;

    // Use refs to track state and prevent unnecessary re-renders
    const isMountedRef = useRef<boolean>(true);
    const dataRef = useRef<DataPoint[]>([]);
    const timeRangeRef = useRef<TimeRange>(timeRange);
    const isLoadingRef = useRef<boolean>(false);
    const dataVersionRef = useRef<number>(0);

    // Stable load data function with debouncing
    const loadData = useCallback(async (): Promise<void> => {
        if (isLoadingRef.current) {
            return; // Already loading, skip duplicate request
        }

        isLoadingRef.current = true;
        setError(null);

        try {
            const currentTimeRange = timeRangeRef.current;
            await fetchPostDynamicsFromStore('1', currentTimeRange); // Channel ID 1 as default

            if (isMountedRef.current && postDynamics) {
                const dataArray = Array.isArray(postDynamics) ? postDynamics : [];
                dataRef.current = dataArray;
                setData(dataArray);
                dataVersionRef.current += 1;
            }
        } catch (err) {
            console.error('PostViewDynamicsChart: Error loading data:', err);
            if (isMountedRef.current) {
                const errorMessage = err instanceof Error ? err.message : 'Failed to load analytics data';
                setError(errorMessage);
            }
        } finally {
            isLoadingRef.current = false;
        }
    }, [fetchPostDynamicsFromStore, postDynamics]); // Include dependencies

    // Handle time range changes with debouncing
    const handleTimeRangeChange = useCallback((event: ChangeEvent<HTMLInputElement>): void => {
        const newTimeRange = event.target.value as TimeRange;
        timeRangeRef.current = newTimeRange;
        setTimeRange(newTimeRange);

        // Debounce time range changes to prevent rapid API calls
        setTimeout(() => {
            if (isMountedRef.current && timeRangeRef.current === newTimeRange) {
                loadData();
            }
        }, 300);
    }, [loadData]);

    // Handle refresh interval changes
    const handleRefreshIntervalChange = useCallback((event: ChangeEvent<HTMLInputElement>): void => {
        const newInterval = event.target.value as RefreshInterval;
        setRefreshInterval(newInterval);
    }, []);

    // Initial load (only once)
    useEffect(() => {
        let mounted = true;

        const initialLoad = async (): Promise<void> => {
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
    }, [loadData]); // loadData is stable via useCallback

    // Auto-refresh logic
    useEffect(() => {
        if (!autoRefresh || refreshInterval === 'disabled') {
            return;
        }

        const intervalMap: Record<RefreshInterval, number> = {
            '30s': 30000,
            '1m': 60000,
            '5m': 300000,
            'disabled': 0
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
    }, [autoRefresh, refreshInterval, loadData]);

    // Cleanup when component unmounts
    useEffect(() => {
        return () => {
            isMountedRef.current = false;
        };
    }, []);

    // Chart data transformation with enhanced validation and memoization
    const chartData = useMemo<ChartDataPoint[]>(() => {
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
            }).filter((item): item is ChartDataPoint => item !== null);

            return transformedData;
        } catch (error) {
            console.error('Error transforming chart data:', error);
            return [];
        }
    }, [data]);

    // Summary statistics with memoization
    const summaryStats = useMemo<SummaryStats | null>(() => {
        if (!chartData || chartData.length === 0) return null;

        try {
            const latest = chartData[chartData.length - 1] || {} as ChartDataPoint;
            const previous = chartData[chartData.length - 2] || {} as ChartDataPoint;

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
            <Paper>
                <Alert severity="error">
                    Error loading data: {error}
                </Alert>
            </Paper>
        );
    }

    return (
        <Paper>
            {/* Header */}
            <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <ChartIcon color="primary" />
                    <Typography variant="h6">
                        Post View Dynamics
                    </Typography>
                </Box>

                <TimeRangeControls
                    timeRange={timeRange as any}
                    refreshInterval={refreshInterval as any}
                    onTimeRangeChange={handleTimeRangeChange as any}
                    onRefreshIntervalChange={handleRefreshIntervalChange as any}
                />
            </Box>

            {/* Summary Stats Cards */}
            {summaryStats && (
                <MetricsSummary {...summaryStats as any} />
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
export default function PostViewDynamicsChartWrapper(): React.ReactElement {
    return (
        <ChartErrorBoundary>
            <MemoizedPostViewDynamicsChart />
        </ChartErrorBoundary>
    );
}
