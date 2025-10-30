/**
 * EmptyState Component
 * Displays a friendly message when no scheduled posts exist
 */

import React from 'react';
import { Paper, Typography, Button, Box } from '@mui/material';
import { Schedule } from '@mui/icons-material';
import { EmptyStateProps } from '../types';

const EmptyState: React.FC<EmptyStateProps> = ({
  message = "No scheduled posts yet",
  actionText,
  onAction
}) => {
  return (
    <Paper
      sx={{
        p: 6,
        textAlign: 'center',
        bgcolor: 'background.paper'
      }}
      elevation={2}
    >
      <Box sx={{ mb: 2 }}>
        <Schedule sx={{ fontSize: 64, color: 'text.secondary', opacity: 0.5 }} />
      </Box>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        {message}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Schedule a post to see it appear here!
      </Typography>
      {actionText && onAction && (
        <Button
          variant="contained"
          onClick={onAction}
          sx={{ mt: 2 }}
        >
          {actionText}
        </Button>
      )}
    </Paper>
  );
};

export default EmptyState;
