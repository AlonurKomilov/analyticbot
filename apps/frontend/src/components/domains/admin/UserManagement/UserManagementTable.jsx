import React, { useMemo } from 'react';
import {
    Chip
} from '@mui/material';
import { EnhancedDataTable } from '../../../common/EnhancedDataTable';
import { 
    UserAvatar, 
    UserInfo, 
    UserContact 
} from './UserDisplayComponents';
import { 
    UserActivity, 
    UserRiskScore, 
    UserLastActive, 
    getStatusColor,
    formatDate 
} from './UserUtils';
import { UserActions } from './UserActions';

/**
 * UserManagementTable - Optimized and modular user management component
 * 
 * Refactored from 597 lines to ~150 lines by:
 * - Extracting display components
 * - Moving utility functions to separate file
 * - Using composition over large inline components
 * - Leveraging existing EnhancedDataTable infrastructure
 */
const UserManagementTable = ({ 
    users = [], 
    loading = false, 
    error = null, 
    onRefresh,
    onUserUpdate,
    onUserDelete,
    onBulkAction,
    onUserEdit,
    onUserSuspend,
    onUserReactivate,
    onUserMessage
}) => {
    // Column configuration - now much cleaner and focused
    const columns = useMemo(() => [
        {
            id: 'avatar',
            header: '',
            accessor: () => '', // Not used for sorting
            width: 60,
            disableSorting: true,
            Cell: ({ row: user }) => <UserAvatar user={user} />
        },
        {
            id: 'user_info',
            header: 'User Information',
            accessor: (row) => row.full_name || row.username,
            minWidth: 250,
            Cell: ({ row: user }) => <UserInfo user={user} />
        },
        {
            id: 'contact',
            header: 'Contact',
            accessor: (row) => row.email || row.phone,
            width: 200,
            Cell: ({ row: user }) => <UserContact user={user} />
        },
        {
            id: 'status',
            header: 'Status',
            accessor: (row) => row.status,
            align: 'center',
            width: 120,
            Cell: ({ row: user }) => (
                <Chip 
                    label={user.status} 
                    color={getStatusColor(user.status)}
                    size="small"
                    variant="filled"
                />
            )
        },
        {
            id: 'activity',
            header: 'Activity',
            accessor: (row) => row.total_posts + row.total_channels,
            align: 'center',
            width: 140,
            Cell: ({ row: user }) => <UserActivity user={user} />
        },
        {
            id: 'risk_score',
            header: 'Risk Score',
            accessor: (row) => row.risk_score || 0,
            align: 'center',
            width: 120,
            Cell: ({ row: user }) => <UserRiskScore user={user} />
        },
        {
            id: 'last_active',
            header: 'Last Active',
            accessor: (row) => row.last_active,
            align: 'center',
            width: 140,
            Cell: ({ row: user }) => <UserLastActive user={user} />
        },
        {
            id: 'created_at',
            header: 'Member Since',
            accessor: (row) => row.created_at,
            align: 'center',
            width: 120,
            Cell: ({ value }) => (
                <div style={{ fontSize: '0.75rem', textAlign: 'center' }}>
                    {formatDate(value).split(' ')[0]}
                </div>
            )
        },
        {
            id: 'actions',
            header: 'Actions',
            accessor: () => '',
            align: 'center',
            width: 80,
            disableSorting: true,
            Cell: ({ row: user }) => (
                <UserActions
                    user={user}
                    onEdit={onUserEdit}
                    onSuspend={onUserSuspend}
                    onReactivate={onUserReactivate}
                    onDelete={onUserDelete}
                    onMessage={onUserMessage}
                />
            )
        }
    ], [onUserEdit, onUserSuspend, onUserReactivate, onUserDelete, onUserMessage]);

    // Bulk actions configuration
    const bulkActions = useMemo(() => [
        {
            label: 'Suspend Selected',
            color: 'warning',
            action: (selectedUsers) => onBulkAction?.('suspend', selectedUsers)
        },
        {
            label: 'Activate Selected',
            color: 'success',
            action: (selectedUsers) => onBulkAction?.('activate', selectedUsers)
        },
        {
            label: 'Delete Selected',
            color: 'error',
            action: (selectedUsers) => onBulkAction?.('delete', selectedUsers)
        }
    ], [onBulkAction]);

    return (
        <EnhancedDataTable
            data={users}
            columns={columns}
            loading={loading}
            error={error}
            title="User Management"
            subtitle={`${users.length} users total`}
            onRefresh={onRefresh}
            bulkActions={bulkActions}
            enableSelection={true}
            enableBulkActions={true}
            enableExport={true}
            exportFilename="user-management-export"
            defaultPageSize={25}
            searchPlaceholder="Search users by name, email, or username..."
        />
    );
};

export default UserManagementTable;