/**
 * Posts Page - Unified post management
 * Shows all posts (scheduled and sent) in one place
 */

import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Add, Schedule, CheckCircle, Send } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { ROUTES } from '@config/routes';
import { usePostStore } from '@store';

// Post interface for type safety - compatible with ScheduledPost
interface Post {
  id: string | number;
  status: string;
  schedule_time?: string | Date;
  scheduled_at?: string | Date;
  scheduledTime?: string;
  channel_id?: number;
  channelId?: string | number;
  channel_name?: string;
  post_text?: string;
  message?: string;
  content?: string;
}

const PostsPage: React.FC = () => {
  const { scheduledPosts, isLoading, error, fetchScheduledPosts } = usePostStore();
  const [allPosts, setAllPosts] = useState<Post[]>([]);

  useEffect(() => {
    // Fetch scheduled posts
    fetchScheduledPosts();
  }, [fetchScheduledPosts]);

  useEffect(() => {
    // Combine all posts (currently only scheduled posts available)
    // In future, can merge with analytics data here
    setAllPosts(scheduledPosts);
  }, [scheduledPosts]);

  const getStatusChip = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'pending':
      case 'scheduled':
        return <Chip icon={<Schedule />} label="Scheduled" color="info" size="small" />;
      case 'sent':
      case 'published':
        return <Chip icon={<CheckCircle />} label="Sent" color="success" size="small" />;
      case 'failed':
      case 'error':
        return <Chip label="Failed" color="error" size="small" />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  const formatDate = (date: string | Date) => {
    if (!date) return '-';
    return new Date(date).toLocaleString();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header with Create Button */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            All Posts
          </Typography>
          <Button
            component={Link}
            to={ROUTES.CREATE_POST}
            variant="contained"
            startIcon={<Add />}
            size="large"
          >
            Create Post
          </Button>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
                        {/* Loading State */}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Empty State */}
        {!isLoading && allPosts.length === 0 && (
          <Paper sx={{ p: 8, textAlign: 'center' }}>
            <Send sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" gutterBottom color="text.secondary">
              No posts yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Create your first post to get started
            </Typography>
            <Button
              component={Link}
              to={ROUTES.CREATE_POST}
              variant="contained"
              startIcon={<Add />}
            >
              Create Post
            </Button>
          </Paper>
        )}

        {/* Posts Table */}
        {!isLoading && allPosts.length > 0 && (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Status</TableCell>
                  <TableCell>Scheduled Date</TableCell>
                  <TableCell>Channel</TableCell>
                  <TableCell>Content Preview</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {allPosts.map((post) => (
                  <TableRow key={post.id} hover>
                    <TableCell>{getStatusChip(post.status)}</TableCell>
                    <TableCell>{formatDate(post.schedule_time || post.scheduled_at || post.scheduledTime || '')}</TableCell>
                    <TableCell>{post.channel_name || `Channel ${post.channel_id || post.channelId}`}</TableCell>
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
                        {post.post_text || post.message || post.content || '-'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Box>
    </Container>
  );
};

export default PostsPage;
