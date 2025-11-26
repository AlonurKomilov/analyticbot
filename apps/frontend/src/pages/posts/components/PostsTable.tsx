/**
 * PostsTable Component
 * Table view for posts with column visibility management
 */

import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  IconButton,
} from '@mui/material';
import { Visibility, Comment, Share, Telegram } from '@mui/icons-material';
import type { Post, VisibleColumns } from '../types/Post';

interface PostsTableProps {
  posts: Post[];
  visibleColumns: VisibleColumns;
  formatDate: (date: string) => string;
  getTelegramLink: (post: Post) => string;
}

export const PostsTable: React.FC<PostsTableProps> = ({
  posts,
  visibleColumns,
  formatDate,
  getTelegramLink,
}) => {
  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            {visibleColumns.channel && <TableCell>Channel</TableCell>}
            {visibleColumns.messageId && <TableCell>Message ID</TableCell>}
            {visibleColumns.content && <TableCell>Content</TableCell>}
            {visibleColumns.views && <TableCell align="right">Views</TableCell>}
            {visibleColumns.forwards && <TableCell align="right">Forwards</TableCell>}
            {visibleColumns.comments && <TableCell align="right">Comments</TableCell>}
            {visibleColumns.reactions && <TableCell align="right">Reactions</TableCell>}
            {visibleColumns.telegram && <TableCell align="center">Telegram</TableCell>}
            {visibleColumns.date && <TableCell>Date</TableCell>}
          </TableRow>
        </TableHead>
        <TableBody>
          {posts.map((post) => (
            <TableRow key={`${post.channel_id}-${post.msg_id}`} hover>
              {visibleColumns.channel && (
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {post.channel_name || `Channel ${post.channel_id}`}
                  </Typography>
                </TableCell>
              )}
              {visibleColumns.messageId && (
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {post.msg_id}
                  </Typography>
                </TableCell>
              )}
              {visibleColumns.content && (
                <TableCell>
                  <Typography
                    variant="body2"
                    sx={{
                      maxWidth: 400,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {post.text || '(Media post)'}
                  </Typography>
                </TableCell>
              )}
              {visibleColumns.views && (
                <TableCell align="right">
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                    <Visibility fontSize="small" color="action" />
                    <Typography variant="body2">{post.metrics?.views || 0}</Typography>
                  </Box>
                </TableCell>
              )}
              {visibleColumns.forwards && (
                <TableCell align="right">
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                    <Share fontSize="small" color="action" />
                    <Typography variant="body2">{post.metrics?.forwards || 0}</Typography>
                  </Box>
                </TableCell>
              )}
              {visibleColumns.comments && (
                <TableCell align="right">
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                    <Comment fontSize="small" color="action" />
                    <Typography variant="body2">{post.metrics?.comments_count || 0}</Typography>
                  </Box>
                </TableCell>
              )}
              {visibleColumns.reactions && (
                <TableCell align="right">
                  <Typography variant="body2">{post.metrics?.reactions_count || 0}</Typography>
                </TableCell>
              )}
              {visibleColumns.telegram && (
                <TableCell align="center">
                  <IconButton
                    component="a"
                    href={getTelegramLink(post)}
                    target="_blank"
                    rel="noopener noreferrer"
                    size="small"
                    color="primary"
                    title="View in Telegram"
                  >
                    <Telegram fontSize="small" />
                  </IconButton>
                </TableCell>
              )}
              {visibleColumns.date && (
                <TableCell>
                  <Typography variant="body2">{formatDate(post.date)}</Typography>
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
