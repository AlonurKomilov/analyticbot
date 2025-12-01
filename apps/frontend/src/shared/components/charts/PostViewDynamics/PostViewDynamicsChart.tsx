/**
 * PostViewDynamicsChart - Main orchestrator for post view dynamics analytics
 *
 * Refactored from 619-line monolithic component to modular architecture.
 * 
 * Extracted modules:
 * - types.ts: Type definitions
 * - utils.ts: Data transformation and statistics calculation
 * - usePostDynamics.ts: State management and data fetching hook
 * - TimeRangeControls.tsx: Time range selection UI
 * - MetricsSummary.tsx: Statistics cards
 * - ChartVisualization.tsx: Recharts visualization
 * - ChartErrorBoundary.tsx: Error boundary wrapper
 * - StatusComponents.tsx: Loading and empty states
 */

import React, { useMemo } from 'react';
import {
    Paper,
    Box,
    Typography,
    Alert,
    Button,
    Chip
} from '@mui/material';
import { BarChart as ChartIcon, ArrowBack } from '@mui/icons-material';
import { uiLogger } from '@/utils/logger';

// Import extracted components
import TimeRangeControls from './TimeRangeControls';
import MetricsSummary from './MetricsSummary';
import ChartVisualization from './ChartVisualization';
import ChartErrorBoundary from './ChartErrorBoundary';
import { LoadingState, ChartEmptyState } from './StatusComponents';

// Import hook and utilities
import { usePostDynamics } from './usePostDynamics';
import { transformChartData, calculateSummaryStats } from './utils';

/**
 * PostViewDynamicsChart - Main component
 */
const PostViewDynamicsChart: React.FC = () => {
    // Use extracted hook for all state and handlers
    const {
        data,
        timeRange,
        refreshInterval,
        metricFilter,
        drillDownDate,
        drillDownHour,
        error,
        isLoading,
        handleTimeRangeChange,
        handleRefreshIntervalChange,
        handleMetricFilterChange,
        handleChartClick,
        handleBackClick
    } = usePostDynamics();

    // Memoized chart data transformation
    const chartData = useMemo(() => transformChartData(data), [data]);

    // Memoized summary statistics
    const summaryStats = useMemo(
        () => calculateSummaryStats(chartData, data),
        [chartData, data]
    );

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
        isLoading,
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

                    {/* Drill-down breadcrumb */}
                    {(drillDownDate || drillDownHour) && (
                        <DrillDownBreadcrumb
                            drillDownDate={drillDownDate}
                            drillDownHour={drillDownHour}
                            timeRange={timeRange}
                            onBackClick={handleBackClick}
                        />
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

            {/* Time range controls - only when not in drill-down mode */}
            {!drillDownDate && !drillDownHour && (
                <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                    <TimeRangeControls
                        timeRange={timeRange}
                        refreshInterval={refreshInterval}
                        metricFilter={metricFilter}
                        onTimeRangeChange={handleTimeRangeChange}
                        onRefreshIntervalChange={handleRefreshIntervalChange}
                        onMetricFilterChange={handleMetricFilterChange}
                        hideRefreshControl={true}
                    />
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
            {isLoading && <LoadingState />}

            {/* Chart */}
            {!isLoading && chartData.length > 0 && (
                <ChartVisualization
                    data={chartData}
                    timeRange={timeRange}
                    metricFilter={metricFilter}
                    onChartClick={!drillDownHour ? handleChartClick : undefined}
                />
            )}

            {/* Empty State */}
            {!isLoading && chartData.length === 0 && <ChartEmptyState />}
        </Paper>
    );
};

/**
 * DrillDownBreadcrumb - Extracted breadcrumb component
 */
interface DrillDownBreadcrumbProps {
    drillDownDate: string | null;
    drillDownHour: string | null;
    timeRange: string;
    onBackClick: () => void;
}

const DrillDownBreadcrumb: React.FC<DrillDownBreadcrumbProps> = ({
    drillDownDate,
    drillDownHour,
    timeRange,
    onBackClick
}) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 'auto' }}>
        <Button
            size="small"
            startIcon={<ArrowBack />}
            onClick={onBackClick}
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
);

// Memoize the component to prevent unnecessary re-renders
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
