/**
 * DeleteUserDialog Component
 *
 * Confirmation dialog for deleting a user.
 * Extracted from UserManagement.tsx god component.
 */

import React from 'react';
import { Alert } from '@mui/material';
import { BaseDialog } from '@/components/common/base';
import type { AdminUserInfo } from '@/services/admin/usersService';

// =============================================================================
// Types
// =============================================================================

export interface DeleteUserDialogProps {
    open: boolean;
    user: AdminUserInfo | null;
    onConfirm: () => void;
    onCancel: () => void;
    loading: boolean;
}

// =============================================================================
// Component
// =============================================================================

const DeleteUserDialog: React.FC<DeleteUserDialogProps> = ({
    open,
    user,
    onConfirm,
    onCancel,
    loading,
}) => {
    return (
        <BaseDialog
            open={open}
            title="Delete User"
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
                Are you sure you want to delete user "{user?.full_name || user?.email}"?
                This action cannot be undone.
            </Alert>
        </BaseDialog>
    );
};

export default DeleteUserDialog;
