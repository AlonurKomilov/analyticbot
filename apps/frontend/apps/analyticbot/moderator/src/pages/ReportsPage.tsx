import React from 'react';
import { Box, Typography, Paper, Alert } from '@mui/material';
import { Report as ReportIcon } from '@mui/icons-material';

const ReportsPage: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        <ReportIcon sx={{ mr: 1, verticalAlign: 'bottom' }} />
        Reports Queue
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Review and handle user-reported channels
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Reports system coming in a future phase. No reports to review at this time.
      </Alert>
      
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1" color="text.secondary">
          This page will allow you to:
        </Typography>
        <ul>
          <li>View reported channels</li>
          <li>Review report reasons</li>
          <li>Take action (remove, warn, dismiss)</li>
          <li>Track report history</li>
        </ul>
      </Paper>
    </Box>
  );
};

export default ReportsPage;
