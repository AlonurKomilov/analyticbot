/**
 * User Management Component (REFACTORED)
 *
 * Admin dashboard for user oversight and management.
 *
 * REFACTORED from 703 lines to ~150 lines by:
 * - Extracting business logic to useUserManagement hook
 * - Extracting UI components (UserTable, UserSearchBar, dialogs)
 * - Using base components (BaseDialog, BaseDataTable)
 *
 * This is now a pure orchestration component.
 */

import React from 'react';
import { Card, CardContent, Typography, Alert } from '@mui/material';
import { useUserManagement } from './hooks/useUserManagement';
import {
    UserTable,
    UserSearchBar,
    SuspendUserDialog,
    DeleteUserDialog,
    ChangeRoleDialog,
    UserStatsDialog,
    UserAuditDialog,
    NotifyUserDialog,
} from './index';
import { spacing, colors, radius } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface UserManagementProps {
    onUserUpdated?: () => void;
}

// =============================================================================
// Component
// =============================================================================

const UserManagement: React.FC<UserManagementProps> = ({ onUserUpdated }) => {
    // Use custom hook for all business logic
    const {
        // State
        users,
        loading,
        error,
        searchTerm,
        page,
        rowsPerPage,

        // Dialog state
        dialogState,
        suspendReason,
        newRole,
        notificationMessage,
        statistics,
        auditLogs,
        dialogLoading,

        // Handlers
        setSearchTerm,
        setPage,
        setRowsPerPage,
        setSuspendReason,
        setNewRole,
        setNotificationMessage,

        // Actions
        loadUsers,
        handleSearch,
        handleSuspendUser,
        handleUnsuspendUser,
        handleUpdateRole,
        handleDeleteUser,
        handleNotifyUser,

        // Dialog actions
        openDialog,
        closeDialog,
    } = useUserManagement(onUserUpdated);

    return (
        <Card
            sx={{
                borderRadius: radius.lg,
                border: `1px solid ${colors.border.default}`,
            }}
            elevation={0}
        >
            <CardContent>
                {/* Header */}
                <Typography
                    variant="h5"
                    sx={{
                        mb: spacing.md,
                        fontWeight: 600,
                        color: colors.text.primary,
                    }}
                >
                    User Management
                </Typography>

                {/* Error Alert */}
                {error && (
                    <Alert severity="error" sx={{ mb: spacing.md }} onClose={() => {}}>
                        {error}
                    </Alert>
                )}

                {/* Search Bar */}
                <UserSearchBar
                    searchTerm={searchTerm}
                    onSearchChange={setSearchTerm}
                    onSearch={handleSearch}
                    onRefresh={loadUsers}
                    loading={loading}
                />

                {/* User Table */}
                <UserTable
                    users={users}
                    loading={loading}
                    page={page}
                    rowsPerPage={rowsPerPage}
                    onPageChange={setPage}
                    onRowsPerPageChange={setRowsPerPage}
                    onSuspendUser={(user) => openDialog('suspend', user)}
                    onUnsuspendUser={handleUnsuspendUser}
                    onDeleteUser={(user) => openDialog('delete', user)}
                    onChangeRole={(user) => openDialog('role', user)}
                    onViewStats={(user) => openDialog('stats', user)}
                    onViewAudit={(user) => openDialog('audit', user)}
                    onNotifyUser={(user) => openDialog('notify', user)}
                />

                {/* Dialogs */}
                <SuspendUserDialog
                    open={dialogState.type === 'suspend'}
                    user={dialogState.user}
                    reason={suspendReason}
                    onReasonChange={setSuspendReason}
                    onConfirm={handleSuspendUser}
                    onCancel={closeDialog}
                    loading={dialogLoading}
                />

                <DeleteUserDialog
                    open={dialogState.type === 'delete'}
                    user={dialogState.user}
                    onConfirm={handleDeleteUser}
                    onCancel={closeDialog}
                    loading={dialogLoading}
                />

                <ChangeRoleDialog
                    open={dialogState.type === 'role'}
                    user={dialogState.user}
                    newRole={newRole}
                    onRoleChange={setNewRole}
                    onConfirm={handleUpdateRole}
                    onCancel={closeDialog}
                    loading={dialogLoading}
                />

                <UserStatsDialog
                    open={dialogState.type === 'stats'}
                    statistics={statistics}
                    loading={dialogLoading}
                    onClose={closeDialog}
                />

                <UserAuditDialog
                    open={dialogState.type === 'audit'}
                    auditLogs={auditLogs}
                    loading={dialogLoading}
                    onClose={closeDialog}
                />

                <NotifyUserDialog
                    open={dialogState.type === 'notify'}
                    user={dialogState.user}
                    message={notificationMessage}
                    onMessageChange={setNotificationMessage}
                    onConfirm={handleNotifyUser}
                    onCancel={closeDialog}
                    loading={dialogLoading}
                />
            </CardContent>
        </Card>
    );
};

export default UserManagement;
