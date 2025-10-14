import React from 'react';
import {
    Box,
    Typography,
    CircularProgress,
    Chip
} from '@mui/material';
import { BarChart as ChartIcon } from '@mui/icons-material';
import EmptyState from '../../EmptyState';

/**
 * LoadingState - Memoized loading indicator for chart data
 */
export const LoadingState = React.memo(() => (
    <Box variant="emptyState">
        <CircularProgress />
        <Typography variant="withIcon">
            Loading analytics data...
        </Typography>
    </Box>
));

LoadingState.displayName = 'LoadingState';

/**
 * ChartEmptyState - Memoized empty state when no chart data is available
 */
export const ChartEmptyState = React.memo(() => (
    <Box sx={{ height: 300 }}>
        <EmptyState
            message="No post activity data for the selected time range"
            icon={<ChartIcon sx={{ fontSize: 48, color: 'text.secondary' }} />}
        />
    </Box>
));

ChartEmptyState.displayName = 'ChartEmptyState';

/**
 * StatusFooter - Memoized footer showing refresh status and indicators
 *
 * @param {Object} props - Component props
 * @param {boolean} props.autoRefresh - Whether auto-refresh is enabled
 * @param {string} props.refreshInterval - Current refresh interval
 * @param {Object} props.summaryStats - Summary statistics for growth indicator
 */
export const StatusFooter = React.memo(({
    autoRefresh = false,
    refreshInterval = 'disabled',
    summaryStats = null,
    hasChannels = true
}) => (
    <Box variant="statusFooter">
        <Typography variant="caption" color="text.secondary">
            Last updated: {new Date().toLocaleTimeString()}
        </Typography>
        <Box variant="chipGroup">
            {autoRefresh && refreshInterval !== 'disabled' && hasChannels && (
                <Chip
                    size="small"
                    label="🔄 Auto-refresh enabled"
                    color="primary"
                    variant="outlined"
                />
            )}
            {!hasChannels && (
                <Chip
                    size="small"
                    label="⏸️ Auto-refresh disabled"
                    color="default"
                    variant="outlined"
                />
            )}
            {summaryStats && summaryStats.growthRate > 10 && (
                <Chip
                    size="small"
                    label={<><span aria-hidden="true">📈</span> High Growth</>}
                    color="success"
                />
            )}
        </Box>
    </Box>
));

StatusFooter.displayName = 'StatusFooter';
