import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { FolderSpecial } from '@mui/icons-material';

const ProjectsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Projects Management
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Manage all platform projects and applications
      </Typography>
      
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 8 }}>
          <FolderSpecial sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Projects Management Coming Soon
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Overview and management of all platform projects
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ProjectsPage;
