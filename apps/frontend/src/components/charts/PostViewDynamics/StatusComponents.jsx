import React from 'react';
import {
    Box,
    Typography,
    CircularProgress,
    Chip
} from '@mui/material';
import { BarChart as ChartIcon } from '@mui/icons-material';

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
 * EmptyState - Memoized empty state when no chart data is available
 */
export const EmptyState = React.memo(() => (
    <Box variant="emptyState" sx={{ height: 300, color: 'text.secondary' }}>
        <ChartIcon variant="large" />
        <Typography variant="h6" gutterBottom>
            No data available
        </Typography>
        <Typography variant="body2">
            No post activity data for the selected time range
        </Typography>
    </Box>
));

EmptyState.displayName = 'EmptyState';

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
    summaryStats = null
}) => (
    <Box variant="statusFooter">
        <Typography variant="caption" color="text.secondary">
            So'ngi yangilash: {new Date().toLocaleTimeString()}
        </Typography>
        <Box variant="chipGroup">
            {autoRefresh && refreshInterval !== 'disabled' && (
                <Chip
                    size="small"
                    label="🔄 Avtomatik yangilash"
                    color="primary"
                    variant="outlined"
                />
            )}
            {summaryStats && summaryStats.growthRate > 10 && (
                <Chip
                    size="small"
                    label={<><span aria-hidden="true">📈</span> Yuqori o'sish</>}
                    color="success"
                />
            )}
        </Box>
    </Box>
));

StatusFooter.displayName = 'StatusFooter';
