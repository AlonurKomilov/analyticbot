/**
 * NotifyUserDialog Component
 *
 * Dialog for sending notifications to a user.
 * Extracted from UserManagement.tsx god component.
 */

import React from 'react';
import { TextField } from '@mui/material';
import { BaseDialog } from '@shared/components/base';
import type { AdminUserInfo } from '@features/admin/services';

// =============================================================================
// Types
// =============================================================================

export interface NotifyUserDialogProps {
    open: boolean;
    user: AdminUserInfo | null;
    message: string;
    onMessageChange: (message: string) => void;
    onConfirm: () => void;
    onCancel: () => void;
    loading: boolean;
}

// =============================================================================
// Component
// =============================================================================

const NotifyUserDialog: React.FC<NotifyUserDialogProps> = ({
    open,
    user,
    message,
    onMessageChange,
    onConfirm,
    onCancel,
    loading,
}) => {
    return (
        <BaseDialog
            open={open}
            title="Send Notification"
            onClose={onCancel}
            maxWidth="sm"
            actions={{
                cancel: {
                    label: 'Cancel',
                    onClick: onCancel,
                    variant: 'text',
                },
                confirm: {
                    label: 'Send',
                    onClick: onConfirm,
                    variant: 'contained',
                    disabled: !message.trim() || loading,
                    loading,
                },
            }}
        >
            <TextField
                fullWidth
                multiline
                rows={4}
                label="Notification Message"
                value={message}
                onChange={(e) => onMessageChange(e.target.value)}
                placeholder={`Enter notification message for ${user?.full_name || user?.email}...`}
                required
                autoFocus
            />
        </BaseDialog>
    );
};

export default NotifyUserDialog;
