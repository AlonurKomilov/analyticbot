/**
 * Scheduled Posts Page
 * View and manage scheduled posts
 */

import React, { useState } from 'react';
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
} from '@mui/material';
import { Edit, Delete, Visibility } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { buildRoute, ROUTES } from '@config/routes';

// Mock data - replace with real API call
const mockScheduledPosts = [
  { id: 1, title: 'Product Launch Announcement', scheduledFor: '2025-10-28 10:00', channel: 'Main' },
  { id: 2, title: 'Weekly Newsletter', scheduledFor: '2025-10-29 09:00', channel: 'Newsletter' },
  { id: 3, title: 'Feature Update', scheduledFor: '2025-10-30 14:00', channel: 'Updates' },
];

const ScheduledPostsPage: React.FC = () => {
  const navigate = useNavigate();
  const [posts] = useState(mockScheduledPosts);

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
            {posts.map((post) => (
              <TableRow key={post.id}>
                <TableCell>{post.title}</TableCell>
                <TableCell>{post.channel}</TableCell>
                <TableCell>{post.scheduledFor}</TableCell>
                <TableCell>
                  <Chip label="Scheduled" color="info" size="small" />
                </TableCell>
                <TableCell align="right">
                  <IconButton
                    size="small"
                    onClick={() => navigate(buildRoute(ROUTES.POST_DETAILS, { id: post.id }))}
                  >
                    <Visibility />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => navigate(buildRoute(ROUTES.EDIT_POST, { id: post.id }))}
                  >
                    <Edit />
                  </IconButton>
                  <IconButton size="small" color="error">
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default ScheduledPostsPage;
