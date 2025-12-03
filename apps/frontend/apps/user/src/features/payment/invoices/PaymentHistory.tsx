/**
 * PaymentHistory Component
 *
 * Extracted from SubscriptionDashboard - displays recent payment transactions
 * with detailed information and status indicators
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip,
  Divider
} from '@mui/material';
import { IconButton } from '@shared/components/ui';
import { StatusChip } from '@shared/components';
import {
  Receipt,
  Download,
  CheckCircle,
  Error,
  Schedule,
  Refresh
} from '@mui/icons-material';
import { formatCurrency, formatDate } from '@features/payment/utils/paymentUtils';

// Types
type PaymentStatus = 'succeeded' | 'paid' | 'failed' | 'pending' | string;
type StatusColor = 'success' | 'error' | 'warning' | 'default';

interface PaymentMethod {
  last4?: string;
  brand?: string;
}

interface Payment {
  id?: string;
  status: PaymentStatus;
  amount: number;
  currency: string;
  description?: string;
  created: string;
  payment_method?: PaymentMethod;
}

interface PaymentHistoryProps {
  paymentHistory?: Payment[];
  onRefresh: () => void;
}

const PaymentHistory: React.FC<PaymentHistoryProps> = ({ paymentHistory, onRefresh }) => {
  const getPaymentStatusIcon = (status: PaymentStatus): React.ReactElement => {
    switch (status) {
      case 'succeeded':
      case 'paid':
        return <CheckCircle sx={{ color: 'success.main', fontSize: 20 }} />;
      case 'failed':
        return <Error sx={{ color: 'error.main', fontSize: 20 }} />;
      case 'pending':
        return <Schedule sx={{ color: 'warning.main', fontSize: 20 }} />;
      default:
        return <Receipt sx={{ color: 'text.secondary', fontSize: 20 }} />;
    }
  };

  const getPaymentStatusColor = (status: PaymentStatus): StatusColor => {
    switch (status) {
      case 'succeeded':
      case 'paid':
        return 'success';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  if (!paymentHistory || paymentHistory.length === 0) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardHeader
          title={
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="h6">Recent Payments</Typography>
              <Tooltip title="Refresh">
                <IconButton onClick={onRefresh} size="small">
                  <Refresh />
                </IconButton>
              </Tooltip>
            </Box>
          }
        />
        <CardContent>
          <Box textAlign="center" py={3}>
            <Receipt sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              No payment history available
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mb: 3 }}>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">Recent Payments</Typography>
            <Tooltip title="Refresh">
              <IconButton onClick={onRefresh} size="small">
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        }
        subheader={`${paymentHistory.length} recent transactions`}
      />
      <CardContent sx={{ pt: 0 }}>
        <List>
          {paymentHistory.map((payment, index) => (
            <React.Fragment key={payment.id || index}>
              <ListItem
                sx={{ px: 0 }}
                secondaryAction={
                  <Box display="flex" alignItems="center" gap={1}>
                    <StatusChip
                      label={payment.status.toUpperCase()}
                      status={getPaymentStatusColor(payment.status) as 'info' | 'success' | 'warning' | 'error'}
                      size="small"
                    />
                    <Tooltip title="Download Receipt">
                      <IconButton size="small">
                        <Download />
                      </IconButton>
                    </Tooltip>
                  </Box>
                }
              >
                <ListItemIcon>
                  {getPaymentStatusIcon(payment.status)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={2}>
                      <Typography variant="body1">
                        {formatCurrency(payment.amount, payment.currency)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {payment.description || 'Subscription payment'}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(payment.created)}
                      </Typography>
                      {payment.payment_method && (
                        <Typography variant="caption" color="text.secondary">
                          •••• {payment.payment_method.last4} • {payment.payment_method.brand?.toUpperCase()}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
              {index < paymentHistory.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default PaymentHistory;
