/**
 * PaymentHistoryDialog Component
 * 
 * Extracted from SubscriptionDashboard - displays detailed payment history
 * in a modal dialog with filtering and export options
 */

import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Tooltip,
  Divider
} from '@mui/material';
import { IconButton } from '../../common/TouchTargetCompliance.jsx';
import { StatusChip } from '../../common';
import {
  Receipt,
  Download,
  CheckCircle,
  Error,
  Schedule,
  Close
} from '@mui/icons-material';
import { Button } from '../../common';
import { formatCurrency, formatDate } from '../utils/paymentUtils.js';

const PaymentHistoryDialog = ({ 
  open, 
  onClose, 
  paymentHistory = [] 
}) => {
  const getPaymentStatusIcon = (status) => {
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

  const getPaymentStatusColor = (status) => {
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

  const handleDownloadReceipt = (paymentId) => {
    console.log('Download receipt for payment:', paymentId);
    // Implement receipt download logic
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">Payment History</Typography>
          <IconButton onClick={onClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent sx={{ minHeight: 400 }}>
        {paymentHistory.length === 0 ? (
          <Box textAlign="center" py={4}>
            <Receipt sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No Payment History
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Your payment transactions will appear here once you make your first payment.
            </Typography>
          </Box>
        ) : (
          <List>
            {paymentHistory.map((payment, index) => (
              <React.Fragment key={payment.id || index}>
                <ListItem
                  sx={{ px: 0 }}
                  secondaryAction={
                    <Box display="flex" alignItems="center" gap={1}>
                      <StatusChip
                        label={payment.status.toUpperCase()}
                        variant={getPaymentStatusColor(payment.status)}
                        size="small"
                      />
                      <Tooltip title="Download Invoice">
                        <IconButton 
                          size="small"
                          onClick={() => handleDownloadReceipt(payment.id)}
                        >
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
                      <Box>
                        <Typography variant="body1" gutterBottom>
                          {formatCurrency(payment.amount, payment.currency)}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {payment.description || 'Subscription payment'}
                        </Typography>
                      </Box>
                    }
                    secondary={
                      <Box mt={1}>
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(payment.created)}
                        </Typography>
                        {payment.payment_method && (
                          <Typography variant="caption" color="text.secondary">
                            Payment method: •••• {payment.payment_method.last4} • {payment.payment_method.brand?.toUpperCase()}
                          </Typography>
                        )}
                        {payment.invoice_id && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                            Invoice: {payment.invoice_id}
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
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3, pt: 1 }}>
        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
        {paymentHistory.length > 0 && (
          <Button variant="primary">
            Export All
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default PaymentHistoryDialog;