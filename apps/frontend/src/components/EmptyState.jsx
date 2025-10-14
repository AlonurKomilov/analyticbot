import React from 'react';
import { Box, Typography } from '@mui/material';

const EmptyState = ({ message = 'No data available', icon = null }) => (
  <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={6}>
    {icon && <Box mb={2}>{icon}</Box>}
    <Typography variant="h6" color="textSecondary" align="center">
      {message}
    </Typography>
  </Box>
);

export default EmptyState;
