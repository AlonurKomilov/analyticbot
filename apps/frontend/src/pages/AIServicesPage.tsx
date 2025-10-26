/**
 * AI Services Overview Page
 * Landing page for all AI-powered features and tools
 */

import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import { AIServicesGrid } from '@features/ai-services';

const AIServicesPage: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI Services
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Leverage AI-powered tools to optimize content, predict trends, and monitor security
        </Typography>
      </Box>

      <AIServicesGrid />
    </Container>
  );
};

export default AIServicesPage;
