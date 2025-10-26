/**
 * SuspendChannelDialog Component
 *
 * Dialog for suspending a channel with reason.
 * Follows the same pattern as SuspendUserDialog for consistency.
 */

import React from 'react';
import { TextField, Alert, Box } from '@mui/material';
import { BaseDialog } from '@shared/components/base';
import type { AdminChannelInfo } from '@/services/admin/channelsService';
import { spacing } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface SuspendChannelDialogProps {
    open: boolean;
    channel: AdminChannelInfo | null;
    reason: string;
    onReasonChange: (reason: string) => void;
    onConfirm: () => void;
    onCancel: () => void;
    loading: boolean;
}

// =============================================================================
// Component
// =============================================================================

const SuspendChannelDialog: React.FC<SuspendChannelDialogProps> = ({
    open,
    channel,
    reason,
    onReasonChange,
    onConfirm,
    onCancel,
    loading,
}) => {
    return (
        <BaseDialog
            open={open}
            title="Suspend Channel"
            onClose={onCancel}
            maxWidth="sm"
            actions={{
                cancel: {
                    label: 'Cancel',
                    onClick: onCancel,
                    variant: 'text',
                },
                confirm: {
                    label: 'Suspend',
                    onClick: onConfirm,
                    variant: 'contained',
                    color: 'warning',
                    disabled: !reason.trim() || loading,
                    loading,
                },
            }}
        >
            <Box>
                <Alert severity="warning" sx={{ mb: spacing.md }}>
                    This will suspend the channel "{channel?.title}" and prevent further activity.
                </Alert>
                <TextField
                    fullWidth
                    multiline
                    rows={3}
                    label="Suspension Reason"
                    value={reason}
                    onChange={(e) => onReasonChange(e.target.value)}
                    placeholder="Enter reason for suspension..."
                    required
                    autoFocus
                />
            </Box>
        </BaseDialog>
    );
};

export default SuspendChannelDialog;
