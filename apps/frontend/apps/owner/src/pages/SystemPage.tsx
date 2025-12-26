import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { Computer } from '@mui/icons-material';

const SystemPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        System Overview
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        System health, metrics, and configuration
      </Typography>
      
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <Computer sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            System Overview Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Detailed system metrics and configuration management
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SystemPage;
