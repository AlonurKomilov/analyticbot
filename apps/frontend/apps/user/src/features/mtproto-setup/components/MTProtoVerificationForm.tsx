/**
 * MTProto Verification Form Component
 * Form for entering verification code from Telegram
 */

import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Typography,
  InputAdornment,
  IconButton,
  Paper,
} from '@mui/material';
import { Visibility, VisibilityOff, Lock } from '@mui/icons-material';
import { useMTProtoStore } from '../hooks';
import type { MTProtoVerifyRequest } from '../types';
import { logger } from '@/utils/logger';

interface MTProtoVerificationFormProps {
  onSuccess: () => void;
  onBack?: () => void;
}

export const MTProtoVerificationForm: React.FC<MTProtoVerificationFormProps> = ({
  onSuccess,
  onBack,
}) => {
  const { verify, isVerifying, phoneCodeHash } = useMTProtoStore();
    const { resendSetup, isSettingUp } = useMTProtoStore();
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState<Omit<MTProtoVerifyRequest, 'phone_code_hash'>>({
    verification_code: '',
    password: '',
  });
  const [errors, setErrors] = useState<Partial<Record<keyof MTProtoVerifyRequest, string>>>({});
  const [needs2FA, setNeeds2FA] = useState(false);

  const handleChange = (field: keyof typeof formData) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData((prev) => ({ ...prev, [field]: e.target.value }));
    // Clear error for this field
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof MTProtoVerifyRequest, string>> = {};

    if (!formData.verification_code || formData.verification_code.length < 5) {
      newErrors.verification_code = 'Verification code must be at least 5 characters';
    }

    if (needs2FA && !formData.password) {
      newErrors.password = '2FA password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate() || !phoneCodeHash) {
      return;
    }

    try {
      await verify({
        ...formData,
        phone_code_hash: phoneCodeHash,
        password: formData.password || undefined,
      });
      onSuccess();
    } catch (error: any) {
      // Check if 2FA is needed - look for various indicators
      const errorMsg = error.message?.toLowerCase() || '';
      const errorDetail = error.response?.data?.detail?.toLowerCase() || '';
      const is2FAError = 
        errorMsg.includes('2fa') || 
        errorMsg.includes('password') ||
        errorMsg.includes('two-factor') ||
        errorDetail.includes('2fa') ||
        errorDetail.includes('password') ||
        errorDetail.includes('two-factor');
      
      if (is2FAError && !needs2FA) {
        // Show 2FA input instead of error
        setNeeds2FA(true);
        // Clear any previous errors - this is not an error, just needs more info
        setErrors({});
        logger.info('2FA required, showing password input');
      } else {
        // Real error - show it
        logger.error('Verification failed:', error);
      }
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          Check your Telegram app for the verification code. It should arrive within a few
          seconds.
        </Typography>
      </Alert>

      <TextField
        fullWidth
        label="Verification Code"
        placeholder="12345"
        value={formData.verification_code}
        onChange={handleChange('verification_code')}
        error={!!errors.verification_code}
        helperText={errors.verification_code || 'Code received via Telegram'}
        margin="normal"
        required
        autoFocus
        inputProps={{
          maxLength: 6,
          pattern: '[0-9]*',
        }}
      />

      {needs2FA && (
        <Paper 
          elevation={0} 
          sx={{ 
            mt: 3, 
            p: 3, 
            bgcolor: 'action.hover',
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'warning.main',
          }}
        >
          {/* Lock Icon */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <Lock sx={{ fontSize: 48, color: 'warning.main' }} />
          </Box>
          
          <Typography variant="h6" align="center" gutterBottom>
            Two-Factor Authentication Required
          </Typography>
          
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Your Telegram account has 2FA enabled. Please enter your password to complete login.
          </Typography>

          <TextField
            fullWidth
            label="2FA Password"
            type={showPassword ? 'text' : 'password'}
            value={formData.password}
            onChange={handleChange('password')}
            error={!!errors.password}
            helperText={errors.password || 'Your Telegram 2FA password'}
            required
            autoFocus
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Lock color="action" />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowPassword(!showPassword)}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        </Paper>
      )}



      <Box display="flex" justifyContent="space-between" mt={3}>
        <Box>
          {onBack && (
            <Button onClick={onBack} disabled={isVerifying || isSettingUp}>
              Back
            </Button>
          )}
          <Button
            onClick={async () => {
              if (!phoneCodeHash) return;
              try {
                await resendSetup();
              } catch (e) {
                logger.error('Resend failed', e);
              }
            }}
            disabled={isSettingUp}
            sx={{ ml: 2 }}
          >
            {isSettingUp ? <CircularProgress size={18} /> : 'Resend code'}
          </Button>
        </Box>

        <Button
          type="submit"
          variant="contained"
          disabled={isVerifying}
          startIcon={isVerifying && <CircularProgress size={20} />}
          sx={{ ml: 'auto' }}
        >
          {isVerifying ? 'Verifying...' : 'Verify & Complete Setup'}
        </Button>
      </Box>
    </Box>
  );
};
