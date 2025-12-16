/**
 * Bot Moderation Page
 * Page wrapper for Bot Moderation Dashboard
 */

import React from 'react';
import { Container } from '@mui/material';
import { BotModerationDashboard } from '@features/bot';

export const BotModerationPage: React.FC = () => {
  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <BotModerationDashboard />
    </Container>
  );
};

export default BotModerationPage;
