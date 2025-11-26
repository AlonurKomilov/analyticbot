/**
 * Post Details Page
 * View detailed information about a specific post
 */

import React from 'react';
import { Container, Typography, Box, Paper, Chip, Button } from '@mui/material';
import { Edit, ArrowBack } from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { ROUTES, buildRoute } from '@config/routes';

const PostDetailsPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  // Mock data - replace with real API call
  const post = {
    id: id || '1',
    title: 'Getting Started Guide',
    content: 'This is a comprehensive guide to getting started with our platform...',
    status: 'published',
    views: 1234,
    date: '2025-10-20',
    author: 'Admin User',
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Button
        startIcon={<ArrowBack />}
        onClick={() => navigate(ROUTES.POSTS)}
        sx={{ mb: 2 }}
      >
        Back to Posts
      </Button>

      <Paper sx={{ p: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
            <Typography variant="h4" component="h1">
              {post.title}
            </Typography>
            <Chip label={post.status} color="success" />
          </Box>

          <Typography variant="body2" color="text.secondary" gutterBottom>
            By {post.author} • {post.date} • {post.views.toLocaleString()} views
          </Typography>
        </Box>

        <Typography variant="body1" sx={{ mb: 4 }}>
          {post.content}
        </Typography>

        <Button
          variant="contained"
          startIcon={<Edit />}
          onClick={() => navigate(buildRoute(ROUTES.EDIT_POST, { id: post.id }))}
        >
          Edit Post
        </Button>
      </Paper>
    </Container>
  );
};

export default PostDetailsPage;
