import React, { useState, useEffect, useMemo, useCallback, useRef, ChangeEvent } from 'react';
import {
    Paper,
    Box,
    Typography,
    Alert,
    Button,
    Chip
} from '@mui/material';
import { BarChart as ChartIcon, ArrowBack } from '@mui/icons-material';
import { useAnalyticsStore, useChannelStore, useUIStore } from '@store';
import { DEFAULT_DEMO_CHANNEL_ID } from '@/__mocks__/constants';
import { uiLogger } from '@/utils/logger';

// Import extracted components
import TimeRangeControls from './TimeRangeControls';
import MetricsSummary from './MetricsSummary';
import ChartVisualization from './ChartVisualization';
import ChartErrorBoundary from './ChartErrorBoundary';
import { LoadingState, ChartEmptyState } from './StatusComponents';

// ============================================================================
// Type Definitions
// ============================================================================

export type TimeRange = '1h' | '6h' | '12h' | '24h' | '7d' | '30d' | '90d' | 'all';
export type RefreshInterval = '30s' | '1m' | '5m' | 'disabled';
export type MetricFilter = 'all' | 'views' | 'reactions' | 'forwards' | 'comments';

interface DataPoint {
    timestamp?: string;
    time?: string;
    views?: number;
    reactions?: number;
    likes?: number;  // Legacy support
    shares?: number;
    forwards?: number;
    comments?: number;
}

interface ChartDataPoint {
    time: string;
    views: number;
    reactions: number;
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
    totalPosts?: number;
    averageViewsTop?: number;
    totalReactions?: number;
    totalComments?: number;     // Discussion group comments
    totalReplies?: number;      // Threaded replies
    totalForwards?: number;
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
    const [timeRange, setTimeRange] = useState<TimeRange>('all');  // Default to All Time
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<DataPoint[]>([]);
    const [refreshInterval, setRefreshInterval] = useState<RefreshInterval>('30s');
    const [metricFilter, setMetricFilter] = useState<MetricFilter>('all');  // Filter for metrics
    const [drillDownDate, setDrillDownDate] = useState<string | null>(null); // For specific day drill-down
    const [drillDownHour, setDrillDownHour] = useState<string | null>(null); // For specific hour minute drill-down

    // Get store function and state (note: we read postDynamics from store directly in loadData)
    const { isLoadingPostDynamics } = useAnalyticsStore();
    const fetchPostDynamicsFromStore = useAnalyticsStore.getState().fetchPostDynamics;
    const { selectedChannel } = useChannelStore();
    const { dataSource } = useUIStore();

    // Use refs to track state and prevent unnecessary re-renders
    const isMountedRef = useRef<boolean>(true);
    const dataRef = useRef<DataPoint[]>([]);
    const timeRangeRef = useRef<TimeRange>(timeRange);
    const isLoadingRef = useRef<boolean>(false);
    const dataVersionRef = useRef<number>(0);
    const isAutoRefreshRef = useRef<boolean>(false); // Track if refresh is automatic

