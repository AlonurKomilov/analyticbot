/**
 * Subscription Page
 * Manage subscription plans and upgrades
 */

import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import { PlanSelector } from '@features/payment';
import { useAuthStore } from '@store/index';

const SubscriptionPage: React.FC = () => {
  const user = useAuthStore((state) => state.user);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Subscription Plans
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Choose the plan that best fits your needs
        </Typography>
      </Box>

      {user && <PlanSelector userId={user.id} />}
    </Container>
  );
};

export default SubscriptionPage;
