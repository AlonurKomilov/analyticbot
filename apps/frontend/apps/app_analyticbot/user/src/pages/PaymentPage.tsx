/**
 * Payment Page
 * Main payment and subscription management hub
 */

import React from 'react';
import { Container, Typography, Box, Grid, Card, CardContent, Button } from '@mui/material';
import { Payment, CreditCard, History, Receipt } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@config/routes';

const PaymentPage: React.FC = () => {
  const navigate = useNavigate();

  const paymentSections = [
    {
      title: 'Subscription',
      description: 'Manage your subscription plan and billing',
      icon: <Payment fontSize="large" />,
      path: ROUTES.SUBSCRIPTION,
    },
    {
      title: 'Payment Methods',
      description: 'Add or update your payment methods',
      icon: <CreditCard fontSize="large" />,
      action: () => console.log('Payment methods'),
    },
    {
      title: 'Payment History',
      description: 'View past transactions and payments',
      icon: <History fontSize="large" />,
      path: ROUTES.PAYMENT_HISTORY,
    },
    {
      title: 'Invoices',
      description: 'Download and manage your invoices',
      icon: <Receipt fontSize="large" />,
      path: ROUTES.INVOICES,
    },
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Payment & Billing
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your subscription, payment methods, and billing information
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {paymentSections.map((section, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {section.icon}
                  <Typography variant="h6" sx={{ ml: 2 }}>
                    {section.title}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {section.description}
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => section.path ? navigate(section.path) : section.action?.()}
                >
                  Manage
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
};

export default PaymentPage;
