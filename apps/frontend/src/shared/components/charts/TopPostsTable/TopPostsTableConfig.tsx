/**
 * Top Posts Table Configuration for EnhancedDataTable
 * Consolidates table logic from TopPostsTable.jsx into reusable configuration
 */

import React, { MouseEvent } from 'react';
import {
    Box,
    Typography,
    Chip,
    IconButton,
    Menu,
    MenuItem,
    Avatar,
    Link,
    ChipPropsColorOverrides
} from '@mui/material';
import { OverridableStringUnion } from '@mui/types';
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
import { formatNumber, formatDate, calculateEngagementRate } from '@/utils/formatters';

// ============================================================================
// Type Definitions
// ============================================================================

export interface Post {
    id: string | number;
    text?: string;
    media?: Array<{ url: string; type?: string }>;
    post_url?: string;
    views?: number;
    likes?: number;
    shares?: number;
    comments?: number;
    date?: string;
    created_at?: string;
    status?: string;
    [key: string]: any;
}

type ChipColor = OverridableStringUnion<
    'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning',
    ChipPropsColorOverrides
>;

interface MetricCellProps {
    value: number;
    icon: React.ElementType;
    color?: string;
    format?: boolean;
}

interface PostDisplayCellProps {
    post: Post;
}

interface EngagementCellProps {
    post: Post;
}

interface StatusCellProps {
    post: Post;
}

interface DateCellProps {
    date: string;
}

interface PostActionsCellProps {
    post: Post;
    onMenuClick: (event: MouseEvent<HTMLButtonElement>, postId: string | number) => void;
    anchorEl: HTMLElement | null;
    selectedPostId: string | number | null;
    onMenuClose: () => void;
}

interface TableColumn {
    id: string;
    label: string;
    align?: 'left' | 'center' | 'right';
    minWidth?: number;
    sortable?: boolean;
    renderCell: (value: any, row: Post, index?: number) => React.ReactNode;
}

interface TableConfig {
    title: string;
    defaultSortField: string;
    defaultSortDirection: 'asc' | 'desc';
    defaultPageSize: number;
    pageSizeOptions: number[];
    enableSearch: boolean;
    searchFields: string[];
    enableExport: boolean;
    enableBulkActions: boolean;
    enableColumnManagement: boolean;
    stickyHeader: boolean;
    maxHeight: number;
}

// ============================================================================
// Post Display Components for Table Cells
// ============================================================================

export const PostDisplayCell: React.FC<PostDisplayCellProps> = ({ post }) => (
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

export const MetricCell: React.FC<MetricCellProps> = ({
    value,
    icon: Icon,
    color = 'text.primary',
    format = true
}) => (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
        <Icon fontSize="small" sx={{ color }} />
        <Typography variant="body2" sx={{ fontWeight: 500, color }}>
            {format ? formatNumber(value) : value}
        </Typography>
    </Box>
);

export const EngagementCell: React.FC<EngagementCellProps> = ({ post }) => {
    const engagementRate = calculateEngagementRate(post);
    const getEngagementColor = (rate: number): string => {
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

export const StatusCell: React.FC<StatusCellProps> = ({ post }) => {
    const getStatusColor = (status?: string): ChipColor => {
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

export const DateCell: React.FC<DateCellProps> = ({ date }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'center' }}>
        <CalendarIcon fontSize="small" sx={{ color: 'text.secondary' }} />
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            {formatDate(date)}
        </Typography>
    </Box>
);

export const PostActionsCell: React.FC<PostActionsCellProps> = ({
    post,
    onMenuClick,
    anchorEl,
    selectedPostId,
    onMenuClose
}) => (
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

// ============================================================================
// Column Configuration for EnhancedDataTable
// ============================================================================

export const createTopPostsColumns = (
    anchorEl: HTMLElement | null,
    selectedPostId: string | number | null,
    onMenuClick: (event: MouseEvent<HTMLButtonElement>, postId: string | number) => void,
    onMenuClose: () => void
): TableColumn[] => [
    {
        id: 'rank',
        label: 'Rank',
        align: 'center',
        minWidth: 80,
        sortable: false,
        renderCell: (_value: any, _row: Post, index: number = 0) => (
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
        renderCell: (_value: any, row: Post) => <PostDisplayCell post={row} />
    },
    {
        id: 'views',
        label: 'Views',
        align: 'center',
        minWidth: 120,
        sortable: true,
        renderCell: (_value: any, row: Post) => (
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
        renderCell: (_value: any, row: Post) => (
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
        renderCell: (_value: any, row: Post) => (
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
        renderCell: (_value: any, row: Post) => (
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
        renderCell: (_value: any, row: Post) => <EngagementCell post={row} />
    },
    {
        id: 'status',
        label: 'Status',
        align: 'center',
        minWidth: 120,
        sortable: true,
        renderCell: (_value: any, row: Post) => <StatusCell post={row} />
    },
    {
        id: 'date',
        label: 'Published',
        align: 'center',
        minWidth: 140,
        sortable: true,
        renderCell: (_value: any, row: Post) => <DateCell date={row.date || row.created_at || ''} />
    },
    {
        id: 'actions',
        label: 'Actions',
        align: 'center',
        minWidth: 100,
        sortable: false,
        renderCell: (_value: any, row: Post) => (
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

// ============================================================================
// Table Configuration Object
// ============================================================================

export const topPostsTableConfig: TableConfig = {
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
