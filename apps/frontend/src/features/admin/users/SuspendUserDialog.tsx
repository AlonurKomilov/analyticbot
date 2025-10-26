/**
 * SuspendUserDialog Component
 *
 * Dialog for suspending a user with reason.
 * Extracted from UserManagement.tsx god component.
 */

import React from 'react';
import { TextField, Alert, Box } from '@mui/material';
import { BaseDialog } from '@shared/components/base';
import type { AdminUserInfo } from '@/services/admin/usersService';
import { spacing } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface SuspendUserDialogProps {
    open: boolean;
    user: AdminUserInfo | null;
    reason: string;
    onReasonChange: (reason: string) => void;
    onConfirm: () => void;
    onCancel: () => void;
    loading: boolean;
}

// =============================================================================
// Component
// =============================================================================

const SuspendUserDialog: React.FC<SuspendUserDialogProps> = ({
    open,
    user,
    reason,
    onReasonChange,
    onConfirm,
    onCancel,
    loading,
}) => {
    return (
        <BaseDialog
            open={open}
            title="Suspend User"
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
                    This will suspend the user "{user?.full_name || user?.email}" and prevent further access.
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

export default SuspendUserDialog;
