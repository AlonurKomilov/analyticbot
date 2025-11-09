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

interface TimeRangeControlsProps {
    timeRange?: TimeRange;
    refreshInterval?: RefreshInterval;
    onTimeRangeChange: (event: SelectChangeEvent<string>) => void;
    onRefreshIntervalChange: (event: SelectChangeEvent<string>) => void;
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
 */
const TimeRangeControls: React.FC<TimeRangeControlsProps> = React.memo(({
    timeRange = '24h',
    refreshInterval = '1m',
    onTimeRangeChange,
    onRefreshIntervalChange
}) => {
    return (
        <Box sx={{ display: 'flex', gap: 2 }}>
            {/* Time Range Selector */}
            <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
                <InputLabel id="time-range-label" size="small">
                    Time Range
                </InputLabel>
                <Select
                    labelId="time-range-label"
                    id="time-range-select"
                    value={timeRange}
                    label="Time Range"
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

            {/* Refresh Interval Selector */}
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
        </Box>
    );
});

TimeRangeControls.displayName = 'TimeRangeControls';

export default TimeRangeControls;
