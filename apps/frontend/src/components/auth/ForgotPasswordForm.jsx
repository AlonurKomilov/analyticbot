import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  Paper,
  CircularProgress,
  Link
} from '@mui/material';
import { Email as EmailIcon, ArrowBack as ArrowBackIcon } from '@mui/icons-material';

const ForgotPasswordForm = ({ onBackToLogin }) => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email) {
      setError('Email is required');
      return;
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message);
        setIsSubmitted(true);
      } else {
        setError(data.detail || 'Failed to send reset email');
      }
    } catch (err) {
      console.error('Forgot password error:', err);
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isSubmitted) {
    return (
      <Paper elevation={3} sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <EmailIcon sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" component="h1" gutterBottom>
            Check Your Email
          </Typography>
        </Box>

        <Alert severity="success" sx={{ mb: 3 }}>
          {message}
        </Alert>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center' }}>
          We've sent password reset instructions to <strong>{email}</strong>. 
          Please check your email and follow the link to reset your password.
        </Typography>

        <Box sx={{ textAlign: 'center' }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={onBackToLogin}
            variant="outlined"
            fullWidth
          >
            Back to Login
          </Button>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <EmailIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h5" component="h1" gutterBottom>
          Forgot Password
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Enter your email address and we'll send you a link to reset your password.
        </Typography>
      </Box>

      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          label="Email Address"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          margin="normal"
          required
          disabled={isLoading}
          error={!!error}
          helperText={error}
          InputProps={{
            startAdornment: <EmailIcon sx={{ color: 'action.active', mr: 1 }} />,
          }}
        />

        <Button
          type="submit"
          fullWidth
          variant="contained"
          disabled={isLoading}
          sx={{ mt: 3, mb: 2, py: 1.5 }}
        >
          {isLoading ? (
            <>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              Sending Reset Link...
            </>
          ) : (
            'Send Reset Link'
          )}
        </Button>
      </form>

      <Box sx={{ textAlign: 'center', mt: 2 }}>
        <Link
          component="button"
          variant="body2"
          onClick={onBackToLogin}
          sx={{ textDecoration: 'none' }}
        >
          <ArrowBackIcon sx={{ fontSize: 16, mr: 0.5 }} />
          Back to Login
        </Link>
      </Box>
    </Paper>
  );
};

export default ForgotPasswordForm;