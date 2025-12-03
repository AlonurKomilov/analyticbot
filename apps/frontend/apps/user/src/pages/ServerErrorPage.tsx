/**
 * 500 Server Error Page
 */

import React from 'react';
import { Container, Typography, Box, Button } from '@mui/material';
import { Refresh, Home } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@config/routes';

const ServerErrorPage: React.FC = () => {
  const navigate = useNavigate();

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
      <Typography variant="h1" component="h1" sx={{ fontSize: '6rem', fontWeight: 'bold' }}>
        500
      </Typography>
      <Typography variant="h4" component="h2" gutterBottom>
        Server Error
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Something went wrong on our end. We're working to fix it. Please try again later.
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        <Button
          variant="outlined"
          startIcon={<Home />}
          onClick={() => navigate(ROUTES.HOME)}
        >
          Go Home
        </Button>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={handleRefresh}
        >
          Refresh Page
        </Button>
      </Box>
    </Container>
  );
};

export default ServerErrorPage;
