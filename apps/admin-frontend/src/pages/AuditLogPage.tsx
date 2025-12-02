import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { History as AuditIcon } from '@mui/icons-material';

const AuditLogPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Audit Log
        </Typography>
        <Typography color="text.secondary">
          View system activity and admin actions
        </Typography>
      </Box>

      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <AuditIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          Audit log features coming soon
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 1 }}>
          Track all admin actions, user activities, and system events
        </Typography>
      </Paper>
    </Box>
  );
};

export default AuditLogPage;