    // Stable load data function with debouncing
    const loadData = useCallback(async (): Promise<void> => {
        uiLogger.debug('PostDynamics: loadData called', { isLoading: isLoadingRef.current });

        if (isLoadingRef.current) {
            uiLogger.debug('PostDynamics: Already loading, skipping');
            return; // Already loading, skip duplicate request
        }

        // Determine which channel ID to use based on data source mode
        // 'api' = Real API with real channel, 'demo'/'mock' = Demo mode with demo channel
        const channelId = (dataSource === 'demo' || dataSource === 'mock')
            ? DEFAULT_DEMO_CHANNEL_ID
            : (selectedChannel?.id?.toString() || null);

        uiLogger.debug('PostDynamics: Channel determination', { dataSource, selectedChannel: selectedChannel?.id, channelId });

        if (!channelId) {
            uiLogger.info('No channel selected - select a channel to view post dynamics');
            setError('info:Please select a channel to view post dynamics'); // Prefix with 'info:' for info alert
            setData([]);
            isLoadingRef.current = false; // Reset loading flag
            return;
        }

        isLoadingRef.current = true;
        uiLogger.debug('PostDynamics: Set loading flag');
        setError(null);

        try {
            const currentTimeRange = timeRangeRef.current;
            uiLogger.debug('PostDynamics: Fetching data', { channelId, timeRange: currentTimeRange, drillDownDate, drillDownHour });

            // 3-level drill-down logic:
            // 1. If drilling into a specific hour, pass start_time/end_time for minute breakdown
            // 2. If drilling into a specific day, pass start_date/end_date for hourly breakdown
            // 3. Otherwise, use standard period
            const customTimeRange = drillDownHour ? {
                start_time: drillDownHour,
                end_time: new Date(new Date(drillDownHour).getTime() + 60 * 60 * 1000 - 1000).toISOString() // +1 hour - 1 second
            } : undefined;

            const customDateRange = drillDownDate && !drillDownHour ? {
                start_date: drillDownDate,
                end_date: drillDownDate
            } : undefined;

            await fetchPostDynamicsFromStore(channelId, currentTimeRange, customDateRange, customTimeRange, isAutoRefreshRef.current);

            // Get the latest data from store after fetch
            const latestPostDynamics = useAnalyticsStore.getState().postDynamics;
            uiLogger.debug('PostDynamics: Received data', { isArray: Array.isArray(latestPostDynamics), length: Array.isArray(latestPostDynamics) ? latestPostDynamics.length : 'N/A' });

            // Debug minute-level data to understand time jumps
            if (drillDownHour && Array.isArray(latestPostDynamics)) {
                const firstPoints = latestPostDynamics.slice(0, 5).map((point, idx) => ({
                    idx,
                    timestamp: point.timestamp,
                    views: point.views
                }));
                const lastPoints = latestPostDynamics.slice(-5).map((point, idx) => ({
                    idx: latestPostDynamics.length - 5 + idx,
                    timestamp: point.timestamp,
                    views: point.views
                }));
                uiLogger.debug('PostDynamics: Minute-level data', {
                    totalPoints: latestPostDynamics.length,
                    firstPoints,
                    lastPoints
                });
            }

            // Handle both object and array responses
            let dataArray: DataPoint[] = [];
            if (Array.isArray(latestPostDynamics)) {
                dataArray = latestPostDynamics;
                uiLogger.debug('PostDynamics: Data is array', { length: dataArray.length });
            } else if (latestPostDynamics && typeof latestPostDynamics === 'object') {
                uiLogger.debug('PostDynamics: Data is object', { keys: Object.keys(latestPostDynamics) });
                // If it's an object, it might have a 'data' or 'dataPoints' property
                if ('dataPoints' in latestPostDynamics) {
                    dataArray = (latestPostDynamics as any).dataPoints || [];
                } else if ('data' in latestPostDynamics) {
                    dataArray = (latestPostDynamics as any).data || [];
                }
            }

            uiLogger.debug('PostDynamics: About to set data', {
                itemCount: dataArray.length,
                firstItem: dataArray[0],
                isMounted: isMountedRef.current
            });

            // ALWAYS set data, even if component unmounted (React will handle it)
            dataRef.current = dataArray;
            setData(dataArray);
            dataVersionRef.current += 1;
            uiLogger.debug('PostDynamics: Data set successfully', { length: dataArray.length, version: dataVersionRef.current });
        } catch (err) {
            uiLogger.error('PostViewDynamicsChart: Error loading data', { error: err });
            if (isMountedRef.current) {
                const errorMessage = err instanceof Error ? err.message : 'Failed to load analytics data';
                setError(errorMessage);
            }
        } finally {
            isLoadingRef.current = false;
            uiLogger.debug('PostDynamics: Released loading flag');
        }
    }, [selectedChannel, dataSource, drillDownDate, drillDownHour]); // Re-run when drilling down

    // Handle time range changes with debouncing
    const handleTimeRangeChange = useCallback((event: ChangeEvent<HTMLInputElement>): void => {
        const newTimeRange = event.target.value as TimeRange;
        uiLogger.debug('PostDynamics: Time range changed', { from: timeRangeRef.current, to: newTimeRange });
        timeRangeRef.current = newTimeRange;
        setTimeRange(newTimeRange);
        uiLogger.debug('PostDynamics: timeRangeRef updated', { current: timeRangeRef.current });

        // Reset loading flag to allow new request
        isLoadingRef.current = false;

        // Debounce time range changes to prevent rapid API calls
        setTimeout(() => {
            uiLogger.debug('PostDynamics: Debounce complete', { timeRange: timeRangeRef.current });
            // Check if time range hasn't changed again during debounce
            if (timeRangeRef.current === newTimeRange) {
                uiLogger.debug('PostDynamics: Calling loadData after debounce');
                loadData();
            } else {
                uiLogger.debug('PostDynamics: Time range changed during debounce, skipping');
            }
        }, 300);
    }, [loadData]);

