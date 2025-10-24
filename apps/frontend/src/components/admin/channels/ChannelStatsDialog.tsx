/**
 * ChannelStatsDialog Component
 *
 * Dialog for displaying channel statistics.
 * Follows the same pattern as UserStatsDialog for consistency.
 */

import React from 'react';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import { BaseDialog } from '@/components/common/base';
import type { ChannelStatistics } from '@/hooks/useChannelManagement';
import { spacing } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface ChannelStatsDialogProps {
    open: boolean;
    statistics: ChannelStatistics | null;
    loading: boolean;
    onClose: () => void;
}

// =============================================================================
// Component
// =============================================================================

const ChannelStatsDialog: React.FC<ChannelStatsDialogProps> = ({
    open,
    statistics,
    loading,
    onClose,
}) => {
    return (
        <BaseDialog
            open={open}
            title="Channel Statistics"
            onClose={onClose}
            maxWidth="sm"
            actions={{
                cancel: {
                    label: 'Close',
                    onClick: onClose,
                    variant: 'text',
                },
            }}
        >
            <Box>
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: spacing.md }}>
                        <CircularProgress />
                    </Box>
                ) : statistics ? (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
                        <Box>
                            <Typography variant="caption" color="text.secondary">
                                Total Channels
                            </Typography>
                            <Typography variant="h6">
                                {statistics.total_channels.toLocaleString()}
                            </Typography>
                        </Box>
                        <Box>
                            <Typography variant="caption" color="text.secondary">
                                Active Channels
                            </Typography>
                            <Typography variant="h6">
                                {statistics.active_channels.toLocaleString()}
                            </Typography>
                        </Box>
                        <Box>
                            <Typography variant="caption" color="text.secondary">
                                Suspended Channels
                            </Typography>
                            <Typography variant="h6">
                                {statistics.suspended_channels.toLocaleString()}
                            </Typography>
                        </Box>
                        <Box>
                            <Typography variant="caption" color="text.secondary">
                                New This Week
                            </Typography>
                            <Typography variant="h6">
                                {statistics.new_this_week.toLocaleString()}
                            </Typography>
                        </Box>
                    </Box>
                ) : (
                    <Alert severity="info">No statistics available</Alert>
                )}
            </Box>
        </BaseDialog>
    );
};

export default ChannelStatsDialog;
