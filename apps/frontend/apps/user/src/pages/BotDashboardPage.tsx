/**
 * Bot Dashboard Page
 * Page wrapper for User Bot Dashboard
 */

import React from 'react';
import { Container } from '@mui/material';
import { UserBotDashboard } from '@features/bot';

export const BotDashboardPage: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <UserBotDashboard />
    </Container>
  );
};

export default BotDashboardPage;
