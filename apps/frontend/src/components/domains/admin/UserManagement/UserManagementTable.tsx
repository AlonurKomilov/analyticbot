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

interface User {
    id?: string | number;
    username?: string;
    full_name?: string;
    email?: string;
    phone?: string;
    status?: string;
    total_posts?: number;
    total_channels?: number;
    risk_score?: number;
    last_active?: string;
    created_at?: string;
    [key: string]: any;
}

interface BulkAction {
    label: string;
    color: 'warning' | 'success' | 'error';
    action: (selectedUsers: User[]) => void;
}

interface UserManagementTableProps {
    users?: User[];
    loading?: boolean;
    error?: string | null;
    onRefresh?: () => void;
    onUserUpdate?: (user: User) => void;
    onUserDelete?: (user: User) => void;
    onBulkAction?: (action: string, selectedUsers: User[]) => void;
    onUserEdit?: (user: User) => void;
    onUserSuspend?: (user: User, reason: string) => void;
    onUserReactivate?: (user: User) => void;
    onUserMessage?: (user: User) => void;
}

/**
 * UserManagementTable - Optimized and modular user management component
 *
 * Refactored from 597 lines to ~150 lines by:
 * - Extracting display components
 * - Moving utility functions to separate file
 * - Using composition over large inline components
 * - Leveraging existing EnhancedDataTable infrastructure
 */
const UserManagementTable: React.FC<UserManagementTableProps> = ({
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
            Cell: ({ row: user }: { row: User }) => <UserAvatar user={user} />
        },
        {
            id: 'user_info',
            header: 'User Information',
            accessor: (row: User) => row.full_name || row.username,
            minWidth: 250,
            Cell: ({ row: user }: { row: User }) => <UserInfo user={user} />
        },
        {
            id: 'contact',
            header: 'Contact',
            accessor: (row: User) => row.email || row.phone,
            width: 200,
            Cell: ({ row: user }: { row: User }) => <UserContact user={user} />
        },
        {
            id: 'status',
            header: 'Status',
            accessor: (row: User) => row.status,
            align: 'center' as const,
            width: 120,
            Cell: ({ row: user }: { row: User }) => (
                <Chip
                    label={user.status}
                    color={getStatusColor(user.status || '')}
                    size="small"
                    variant="filled"
                />
            )
        },
        {
            id: 'activity',
            header: 'Activity',
            accessor: (row: User) => (row.total_posts || 0) + (row.total_channels || 0),
            align: 'center' as const,
            width: 140,
            Cell: ({ row: user }: { row: User }) => <UserActivity user={user} />
        },
        {
            id: 'risk_score',
            header: 'Risk Score',
            accessor: (row: User) => row.risk_score || 0,
            align: 'center' as const,
            width: 120,
            Cell: ({ row: user }: { row: User }) => <UserRiskScore user={user} />
        },
        {
            id: 'last_active',
            header: 'Last Active',
            accessor: (row: User) => row.last_active,
            align: 'center' as const,
            width: 140,
            Cell: ({ row: user }: { row: User }) => <UserLastActive user={user} />
        },
        {
            id: 'created_at',
            header: 'Member Since',
            accessor: (row: User) => row.created_at,
            align: 'center' as const,
            width: 120,
            Cell: ({ value }: { value?: string }) => (
                <div style={{ fontSize: '0.75rem', textAlign: 'center' }}>
                    {formatDate(value).split(' ')[0]}
                </div>
            )
        },
        {
            id: 'actions',
            header: 'Actions',
            accessor: () => '',
            align: 'center' as const,
            width: 80,
            disableSorting: true,
            Cell: ({ row: user }: { row: User }) => (
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
    const bulkActions: BulkAction[] = useMemo(() => [
        {
            label: 'Suspend Selected',
            color: 'warning',
            action: (selectedUsers: User[]) => onBulkAction?.('suspend', selectedUsers)
        },
        {
            label: 'Activate Selected',
            color: 'success',
            action: (selectedUsers: User[]) => onBulkAction?.('activate', selectedUsers)
        },
        {
            label: 'Delete Selected',
            color: 'error',
            action: (selectedUsers: User[]) => onBulkAction?.('delete', selectedUsers)
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
