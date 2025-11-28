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
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Visibility,
  Comment,
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
import type { Post, VisibleColumns, PostMediaFlags } from '../types/Post';

/** Content type icon component */
const ContentTypeIcons: React.FC<{ flags?: PostMediaFlags; hasText: boolean }> = ({ flags, hasText }) => {
  if (!flags) return null;

  const iconSize = 14;
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
    contentTypes.push({ icon: <Mic sx={iconStyle} />, label: 'Voice/Video Note', color: '#FF9800' });
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
  if (hasText && (flags.text_length > 0 || contentTypes.length > 0)) {
    // Only show text icon if there's actual text and other media
    if (flags.text_length > 0 && contentTypes.length > 0) {
      contentTypes.push({ icon: <TextFields sx={iconStyle} />, label: 'Text', color: '#795548' });
    }
  }

  if (contentTypes.length === 0) {
    // Text-only post
    if (hasText) {
      return (
        <Box sx={{ display: 'flex', gap: 0.3, mt: 0.5, flexWrap: 'wrap' }}>
          <Tooltip title="Text" arrow placement="top">
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              color: '#795548',
              opacity: 0.8,
            }}>
              <TextFields sx={iconStyle} />
            </Box>
          </Tooltip>
        </Box>
      );
    }
    return null;
  }

  return (
    <Box sx={{ display: 'flex', gap: 0.3, mt: 0.5, flexWrap: 'wrap' }}>
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
                  <Box>
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
                    <ContentTypeIcons 
                      flags={post.media_flags} 
                      hasText={Boolean(post.text && post.text.trim().length > 0)} 
                    />
                  </Box>
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