    // Handle refresh interval changes
    const handleRefreshIntervalChange = useCallback((event: ChangeEvent<HTMLInputElement>): void => {
        const newInterval = event.target.value as RefreshInterval;
        setRefreshInterval(newInterval);
    }, []);

    // Handle metric filter changes
    const handleMetricFilterChange = useCallback((event: ChangeEvent<HTMLInputElement>): void => {
        const newFilter = event.target.value as MetricFilter;
        setMetricFilter(newFilter);
    }, []);

    // Handle drill-down: click on a data point to see deeper breakdown
    const handleChartClick = useCallback((data: any) => {
        uiLogger.debug('PostDynamics: handleChartClick called', { data, timeRange, drillDownDate, drillDownHour });

        // Recharts onClick gives us activeLabel (timestamp)
        if (!data || !data.activeLabel) {
            uiLogger.debug('PostDynamics: No activeLabel in click data');
            return;
        }

        const clickedTimestamp = data.activeLabel;
        uiLogger.debug('PostDynamics: Clicked timestamp', { timestamp: clickedTimestamp });
        const clickedDate = new Date(clickedTimestamp);

        // 3-level drill-down logic:
        // - If in minute view (drillDownHour exists): Already at deepest level, do nothing
        // - If in hour view (drillDownDate exists): Drill into specific hour → minute view
        // - If in day view (90d, 30d, etc): Drill into specific day → hour view

        if (drillDownHour) {
            // Already showing minutes, can't drill deeper
            uiLogger.debug('PostDynamics: Already at minute level, cannot drill deeper');
            return;
        } else if (drillDownDate) {
            // Currently showing hours for a specific day, drill into specific hour
            const hourTimestamp = clickedDate.toISOString();
            uiLogger.debug('PostDynamics: Drilling into hour', { timestamp: hourTimestamp });
            setDrillDownHour(hourTimestamp);
        } else if (timeRange !== '1h' && timeRange !== '6h' && timeRange !== '12h' && timeRange !== '24h') {
            // Currently showing days, drill into specific day
            const dateStr = clickedDate.toISOString().split('T')[0]; // Get YYYY-MM-DD
            uiLogger.debug('PostDynamics: Drilling into day', { date: dateStr });
            setDrillDownDate(dateStr);
        } else {
            uiLogger.debug('PostDynamics: Already in hourly view, not drilling down');
        }
    }, [timeRange, drillDownDate, drillDownHour]);    // Handle back navigation from drill-down
    const handleBackClick = useCallback(() => {
        uiLogger.debug('PostDynamics: Navigating back from drill-down', { drillDownHour });
        if (drillDownHour) {
            // Go back from minute view to hour view
            setDrillDownHour(null);
        } else {
            // Go back from hour view to day view
            setDrillDownDate(null);
        }
    }, [drillDownHour]);

    // Initial load when component mounts or when selectedChannel/dataSource changes
    useEffect(() => {
        uiLogger.debug('PostDynamics: Initial load effect triggered', { selectedChannel: selectedChannel?.id, dataSource });

        // Load if: (1) demo/mock mode OR (2) api mode with selected channel
        const shouldLoad = (dataSource === 'demo' || dataSource === 'mock')
            || (dataSource === 'api' && selectedChannel?.id);

        if (shouldLoad) {
            uiLogger.debug('PostDynamics: Calling loadData immediately');
            loadData();
        } else {
            uiLogger.debug('PostDynamics: Skipping load - no channel selected for API mode');
        }
    }, [selectedChannel, dataSource, loadData]); // Trigger when channel or dataSource changes

    // Auto-refresh logic - DISABLED for performance
    // Historical post data doesn't change frequently (Telegram updates metrics every few hours)
    // Users can manually refresh using the refresh button if needed
    useEffect(() => {
        // Auto-refresh intentionally disabled to:
        // - Reduce server load and database queries
        // - Save battery on user devices
        // - Prevent disruption during drill-down analysis
        // - Avoid unnecessary API calls for historical data that rarely changes
        return () => {
            // Cleanup placeholder
        };
    }, []);

    // Cleanup when component unmounts
    useEffect(() => {
        return () => {
            isMountedRef.current = false;
        };
    }, []);

