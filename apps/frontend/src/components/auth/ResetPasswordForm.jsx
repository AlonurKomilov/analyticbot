import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  Paper,
  CircularProgress,
  InputAdornment,
  IconButton,
  LinearProgress
} from '@mui/material';
import {
  Lock as LockIcon,
  Visibility,
  VisibilityOff,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

const ResetPasswordForm = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Password strength calculation
  const calculatePasswordStrength = (password) => {
    let strength = 0;
    const checks = {
      length: password.length >= 8,
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      numbers: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    strength = Object.values(checks).filter(Boolean).length;
    return { strength, checks };
  };

  const { strength, checks } = calculatePasswordStrength(formData.newPassword);

  const getStrengthColor = () => {
    if (strength <= 2) return 'error';
    if (strength <= 3) return 'warning';
    return 'success';
  };

  const getStrengthText = () => {
    if (strength <= 2) return 'Weak';
    if (strength <= 3) return 'Medium';
    return 'Strong';
  };

  useEffect(() => {
    if (!token) {
      navigate('/login', { replace: true });
    }
  }, [token, navigate]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const validateForm = () => {
    if (!formData.newPassword) {
      return 'New password is required';
    }

    if (formData.newPassword.length < 8) {
      return 'Password must be at least 8 characters long';
    }

    if (formData.newPassword !== formData.confirmPassword) {
      return 'Passwords do not match';
    }

    if (strength < 3) {
      return 'Password is too weak. Please include uppercase, lowercase, numbers, and special characters.';
    }

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          new_password: formData.newPassword
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess(true);
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login', { replace: true });
        }, 3000);
      } else {
        setError(data.detail || 'Failed to reset password');
      }
    } catch (err) {
      console.error('Reset password error:', err);
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <Paper elevation={3} sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <CheckCircleIcon sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" component="h1" gutterBottom color="success.main">
            Password Reset Successful
          </Typography>
        </Box>

        <Alert severity="success" sx={{ mb: 3 }}>
          Your password has been successfully reset. You will be redirected to the login page shortly.
        </Alert>

        <Box sx={{ textAlign: 'center' }}>
          <Button
            variant="contained"
            onClick={() => navigate('/login', { replace: true })}
            fullWidth
          >
            Go to Login
          </Button>
        </Box>
      </Paper>
    );
  }

  if (!token) {
    return null; // Will redirect
  }

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <LockIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h5" component="h1" gutterBottom>
          Reset Password
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Enter your new password below
        </Typography>
      </Box>

      <form onSubmit={handleSubmit}>
        <TextField
          fullWidth
          label="New Password"
          name="newPassword"
          type={showPassword ? 'text' : 'password'}
          value={formData.newPassword}
          onChange={handleInputChange}
          margin="normal"
          required
          disabled={isLoading}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <LockIcon />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowPassword(!showPassword)}
                  edge="end"
                  aria-label="toggle password visibility"
                >
                  {showPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        {formData.newPassword && (
          <Box sx={{ mt: 1, mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="body2" sx={{ mr: 2 }}>
                Password Strength:
              </Typography>
              <Typography variant="body2" color={`${getStrengthColor()}.main`} sx={{ fontWeight: 'bold' }}>
                {getStrengthText()}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={(strength / 5) * 100}
              color={getStrengthColor()}
              sx={{ height: 6, borderRadius: 3 }}
            />
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Password must contain:
              </Typography>
              <Box sx={{ mt: 0.5 }}>
                <Typography variant="caption" color={checks.length ? 'success.main' : 'text.secondary'}>
                  ✓ At least 8 characters
                </Typography>
                <br />
                <Typography variant="caption" color={checks.uppercase ? 'success.main' : 'text.secondary'}>
                  ✓ Uppercase letter
                </Typography>
                <br />
                <Typography variant="caption" color={checks.lowercase ? 'success.main' : 'text.secondary'}>
                  ✓ Lowercase letter
                </Typography>
                <br />
                <Typography variant="caption" color={checks.numbers ? 'success.main' : 'text.secondary'}>
                  ✓ Number
                </Typography>
                <br />
                <Typography variant="caption" color={checks.special ? 'success.main' : 'text.secondary'}>
                  ✓ Special character
                </Typography>
              </Box>
            </Box>
          </Box>
        )}

        <TextField
          fullWidth
          label="Confirm New Password"
          name="confirmPassword"
          type={showConfirmPassword ? 'text' : 'password'}
          value={formData.confirmPassword}
          onChange={handleInputChange}
          margin="normal"
          required
          disabled={isLoading}
          error={formData.confirmPassword && formData.newPassword !== formData.confirmPassword}
          helperText={
            formData.confirmPassword && formData.newPassword !== formData.confirmPassword
              ? 'Passwords do not match'
              : ''
          }
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <LockIcon />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  edge="end"
                  aria-label="toggle confirm password visibility"
                >
                  {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        <Button
          type="submit"
          fullWidth
          variant="contained"
          disabled={isLoading || strength < 3}
          sx={{ mt: 3, mb: 2, py: 1.5 }}
        >
          {isLoading ? (
            <>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              Resetting Password...
            </>
          ) : (
            'Reset Password'
          )}
        </Button>
      </form>
    </Paper>
  );
};

export default ResetPasswordForm;
