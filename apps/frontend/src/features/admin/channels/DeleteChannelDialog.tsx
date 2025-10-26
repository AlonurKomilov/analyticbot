/**
 * DeleteChannelDialog Component
 *
 * Confirmation dialog for deleting a channel.
 * Follows the same pattern as DeleteUserDialog for consistency.
 */

import React from 'react';
import { Alert } from '@mui/material';
import { BaseDialog } from '@shared/components/base';
import type { AdminChannelInfo } from '@/services/admin/channelsService';

// =============================================================================
// Types
// =============================================================================

export interface DeleteChannelDialogProps {
    open: boolean;
    channel: AdminChannelInfo | null;
    onConfirm: () => void;
    onCancel: () => void;
    loading: boolean;
}

// =============================================================================
// Component
// =============================================================================

const DeleteChannelDialog: React.FC<DeleteChannelDialogProps> = ({
    open,
    channel,
    onConfirm,
    onCancel,
    loading,
}) => {
    return (
        <BaseDialog
            open={open}
            title="Delete Channel"
            onClose={onCancel}
            maxWidth="sm"
            actions={{
                cancel: {
                    label: 'Cancel',
                    onClick: onCancel,
                    variant: 'text',
                },
                confirm: {
                    label: 'Delete',
                    onClick: onConfirm,
                    variant: 'contained',
                    color: 'error',
                    disabled: loading,
                    loading,
                },
            }}
        >
            <Alert severity="error">
                Are you sure you want to delete channel "{channel?.title}"?
                This action cannot be undone.
            </Alert>
        </BaseDialog>
    );
};

export default DeleteChannelDialog;
