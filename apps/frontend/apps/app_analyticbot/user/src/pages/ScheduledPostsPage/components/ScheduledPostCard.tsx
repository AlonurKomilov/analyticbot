/**
 * ScheduledPostCard Component
 * Displays a single scheduled post with OLD design (full text, badges, etc.)
 * Based on the superior UX from legacy ScheduledPostsList
 */

import React from 'react';
import {
  ListItem,
  ListItemText,
  IconButton,
  Box,
  Typography,
  Chip
} from '@mui/material';
import { Delete } from '@mui/icons-material';
import { ScheduledPostCardProps } from '../types';

const ScheduledPostCard: React.FC<ScheduledPostCardProps> = ({
  post,
  onDelete,
  isDeleting = false
}) => {
  const handleDelete = () => {
    onDelete(post.id);
  };

  // Format scheduled time - handle both old (scheduled_at, schedule_time) and new (scheduledTime) formats
  const scheduledTime = post.scheduledTime || post.scheduled_at || post.schedule_time;
  const formattedTime = scheduledTime
    ? new Date(scheduledTime).toLocaleString()
    : 'Not scheduled';

  // Get channel name - handle both old (channel_name) and new (channelId) formats
  const channelName = post.channel_name || (post.channelId ? `Channel ${post.channelId}` : `Channel ${post.channel_id || 'Unknown'}`);

  // Get post content - handle both old (text, title) and new (content) formats
  const postContent = post.content || post.text || post.title || '';

  // Get file type badge color
  const getFileTypeBadgeColor = (fileType?: string) => {
    switch (fileType?.toLowerCase()) {
      case 'photo':
        return 'primary';
      case 'video':
        return 'secondary';
      case 'document':
        return 'info';
      case 'audio':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <ListItem
      secondaryAction={
        <IconButton
          edge="end"
          aria-label="delete"
          onClick={handleDelete}
          disabled={isDeleting}
          color="error"
        >
          <Delete />
        </IconButton>
      }
      sx={{
        borderBottom: '1px solid',
        borderColor: 'divider',
        pb: 2,
        mb: 2,
        '&:last-child': {
          borderBottom: 0,
          mb: 0
        }
      }}
    >
      <ListItemText
        primary={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            {/* File type badge (from OLD design) */}
            {post.file_type && (
              <Chip
                label={post.file_type.toUpperCase()}
                size="small"
                color={getFileTypeBadgeColor(post.file_type)}
                sx={{ fontWeight: 600 }}
              />
            )}
            {/* Channel name */}
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              To: {channelName}
            </Typography>
          </Box>
        }
        secondary={
          <>
            {/* Full post text (from OLD design - NOT truncated!) */}
            <Typography
              variant="body1"
              component="span"
              sx={{
                mb: 0.5,
                wordBreak: 'break-word',
                color: 'text.primary',
                display: 'block',
                whiteSpace: 'pre-wrap'
              }}
            >
              {postContent || <em>(No caption)</em>}
            </Typography>
            {/* Scheduled time */}
            <Typography
              variant="caption"
              color="text.secondary"
              component="span"
              sx={{ display: 'block' }}
            >
              Scheduled for: {formattedTime}
            </Typography>
          </>
        }
      />
    </ListItem>
  );
};

export default ScheduledPostCard;
