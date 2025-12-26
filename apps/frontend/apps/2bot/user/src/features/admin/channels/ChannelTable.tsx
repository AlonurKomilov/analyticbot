/**
 * ChannelTable Component
 *
 * Displays channels in a table format using BaseDataTable.
 * Follows the same pattern as UserTable for consistency.
 *
 * Features:
 * - Sortable columns
 * - Pagination
 * - Channel avatars and status badges
 * - Actions menu per row
 */

import React from 'react';
import { Box, Avatar, Typography, Chip, IconButton, Menu, MenuItem, Divider } from '@mui/material';
import {
    MoreVert as MoreIcon,
    Block as BlockIcon,
    CheckCircle as CheckCircleIcon,
    CheckCircle as ActiveIcon,
    Delete as DeleteIcon,
    History as HistoryIcon,
    Assessment as StatsIcon,
} from '@mui/icons-material';
import { BaseDataTable, BaseColumn } from '@shared/components/base';
import type { AdminChannelInfo } from '@features/admin/services';
import { spacing, colors, typography } from '@/theme/tokens';

// =============================================================================
// Types
// =============================================================================

export interface ChannelTableProps {
    channels: AdminChannelInfo[];
    loading: boolean;
    page: number;
    rowsPerPage: number;
    onPageChange: (page: number) => void;
    onRowsPerPageChange: (rowsPerPage: number) => void;
    onSuspendChannel: (channel: AdminChannelInfo) => void;
    onUnsuspendChannel: (channel: AdminChannelInfo) => void;
    onDeleteChannel: (channel: AdminChannelInfo) => void;
    onViewStats: (channel: AdminChannelInfo) => void;
    onViewAudit: (channel: AdminChannelInfo) => void;
}

// =============================================================================
// Helper Functions
// =============================================================================

