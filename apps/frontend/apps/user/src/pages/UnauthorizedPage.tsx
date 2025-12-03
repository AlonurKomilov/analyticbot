/**
 * 401 Unauthorized Page
 */

import React from 'react';
import { Container, Typography, Box, Button } from '@mui/material';
import { Login, Home } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@config/routes';

const UnauthorizedPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
      <Typography variant="h1" component="h1" sx={{ fontSize: '6rem', fontWeight: 'bold' }}>
        401
      </Typography>
      <Typography variant="h4" component="h2" gutterBottom>
        Unauthorized Access
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        You don't have permission to access this page. Please log in or contact support.
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
          startIcon={<Login />}
          onClick={() => navigate(ROUTES.LOGIN)}
        >
          Log In
        </Button>
      </Box>
    </Container>
  );
};

export default UnauthorizedPage;
