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
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useMTProtoStore } from '../hooks';
import type { MTProtoVerifyRequest } from '../types';

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
      // Check if 2FA is needed
      if (error.message?.includes('2FA') || error.message?.includes('password')) {
        setNeeds2FA(true);
      }
      console.error('Verification failed:', error);
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
        <>
          <Alert severity="warning" sx={{ mt: 2, mb: 2 }}>
            <Typography variant="body2">
              Your account has Two-Factor Authentication (2FA) enabled. Please enter your
              password below.
            </Typography>
          </Alert>

          <TextField
            fullWidth
            label="2FA Password"
            type={showPassword ? 'text' : 'password'}
            value={formData.password}
            onChange={handleChange('password')}
            error={!!errors.password}
            helperText={errors.password || 'Your Telegram 2FA password'}
            margin="normal"
            required
            InputProps={{
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
        </>
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
                console.error('Resend failed', e);
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
