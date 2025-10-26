/**
 * ChangeRoleDialog Component
 *
 * Dialog for changing a user's role.
 * Extracted from UserManagement.tsx god component.
 */

import React from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import { BaseDialog } from '@shared/components/base';
import type { AdminUserInfo } from '@features/admin/services';
import type { UserRole } from './hooks/useUserManagement';

// =============================================================================
// Types
// =============================================================================

export interface ChangeRoleDialogProps {
    open: boolean;
    user: AdminUserInfo | null;
    newRole: UserRole;
    onRoleChange: (role: UserRole) => void;
    onConfirm: () => void;
    onCancel: () => void;
    loading: boolean;
}

// =============================================================================
// Component
// =============================================================================

const ChangeRoleDialog: React.FC<ChangeRoleDialogProps> = ({
    open,
    newRole,
    onRoleChange,
    onConfirm,
    onCancel,
    loading,
}) => {
    return (
        <BaseDialog
            open={open}
            title="Change User Role"
            onClose={onCancel}
            maxWidth="sm"
            actions={{
                cancel: {
                    label: 'Cancel',
                    onClick: onCancel,
                    variant: 'text',
                },
                confirm: {
                    label: 'Update Role',
                    onClick: onConfirm,
                    variant: 'contained',
                    disabled: loading,
                    loading,
                },
            }}
        >
            <FormControl fullWidth>
                <InputLabel>New Role</InputLabel>
                <Select<UserRole>
                    value={newRole}
                    label="New Role"
                    onChange={(e) => onRoleChange(e.target.value as UserRole)}
                    autoFocus
                >
                    <MenuItem value="viewer">Viewer (Read-only)</MenuItem>
                    <MenuItem value="user">User</MenuItem>
                    <MenuItem value="moderator">Moderator</MenuItem>
                    <MenuItem value="admin">Admin</MenuItem>
                    <MenuItem value="owner">Owner</MenuItem>
                </Select>
            </FormControl>
        </BaseDialog>
    );
};

export default ChangeRoleDialog;
