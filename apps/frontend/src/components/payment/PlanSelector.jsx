import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Button,
  Box,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  Check,
  Star,
  TrendingUp,
  Security,
  Speed,
  Support
} from '@mui/icons-material';
import { paymentAPI } from '../../services/api';
import PaymentForm from './PaymentForm';

const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

const getFeatureIcon = (feature) => {
  const featureLower = feature.toLowerCase();
  if (featureLower.includes('analytics') || featureLower.includes('insight')) {
    return <TrendingUp sx={{ fontSize: 16 }} />;
  }
  if (featureLower.includes('security') || featureLower.includes('secure')) {
    return <Security sx={{ fontSize: 16 }} />;
  }
  if (featureLower.includes('speed') || featureLower.includes('fast')) {
    return <Speed sx={{ fontSize: 16 }} />;
  }
  if (featureLower.includes('support')) {
    return <Support sx={{ fontSize: 16 }} />;
  }
  return <Check sx={{ fontSize: 16 }} />;
};

const PlanCard = ({
  plan,
  billingCycle,
  isPopular,
  isSelected,
  onSelect,
  disabled = false
}) => {
  const price = billingCycle === 'yearly' ? plan.price_yearly : plan.price_monthly;
  const originalPrice = billingCycle === 'yearly' ? plan.price_monthly * 12 : null;
  const savings = originalPrice ? originalPrice - price : 0;
  const savingsPercentage = originalPrice ? Math.round((savings / originalPrice) * 100) : 0;

  return (
    <Card
      sx={{
        position: 'relative',
        border: isSelected ? 2 : 1,
        borderColor: isSelected ? 'primary.main' : 'divider',
        cursor: disabled ? 'default' : 'pointer',
        opacity: disabled ? 0.6 : 1,
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          borderColor: disabled ? 'divider' : 'primary.main',
          transform: disabled ? 'none' : 'translateY(-2px)',
          boxShadow: disabled ? 1 : 4,
        },
      }}
      onClick={() => !disabled && onSelect(plan)}
    >
      {isPopular && (
        <Box
          sx={{
            position: 'absolute',
            top: -8,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 1,
          }}
        >
          <Chip
            icon={<Star sx={{ fontSize: 16 }} />}
            label="Most Popular"
            color="primary"
            size="small"
            sx={{ fontWeight: 'bold' }}
          />
        </Box>
      )}

      <CardHeader
        title={
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6" fontWeight="bold">
              {plan.name}
            </Typography>
            <Radio
              checked={isSelected}
              disabled={disabled}
              color="primary"
            />
          </Box>
        }
        sx={{ pb: 1 }}
      />

      <CardContent>
        {/* Pricing */}
        <Box mb={3}>
          <Box display="flex" alignItems="baseline" gap={1}>
            <Typography variant="h4" fontWeight="bold" color="primary">
              {price ? formatCurrency(price, plan.currency) : 'Free'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              / {billingCycle === 'yearly' ? 'year' : 'month'}
            </Typography>
          </Box>

          {billingCycle === 'yearly' && originalPrice && savings > 0 && (
            <Box mt={1}>
              <Typography
                variant="body2"
                sx={{ textDecoration: 'line-through' }}
                color="text.secondary"
              >
                {formatCurrency(originalPrice, plan.currency)}/year
              </Typography>
              <Chip
                label={`Save ${savingsPercentage}%`}
                color="success"
                size="small"
                sx={{ ml: 1 }}
              />
            </Box>
          )}
        </Box>

        {/* Limits */}
        <Box mb={3}>
          {plan.max_channels && (
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Up to {plan.max_channels} channels
            </Typography>
          )}
          {plan.max_posts_per_month && (
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {plan.max_posts_per_month} posts per month
            </Typography>
          )}
        </Box>

        {/* Features */}
        {plan.features && plan.features.length > 0 && (
          <>
            <Divider sx={{ mb: 2 }} />
            <List dense sx={{ py: 0 }}>
              {plan.features.map((feature, index) => (
                <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                  <ListItemIcon sx={{ minWidth: 24, color: 'success.main' }}>
                    {getFeatureIcon(feature)}
                  </ListItemIcon>
                  <ListItemText
                    primary={feature}
                    primaryTypographyProps={{
                      variant: 'body2',
                      color: 'text.secondary'
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </>
        )}
      </CardContent>
    </Card>
  );
};

const PlanSelector = ({
  userId,
  onPlanSelected,
  showPaymentForm = false,
  preselectedPlanId = null
}) => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showPayment, setShowPayment] = useState(showPaymentForm);

  useEffect(() => {
    loadPlans();
  }, []);

  useEffect(() => {
    if (preselectedPlanId && plans.length > 0) {
      const plan = plans.find(p => p.id === preselectedPlanId);
      if (plan) {
        setSelectedPlan(plan);
      }
    }
  }, [preselectedPlanId, plans]);

  const loadPlans = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await paymentAPI.getAvailablePlans();
      const activePlans = response.filter(plan => plan.is_active);
      setPlans(activePlans);

      // Auto-select most popular plan if none selected
      if (!selectedPlan && activePlans.length > 0) {
        const popularPlan = activePlans.find(plan =>
          plan.name.toLowerCase().includes('pro') ||
          plan.name.toLowerCase().includes('premium')
        ) || activePlans[Math.floor(activePlans.length / 2)];
        setSelectedPlan(popularPlan);
      }

    } catch (err) {
      setError(err.message || 'Failed to load plans');
    } finally {
      setLoading(false);
    }
  };

  const handlePlanSelect = (plan) => {
    setSelectedPlan(plan);
    onPlanSelected && onPlanSelected(plan);
  };

  const handleContinueToPayment = () => {
    if (selectedPlan) {
      setShowPayment(true);
    }
  };

  const handlePaymentSuccess = (subscriptionResponse) => {
    // Handle successful payment
    console.log('Payment successful:', subscriptionResponse);
    onPlanSelected && onPlanSelected(selectedPlan, subscriptionResponse);
  };

  const handlePaymentError = (error) => {
    setError(error.message || 'Payment failed');
    setShowPayment(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" py={8}>
        <CircularProgress />
        <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
          Loading subscription plans...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
        <Button size="small" onClick={loadPlans} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  if (showPayment && selectedPlan) {
    const planPriceId = billingCycle === 'yearly'
      ? selectedPlan.stripe_yearly_price_id || selectedPlan.stripe_price_id
      : selectedPlan.stripe_price_id;

    return (
      <Box>
        <Box mb={3}>
          <Button
            variant="text"
            onClick={() => setShowPayment(false)}
            sx={{ mb: 2 }}
          >
            ← Back to Plans
          </Button>
          <Typography variant="h5" gutterBottom>
            Complete Your Subscription
          </Typography>
          <Typography variant="body1" color="text.secondary">
            You've selected the <strong>{selectedPlan.name}</strong> plan
            {billingCycle === 'yearly' && selectedPlan.price_yearly ? (
              ` for ${formatCurrency(selectedPlan.price_yearly, selectedPlan.currency)}/year`
            ) : selectedPlan.price_monthly ? (
              ` for ${formatCurrency(selectedPlan.price_monthly, selectedPlan.currency)}/month`
            ) : null}
          </Typography>
        </Box>

        <PaymentForm
          planId={planPriceId}
          userId={userId}
          onSuccess={handlePaymentSuccess}
          onError={handlePaymentError}
          trialDays={selectedPlan.trial_days}
        />
      </Box>
    );
  }

  return (
    <Box>
      <Box textAlign="center" mb={4}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          Choose Your Plan
        </Typography>
        <Typography variant="body1" color="text.secondary" mb={3}>
          Select the perfect plan for your analytics needs
        </Typography>

        {/* Billing Cycle Toggle */}
        <FormControl>
          <RadioGroup
            row
            value={billingCycle}
            onChange={(e) => setBillingCycle(e.target.value)}
            sx={{
              gap: 2,
              justifyContent: 'center',
              '& .MuiFormControlLabel-root': {
                border: 1,
                borderColor: 'divider',
                borderRadius: 1,
                px: 2,
                py: 1,
                m: 0,
              },
              '& .Mui-checked + .MuiFormControlLabel-label': {
                fontWeight: 'bold',
              },
            }}
          >
            <FormControlLabel
              value="monthly"
              control={<Radio size="small" />}
              label="Monthly"
            />
            <FormControlLabel
              value="yearly"
              control={<Radio size="small" />}
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  Yearly
                  <Chip label="Save 20%" color="success" size="small" />
                </Box>
              }
            />
          </RadioGroup>
        </FormControl>
      </Box>

      {/* Plans Grid */}
      <Grid container spacing={3} mb={4}>
        {plans.map((plan, index) => {
          const isPopular = plan.name.toLowerCase().includes('pro') ||
                           plan.name.toLowerCase().includes('premium') ||
                           index === Math.floor(plans.length / 2);

          const hasPrice = billingCycle === 'yearly' ? plan.price_yearly : plan.price_monthly;

          return (
            <Grid item xs={12} md={plans.length <= 2 ? 6 : 4} key={plan.id}>
              <PlanCard
                plan={plan}
                billingCycle={billingCycle}
                isPopular={isPopular}
                isSelected={selectedPlan?.id === plan.id}
                onSelect={handlePlanSelect}
                disabled={!hasPrice}
              />
            </Grid>
          );
        })}
      </Grid>

      {/* Continue Button */}
      {selectedPlan && (
        <Box textAlign="center">
          <Button
            variant="contained"
            size="large"
            onClick={handleContinueToPayment}
            sx={{ minWidth: 200, py: 1.5 }}
          >
            Continue to Payment
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default PlanSelector;
