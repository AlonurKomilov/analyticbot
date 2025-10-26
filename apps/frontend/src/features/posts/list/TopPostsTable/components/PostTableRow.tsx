import React from 'react';
import {
    TableCell,
    TableRow,
    Typography,
    Avatar,
    Box,
    Tooltip
} from '@mui/material';
import PostMetricBadge from './PostMetricBadge';
import PostActionMenu from './PostActionMenu';
import { formatNumber, formatDate, calculateEngagementRate, type Post } from '@features/posts/list/TopPostsTable/utils/postTableUtils';

interface PostTableRowProps {
    post: Post;
    index: number;
    anchorEl: HTMLElement | null;
    selectedPostId: string | number | null;
    onMenuClick: (event: React.MouseEvent<HTMLElement>, postId: string | number) => void;
    onMenuClose: () => void;
}

const PostTableRow: React.FC<PostTableRowProps> = ({
    post,
    index,
    anchorEl,
    selectedPostId,
    onMenuClick,
    onMenuClose
}) => {
    return (
        <TableRow
            key={post.id}
            sx={{
                '&:nth-of-type(odd)': { bgcolor: 'action.hover' },
                '&:hover': { bgcolor: 'action.selected' }
            }}
        >
            <TableCell align="center">
                <Typography variant="h6" component="div" sx={{ fontSize: '1rem' }}>
                    #{index + 1}
                </Typography>
            </TableCell>

            <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Avatar
                        src={post.thumbnail}
                        alt={post.title || 'Post thumbnail'}
                        sx={{ width: 40, height: 40 }}
                    >
                        📝
                    </Avatar>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography
                            variant="subtitle2"
                            sx={{
                                fontWeight: 'bold',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                mb: 0.5
                            }}
                        >
                            {post.title || 'Untitled Post'}
                        </Typography>
                        <Typography
                            variant="caption"
                            color="primary.main"
                            sx={{
                                display: 'inline-block',
                                px: 1,
                                py: 0.25,
                                borderRadius: 1,
                                bgcolor: 'primary.light',
                                color: 'primary.contrastText'
                            }}
                        >
                            {post.type || 'General'}
                        </Typography>
                    </Box>
                </Box>
            </TableCell>

            <TableCell align="center">
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {formatNumber(post.views || 0)}
                </Typography>
            </TableCell>

            <TableCell align="center">
                <Typography variant="body2">
                    {formatNumber(post.likes || 0)}
                </Typography>
            </TableCell>

            <TableCell align="center">
                <Typography variant="body2">
                    {formatNumber(post.shares || 0)}
                </Typography>
            </TableCell>

            <TableCell align="center">
                <Typography variant="body2">
                    {formatNumber(post.comments || 0)}
                </Typography>
            </TableCell>

            <TableCell align="center">
                <Typography
                    variant="body2"
                    sx={{
                        fontWeight: 'bold',
                        color: parseFloat(calculateEngagementRate(post)) > 5 ? 'success.main' : 'text.primary'
                    }}
                >
                    {calculateEngagementRate(post)}%
                </Typography>
            </TableCell>

            <TableCell align="center">
                <PostMetricBadge post={post as any} />
            </TableCell>

            <TableCell align="center">
                <Tooltip title={post.created_at ? new Date(post.created_at).toLocaleString() : ''}>
                    <Typography variant="caption" color="text.secondary">
                        {post.created_at ? formatDate(post.created_at) : 'N/A'}
                    </Typography>
                </Tooltip>
            </TableCell>

            <TableCell align="center">
                <PostActionMenu
                    post={post as any}
                    anchorEl={anchorEl}
                    selectedPostId={selectedPostId}
                    onMenuClick={onMenuClick}
                    onMenuClose={onMenuClose}
                />
            </TableCell>
        </TableRow>
    );
};

export default PostTableRow;
