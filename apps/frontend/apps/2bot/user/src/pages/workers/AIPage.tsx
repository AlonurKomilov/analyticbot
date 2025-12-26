/**
 * AI Dashboard Page
 * Renders the User AI Dashboard from features/ai
 */

import React from 'react';
import { Container } from '@mui/material';
import { UserAIDashboard } from '@/features/ai';

const AIPage: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <UserAIDashboard />
    </Container>
  );
};

export default AIPage;
