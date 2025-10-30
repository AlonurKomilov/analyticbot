/**
 * LoadingState Component
 * Displays a centered loading spinner
 */

import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

const LoadingState: React.FC = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8
      }}
      role="status"
      aria-live="polite"
    >
      <CircularProgress size={48} />
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ mt: 2 }}
      >
        Loading scheduled posts...
      </Typography>
    </Box>
  );
};

export default LoadingState;