const formatLastActivity = (dateString: string): string => {
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

const ChannelTable: React.FC<ChannelTableProps> = ({
    channels,
    loading,
    page,
    rowsPerPage,
    onPageChange,
    onRowsPerPageChange,
    onSuspendChannel,
    onUnsuspendChannel,
    onDeleteChannel,
    onViewStats,
    onViewAudit,
}) => {
    const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
    const [selectedChannel, setSelectedChannel] = React.useState<AdminChannelInfo | null>(null);

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, channel: AdminChannelInfo) => {
        setAnchorEl(event.currentTarget);
        setSelectedChannel(channel);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setSelectedChannel(null);
    };

    const handleAction = (action: () => void) => {
        action();
        handleMenuClose();
    };

    // Define columns
    const columns: BaseColumn<AdminChannelInfo>[] = [
        {
            id: 'channel',
            label: 'Channel',
            sortable: true,
            render: (channel) => (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                    <Avatar
                        sx={{
                            width: '32px',
                            height: '32px',
                            fontSize: typography.fontSize.sm,
                        }}
                    >
                        {channel.title[0].toUpperCase()}
                    </Avatar>
                    <Box>
                        <Typography
                            sx={{
                                fontSize: typography.fontSize.sm,
                                fontWeight: typography.fontWeight.medium,
                                color: colors.text.primary,
                            }}
                        >
                            {channel.title}
                        </Typography>
                        <Typography
                            sx={{
                                fontSize: typography.fontSize.xs,
                                color: colors.text.secondary,
                            }}
                        >
                            @{channel.username}
                        </Typography>
                    </Box>
                </Box>
            ),
            getValue: (channel) => channel.title,
        },
        {
            id: 'status',
            label: 'Status',
            sortable: true,
            render: (channel) => {
                if (channel.status === 'suspended') {
                    return (
                        <Chip
                            label="Suspended"
                            color="error"
                            size="small"
                            icon={<BlockIcon />}
                            sx={{ fontSize: typography.fontSize.xs }}
                        />
                    );
                } else if (channel.status === 'deleted') {
                    return (
                        <Chip
                            label="Deleted"
                            color="default"
                            size="small"
                            icon={<DeleteIcon />}
                            sx={{ fontSize: typography.fontSize.xs }}
                        />
                    );
                } else {
                    return (
                        <Chip
                            label="Active"
                            color="success"
                            size="small"
                            icon={<ActiveIcon />}
                            sx={{ fontSize: typography.fontSize.xs }}
                        />
                    );
                }
            },
            getValue: (channel) => channel.status,
        },
        {
            id: 'subscribers',
            label: 'Subscribers',
            align: 'right',
            sortable: true,
            render: (channel) => (
                <Typography
                    sx={{
                        fontSize: typography.fontSize.sm,
                        fontWeight: typography.fontWeight.medium,
                        color: colors.text.primary,
                    }}
                >
                    {channel.total_views?.toLocaleString() || 'N/A'}
                </Typography>
            ),
            getValue: (channel) => channel.total_views || 0,
        },
        {
            id: 'posts',
            label: 'Posts',
            align: 'right',
            sortable: true,
            render: (channel) => (
                <Typography
                    sx={{
                        fontSize: typography.fontSize.sm,
                        fontWeight: typography.fontWeight.medium,
                        color: colors.text.primary,
                    }}
                >
                    {channel.total_posts?.toLocaleString() || 'N/A'}
                </Typography>
            ),
            getValue: (channel) => channel.total_posts || 0,
        },
        {
            id: 'last_activity',
            label: 'Last Activity',
            sortable: true,
            render: (channel) => (
                <Typography
                    sx={{
                        fontSize: typography.fontSize.sm,
                        color: colors.text.secondary,
                    }}
                >
                    {formatLastActivity(channel.last_activity)}
                </Typography>
            ),
            getValue: (channel) => channel.last_activity || '',
        },
        {
            id: 'actions',
            label: 'Actions',
            align: 'center',
            render: (channel) => (
                <IconButton
                    size="small"
                    onClick={(e) => handleMenuOpen(e, channel)}
                    aria-label="Channel actions"
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
                data={channels}
                loading={loading}
                getRowId={(channel) => channel.channel_id}
                pagination={{
                    page,
                    rowsPerPage,
                    totalCount: channels.length,
                    onPageChange,
                    onRowsPerPageChange,
                    rowsPerPageOptions: [5, 10, 25, 50],
                }}
                emptyStateTitle="No channels found"
                emptyStateDescription="There are no channels to display"
                ariaLabel="Channels table"
            />

            {/* Actions Menu */}
            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
                {selectedChannel && (
                    <>
                        <MenuItem onClick={() => handleAction(() => onViewStats(selectedChannel))}>
                            <StatsIcon fontSize="small" sx={{ mr: spacing.sm }} />
                            View Statistics
                        </MenuItem>
                        <MenuItem onClick={() => handleAction(() => onViewAudit(selectedChannel))}>
                            <HistoryIcon fontSize="small" sx={{ mr: spacing.sm }} />
                            View Audit Log
                        </MenuItem>
                        <Divider />
                        {selectedChannel.status === 'suspended' ? (
                            <MenuItem onClick={() => handleAction(() => onUnsuspendChannel(selectedChannel))}>
                                <CheckCircleIcon fontSize="small" sx={{ mr: spacing.sm, color: colors.success.main }} />
                                Unsuspend Channel
                            </MenuItem>
                        ) : (
                            <MenuItem onClick={() => handleAction(() => onSuspendChannel(selectedChannel))}>
                                <BlockIcon fontSize="small" sx={{ mr: spacing.sm, color: colors.warning.main }} />
                                Suspend Channel
                            </MenuItem>
                        )}
                        <MenuItem onClick={() => handleAction(() => onDeleteChannel(selectedChannel))}>
                            <DeleteIcon fontSize="small" sx={{ mr: spacing.sm, color: colors.error.main }} />
                            Delete Channel
                        </MenuItem>
                    </>
                )}
            </Menu>
        </>
    );
};

export default ChannelTable;
