/**
 * Top Posts Table Configuration for EnhancedDataTable
 * Consolidates table logic from TopPostsTable.jsx into reusable configuration
 */

import React from 'react';
import {
    Box,
    Typography,
    Chip,
    IconButton,
    Menu,
    MenuItem,
    Avatar,
    Link
} from '@mui/material';
import {
    Visibility as ViewsIcon,
    Favorite as LikeIcon,
    Share as ShareIcon,
    Comment as CommentIcon,
    CalendarToday as CalendarIcon,
    MoreVert as MoreIcon,
    TrendingUp as TrendingIcon,
    Image as ImageIcon
} from '@mui/icons-material';
import { formatNumber, formatDate, calculateEngagementRate } from '@utils/formatters';

// Post display components for table cells
export const PostDisplayCell = ({ post }) => (
    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, maxWidth: 350 }}>
        {post.media && post.media.length > 0 && (
            <Avatar
                variant="rounded"
                sx={{ width: 48, height: 48, flexShrink: 0 }}
                src={post.media[0].url}
            >
                <ImageIcon />
            </Avatar>
        )}
        <Box sx={{ minWidth: 0, flex: 1 }}>
            <Typography
                variant="body2"
                sx={{
                    fontWeight: 500,
                    lineHeight: 1.4,
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden'
                }}
            >
                {post.text || 'No text content'}
            </Typography>
            {post.post_url && (
                <Link
                    href={post.post_url}
                    target="_blank"
                    variant="caption"
                    sx={{ color: 'primary.main', textDecoration: 'none' }}
                >
                    View Original
                </Link>
            )}
        </Box>
    </Box>
);

export const MetricCell = ({ value, icon: Icon, color = 'text.primary', format = true }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
        <Icon fontSize="small" sx={{ color }} />
        <Typography variant="body2" sx={{ fontWeight: 500, color }}>
            {format ? formatNumber(value) : value}
        </Typography>
    </Box>
);

export const EngagementCell = ({ post }) => {
    const engagementRate = calculateEngagementRate(post);
    const getEngagementColor = (rate) => {
        if (rate >= 5) return 'success.main';
        if (rate >= 2) return 'warning.main';
        return 'text.secondary';
    };

    return (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
            <TrendingIcon
                fontSize="small"
                sx={{ color: getEngagementColor(engagementRate) }}
            />
            <Typography
                variant="body2"
                sx={{
                    fontWeight: 500,
                    color: getEngagementColor(engagementRate)
                }}
            >
                {engagementRate.toFixed(1)}%
            </Typography>
        </Box>
    );
};

export const StatusCell = ({ post }) => {
    const getStatusColor = (status) => {
        switch (status?.toLowerCase()) {
            case 'published': return 'success';
            case 'scheduled': return 'info';
            case 'draft': return 'warning';
            case 'archived': return 'default';
            default: return 'primary';
        }
    };

    return (
        <Chip
            label={post.status || 'Published'}
            color={getStatusColor(post.status)}
            size="small"
            variant="filled"
        />
    );
};

export const DateCell = ({ date }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'center' }}>
        <CalendarIcon fontSize="small" sx={{ color: 'text.secondary' }} />
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            {formatDate(date)}
        </Typography>
    </Box>
);

export const PostActionsCell = ({ post, onMenuClick, anchorEl, selectedPostId, onMenuClose }) => (
    <>
        <IconButton
            size="small"
            onClick={(event) => onMenuClick(event, post.id)}
            aria-label={`Actions for post ${post.id}`}
        >
            <MoreIcon />
        </IconButton>
        <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl) && selectedPostId === post.id}
            onClose={onMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        >
            <MenuItem onClick={onMenuClose}>View Details</MenuItem>
            <MenuItem onClick={onMenuClose}>Edit Post</MenuItem>
            <MenuItem onClick={onMenuClose}>Duplicate</MenuItem>
            <MenuItem onClick={onMenuClose} sx={{ color: 'error.main' }}>
                Delete
            </MenuItem>
        </Menu>
    </>
);

// Column configuration for EnhancedDataTable
export const createTopPostsColumns = (anchorEl, selectedPostId, onMenuClick, onMenuClose) => [
    {
        id: 'rank',
        label: 'Rank',
        align: 'center',
        minWidth: 80,
        sortable: false,
        renderCell: (value, row, index) => (
            <Typography variant="h6" sx={{ fontWeight: 600, color: 'primary.main' }}>
                #{index + 1}
            </Typography>
        )
    },
    {
        id: 'post',
        label: 'Post',
        minWidth: 300,
        sortable: false,
        renderCell: (value, row) => <PostDisplayCell post={row} />
    },
    {
        id: 'views',
        label: 'Views',
        align: 'center',
        minWidth: 120,
        sortable: true,
        renderCell: (value, row) => (
            <MetricCell
                value={row.views || 0}
                icon={ViewsIcon}
                color="primary.main"
            />
        )
    },
    {
        id: 'likes',
        label: 'Likes',
        align: 'center',
        minWidth: 120,
        sortable: true,
        renderCell: (value, row) => (
            <MetricCell
                value={row.likes || 0}
                icon={LikeIcon}
                color="error.main"
            />
        )
    },
    {
        id: 'shares',
        label: 'Shares',
        align: 'center',
        minWidth: 120,
        sortable: true,
        renderCell: (value, row) => (
            <MetricCell
                value={row.shares || 0}
                icon={ShareIcon}
                color="info.main"
            />
        )
    },
    {
        id: 'comments',
        label: 'Comments',
        align: 'center',
        minWidth: 120,
        sortable: true,
        renderCell: (value, row) => (
            <MetricCell
                value={row.comments || 0}
                icon={CommentIcon}
                color="warning.main"
            />
        )
    },
    {
        id: 'engagement',
        label: 'Engagement %',
        align: 'center',
        minWidth: 140,
        sortable: true,
        renderCell: (value, row) => <EngagementCell post={row} />
    },
    {
        id: 'status',
        label: 'Status',
        align: 'center',
        minWidth: 120,
        sortable: true,
        renderCell: (value, row) => <StatusCell post={row} />
    },
    {
        id: 'date',
        label: 'Published',
        align: 'center',
        minWidth: 140,
        sortable: true,
        renderCell: (value, row) => <DateCell date={row.date || row.created_at} />
    },
    {
        id: 'actions',
        label: 'Actions',
        align: 'center',
        minWidth: 100,
        sortable: false,
        renderCell: (value, row) => (
            <PostActionsCell
                post={row}
                onMenuClick={onMenuClick}
                anchorEl={anchorEl}
                selectedPostId={selectedPostId}
                onMenuClose={onMenuClose}
            />
        )
    }
];

// Table configuration object
export const topPostsTableConfig = {
    title: 'Top Posts Analytics',
    defaultSortField: 'views',
    defaultSortDirection: 'desc',
    defaultPageSize: 10,
    pageSizeOptions: [5, 10, 25, 50],
    enableSearch: true,
    searchFields: ['text', 'status'],
    enableExport: true,
    enableBulkActions: false,
    enableColumnManagement: true,
    stickyHeader: true,
    maxHeight: 600
};
