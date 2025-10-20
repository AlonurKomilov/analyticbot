import React from 'react';
import {
    Box,
    Avatar,
    Chip,
    Typography,
    Tooltip
} from '@mui/material';
import {
    TrendingUp as TrendingUpIcon,
    Favorite as LikeIcon,
    Share as ShareIcon,
    Comment as CommentIcon,
    Visibility as ViewsIcon,
    CalendarToday as CalendarIcon
} from '@mui/icons-material';
import { StatusChip } from '@components/common/IconSystem';
import { formatNumber, formatDate, calculateEngagementRate, getPerformanceScore, getPerformanceLevel } from './PostsUtils';

interface PostRow {
    id?: string | number;
    title?: string;
    content?: string;
    thumbnail?: string;
    type?: string;
    views?: number;
    likes?: number;
    shares?: number;
    comments?: number;
    date?: string;
    status?: 'trending' | 'published';
}

interface PostDisplayCellProps {
    row: PostRow;
}

interface MetricCellProps {
    value: number;
}

interface DateCellProps {
    value: string;
}

/**
 * Post title and content display with thumbnail
 */
export const PostDisplayCell: React.FC<PostDisplayCellProps> = ({ row }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {row.thumbnail && (
            <Avatar
                src={row.thumbnail}
                variant="rounded"
                sx={{ width: 48, height: 48 }}
            />
        )}
        <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
                variant="body2"
                sx={{
                    fontWeight: 'medium',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                }}
            >
                {row.title || row.content || 'Post content'}
            </Typography>
            {row.type && (
                <Chip
                    size="small"
                    label={row.type}
                    variant="outlined"
                    sx={{ mt: 0.5, height: 20, fontSize: '0.7rem' }}
                />
            )}
        </Box>
    </Box>
);

/**
 * Views metric display with icon
 */
export const ViewsCell: React.FC<MetricCellProps> = ({ value }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
        <ViewsIcon fontSize="small" color="primary" />
        <Typography variant="body2" fontWeight="medium">
            {formatNumber(value)}
        </Typography>
    </Box>
);

/**
 * Likes metric display with icon
 */
export const LikesCell: React.FC<MetricCellProps> = ({ value }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
        <LikeIcon fontSize="small" color="error" />
        <Typography variant="body2" fontWeight="medium">
            {formatNumber(value)}
        </Typography>
    </Box>
);

/**
 * Shares metric display with icon
 */
export const SharesCell: React.FC<MetricCellProps> = ({ value }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
        <ShareIcon fontSize="small" color="success" />
        <Typography variant="body2" fontWeight="medium">
            {formatNumber(value)}
        </Typography>
    </Box>
);

/**
 * Comments metric display with icon
 */
export const CommentsCell: React.FC<MetricCellProps> = ({ value }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
        <CommentIcon fontSize="small" color="info" />
        <Typography variant="body2" fontWeight="medium">
            {formatNumber(value)}
        </Typography>
    </Box>
);

/**
 * Engagement rate display with progress indicator
 */
export const EngagementCell: React.FC<PostDisplayCellProps> = ({ row }) => {
    const rate = calculateEngagementRate(row);
    const rateNum = parseFloat(rate);

    return (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
            <Typography variant="body2" fontWeight="medium">
                {rate}%
            </Typography>
            <Box
                sx={{
                    width: 40,
                    height: 4,
                    backgroundColor: 'grey.300',
                    borderRadius: 2,
                    overflow: 'hidden'
                }}
            >
                <Box
                    sx={{
                        width: `${Math.min(rateNum * 2, 100)}%`,
                        height: '100%',
                        backgroundColor: rateNum > 5 ? 'success.main' : rateNum > 2 ? 'warning.main' : 'error.main',
                        borderRadius: 2
                    }}
                />
            </Box>
        </Box>
    );
};

/**
 * Performance score with color-coded chip
 */
export const PerformanceCell: React.FC<PostDisplayCellProps> = ({ row }) => {
    const score = getPerformanceScore(row);
    const { level, color } = getPerformanceLevel(score);

    return (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Tooltip title={`Performance Score: ${score}/100`}>
                <StatusChip
                    label={level}
                    status={color}
                    size="small"
                />
            </Tooltip>
        </Box>
    );
};

/**
 * Date display with relative time
 */
export const DateCell: React.FC<DateCellProps> = ({ value }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
        <CalendarIcon fontSize="small" color="action" />
        <Typography variant="body2" color="text.secondary">
            {formatDate(value)}
        </Typography>
    </Box>
);

/**
 * Status indicator with trending icon
 */
export const StatusCell: React.FC<PostDisplayCellProps> = ({ row }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
        {row.status === 'trending' && (
            <Tooltip title="Trending Post">
                <TrendingUpIcon fontSize="small" color="warning" />
            </Tooltip>
        )}
        <StatusChip
            label={row.status === 'trending' ? 'Trending' : 'Published'}
            status={row.status === 'trending' ? 'warning' : 'success'}
            size="small"
        />
    </Box>
);
