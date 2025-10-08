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

export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

export const getStatusColor = (status) => {
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

export const getStatusIcon = (status) => {
  switch (status) {
    case 'active':
      return <CheckCircle sx={{ fontSize: 16 }} />;
    case 'trialing':
      return <TrendingUp sx={{ fontSize: 16 }} />;
    case 'past_due':
      return <Warning sx={{ fontSize: 16 }} />;
    case 'incomplete':
    case 'canceled':
    case 'cancelled':
      return <Cancel sx={{ fontSize: 16 }} />;
    default:
      return null;
  }
};

export const calculateDaysUntilNextBilling = (currentPeriodEnd) => {
  if (!currentPeriodEnd) return 0;
  return Math.ceil((new Date(currentPeriodEnd) - new Date()) / (1000 * 60 * 60 * 24));
};
