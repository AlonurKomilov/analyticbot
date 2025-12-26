import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { People } from '@mui/icons-material';

const UsersPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Users Management
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Manage all platform users across all projects
      </Typography>
      
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <People sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            User Management Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Full user management with suspend, reactivate, and role management
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default UsersPage;
