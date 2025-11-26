/**
 * PostsGrid Component
 * Card-based grid view for posts
 */

import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  Button,
} from '@mui/material';
import { Visibility, Reply, Share, Telegram } from '@mui/icons-material';
import type { Post } from '../types/Post';

interface PostsGridProps {
  posts: Post[];
  formatDate: (date: string) => string;
  getTelegramLink: (post: Post) => string;
}

export const PostsGrid: React.FC<PostsGridProps> = ({
  posts,
  formatDate,
  getTelegramLink,
}) => {
  return (
    <Grid container spacing={2}>
      {posts.map((post) => (
        <Grid item xs={12} sm={6} md={4} key={`${post.channel_id}-${post.msg_id}`}>
          <Card>
            <CardContent>
              {/* Channel & Message ID */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                <Typography variant="subtitle2" fontWeight="bold" color="primary">
                  {post.channel_name || `Channel ${post.channel_id}`}
                </Typography>
                <Chip label={`#${post.msg_id}`} size="small" />
              </Box>

              {/* Content */}
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  mb: 2,
                  display: '-webkit-box',
                  overflow: 'hidden',
                  WebkitBoxOrient: 'vertical',
                  WebkitLineClamp: 3,
                  minHeight: 60
                }}
              >
                {post.text || '(Media post)'}
              </Typography>

              {/* Metrics */}
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Visibility fontSize="small" color="action" />
                  <Typography variant="body2">{post.metrics?.views || 0}</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Share fontSize="small" color="action" />
                  <Typography variant="body2">{post.metrics?.forwards || 0}</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Reply fontSize="small" color="action" />
                  <Typography variant="body2">{post.metrics?.comments_count || 0}</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Typography variant="body2">❤️ {post.metrics?.reactions_count || 0}</Typography>
                </Box>
              </Box>

              {/* Date */}
              <Typography variant="caption" color="text.secondary">
                {formatDate(post.date)}
              </Typography>
            </CardContent>
            <CardActions>
              <Button
                component="a"
                href={getTelegramLink(post)}
                target="_blank"
                rel="noopener noreferrer"
                size="small"
                startIcon={<Telegram />}
                fullWidth
              >
                View in Telegram
              </Button>
            </CardActions>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};
