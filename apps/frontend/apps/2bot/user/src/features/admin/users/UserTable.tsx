/**
 * UserTable Component
 *
 * Displays users in a table format using BaseDataTable.
 * Extracted from UserManagement.tsx god component.
 *
 * Features:
 * - Sortable columns
 * - Pagination
 * - User avatars and status badges
 * - Role chips with colors
 * - Actions menu per row
 */

import React from 'react';
import {  Box, Avatar, Typography, Chip, IconButton, Menu, MenuItem, Divider } from '@mui/material';
import {
    MoreVert as MoreIcon,
    Block as BlockIcon,
    CheckCircle as CheckCircleIcon,
    CheckCircle as ActiveIcon,
    Delete as DeleteIcon,
    History as HistoryIcon,
    Assessment as StatsIcon,
    Email as EmailIcon,
    AdminPanelSettings as AdminIcon,
    Person as PersonIcon,
} from '@mui/icons-material';
import { BaseDataTable, BaseColumn } from '@shared/components/base';
import type { AdminUserInfo } from '@features/admin/services';
import { spacing, colors, typography } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface UserTableProps {
    users: AdminUserInfo[];
    loading: boolean;
    page: number;
    rowsPerPage: number;
    onPageChange: (page: number) => void;
    onRowsPerPageChange: (rowsPerPage: number) => void;
    onSuspendUser: (user: AdminUserInfo) => void;
    onUnsuspendUser: (user: AdminUserInfo) => void;
    onDeleteUser: (user: AdminUserInfo) => void;
    onChangeRole: (user: AdminUserInfo) => void;
    onViewStats: (user: AdminUserInfo) => void;
    onViewAudit: (user: AdminUserInfo) => void;
    onNotifyUser: (user: AdminUserInfo) => void;
}

// =============================================================================
// Helper Functions
// =============================================================================

const getRoleColor = (role: string): 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'success' => {
    const roleColors: Record<string, any> = {
        owner: 'error',
        admin: 'warning',
        moderator: 'primary',
        user: 'success',
        viewer: 'default',
    };
    return roleColors[role.toLowerCase()] || 'default';
};

const getRoleIcon = (role: string) => {
    const icons: Record<string, React.ReactElement> = {
        owner: <AdminIcon fontSize="small" />,
        admin: <AdminIcon fontSize="small" />,
        moderator: <PersonIcon fontSize="small" />,
        user: <PersonIcon fontSize="small" />,
        viewer: <PersonIcon fontSize="small" />,
    };
    return icons[role.toLowerCase()];
};

const formatLastActive = (dateString: string | null): string => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
};

// =============================================================================
// Component
// =============================================================================

