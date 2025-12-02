import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';

const SettingsPage: React.FC = () => {
  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Admin Settings
        </Typography>
        <Typography color="text.secondary">
          Configure admin panel and system settings
        </Typography>
      </Box>

      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <SettingsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          Admin settings coming soon
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 1 }}>
          Configure system settings, API keys, and admin preferences
        </Typography>
      </Paper>
    </Box>
  );
};

export default SettingsPage;
