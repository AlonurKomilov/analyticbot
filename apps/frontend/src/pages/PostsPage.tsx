/**
 * Posts Page
 * Note: This page is currently not connected to a backend endpoint.
 * The system tracks posts in two places:
 * 1. Scheduled Posts (future posts to be sent)
 * 2. Analytics (historical data for posts sent through the bot)
 * 
 * Use the "Scheduled Posts" page to manage upcoming posts.
 */

import React from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  Alert,
} from '@mui/material';
import { Schedule, Analytics, Info } from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { ROUTES } from '@config/routes';

const PostsPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Typography variant="h4" component="h1" gutterBottom>
          Posts
        </Typography>

        {/* Info Alert */}
        <Alert severity="info" icon={<Info />} sx={{ mb: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            <strong>Post Management Architecture</strong>
          </Typography>
          <Typography variant="body2" component="div">
            The system tracks posts in two locations:
            <ul style={{ marginTop: 8, marginBottom: 0 }}>
              <li><strong>Scheduled Posts:</strong> Posts waiting to be sent (future)</li>
              <li><strong>Analytics:</strong> Performance data for posts already sent through the bot</li>
            </ul>
          </Typography>
        </Alert>

        {/* Navigation Cards */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
          {/* Scheduled Posts Card */}
          <Paper
            elevation={2}
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
              '&:hover': {
                elevation: 4,
                transform: 'translateY(-2px)',
                transition: 'all 0.2s',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Schedule color="primary" fontSize="large" />
              <Typography variant="h6">Scheduled Posts</Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              View and manage posts that are scheduled to be published in the future.
              Create, edit, or cancel upcoming posts.
            </Typography>
            <Button
              component={Link}
              to={ROUTES.SCHEDULED_POSTS}
              variant="contained"
              sx={{ mt: 'auto' }}
            >
              Go to Scheduled Posts
            </Button>
          </Paper>

          {/* Analytics Card */}
          <Paper
            elevation={2}
            sx={{
              p: 3,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
              '&:hover': {
                elevation: 4,
                transform: 'translateY(-2px)',
                transition: 'all 0.2s',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Analytics color="primary" fontSize="large" />
              <Typography variant="h6">Post Analytics</Typography>
            </Box>
                        <Typography variant="body2" color="text.secondary">
              View historical data and insights for posts that have been sent through your bot.
              Track engagement, views, and performance metrics.
            </Typography>
            <Button
              component={Link}
              to={ROUTES.ANALYTICS}
              variant="contained"
              sx={{ mt: 'auto' }}
            >
              Go to Analytics
            </Button>
          </Paper>
        </Box>

        {/* Technical Note */}
        <Alert severity="warning" sx={{ mt: 3 }}>
          <Typography variant="body2">
            <strong>Note:</strong> General post listing is not available because posts don't exist
            as standalone entities. They're either scheduled (future) or tracked in analytics (past).
            Analytics only show posts that were sent through the bot system.
          </Typography>
        </Alert>
      </Box>
    </Container>
  );
};

export { PostsPage };
export default PostsPage;
