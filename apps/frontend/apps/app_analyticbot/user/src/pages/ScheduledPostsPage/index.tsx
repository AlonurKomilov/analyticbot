/**
 * Scheduled Posts Page
 * Modern, modular implementation combining best features from old and new versions
 *
 * Architecture:
 * - useScheduledPosts: Data fetching
 * - usePostActions: Post manipulation
 * - Conditional rendering: LoadingState -> ErrorAlert -> EmptyState -> ScheduledPostsList
 */

import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@config/routes';

// Hooks
import { useScheduledPosts } from './hooks/useScheduledPosts';
import { usePostActions } from './hooks/usePostActions';

// Components
import LoadingState from './components/LoadingState';
import ErrorAlert from './components/ErrorAlert';
import EmptyState from './components/EmptyState';
import ScheduledPostsList from './components/ScheduledPostsList';

const ScheduledPostsPage: React.FC = () => {
  const navigate = useNavigate();

  // Data fetching
  const { posts, isLoading, error, refetch } = useScheduledPosts();

  // Post actions
  const { handleDelete, isDeleting } = usePostActions();

  // Debug logging
  console.log('📊 ScheduledPostsPage State:', {
    postsCount: posts?.length || 0,
    isLoading,
    error,
    posts: posts?.slice(0, 2) // Log first 2 posts for debugging
  });

  // Handler for empty state action
  const handleCreatePost = () => {
    navigate(ROUTES.CREATE_POST);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Scheduled Posts
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your posts scheduled for future publication
        </Typography>
      </Box>

      {/* Conditional Rendering */}
      {isLoading && <LoadingState />}

      {!isLoading && error && (
        <ErrorAlert error={error} onRetry={refetch} />
      )}

      {!isLoading && !error && posts.length === 0 && (
        <EmptyState
          message="No scheduled posts yet"
          actionText="Create Your First Post"
          onAction={handleCreatePost}
        />
      )}

      {!isLoading && !error && posts.length > 0 && (
        <ScheduledPostsList
          posts={posts}
          onDelete={handleDelete}
          isDeleting={isDeleting}
        />
      )}
    </Container>
  );
};

export default ScheduledPostsPage;