    // Chart data transformation with enhanced validation and memoization
    const chartData = useMemo<ChartDataPoint[]>(() => {
        uiLogger.debug('PostDynamics: Transforming chart data', { dataLength: data?.length, isArray: Array.isArray(data) });

        if (!data || !Array.isArray(data) || data.length === 0) {
            uiLogger.debug('PostDynamics: No data to transform, returning empty array');
            return [];
        }

        try {
            uiLogger.debug('PostDynamics: Starting transformation', { itemCount: data.length });
            const transformedData = data.map((point, index) => {
                if (!point || typeof point !== 'object') {
                    uiLogger.warn('PostDynamics: Invalid point', { index, point });
                    return null;
                }

                // Format time based on data granularity
                let timeLabel: string;
                if (point.timestamp) {
                    const date = new Date(point.timestamp);
                    // If data spans multiple days, show date; otherwise show time
                    const firstTimestamp = data[0]?.timestamp;
                    const lastTimestamp = data[data.length - 1]?.timestamp;
                    const isMultiDay = data.length > 1 &&
                        firstTimestamp && lastTimestamp &&
                        new Date(firstTimestamp).toDateString() !== new Date(lastTimestamp).toDateString();

                    if (isMultiDay) {
                        // Show date for multi-day views
                        timeLabel = date.toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric'
                        });
                    } else {
                        // Show time for single-day views
                        timeLabel = date.toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                    }
                } else {
                    timeLabel = point.time || `Point ${index + 1}`;
                }

                const transformed = {
                    time: timeLabel,
                    views: Math.max(0, Number(point.views) || 0),
                    reactions: Math.max(0, Number(point.reactions || point.likes) || 0),
                    shares: Math.max(0, Number(point.shares || point.forwards) || 0),
                    comments: Math.max(0, Number(point.comments) || 0),
                    timestamp: point.timestamp || new Date().toISOString()
                };

                if (index === 0) {
                    uiLogger.debug('PostDynamics: First transformed item', { transformed });
                }

                return transformed;
            }).filter((item): item is ChartDataPoint => item !== null);

            uiLogger.debug('PostDynamics: Transformed chart data', { outputLength: transformedData.length });
            return transformedData;
        } catch (error) {
            uiLogger.error('PostDynamics: Error transforming chart data', { error });
            return [];
        }
    }, [data]);

    // Summary statistics with memoization
    const summaryStats = useMemo<SummaryStats | null>(() => {
        uiLogger.debug('PostDynamics: Calculating summary stats', { chartDataLength: chartData?.length });

        if (!chartData || chartData.length === 0) {
            uiLogger.debug('PostDynamics: No chartData for summary stats');
            return null;
        }

        try {
            const latest = chartData[chartData.length - 1] || {} as ChartDataPoint;
            const previous = chartData[chartData.length - 2] || {} as ChartDataPoint;

            const total = chartData.reduce((sum, item) => sum + (item.views || 0), 0);
            const avgViews = Math.round(total / chartData.length) || 0;
            const currentViews = latest.views || 0;
            const previousViews = previous.views || 0;
            const growth = previousViews > 0 ? ((currentViews - previousViews) / previousViews * 100) : 0;

            // Calculate engagement metrics from chart data
            const totalReactions = chartData.reduce((sum, item) => sum + (item.reactions || 0), 0);
            const totalComments = chartData.reduce((sum, item) => sum + (item.comments || 0), 0);
            const totalForwards = chartData.reduce((sum, item) => sum + (item.shares || 0), 0);

            // Calculate totals for top stats (if available from raw data)
            const postsData = Array.isArray(data) ? data : [];
            const totalPosts = postsData.reduce((sum: number, point: any) =>
                sum + (point.post_count || point.postCount || 0), 0
            );
            const totalViewsAll = postsData.reduce((sum: number, post: any) => sum + (post.views || 0), 0);
            const avgViewsAll = totalPosts > 0 ? Math.round(totalViewsAll / totalPosts) : 0;
            const totalReplies = postsData.reduce((sum: number, post: any) =>
                sum + (post.threaded_replies_count || post.threaded_replies || 0), 0
            );

            const stats = {
                totalViews: total,
                currentViews,
                averageViews: avgViews,
                growthRate: Number(growth.toFixed(1)),
                peakViews: Math.max(...chartData.map(d => d.views || 0)),
                dataPoints: chartData.length,
                // Additional stats for top metrics
                totalPosts: totalPosts || 0,
                averageViewsTop: avgViewsAll,
                totalReactions: totalReactions || 0,
                totalComments: totalComments || 0,
                totalReplies: totalReplies || 0,
                totalForwards: totalForwards || 0
            };

            uiLogger.debug('PostDynamics: Summary stats calculated', { totalViews: stats.totalViews, currentViews: stats.currentViews });
            return stats;
        } catch (error) {
            uiLogger.error('PostDynamics: Error calculating summary stats', { error });
            return null;
        }
    }, [chartData, data]);

    // Error state
    if (error) {
        const isInfo = error.startsWith('info:');
        const message = isInfo ? error.replace('info:', '') : error;
        const severity = isInfo ? 'info' : 'error';

        return (
            <Paper>
                <Alert severity={severity}>
                    {message}
                </Alert>
            </Paper>
        );
    }

    uiLogger.debug('PostDynamics: Rendering component', {
        isLoading: isLoadingPostDynamics,
        chartDataLength: chartData.length,
        hasSummaryStats: !!summaryStats
    });

    return (
        <Paper>
            {/* Header */}
            <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <ChartIcon color="primary" />
                    <Typography variant="h6">
                        Post View Dynamics
                    </Typography>

                    {/* Drill-down breadcrumb - 3 levels: day → hour → minute */}
                    {(drillDownDate || drillDownHour) && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 'auto' }}>
                            <Button
                                size="small"
                                startIcon={<ArrowBack />}
                                onClick={handleBackClick}
                                variant="outlined"
                            >
                                Back to {drillDownHour ? 'hourly view' : `${timeRange} overview`}
                            </Button>
                            {drillDownHour ? (
                                <Chip
                                    label={`Viewing: ${new Date(drillDownHour).toLocaleString('en-US', {
                                        month: 'short',
                                        day: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        hour12: true
                                    })} (Minutes)`}
                                    color="secondary"
                                    variant="outlined"
                                />
                            ) : (
                                <Chip
                                    label={`Viewing: ${new Date(drillDownDate!).toLocaleDateString('en-US', {
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric'
                                    })} (Hourly)`}
                                    color="primary"
                                    variant="outlined"
                                />
                            )}
                        </Box>
                    )}
                </Box>
            </Box>

            {/* Summary Stats Cards */}
            {summaryStats && (
                <MetricsSummary stats={{
                    totalViews: summaryStats.totalViews,
                    totalReactions: summaryStats.totalReactions || 0,
                    totalComments: summaryStats.totalComments || 0,
                    totalForwards: summaryStats.totalForwards || 0,
                    growthPercentage: summaryStats.growthRate,
                    peakViews: summaryStats.peakViews,
                    totalPosts: summaryStats.totalPosts,
                    averageViews: summaryStats.averageViewsTop
                }} />
            )}

            {/* Show time range only when NOT in drill-down mode - Moved below summary cards */}
            {!drillDownDate && !drillDownHour && (
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                    <TimeRangeControls
                        timeRange={timeRange as any}
                        refreshInterval={refreshInterval as any}
                        metricFilter={metricFilter as any}
                        onTimeRangeChange={handleTimeRangeChange as any}
                        onRefreshIntervalChange={handleRefreshIntervalChange as any}
                        onMetricFilterChange={handleMetricFilterChange as any}
                        hideRefreshControl={true}  // Hide auto-refresh - not needed for historical data
                    />
                    {/* Hint for drill-down discoverability - placed next to Time Period */}
                    {chartData && chartData.length > 0 && (
                        <Chip
                            label="Tip: Click any data point to view hourly breakdown"
                            color="primary"
                            variant="outlined"
                            size="small"
                        />
                    )}
                </Box>
            )}

            {/* Hint for drill-down when in hourly view */}
            {drillDownDate && !drillDownHour && chartData && chartData.length > 0 && (
                <Box sx={{ mt: 2, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                        label="Tip: Click any hour to view minute-by-minute breakdown"
                        color="primary"
                        variant="outlined"
                        size="small"
                    />
                </Box>
            )}

            {/* Loading State */}
            {isLoadingPostDynamics && <LoadingState />}

            {/* Chart */}
            {!isLoadingPostDynamics && chartData.length > 0 && (
                <>
                    <ChartVisualization
                        data={chartData}
                        timeRange={timeRange}
                        metricFilter={metricFilter}
                        onChartClick={!drillDownHour ? handleChartClick : undefined}
                    />
                </>
            )}

            {/* Empty State */}
            {!isLoadingPostDynamics && chartData.length === 0 && <ChartEmptyState />}
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
