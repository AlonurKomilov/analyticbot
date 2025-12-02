import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { SmartToy as BotsIcon } from '@mui/icons-material';

const BotsPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Bot Management
        </Typography>
        <Typography color="text.secondary">
          Manage connected Telegram bots
        </Typography>
      </Box>

      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <BotsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          Bot management features coming soon
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 1 }}>
          View and manage user bots, health status, and configurations
        </Typography>
      </Paper>
    </Box>
  );
};

export default BotsPage;
