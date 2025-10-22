/**
 * Payment Utilities
 *
 * Shared utility functions for payment and subscription components
 */

import React from 'react';
import {
  CheckCircle,
  TrendingUp,
  Warning,
  Cancel
} from '@mui/icons-material';

export type SubscriptionStatus = 'active' | 'trialing' | 'past_due' | 'incomplete' | 'canceled' | 'cancelled' | 'incomplete_expired';
export type StatusColor = 'success' | 'info' | 'warning' | 'error' | 'default';

export const formatDate = (dateString: string | Date): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

export const getStatusColor = (status: SubscriptionStatus | string): StatusColor => {
  switch (status) {
    case 'active':
      return 'success';
    case 'trialing':
      return 'info';
    case 'past_due':
      return 'warning';
    case 'incomplete':
    case 'canceled':
    case 'cancelled':
      return 'error';
    case 'incomplete_expired':
      return 'warning';
    default:
      return 'default';
  }
};

export const getStatusIcon = (status: SubscriptionStatus | string): React.ReactElement | null => {
  const iconProps = { sx: { fontSize: 16 } };

  switch (status) {
    case 'active':
      return React.createElement(CheckCircle, iconProps);
    case 'trialing':
      return React.createElement(TrendingUp, iconProps);
    case 'past_due':
      return React.createElement(Warning, iconProps);
    case 'incomplete':
    case 'canceled':
    case 'cancelled':
      return React.createElement(Cancel, iconProps);
    default:
      return null;
  }
};

export const calculateDaysUntilNextBilling = (currentPeriodEnd: string | Date | null | undefined): number => {
  if (!currentPeriodEnd) return 0;
  return Math.ceil((new Date(currentPeriodEnd).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
};
