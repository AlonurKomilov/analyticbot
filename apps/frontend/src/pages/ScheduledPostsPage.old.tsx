/**
 * Scheduled Posts Page
 * View and manage scheduled posts
 */

import React, { useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Edit, Delete, Visibility } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { buildRoute, ROUTES } from '@config/routes';
import { usePostStore } from '@/store';

const ScheduledPostsPage: React.FC = () => {
  const navigate = useNavigate();
  const { scheduledPosts, isLoading, error, fetchScheduledPosts, cancelScheduledPost } = usePostStore();

  // Fetch scheduled posts on component mount
  useEffect(() => {
    fetchScheduledPosts();
  }, [fetchScheduledPosts]);

  const handleDelete = async (postId: string) => {
    if (window.confirm('Are you sure you want to cancel this scheduled post?')) {
      try {
        await cancelScheduledPost(postId);
      } catch (error) {
        console.error('Failed to cancel post:', error);
      }
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Scheduled Posts
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage posts scheduled for future publication
        </Typography>
      </Box>

      {/* Loading State */}
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Empty State */}
      {!isLoading && !error && scheduledPosts.length === 0 && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Scheduled Posts
          </Typography>
          <Typography variant="body2" color="text.secondary">
            You don't have any posts scheduled yet. Create a post and schedule it for later!
          </Typography>
        </Paper>
      )}

      {/* Posts Table */}
      {!isLoading && scheduledPosts.length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Channel</TableCell>
                <TableCell>Scheduled For</TableCell>
                <TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {scheduledPosts.map((post) => (
                <TableRow key={post.id}>
                  <TableCell>{post.title || post.text?.substring(0, 50) || 'Untitled'}</TableCell>
                  <TableCell>{post.channel_name || `Channel ${post.channel_id}`}</TableCell>
                  <TableCell>
                    {new Date(post.scheduled_at).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={post.status || 'Scheduled'}
                      color={post.status === 'published' ? 'success' : 'info'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={() => navigate(buildRoute(ROUTES.POST_DETAILS, { id: post.id }))}
                      title="View details"
                    >
                      <Visibility />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => navigate(buildRoute(ROUTES.EDIT_POST, { id: post.id }))}
                      title="Edit post"
                    >
                      <Edit />
                    </IconButton>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(post.id.toString())}
                      title="Cancel scheduled post"
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Container>
  );
};

export default ScheduledPostsPage;
