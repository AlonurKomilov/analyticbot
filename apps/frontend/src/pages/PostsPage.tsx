/**
 * Posts Page
 * List and manage all posts
 */

import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  IconButton,
} from '@mui/material';
import { Add, Edit, Delete, Visibility } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ROUTES, buildRoute } from '@config/routes';

// Mock data - replace with real API call
const mockPosts = [
  { id: 1, title: 'Getting Started Guide', status: 'published', views: 1234, date: '2025-10-20' },
  { id: 2, title: 'Feature Announcement', status: 'draft', views: 0, date: '2025-10-22' },
  { id: 3, title: 'Weekly Update', status: 'scheduled', views: 567, date: '2025-10-25' },
];

const PostsPage: React.FC = () => {
  const navigate = useNavigate();
  const [posts] = useState(mockPosts);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'success';
      case 'draft':
        return 'default';
      case 'scheduled':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Posts
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Create and manage your content
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => navigate(ROUTES.CREATE_POST)}
        >
          Create Post
        </Button>
      </Box>

      <Grid container spacing={3}>
        {posts.map((post) => (
          <Grid item xs={12} md={6} key={post.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
                  <Typography variant="h6" component="h2">
                    {post.title}
                  </Typography>
                  <Chip
                    label={post.status}
                    color={getStatusColor(post.status)}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Published: {post.date}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Views: {post.views.toLocaleString()}
                </Typography>
              </CardContent>
              <CardActions>
                <IconButton
                  size="small"
                  onClick={() => navigate(buildRoute(ROUTES.POST_DETAILS, { id: post.id }))}
                  aria-label="view post"
                >
                  <Visibility />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={() => navigate(buildRoute(ROUTES.EDIT_POST, { id: post.id }))}
                  aria-label="edit post"
                >
                  <Edit />
                </IconButton>
                <IconButton size="small" color="error" aria-label="delete post">
                  <Delete />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default PostsPage;
