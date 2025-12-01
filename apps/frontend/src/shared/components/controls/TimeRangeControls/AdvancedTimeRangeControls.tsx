/**
 * AdvancedTimeRangeControls - Feature-rich time range controls
 * 
 * Used for analytics dashboards requiring:
 * - Time period selection
 * - Refresh interval control
 * - Metric filtering
 * 
 * @example
 * ```tsx
 * <AdvancedTimeRangeControls
 *   timeRange="24h"
 *   onTimeRangeChange={(range) => setTimeRange(range)}
 *   hideRefreshControl
 * />
 * ```
 */

import React from 'react';
import {
    Box,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    SelectChangeEvent
} from '@mui/material';
import type { AdvancedTimeRangeControlsProps, TimeRange, RefreshInterval, MetricFilter } from './types';

const AdvancedTimeRangeControls: React.FC<AdvancedTimeRangeControlsProps> = React.memo(({
    timeRange = '24h',
    refreshInterval = '1m',
    metricFilter = 'all',
    onTimeRangeChange,
    onRefreshIntervalChange,
    onMetricFilterChange,
    hideRefreshControl = false,
    hideMetricFilter = false
}) => {
    const handleTimeRangeChange = (e: SelectChangeEvent<string>) => {
        onTimeRangeChange(e.target.value as TimeRange);
    };

    const handleRefreshIntervalChange = (e: SelectChangeEvent<string>) => {
        onRefreshIntervalChange?.(e.target.value as RefreshInterval);
    };

    const handleMetricFilterChange = (e: SelectChangeEvent<string>) => {
        onMetricFilterChange?.(e.target.value as MetricFilter);
    };

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
                    onChange={handleTimeRangeChange}
                >
                    <MenuItem value="1h">Last Hour</MenuItem>
                    <MenuItem value="6h">Last 6 Hours</MenuItem>
                    <MenuItem value="24h">Last 24 Hours</MenuItem>
                    <MenuItem value="7d">Last 7 Days</MenuItem>
                    <MenuItem value="14d">Last 14 Days</MenuItem>
                    <MenuItem value="30d">Last 30 Days</MenuItem>
                    <MenuItem value="90d">Last 90 Days</MenuItem>
                    <MenuItem value="all">All Time</MenuItem>
                </Select>
            </FormControl>

            {/* Metric Filter Selector */}
            {!hideMetricFilter && onMetricFilterChange && (
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
                        onChange={handleMetricFilterChange}
                    >
                        <MenuItem value="all">All Metrics</MenuItem>
                        <MenuItem value="views">Views</MenuItem>
                        <MenuItem value="reactions">Reactions</MenuItem>
                        <MenuItem value="forwards">Forwards</MenuItem>
                        <MenuItem value="comments">Comments</MenuItem>
                    </Select>
                </FormControl>
            )}

            {/* Refresh Interval Selector */}
            {!hideRefreshControl && onRefreshIntervalChange && (
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
                        onChange={handleRefreshIntervalChange}
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

AdvancedTimeRangeControls.displayName = 'AdvancedTimeRangeControls';

export default AdvancedTimeRangeControls;
