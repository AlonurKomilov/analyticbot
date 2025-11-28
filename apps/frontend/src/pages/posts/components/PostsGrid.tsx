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
  Tooltip,
} from '@mui/material';
import {
  Visibility,
  Reply,
  Share,
  Telegram,
  Image as ImageIcon,
  Videocam,
  AudioFile,
  Mic,
  InsertDriveFile,
  Gif,
  EmojiEmotions,
  Poll,
  Link as LinkIcon,
  TextFields,
} from '@mui/icons-material';
import type { Post, PostMediaFlags } from '../types/Post';

/** Content type icon component for grid view */
const ContentTypeChips: React.FC<{ flags?: PostMediaFlags; hasText: boolean }> = ({ flags, hasText }) => {
  if (!flags) return null;

  const iconSize = 12;
  const iconStyle = { fontSize: iconSize };

  // Build list of content types present
  const contentTypes: Array<{ icon: React.ReactNode; label: string; color: string }> = [];

  if (flags.has_photo) {
    contentTypes.push({ icon: <ImageIcon sx={iconStyle} />, label: 'Photo', color: '#4CAF50' });
  }
  if (flags.has_video) {
    contentTypes.push({ icon: <Videocam sx={iconStyle} />, label: 'Video', color: '#2196F3' });
  }
  if (flags.has_gif) {
    contentTypes.push({ icon: <Gif sx={iconStyle} />, label: 'GIF', color: '#9C27B0' });
  }
  if (flags.has_voice) {
    contentTypes.push({ icon: <Mic sx={iconStyle} />, label: 'Voice', color: '#FF9800' });
  }
  if (flags.has_audio) {
    contentTypes.push({ icon: <AudioFile sx={iconStyle} />, label: 'Audio', color: '#E91E63' });
  }
  if (flags.has_document) {
    contentTypes.push({ icon: <InsertDriveFile sx={iconStyle} />, label: 'File', color: '#607D8B' });
  }
  if (flags.has_sticker) {
    contentTypes.push({ icon: <EmojiEmotions sx={iconStyle} />, label: 'Sticker', color: '#FFEB3B' });
  }
  if (flags.has_poll) {
    contentTypes.push({ icon: <Poll sx={iconStyle} />, label: 'Poll', color: '#00BCD4' });
  }
  if (flags.has_link) {
    contentTypes.push({ icon: <LinkIcon sx={iconStyle} />, label: 'Link', color: '#3F51B5' });
  }
  if (hasText && flags.text_length > 0 && contentTypes.length > 0) {
    contentTypes.push({ icon: <TextFields sx={iconStyle} />, label: 'Text', color: '#795548' });
  }

  if (contentTypes.length === 0) {
    if (hasText) {
      return (
        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
          <Chip
            icon={<TextFields sx={iconStyle} />}
            label="Text"
            size="small"
            sx={{
              height: 20,
              fontSize: '0.7rem',
              '& .MuiChip-icon': { color: '#795548' },
              '& .MuiChip-label': { px: 0.5 }
            }}
            variant="outlined"
          />
        </Box>
      );
    }
    return null;
  }

  return (
    <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
      {contentTypes.map((ct, index) => (
        <Tooltip key={index} title={ct.label} arrow placement="top">
          <Box sx={{
            display: 'flex',
            alignItems: 'center',
            color: ct.color,
            opacity: 0.9,
          }}>
            {ct.icon}
          </Box>
        </Tooltip>
      ))}
    </Box>
  );
};

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
              <Box sx={{ mb: 2 }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    display: '-webkit-box',
                    overflow: 'hidden',
                    WebkitBoxOrient: 'vertical',
                    WebkitLineClamp: 3,
                    minHeight: 60
                  }}
                >
                  {post.text || '(Media post)'}
                </Typography>
                <ContentTypeChips
                  flags={post.media_flags}
                  hasText={Boolean(post.text && post.text.trim().length > 0)}
                />
              </Box>

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
