/**
 * ChannelAuditDialog Component
 *
 * Dialog for displaying channel audit logs.
 * Follows the same pattern as UserAuditDialog for consistency.
 */

import React from 'react';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import { BaseDialog } from '@shared/components/base';
import type { ChannelAuditLog } from './hooks/useChannelManagement';
import { spacing, colors } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface ChannelAuditDialogProps {
    open: boolean;
    auditLogs: ChannelAuditLog[];
    loading: boolean;
    onClose: () => void;
}

// =============================================================================
// Component
// =============================================================================

const ChannelAuditDialog: React.FC<ChannelAuditDialogProps> = ({
    open,
    auditLogs,
    loading,
    onClose,
}) => {
    return (
        <BaseDialog
            open={open}
            title="Audit Log"
            onClose={onClose}
            maxWidth="md"
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
                ) : auditLogs.length > 0 ? (
                    <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                        {auditLogs.map((log, index) => (
                            <Box
                                key={index}
                                sx={{
                                    mb: spacing.md,
                                    pb: spacing.md,
                                    borderBottom: `1px solid ${colors.border.default}`,
                                    '&:last-child': {
                                        borderBottom: 'none',
                                        mb: 0,
                                        pb: 0,
                                    },
                                }}
                            >
                                <Typography variant="body2" fontWeight="medium">
                                    {log.action}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                    by {log.admin_email} • {new Date(log.timestamp).toLocaleString()}
                                </Typography>
                                {log.details && Object.keys(log.details).length > 0 && (
                                    <Typography
                                        variant="caption"
                                        display="block"
                                        sx={{ mt: spacing.xs, fontFamily: 'monospace' }}
                                    >
                                        {JSON.stringify(log.details, null, 2)}
                                    </Typography>
                                )}
                            </Box>
                        ))}
                    </Box>
                ) : (
                    <Alert severity="info">No audit logs available</Alert>
                )}
            </Box>
        </BaseDialog>
    );
};

export default ChannelAuditDialog;
