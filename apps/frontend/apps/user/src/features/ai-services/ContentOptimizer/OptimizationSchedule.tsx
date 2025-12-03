/**
 * Optimization Schedule Component
 * Schedule configuration for automated optimizations
 */

import React from 'react';
import { CardContent, Typography, Alert } from '@mui/material';

export const OptimizationSchedule: React.FC = () => {
  return (
    <CardContent>
      <Typography variant="h6" sx={{ mb: 3 }}>
        Optimization Schedule
      </Typography>

      <Alert severity="info">
        Scheduled optimization features coming soon. Currently running in real-time mode.
      </Alert>
    </CardContent>
  );
};

export default OptimizationSchedule;
