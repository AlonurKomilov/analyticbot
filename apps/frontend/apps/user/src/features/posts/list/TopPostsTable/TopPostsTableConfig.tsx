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
    EmojiEvents as TrophyIcon
} from '@mui/icons-material';
import { formatNumber, calculateEngagementRate } from '@/utils/formatters';

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
    onMenuClick: (element: HTMLElement, postId: string | number) => void;
}

interface TableColumn {
    id: string;
    header: string;
    align?: 'left' | 'center' | 'right';
    minWidth?: number;
    sortable?: boolean;
    Cell?: React.ComponentType<{ value: any; row: Post; rowIndex?: number }>;  // Use rowIndex like EnhancedDataTable
    accessor?: (row: Post) => any;
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

export const PostDisplayCell: React.FC<PostDisplayCellProps> = ({ post }) => {
    return (
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, maxWidth: 400 }}>
            <Box sx={{ minWidth: 0, flex: 1 }}>
                {/* Post Text */}
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
                        sx={{ color: 'primary.main', textDecoration: 'none', mt: 0.5, display: 'block' }}
                    >
                        View Original
                    </Link>
                )}
            </Box>
        </Box>
    );
};

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
    // Use backend's engagement_rate if available, otherwise calculate
    const engagementRate = post.engagement_rate !== undefined
        ? post.engagement_rate
        : calculateEngagementRate(post);

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

export const DateCell: React.FC<DateCellProps> = ({ date }) => {
    // Format date to a more readable format
    const formatDateReadable = (dateString: string): string => {
        if (!dateString) return 'Unknown';

        try {
            const postDate = new Date(dateString);
            const now = new Date();
            const diffInHours = (now.getTime() - postDate.getTime()) / (1000 * 60 * 60);

            // If less than 24 hours, show relative time
            if (diffInHours < 24) {
                if (diffInHours < 1) {
                    return `${Math.floor(diffInHours * 60)}m ago`;
                }
                return `${Math.floor(diffInHours)}h ago`;
            }

            // If less than 7 days, show days ago
            if (diffInHours < 168) {
                return `${Math.floor(diffInHours / 24)}d ago`;
            }

            // Otherwise show formatted date: "Jan 15, 2025"
            return postDate.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
        } catch (e) {
            return 'Invalid date';
        }
    };

    return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, justifyContent: 'center' }}>
            <CalendarIcon fontSize="small" sx={{ color: 'text.secondary' }} />
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                {formatDateReadable(date)}
            </Typography>
        </Box>
    );
};

export const PostActionsCell: React.FC<PostActionsCellProps> = ({
    post,
    onMenuClick
}) => {
    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        event.stopPropagation();
        // Pass the button element directly, not the event
        onMenuClick(event.currentTarget as any, post.msg_id || post.id);
    };

    return (
        <IconButton
            size="small"
            onClick={handleClick}
            aria-label={`Actions for post ${post.msg_id || post.id}`}
        >
            <MoreIcon />
        </IconButton>
    );
};

// ============================================================================
// Column Configuration for EnhancedDataTable
// ============================================================================

export const createTopPostsColumns = (): TableColumn[] => [
    {
        id: 'rank',
        header: 'Rank',
        align: 'center',
        minWidth: 80,
        sortable: false,
        Cell: ({ rowIndex = 0 }: { value: any; row: Post; rowIndex?: number }) => {
            const rank = rowIndex + 1;

            // Trophy colors for top 3
            const getTrophyColor = (rank: number) => {
                if (rank === 1) return '#FFD700'; // Gold
                if (rank === 2) return '#C0C0C0'; // Silver
                if (rank === 3) return '#CD7F32'; // Bronze
                return null;
            };

            const trophyColor = getTrophyColor(rank);

            return (
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                    {trophyColor && (
                        <TrophyIcon sx={{ color: trophyColor, fontSize: 20 }} />
                    )}
                    <Typography
                        variant="h6"
                        sx={{
                            fontWeight: 600,
                            color: trophyColor || 'primary.main'
                        }}
                    >
                        {rank}
                    </Typography>
                </Box>
            );
        }
    },
    {
        id: 'message_id',
        header: 'Message ID',
        align: 'center',
        minWidth: 120,
        sortable: false,
        Cell: ({ row }: { row: Post }) => (
            <Typography variant="body2" sx={{ color: 'text.secondary', fontFamily: 'monospace' }}>
                {row.msg_id}
            </Typography>
        )
    },
    {
        id: 'post',
        header: 'Post Content',
        minWidth: 350,
        sortable: false,
        Cell: ({ row }: { row: Post }) => <PostDisplayCell post={row} />
    },
    {
        id: 'views',
        header: 'Views',
        align: 'center',
        minWidth: 120,
        sortable: false,
        Cell: ({ row }: { row: Post }) => (
            <MetricCell
                value={row.views || 0}
                icon={ViewsIcon}
                color="primary.main"
            />
        )
    },
    {
        id: 'reactions',
        header: 'Reactions',
        align: 'center',
        minWidth: 120,
        sortable: false,
        Cell: ({ row }: { row: Post }) => (
            <MetricCell
                value={row.reactions_count || row.likes || 0}
                icon={LikeIcon}
                color="error.main"
            />
        )
    },
    {
        id: 'shares',
        header: 'Forwards',
        align: 'center',
        minWidth: 120,
        sortable: false,
        Cell: ({ row }: { row: Post }) => (
            <MetricCell
                value={row.forwards || row.shares || 0}
                icon={ShareIcon}
                color="success.main"
            />
        )
    },
    {
        id: 'comments',
        header: 'Comments',
        align: 'center',
        minWidth: 120,
        sortable: false,
        Cell: ({ row }: { row: Post }) => (
            <MetricCell
                value={row.replies_count || row.comments || 0}
                icon={CommentIcon}
                color="warning.main"
            />
        )
    },
    {
        id: 'engagement',
        header: 'Engagement',
        align: 'center',
        minWidth: 140,
        sortable: false,
        Cell: ({ row }: { row: Post }) => <EngagementCell post={row} />
    },
    {
        id: 'date',
        header: 'Date',
        align: 'center',
        minWidth: 160,
        sortable: false,
        Cell: ({ row }: { row: Post }) => <DateCell date={row.date || row.created_at || ''} />
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
    enableSearch: false,
    searchFields: ['text', 'status'],
    enableExport: false,
    enableBulkActions: false,
    enableColumnManagement: true,
    stickyHeader: true,
    maxHeight: 600
};
