/**
 * SubscriptionCard Component
 *
 * Extracted from SubscriptionDashboard - displays subscription plan details,
 * status, billing information, and quick actions
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Alert,
  Grid,
  Tooltip
} from '@mui/material';
import { IconButton } from '../../common/TouchTargetCompliance';
import { StatusChip } from '../../common';
import {
  Settings,
  History,
  CalendarToday
} from '@mui/icons-material';
import { formatCurrency, formatDate, getStatusColor, getStatusIcon, calculateDaysUntilNextBilling } from '../utils/paymentUtils';

interface PaymentMethod {
  last4?: string;
  [key: string]: any;
}

interface Subscription {
  plan_name?: string;
  status: string;
  amount?: number;
  currency?: string;
  billing_cycle?: string;
  current_period_start?: string | Date;
  current_period_end?: string | Date;
  payment_method?: PaymentMethod;
  [key: string]: any;
}

interface SubscriptionCardProps {
  subscription: Subscription;
  onHistoryClick: () => void;
  onSettingsClick: () => void;
}

const SubscriptionCard: React.FC<SubscriptionCardProps> = ({
  subscription,
  onHistoryClick,
  onSettingsClick
}) => {
  const daysUntilNextBilling = calculateDaysUntilNextBilling(subscription.current_period_end);
  const isTrialing = subscription.status === 'trialing';
  const isCanceled = subscription.status === 'canceled' || subscription.status === 'cancelled';
  const isPastDue = subscription.status === 'past_due';

  return (
    <Card sx={{ mb: 3 }}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">Current Subscription</Typography>
            <Box display="flex" gap={1}>
              <Tooltip title="Payment History">
                <IconButton onClick={onHistoryClick}>
                  <History />
                </IconButton>
              </Tooltip>
              <Tooltip title="Manage Subscription">
                <IconButton onClick={onSettingsClick}>
                  <Settings />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        }
      />
      <CardContent>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box mb={2}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Plan & Status
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Typography variant="h6">
                  {subscription.plan_name || 'Subscription Plan'}
                </Typography>
                <StatusChip
                  icon={getStatusIcon(subscription.status) as any}
                  label={subscription.status.toUpperCase()}
                  variant={getStatusColor(subscription.status) as any}
                  size="small"
                />
              </Box>
              {subscription.amount && (
                <Typography variant="body2" color="text.secondary">
                  {formatCurrency(subscription.amount, subscription.currency)} per {subscription.billing_cycle}
                </Typography>
              )}
            </Box>

            {isTrialing && (
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  You're in your free trial period.
                  {daysUntilNextBilling > 0 && ` ${daysUntilNextBilling} days remaining.`}
                </Typography>
              </Alert>
            )}

            {isPastDue && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Your payment is past due. Please update your payment method to continue service.
                </Typography>
              </Alert>
            )}

            {isCanceled && (
              <Alert severity="error" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Your subscription has been canceled.
                  {subscription.current_period_end && ` Access ends on ${formatDate(subscription.current_period_end)}.`}
                </Typography>
              </Alert>
            )}
          </Grid>

          <Grid item xs={12} md={6}>
            <Box>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Billing Information
              </Typography>

              {subscription.current_period_start && (
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <CalendarToday sx={{ fontSize: 16, color: 'text.secondary' }} />
                  <Typography variant="body2">
                    Current period: {formatDate(subscription.current_period_start)} - {subscription.current_period_end ? formatDate(subscription.current_period_end) : 'N/A'}
                  </Typography>
                </Box>
              )}

              {!isCanceled && subscription.current_period_end && (
                <Typography variant="body2" color="text.secondary">
                  Next billing: {formatDate(subscription.current_period_end)}
                  {daysUntilNextBilling > 0 && ` (${daysUntilNextBilling} days)`}
                </Typography>
              )}

              {subscription.payment_method && (
                <Typography variant="body2" color="text.secondary" mt={1}>
                  Payment method: •••• {subscription.payment_method.last4 || 'Hidden'}
                </Typography>
              )}
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SubscriptionCard;
