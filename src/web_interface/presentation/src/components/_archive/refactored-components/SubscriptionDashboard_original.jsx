import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Box,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Divider,
  LinearProgress,
  Grid,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Settings,
  Cancel,
  History,
  CreditCard,
  CalendarToday,
  TrendingUp,
  Warning,
  CheckCircle
} from '@mui/icons-material';
import { paymentAPI } from '../../services/api';

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

const getStatusColor = (status) => {
  switch (status) {
    case 'active':
      return 'success';
    case 'trialing':
      return 'info';
    case 'past_due':
      return 'warning';
    case 'canceled':
    case 'cancelled':
      return 'error';
    case 'incomplete':
      return 'warning';
    default:
      return 'default';
  }
};

const getStatusIcon = (status) => {
  switch (status) {
    case 'active':
      return <CheckCircle sx={{ fontSize: 16 }} />;
    case 'trialing':
      return <TrendingUp sx={{ fontSize: 16 }} />;
    case 'past_due':
      return <Warning sx={{ fontSize: 16 }} />;
    case 'canceled':
    case 'cancelled':
      return <Cancel sx={{ fontSize: 16 }} />;
    default:
      return null;
  }
};

const SubscriptionDashboard = ({ userId }) => {
  const [subscription, setSubscription] = useState(null);
  const [paymentHistory, setPaymentHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [canceling, setCanceling] = useState(false);
  const [historyDialogOpen, setHistoryDialogOpen] = useState(false);

  useEffect(() => {
    loadSubscriptionData();
  }, [userId]);

  const loadSubscriptionData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load subscription data
      const subResponse = await paymentAPI.getUserSubscription(userId);
      setSubscription(subResponse.subscription);

      // Load payment history
      const historyResponse = await paymentAPI.getPaymentHistory(userId, 10);
      setPaymentHistory(historyResponse.payments || []);

    } catch (err) {
      setError(err.message || 'Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async (immediate = false) => {
    try {
      setCanceling(true);
      await paymentAPI.cancelSubscription({
        user_id: userId,
        immediate: immediate
      });
      
      // Reload subscription data
      await loadSubscriptionData();
      setCancelDialogOpen(false);
      
    } catch (err) {
      setError(err.message || 'Failed to cancel subscription');
    } finally {
      setCanceling(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" flexDirection="column" alignItems="center" py={4}>
            <LinearProgress sx={{ width: '100%', mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Loading subscription information...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
        <Button
          size="small"
          onClick={loadSubscriptionData}
          sx={{ ml: 2 }}
        >
          Retry
        </Button>
      </Alert>
    );
  }

  if (!subscription) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 6 }}>
          <CreditCard sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No Active Subscription
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            You don't have an active subscription. Choose a plan to get started.
          </Typography>
          <Button variant="contained" color="primary">
            View Plans
          </Button>
        </CardContent>
      </Card>
    );
  }

  const daysUntilNextBilling = subscription.current_period_end
    ? Math.ceil((new Date(subscription.current_period_end) - new Date()) / (1000 * 60 * 60 * 24))
    : 0;

  const isTrialing = subscription.status === 'trialing';
  const isCanceled = subscription.status === 'canceled' || subscription.status === 'cancelled';
  const isPastDue = subscription.status === 'past_due';

  return (
    <Box>
      {/* Main Subscription Card */}
      <Card sx={{ mb: 3 }}>
        <CardHeader
          title={
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Typography variant="h6">Current Subscription</Typography>
              <Box display="flex" gap={1}>
                <Tooltip title="Payment History">
                  <IconButton onClick={() => setHistoryDialogOpen(true)}>
                    <History />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Manage Subscription">
                  <IconButton>
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
                  <Chip
                    icon={getStatusIcon(subscription.status)}
                    label={subscription.status.toUpperCase()}
                    color={getStatusColor(subscription.status)}
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
                    Your payment is past due. Please update your payment method to continue your subscription.
                  </Typography>
                </Alert>
              )}

              {isCanceled && subscription.current_period_end && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    Your subscription has been canceled and will end on{' '}
                    {formatDate(subscription.current_period_end)}.
                  </Typography>
                </Alert>
              )}
            </Grid>

            <Grid item xs={12} md={6}>
              <Box mb={2}>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Billing Information
                </Typography>
                {subscription.current_period_start && (
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    <CalendarToday sx={{ fontSize: 16, color: 'text.secondary' }} />
                    <Typography variant="body2">
                      Current period: {formatDate(subscription.current_period_start)}
                      {subscription.current_period_end && ` - ${formatDate(subscription.current_period_end)}`}
                    </Typography>
                  </Box>
                )}
                {subscription.current_period_end && !isCanceled && (
                  <Typography variant="body2" color="text.secondary">
                    Next billing: {formatDate(subscription.current_period_end)}
                    {daysUntilNextBilling > 0 && ` (${daysUntilNextBilling} days)`}
                  </Typography>
                )}
              </Box>

              <Box display="flex" gap={1} flexWrap="wrap">
                {!isCanceled && (
                  <Button
                    variant="outlined"
                    color="error"
                    size="small"
                    startIcon={<Cancel />}
                    onClick={() => setCancelDialogOpen(true)}
                  >
                    Cancel Subscription
                  </Button>
                )}
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<CreditCard />}
                >
                  Update Payment Method
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Usage/Features Card */}
      {subscription.plan_details && (
        <Card>
          <CardHeader title="Plan Features & Usage" />
          <CardContent>
            <Grid container spacing={2}>
              {subscription.plan_details.max_channels && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Channels
                  </Typography>
                  <Typography variant="body1">
                    {subscription.current_usage?.channels || 0} / {subscription.plan_details.max_channels}
                  </Typography>
                </Grid>
              )}
              {subscription.plan_details.max_posts_per_month && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Posts This Month
                  </Typography>
                  <Typography variant="body1">
                    {subscription.current_usage?.posts || 0} / {subscription.plan_details.max_posts_per_month}
                  </Typography>
                </Grid>
              )}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Cancel Subscription Dialog */}
      <Dialog open={cancelDialogOpen} onClose={() => setCancelDialogOpen(false)}>
        <DialogTitle>Cancel Subscription</DialogTitle>
        <DialogContent>
          <Typography gutterBottom>
            Are you sure you want to cancel your subscription?
          </Typography>
          {subscription.current_period_end && (
            <Typography variant="body2" color="text.secondary">
              Your subscription will remain active until {formatDate(subscription.current_period_end)}.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCancelDialogOpen(false)}>
            Keep Subscription
          </Button>
          <Button
            onClick={() => handleCancelSubscription(false)}
            color="error"
            disabled={canceling}
          >
            {canceling ? 'Canceling...' : 'Cancel Subscription'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Payment History Dialog */}
      <Dialog
        open={historyDialogOpen}
        onClose={() => setHistoryDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Payment History</DialogTitle>
        <DialogContent>
          {paymentHistory.length > 0 ? (
            <List>
              {paymentHistory.map((payment, index) => (
                <React.Fragment key={payment.id}>
                  <ListItem>
                    <ListItemText
                      primary={
                        <Box display="flex" justifyContent="space-between" alignItems="center">
                          <Typography variant="body1">
                            {formatCurrency(payment.amount, payment.currency)}
                          </Typography>
                          <Chip
                            label={payment.status.toUpperCase()}
                            color={getStatusColor(payment.status)}
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {formatDate(payment.created_at)}
                          </Typography>
                          {payment.description && (
                            <Typography variant="body2" color="text.secondary">
                              {payment.description}
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
          ) : (
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
              No payment history available
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SubscriptionDashboard;
