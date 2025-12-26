import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { Settings } from '@mui/icons-material';

const SettingsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Settings
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Platform configuration and preferences
      </Typography>
      
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <Settings sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Settings Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Platform-wide configuration and preferences
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SettingsPage;
