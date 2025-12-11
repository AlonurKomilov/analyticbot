/**
 * MTProto Simple Setup Form Component
 * Simplified form that only requires phone number
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
} from '@mui/material';
import { Phone, Send } from '@mui/icons-material';
import { useMTProtoStore } from '../hooks';

interface MTProtoSimpleSetupFormProps {
  onSuccess: () => void;
  onPhoneChange?: (phone: string) => void; // Notify parent of phone changes
}

export const MTProtoSimpleSetupForm: React.FC<MTProtoSimpleSetupFormProps> = ({
  onSuccess,
  onPhoneChange,
}) => {
  const { setupSimple, isSettingUp, error } = useMTProtoStore();
  const [phone, setPhone] = useState('');
  const [phoneError, setPhoneError] = useState<string | null>(null);

  const validatePhone = (): boolean => {
    let cleanPhone = phone.trim();
    
    // Add + if missing
    if (!cleanPhone.startsWith('+')) {
      cleanPhone = '+' + cleanPhone;
    }
    
    // Remove spaces and dashes for validation
    const digits = cleanPhone.replace(/[^\d]/g, '');
    
    if (digits.length < 10) {
      setPhoneError('Phone number must be at least 10 digits with country code');
      return false;
    }
    
    if (digits.length > 15) {
      setPhoneError('Phone number is too long');
      return false;
    }
    
    setPhoneError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validatePhone()) {
      return;
    }

    // Format phone
    let cleanPhone = phone.trim();
    if (!cleanPhone.startsWith('+')) {
      cleanPhone = '+' + cleanPhone;
    }

    const result = await setupSimple(cleanPhone);
    if (result) {
      onSuccess();
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>📱 Quick Setup</strong>
          <br />
          Enter your Telegram phone number to receive a verification code.
          This connects your Telegram account to enable channel history reading.
        </Typography>
      </Alert>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TextField
        fullWidth
        label="Phone Number"
        placeholder="+1234567890"
        value={phone}
        onChange={(e) => {
          const newPhone = e.target.value;
          setPhone(newPhone);
          setPhoneError(null);
          onPhoneChange?.(newPhone); // Notify parent
        }}
        error={!!phoneError}
        helperText={phoneError || 'Enter your phone number with country code (e.g., +1234567890)'}
        required
        sx={{ mb: 3 }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Phone />
            </InputAdornment>
          ),
        }}
      />

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button
          type="submit"
          variant="contained"
          disabled={isSettingUp || !phone.trim()}
          startIcon={isSettingUp ? <CircularProgress size={16} color="inherit" /> : <Send />}
          size="large"
        >
          {isSettingUp ? 'Sending Code...' : 'Send Verification Code'}
        </Button>
      </Box>

      <Alert severity="warning" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>⚠️ Important:</strong> You will receive a code in your Telegram app. 
          Make sure you have access to Telegram on this device or another device to get the code.
        </Typography>
      </Alert>
    </Box>
  );
};