const UserTable: React.FC<UserTableProps> = ({
    users,
    loading,
    page,
    rowsPerPage,
    onPageChange,
    onRowsPerPageChange,
    onSuspendUser,
    onUnsuspendUser,
    onDeleteUser,
    onChangeRole,
    onViewStats,
    onViewAudit,
    onNotifyUser,
}) => {
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const [selectedUser, setSelectedUser] = React.useState<AdminUserInfo | null>(null);

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, user: AdminUserInfo) => {
        setAnchorEl(event.currentTarget);
        setSelectedUser(user);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setSelectedUser(null);
    };

    const handleAction = (action: () => void) => {
        action();
        handleMenuClose();
    };

    // Define columns
    const columns: BaseColumn<AdminUserInfo>[] = [
        {
            id: 'user',
            label: 'User',
            sortable: true,
            render: (user) => (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                    <Avatar
                        sx={{
                            width: '32px',
                            height: '32px',
                            fontSize: typography.fontSize.sm,
                        }}
                    >
                        {(user.full_name || user.email)[0].toUpperCase()}
                    </Avatar>
                    <Box>
                        <Typography
                            sx={{
                                fontSize: typography.fontSize.sm,
                                fontWeight: typography.fontWeight.medium,
                                color: colors.text.primary,
                            }}
                        >
                            {user.full_name || user.email}
                        </Typography>
                        <Typography
                            sx={{
                                fontSize: typography.fontSize.xs,
                                color: colors.text.secondary,
                            }}
                        >
                            {user.telegram_username
                                ? `@${user.telegram_username}`
                                : `TG: ${user.telegram_id || 'N/A'}`}
                        </Typography>
                    </Box>
                </Box>
            ),
            getValue: (user) => user.full_name || user.email,
        },
        {
            id: 'role',
            label: 'Role',
            sortable: true,
            render: (user) => (
                <Chip
                    label={user.role}
                    color={getRoleColor(user.role)}
                    size="small"
                    icon={getRoleIcon(user.role)}
                    sx={{ fontSize: typography.fontSize.xs }}
                />
            ),
            getValue: (user) => user.role,
        },
        {
            id: 'status',
            label: 'Status',
            sortable: true,
            render: (user) => (
                <Chip
                    label={user.status === 'suspended' ? 'Suspended' : 'Active'}
                    color={user.status === 'suspended' ? 'error' : 'success'}
                    size="small"
                    icon={user.status === 'suspended' ? <BlockIcon /> : <ActiveIcon />}
                    sx={{ fontSize: typography.fontSize.xs }}
                />
            ),
            getValue: (user) => user.status,
        },
        {
            id: 'channels_count',
            label: 'Channels',
            align: 'right',
            sortable: true,
            render: (user) => (
                <Typography
                    sx={{
                        fontSize: typography.fontSize.sm,
                        fontWeight: typography.fontWeight.medium,
                        color: colors.text.primary,
                    }}
                >
                    {user.total_channels || 0}
                </Typography>
            ),
            getValue: (user) => user.total_channels || 0,
        },
        {
            id: 'last_active',
            label: 'Last Active',
            sortable: true,
            render: (user) => (
                <Typography
                    sx={{
                        fontSize: typography.fontSize.sm,
                        color: colors.text.secondary,
                    }}
                >
                    {formatLastActive(user.last_login)}
                </Typography>
            ),
            getValue: (user) => user.last_login || '',
        },
        {
            id: 'actions',
            label: 'Actions',
            align: 'center',
            render: (user) => (
                <IconButton
                    size="small"
                    onClick={(e) => handleMenuOpen(e, user)}
                    aria-label="User actions"
                >
                    <MoreIcon />
                </IconButton>
            ),
        },
    ];

    return (
        <>
            <BaseDataTable
                columns={columns}
                data={users}
                loading={loading}
                getRowId={(user) => user.user_id}
                pagination={{
                    page,
                    rowsPerPage,
                    totalCount: users.length,
                    onPageChange,
                    onRowsPerPageChange,
                    rowsPerPageOptions: [5, 10, 25, 50],
                }}
                emptyStateTitle="No users found"
                emptyStateDescription="There are no users to display"
                ariaLabel="Users table"
            />

            {/* Actions Menu */}
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
                {selectedUser && (
                    <>
                        <MenuItem onClick={() => handleAction(() => onChangeRole(selectedUser))}>
                            <AdminIcon fontSize="small" sx={{ mr: spacing.sm }} />
                            Change Role
                        </MenuItem>
                        <MenuItem onClick={() => handleAction(() => onNotifyUser(selectedUser))}>
                            <EmailIcon fontSize="small" sx={{ mr: spacing.sm }} />
                            Send Notification
                        </MenuItem>
                        <Divider />
                        <MenuItem onClick={() => handleAction(() => onViewStats(selectedUser))}>
                            <StatsIcon fontSize="small" sx={{ mr: spacing.sm }} />
                            View Statistics
                        </MenuItem>
                        <MenuItem onClick={() => handleAction(() => onViewAudit(selectedUser))}>
                            <HistoryIcon fontSize="small" sx={{ mr: spacing.sm }} />
                            View Audit Log
                        </MenuItem>
                        <Divider />
                        {selectedUser.status === 'suspended' ? (
                            <MenuItem onClick={() => handleAction(() => onUnsuspendUser(selectedUser))}>
                                <CheckCircleIcon fontSize="small" sx={{ mr: spacing.sm, color: colors.success.main }} />
                                Unsuspend User
                            </MenuItem>
                        ) : (
                            <MenuItem onClick={() => handleAction(() => onSuspendUser(selectedUser))}>
                                <BlockIcon fontSize="small" sx={{ mr: spacing.sm, color: colors.warning.main }} />
                                Suspend User
                            </MenuItem>
                        )}
                        <MenuItem onClick={() => handleAction(() => onDeleteUser(selectedUser))}>
                            <DeleteIcon fontSize="small" sx={{ mr: spacing.sm, color: colors.error.main }} />
                            Delete User
                        </MenuItem>
                    </>
                )}
            </Menu>
        </>
    );
};

export default UserTable;
