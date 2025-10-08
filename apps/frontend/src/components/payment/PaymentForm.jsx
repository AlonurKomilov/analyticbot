import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';
import {
  Alert,
  Button,
  Card,
  CardContent,
  CardHeader,
  FormControl,
  FormHelperText,
  Typography,
  Box,
  CircularProgress,
  Divider
} from '@mui/material';
import { CreditCard, Lock, CheckCircle } from '@mui/icons-material';
import { paymentAPI } from '../../services/api';

// Initialize Stripe
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);

const CARD_ELEMENT_OPTIONS = {
  style: {
    base: {
      fontSize: '16px',
      color: '#424770',
      '::placeholder': {
        color: '#aab7c4',
      },
      fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
      fontSmoothing: 'antialiased',
    },
    invalid: {
      color: '#9e2146',
    },
  },
  hidePostalCode: false,
};

const PaymentFormContent = ({
  planId,
  userId,
  onSuccess,
  onError,
  trialDays = null
}) => {
  const stripe = useStripe();
  const elements = useElements();

  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [cardComplete, setCardComplete] = useState(false);

  const handleCardChange = (event) => {
    setError(null);
    setCardComplete(event.complete);

    if (event.error) {
      setError(event.error.message);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      setError('Stripe has not loaded properly. Please refresh the page.');
      return;
    }

    if (!cardComplete) {
      setError('Please complete your card information.');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      const cardElement = elements.getElement(CardElement);

      // Create payment method
      const { error: stripeError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: cardElement,
        billing_details: {
          name: 'Customer Name', // You might want to collect this from the user
        },
      });

      if (stripeError) {
        throw new Error(stripeError.message);
      }

      // Create subscription with the payment method
      const response = await paymentAPI.createSubscription({
        user_id: userId,
        plan_id: planId,
        payment_method_id: paymentMethod.id,
        trial_days: trialDays
      });

      if (response.status === 'active' || response.status === 'trialing') {
        setSuccess(true);
        onSuccess && onSuccess(response);
      } else if (response.status === 'incomplete') {
        // Handle 3D Secure or other authentication
        const { error: confirmError } = await stripe.confirmCardPayment(
          response.client_secret
        );

        if (confirmError) {
          throw new Error(confirmError.message);
        } else {
          setSuccess(true);
          onSuccess && onSuccess(response);
        }
      } else {
        throw new Error('Subscription creation failed');
      }

    } catch (err) {
      setError(err.message || 'An unexpected error occurred');
      onError && onError(err);
    } finally {
      setProcessing(false);
    }
  };

  if (success) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Payment Successful!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Your subscription has been activated successfully.
            {trialDays && ` You have ${trialDays} days of free trial.`}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" gap={1}>
            <CreditCard />
            <Typography variant="h6">Payment Information</Typography>
          </Box>
        }
        subheader="Enter your card details to complete your subscription"
      />
      <CardContent>
        <form onSubmit={handleSubmit}>
          <FormControl fullWidth sx={{ mb: 3 }}>
            <Box
              sx={{
                border: '1px solid',
                borderColor: error ? 'error.main' : 'grey.300',
                borderRadius: 1,
                p: 2,
                backgroundColor: 'background.paper',
                '&:hover': {
                  borderColor: error ? 'error.main' : 'primary.main',
                },
                '&:focus-within': {
                  borderColor: 'primary.main',
                  borderWidth: 2,
                },
              }}
            >
              <CardElement
                options={CARD_ELEMENT_OPTIONS}
                onChange={handleCardChange}
              />
            </Box>
            {error && (
              <FormHelperText error>{error}</FormHelperText>
            )}
          </FormControl>

          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Lock sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="caption" color="text.secondary">
              Your payment information is encrypted and secure
            </Typography>
          </Box>

          {trialDays && (
            <>
              <Divider sx={{ my: 2 }} />
              <Alert severity="info" sx={{ mb: 2 }}>
                You won't be charged today. Your {trialDays}-day free trial will begin immediately,
                and billing will start after the trial period ends.
              </Alert>
            </>
          )}

          <Button
            type="submit"
            variant="contained"
            fullWidth
            size="large"
            disabled={!stripe || processing || !cardComplete}
            sx={{ mt: 2 }}
          >
            {processing ? (
              <Box display="flex" alignItems="center" gap={1}>
                <CircularProgress size={20} color="inherit" />
                Processing...
              </Box>
            ) : trialDays ? (
              `Start ${trialDays}-Day Free Trial`
            ) : (
              'Subscribe Now'
            )}
          </Button>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </form>
      </CardContent>
    </Card>
  );
};

const PaymentForm = (props) => {
  return (
    <Elements stripe={stripePromise}>
      <PaymentFormContent {...props} />
    </Elements>
  );
};

export default PaymentForm;
