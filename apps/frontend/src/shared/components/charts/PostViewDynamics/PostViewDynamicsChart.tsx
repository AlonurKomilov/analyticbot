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

// Import extracted components
import TimeRangeControls from './TimeRangeControls.jsx';
import MetricsSummary from './MetricsSummary.jsx';
import ChartVisualization from './ChartVisualization';
import ChartErrorBoundary from './ChartErrorBoundary.jsx';
import { LoadingState, ChartEmptyState, StatusFooter } from './StatusComponents.jsx';

// ============================================================================
// Type Definitions
// ============================================================================

export type TimeRange = '1h' | '6h' | '12h' | '24h' | '7d' | '30d' | '90d' | 'all';
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
    const [timeRange, setTimeRange] = useState<TimeRange>('30d');
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<DataPoint[]>([]);
    const [autoRefresh] = useState<boolean>(true);
    const [refreshInterval, setRefreshInterval] = useState<RefreshInterval>('30s');
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

    // Stable load data function with debouncing
    const loadData = useCallback(async (): Promise<void> => {
        console.log('🚀 PostDynamics: loadData called! isLoadingRef=', isLoadingRef.current);

        if (isLoadingRef.current) {
            console.log('⏸️  PostDynamics: Already loading, skipping...');
            return; // Already loading, skip duplicate request
        }

        // Determine which channel ID to use based on data source mode
        // 'api' = Real API with real channel, 'demo'/'mock' = Demo mode with demo channel
        const channelId = (dataSource === 'demo' || dataSource === 'mock')
            ? DEFAULT_DEMO_CHANNEL_ID
            : (selectedChannel?.id?.toString() || null);

        console.log('🔍 PostDynamics: dataSource =', dataSource);
        console.log('🔍 PostDynamics: selectedChannel =', selectedChannel);
        console.log('🔍 PostDynamics: channelId =', channelId);

        if (!channelId) {
            console.info('💡 No channel selected - select a channel to view post dynamics');
            setError('info:Please select a channel to view post dynamics'); // Prefix with 'info:' for info alert
            setData([]);
            isLoadingRef.current = false; // Reset loading flag
            return;
        }

        isLoadingRef.current = true;
        console.log('🔒 PostDynamics: Set isLoadingRef = true');
        setError(null);

        try {
            const currentTimeRange = timeRangeRef.current;
            console.log(`📊 Fetching post dynamics for channel: ${channelId}, timeRange: ${currentTimeRange}, drillDownDate: ${drillDownDate}`);

            // 2-level drill-down logic (minutes removed - no minute-level data available):
            // 1. If drilling into a specific day, pass start_date/end_date for hourly breakdown
            // 2. Otherwise, use standard period

            const customDateRange = drillDownDate ? {
                start_date: drillDownDate,
                end_date: drillDownDate
            } : undefined;

            await fetchPostDynamicsFromStore(channelId, currentTimeRange, customDateRange, undefined);

            // Get the latest data from store after fetch
            const latestPostDynamics = useAnalyticsStore.getState().postDynamics;
            console.log('📥 PostDynamics: Received data =', latestPostDynamics);
            console.log('📥 PostDynamics: Is array?', Array.isArray(latestPostDynamics));

            // Handle both object and array responses
            let dataArray: DataPoint[] = [];
            if (Array.isArray(latestPostDynamics)) {
                dataArray = latestPostDynamics;
                console.log('📥 PostDynamics: Array length =', dataArray.length);
            } else if (latestPostDynamics && typeof latestPostDynamics === 'object') {
                console.log('📥 PostDynamics: Object keys =', Object.keys(latestPostDynamics));
                // If it's an object, it might have a 'data' or 'dataPoints' property
                if ('dataPoints' in latestPostDynamics) {
                    dataArray = (latestPostDynamics as any).dataPoints || [];
                } else if ('data' in latestPostDynamics) {
                    dataArray = (latestPostDynamics as any).data || [];
                }
            }

            console.log('💾 PostDynamics: About to call setData with', dataArray.length, 'items');
            console.log('💾 PostDynamics: First item:', dataArray[0]);
            console.log('💾 PostDynamics: isMountedRef.current =', isMountedRef.current);

            // ALWAYS set data, even if component unmounted (React will handle it)
            dataRef.current = dataArray;
            setData(dataArray);
            dataVersionRef.current += 1;
            console.log('✅ PostDynamics: Data set successfully, length =', dataArray.length);
            console.log('✅ PostDynamics: dataVersionRef =', dataVersionRef.current);
        } catch (err) {
            console.error('❌ PostViewDynamicsChart: Error loading data:', err);
            if (isMountedRef.current) {
                const errorMessage = err instanceof Error ? err.message : 'Failed to load analytics data';
                setError(errorMessage);
            }
        } finally {
            isLoadingRef.current = false;
            console.log('🔓 PostDynamics: Set isLoadingRef = false');
        }
    }, [selectedChannel, dataSource, drillDownDate]); // Re-run when drilling down (removed drillDownHour)

    // Handle time range changes with debouncing
    const handleTimeRangeChange = useCallback((event: ChangeEvent<HTMLInputElement>): void => {
        const newTimeRange = event.target.value as TimeRange;
        console.log('⏰ PostDynamics: Time range changed from', timeRangeRef.current, 'to', newTimeRange);
        timeRangeRef.current = newTimeRange;
        setTimeRange(newTimeRange);
        console.log('⏰ PostDynamics: timeRangeRef.current now =', timeRangeRef.current);

        // Reset loading flag to allow new request
        isLoadingRef.current = false;

        // Debounce time range changes to prevent rapid API calls
        setTimeout(() => {
            console.log('⏰ PostDynamics: Debounce complete, calling loadData with timeRange:', timeRangeRef.current);
            // Check if time range hasn't changed again during debounce
            if (timeRangeRef.current === newTimeRange) {
                console.log('⏰ PostDynamics: Condition passed, calling loadData()');
                loadData();
            } else {
                console.log('⏰ PostDynamics: Time range changed during debounce, skipping');
            }
        }, 300);
    }, [loadData]);

    // Handle refresh interval changes
    const handleRefreshIntervalChange = useCallback((event: ChangeEvent<HTMLInputElement>): void => {
        const newInterval = event.target.value as RefreshInterval;
        setRefreshInterval(newInterval);
    }, []);

    // Handle drill-down: click on a data point to see deeper breakdown
    const handleChartClick = useCallback((data: any) => {
        console.log('🎯 handleChartClick called with data:', data);
        console.log('🎯 Current timeRange:', timeRange);
        console.log('🎯 Current drillDownDate:', drillDownDate);
        console.log('🎯 Current drillDownHour:', drillDownHour);

        // Recharts onClick gives us activeLabel (timestamp)
        if (!data || !data.activeLabel) {
            console.log('⚠️  No activeLabel in click data');
            return;
        }

        const clickedTimestamp = data.activeLabel;
        console.log('🎯 Clicked timestamp from activeLabel:', clickedTimestamp);
        const clickedDate = new Date(clickedTimestamp);

        // 2-level drill-down logic (minutes disabled - we don't have minute-level data):
        // - If in hour view (drillDownDate exists): Already at deepest level, do nothing
        // - If in day view (90d, 30d, etc): Drill into specific day → hour view

        if (drillDownDate) {
            // Already showing hours for a specific day, can't drill deeper
            console.log('⚠️  Already at hour level (deepest available), cannot drill deeper');
            return;
        } else if (timeRange !== '1h' && timeRange !== '6h' && timeRange !== '12h' && timeRange !== '24h') {
            // Currently showing days, drill into specific day
            const dateStr = clickedDate.toISOString().split('T')[0]; // Get YYYY-MM-DD
            console.log(`🔍 Drilling into day: ${dateStr}`);
            setDrillDownDate(dateStr);
        } else {
            console.log('⚠️  Already in hourly view, not drilling down');
        }
    }, [timeRange, drillDownDate, drillDownHour]);

    // Handle back navigation from drill-down
    const handleBackClick = useCallback(() => {
        console.log('⬅️  Navigating back from drill-down');
        // Only one level of drill-down (day → hour), so always go back to day view
        setDrillDownDate(null);
        setDrillDownHour(null);
    }, []);

    // Initial load when component mounts or when selectedChannel/dataSource changes
    useEffect(() => {
        console.log('🎬 PostDynamics: Initial load effect triggered');
        console.log('🔍 PostDynamics: selectedChannel =', selectedChannel?.id);
        console.log('🔍 PostDynamics: dataSource =', dataSource);

        // Load if: (1) demo/mock mode OR (2) api mode with selected channel
        const shouldLoad = (dataSource === 'demo' || dataSource === 'mock')
            || (dataSource === 'api' && selectedChannel?.id);

        if (shouldLoad) {
            console.log('📞 PostDynamics: Calling loadData() immediately');
            loadData();
        } else {
            console.log('⏸️  PostDynamics: Skipping load - no channel selected for API mode');
        }
    }, [selectedChannel, dataSource, loadData]); // Trigger when channel or dataSource changes

    // Auto-refresh logic
    useEffect(() => {
        // Don't set up auto-refresh if no channel is selected
        // demo/mock = use demo channel, api = use selected channel
        const channelId = (dataSource === 'demo' || dataSource === 'mock')
            ? DEFAULT_DEMO_CHANNEL_ID
            : (selectedChannel?.id?.toString() || null);

        if (!channelId || !autoRefresh || refreshInterval === 'disabled') {
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
            // Only auto-refresh if not currently loading
            if (!isLoadingRef.current) {
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
    }, [autoRefresh, refreshInterval, loadData, selectedChannel, dataSource]);

    // Cleanup when component unmounts
    useEffect(() => {
        return () => {
            isMountedRef.current = false;
        };
    }, []);

    // Chart data transformation with enhanced validation and memoization
    const chartData = useMemo<ChartDataPoint[]>(() => {
        console.log('🔄 PostDynamics: Transforming chart data, input data =', data);
        console.log('🔄 PostDynamics: data length =', data?.length);
        console.log('🔄 PostDynamics: data is array?', Array.isArray(data));

        if (!data || !Array.isArray(data) || data.length === 0) {
            console.log('⚠️  PostDynamics: No data to transform, returning empty array');
            return [];
        }

        try {
            console.log('🔄 PostDynamics: Starting transformation of', data.length, 'items');
            const transformedData = data.map((point, index) => {
                if (!point || typeof point !== 'object') {
                    console.warn('⚠️  PostDynamics: Invalid point at index', index, ':', point);
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
                    likes: Math.max(0, Number(point.likes || point.reactions) || 0),
                    shares: Math.max(0, Number(point.shares || point.forwards) || 0),
                    comments: Math.max(0, Number(point.comments) || 0),
                    timestamp: point.timestamp || new Date().toISOString()
                };

                if (index === 0) {
                    console.log('🔄 PostDynamics: First transformed item:', transformed);
                }

                return transformed;
            }).filter((item): item is ChartDataPoint => item !== null);

            console.log('✅ PostDynamics: Transformed chart data, output length =', transformedData.length);
            return transformedData;
        } catch (error) {
            console.error('❌ PostDynamics: Error transforming chart data:', error);
            return [];
        }
    }, [data]);

    // Summary statistics with memoization
    const summaryStats = useMemo<SummaryStats | null>(() => {
        console.log('📊 PostDynamics: Calculating summary stats, chartData length =', chartData?.length);

        if (!chartData || chartData.length === 0) {
            console.log('⚠️  PostDynamics: No chartData for summary stats');
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

            const stats = {
                totalViews: total,
                currentViews,
                averageViews: avgViews,
                growthRate: Number(growth.toFixed(1)),
                peakViews: Math.max(...chartData.map(d => d.views || 0)),
                dataPoints: chartData.length
            };

            console.log('✅ PostDynamics: Summary stats calculated:', stats);
            return stats;
        } catch (error) {
            console.error('❌ PostDynamics: Error calculating summary stats:', error);
            return null;
        }
    }, [chartData]);

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

    console.log('🎨 PostDynamics: Rendering component');
    console.log('   - isLoadingPostDynamics:', isLoadingPostDynamics);
    console.log('   - chartData.length:', chartData.length);
    console.log('   - summaryStats:', summaryStats ? 'present' : 'null');

    return (
        <Paper>
            {/* Header */}
            <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <ChartIcon color="primary" />
                    <Typography variant="h6">
                        Post View Dynamics
                    </Typography>

                    {/* Drill-down breadcrumb - 2 levels only (day → hour) */}
                    {drillDownDate && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 'auto' }}>
                            <Button
                                size="small"
                                startIcon={<ArrowBack />}
                                onClick={handleBackClick}
                                variant="outlined"
                            >
                                Back to {timeRange} overview
                            </Button>
                            <Chip
                                label={`Viewing: ${new Date(drillDownDate!).toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric'
                                })} (Hourly)`}
                                color="primary"
                                variant="outlined"
                            />
                        </Box>
                    )}
                </Box>

                {!drillDownDate && (
                    <TimeRangeControls
                        timeRange={timeRange as any}
                        refreshInterval={refreshInterval as any}
                        onTimeRangeChange={handleTimeRangeChange as any}
                        onRefreshIntervalChange={handleRefreshIntervalChange as any}
                    />
                )}
            </Box>

            {/* Summary Stats Cards */}
            {summaryStats && (
                <MetricsSummary stats={{
                    totalViews: summaryStats.totalViews,
                    averageEngagement: summaryStats.averageViews,
                    growthPercentage: summaryStats.growthRate,
                    peakViews: summaryStats.peakViews
                }} />
            )}

            {/* Hint for drill-down discoverability */}
            {!drillDownDate && chartData && chartData.length > 0 && (
                <Box sx={{ mt: 2, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                        label="Tip: Click any data point to view hourly breakdown"
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
                    {console.log('🎨 Rendering ChartVisualization with:', {
                        dataLength: chartData.length,
                        timeRange,
                        drillDownDate,
                        hasClickHandler: !drillDownDate ? 'YES' : 'NO (already at deepest level)'
                    })}
                    <ChartVisualization
                        data={chartData}
                        timeRange={timeRange}
                        onChartClick={!drillDownDate ? handleChartClick : undefined}
                    />
                </>
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
