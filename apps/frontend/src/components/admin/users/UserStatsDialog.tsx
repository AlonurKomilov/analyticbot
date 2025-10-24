/**
 * UserStatsDialog Component
 *
 * Dialog for displaying user statistics.
 * Extracted from UserManagement.tsx god component.
 */

import React from 'react';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import { BaseDialog } from '@/components/common/base';
import type { UserStatistics } from '@/hooks/useUserManagement';
import { spacing } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface UserStatsDialogProps {
    open: boolean;
    statistics: UserStatistics | null;
    loading: boolean;
    onClose: () => void;
}

// =============================================================================
// Component
// =============================================================================

const UserStatsDialog: React.FC<UserStatsDialogProps> = ({
    open,
    statistics,
    loading,
    onClose,
}) => {
    return (
        <BaseDialog
            open={open}
            title="User Statistics"
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
                                Total Users
                            </Typography>
                            <Typography variant="h6">
                                {statistics.total_users.toLocaleString()}
                            </Typography>
                        </Box>
                        <Box>
                            <Typography variant="caption" color="text.secondary">
                                Active Users
                            </Typography>
                            <Typography variant="h6">
                                {statistics.active_users.toLocaleString()}
                            </Typography>
                        </Box>
                        <Box>
                            <Typography variant="caption" color="text.secondary">
                                Premium Users
                            </Typography>
                            <Typography variant="h6">
                                {statistics.premium_users.toLocaleString()}
                            </Typography>
                        </Box>
                        <Box>
                            <Typography variant="caption" color="text.secondary">
                                Logins Today
                            </Typography>
                            <Typography variant="h6">
                                {statistics.total_logins_today.toLocaleString()}
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

export default UserStatsDialog;
