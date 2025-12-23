/**
 * LoadingSkeleton Component
 * Loading state skeleton for the overview page
 */

import React from 'react';
import { Box, Grid, Skeleton } from '@mui/material';

export const LoadingSkeleton: React.FC = () => (
  <Box>
    <Skeleton variant="rectangular" height={120} sx={{ mb: 3, borderRadius: 2 }} />
    <Grid container spacing={2}>
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <Grid item xs={12} sm={6} md={4} lg={2} key={i}>
          <Skeleton variant="rectangular" height={120} sx={{ borderRadius: 2 }} />
        </Grid>
      ))}
    </Grid>
    <Grid container spacing={3} sx={{ mt: 2 }}>
      <Grid item xs={12} md={8}>
        <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 2 }} />
      </Grid>
      <Grid item xs={12} md={4}>
        <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 2 }} />
      </Grid>
    </Grid>
  </Box>
);

export default LoadingSkeleton;
