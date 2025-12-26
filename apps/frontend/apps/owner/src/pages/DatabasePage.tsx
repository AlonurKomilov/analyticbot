import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { Storage } from '@mui/icons-material';

const DatabasePage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Database Management
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Database statistics, backups, and maintenance
      </Typography>
      
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <Storage sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Database Management Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Backup management, query execution, and maintenance tools
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DatabasePage;
