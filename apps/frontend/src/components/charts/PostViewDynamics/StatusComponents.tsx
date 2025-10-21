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
export const LoadingState: React.FC = React.memo(() => (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>
            Loading analytics data...
        </Typography>
    </Box>
));

LoadingState.displayName = 'LoadingState';

/**
 * ChartEmptyState - Memoized empty state when no chart data is available
 */
export const ChartEmptyState: React.FC = React.memo(() => (
    <Box sx={{ height: 300 }}>
        <EmptyState
            message="No post activity data for the selected time range"
            icon={<ChartIcon sx={{ fontSize: 48, color: 'text.secondary' }} />}
        />
    </Box>
));

ChartEmptyState.displayName = 'ChartEmptyState';

interface SummaryStats {
    growthRate?: number;
}

interface StatusFooterProps {
    autoRefresh?: boolean;
    refreshInterval?: string;
    summaryStats?: SummaryStats | null;
    hasChannels?: boolean;
}

/**
 * StatusFooter - Memoized footer showing refresh status and indicators
 *
 * @param props - Component props
 * @param props.autoRefresh - Whether auto-refresh is enabled
 * @param props.refreshInterval - Current refresh interval
 * @param props.summaryStats - Summary statistics for growth indicator
 * @param props.hasChannels - Whether user has channels configured
 */
export const StatusFooter: React.FC<StatusFooterProps> = React.memo(({
    autoRefresh = false,
    refreshInterval = 'disabled',
    summaryStats = null,
    hasChannels = true
}) => (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
            Last updated: {new Date().toLocaleTimeString()}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
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
            {summaryStats && summaryStats.growthRate !== undefined && summaryStats.growthRate > 10 && (
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
