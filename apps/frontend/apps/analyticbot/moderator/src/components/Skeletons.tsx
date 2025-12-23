import React from 'react';
import { Box, Skeleton, Paper, Grid } from '@mui/material';

export const PageSkeleton: React.FC = () => (
  <Box sx={{ p: 3 }}>
    <Skeleton variant="text" width={200} height={40} sx={{ mb: 2 }} />
    <Grid container spacing={2} sx={{ mb: 3 }}>
      {[1, 2, 3, 4].map((i) => (
        <Grid item xs={6} sm={3} key={i}>
          <Paper sx={{ p: 2 }}>
            <Skeleton variant="text" width="60%" />
            <Skeleton variant="text" width="40%" />
          </Paper>
        </Grid>
      ))}
    </Grid>
    <Paper sx={{ p: 2 }}>
      <Skeleton variant="rectangular" height={300} />
    </Paper>
  </Box>
);

export const TableSkeleton: React.FC = () => (
  <Box>
    {[1, 2, 3, 4, 5].map((i) => (
      <Skeleton key={i} variant="rectangular" height={52} sx={{ mb: 0.5 }} />
    ))}
  </Box>
);
