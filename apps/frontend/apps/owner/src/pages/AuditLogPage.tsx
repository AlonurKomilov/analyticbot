import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { History } from '@mui/icons-material';

const AuditLogPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Audit Log
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Track all system activities and changes
      </Typography>
      
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <History sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Audit Log Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Complete audit trail of all platform activities
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AuditLogPage;
