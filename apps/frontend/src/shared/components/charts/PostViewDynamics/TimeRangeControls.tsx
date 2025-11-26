import React from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    SelectChangeEvent
} from '@mui/material';

export type TimeRange = '1h' | '6h' | '24h' | '7d' | '30d' | '90d' | 'all';
export type RefreshInterval = '30s' | '1m' | '5m' | '10m';
export type MetricFilter = 'all' | 'views' | 'reactions' | 'forwards' | 'comments';

interface TimeRangeControlsProps {
    timeRange?: TimeRange;
    refreshInterval?: RefreshInterval;
    metricFilter?: MetricFilter;
    onTimeRangeChange: (event: SelectChangeEvent<string>) => void;
    onRefreshIntervalChange: (event: SelectChangeEvent<string>) => void;
    onMetricFilterChange?: (event: SelectChangeEvent<string>) => void;
    hideRefreshControl?: boolean;  // NEW: Option to hide refresh control
}

/**
 * TimeRangeControls - Memoized time range and refresh interval controls
 *
 * Optimized for multi-user dashboard performance by preventing unnecessary re-renders
 * when parent component state changes.
 *
 * @param props - Component props
 * @param props.timeRange - Current time range value
 * @param props.refreshInterval - Current refresh interval value
 * @param props.onTimeRangeChange - Time range change handler
 * @param props.onRefreshIntervalChange - Refresh interval change handler
 * @param props.hideRefreshControl - If true, hides the refresh interval selector
 */
const TimeRangeControls: React.FC<TimeRangeControlsProps> = React.memo(({
    timeRange = '24h',
    refreshInterval = '1m',
    metricFilter = 'all',
    onTimeRangeChange,
    onRefreshIntervalChange,
    onMetricFilterChange,
    hideRefreshControl = false
}) => {
    return (
        <Box sx={{ display: 'flex', gap: 2 }}>
            {/* Time Period Selector */}
            <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
                <InputLabel id="time-range-label" size="small">
                    Time Period
                </InputLabel>
                <Select
                    labelId="time-range-label"
                    id="time-range-select"
                    value={timeRange}
                    label="Time Period"
                    size="small"
                    onChange={onTimeRangeChange}
                >
                    <MenuItem value="1h">Last Hour</MenuItem>
                    <MenuItem value="6h">Last 6 Hours</MenuItem>
                    <MenuItem value="24h">Last 24 Hours</MenuItem>
                    <MenuItem value="7d">Last 7 Days</MenuItem>
                    <MenuItem value="30d">Last 30 Days</MenuItem>
                    <MenuItem value="90d">Last 90 Days</MenuItem>
                    <MenuItem value="all">All Time</MenuItem>
                </Select>
            </FormControl>

            {/* Metric Filter Selector */}
            {onMetricFilterChange && (
                <FormControl variant="outlined" size="small" sx={{ minWidth: 140 }}>
                    <InputLabel id="metric-filter-label" size="small">
                        Show Metric
                    </InputLabel>
                    <Select
                        labelId="metric-filter-label"
                        id="metric-filter-select"
                        value={metricFilter}
                        label="Show Metric"
                        size="small"
                        onChange={onMetricFilterChange}
                    >
                        <MenuItem value="all">All Metrics</MenuItem>
                        <MenuItem value="views">Views</MenuItem>
                        <MenuItem value="reactions">Reactions</MenuItem>
                        <MenuItem value="forwards">Forwards</MenuItem>
                        <MenuItem value="comments">Comments</MenuItem>
                    </Select>
                </FormControl>
            )}

            {/* Refresh Interval Selector - Hidden when hideRefreshControl=true */}
            {!hideRefreshControl && (
                <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
                    <InputLabel id="refresh-interval-label" size="small">
                        Refresh
                    </InputLabel>
                    <Select
                        labelId="refresh-interval-label"
                        id="refresh-interval-select"
                        value={refreshInterval}
                        label="Refresh"
                        size="small"
                        onChange={onRefreshIntervalChange}
                    >
                        <MenuItem value="30s">30 seconds</MenuItem>
                        <MenuItem value="1m">1 minute</MenuItem>
                        <MenuItem value="5m">5 minutes</MenuItem>
                        <MenuItem value="10m">10 minutes</MenuItem>
                    </Select>
                </FormControl>
            )}
        </Box>
    );
});

TimeRangeControls.displayName = 'TimeRangeControls';

export default TimeRangeControls;
