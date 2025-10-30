/**
 * Bot Setup Page
 * Page wrapper for Bot Setup Wizard
 */

import React from 'react';
import { Container } from '@mui/material';
import { BotSetupWizard } from '@/components/bot';

export const BotSetupPage: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <BotSetupWizard />
    </Container>
  );
};

export default BotSetupPage;
