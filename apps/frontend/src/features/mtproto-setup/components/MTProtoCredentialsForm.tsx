/**
 * MTProto Credentials Form Component
 * Form for entering API ID, API Hash, and Phone Number
 */

import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Typography,
  Link,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';
import { useMTProtoStore } from '../hooks';
import type { MTProtoSetupRequest } from '../types';

interface MTProtoCredentialsFormProps {
  onSuccess: () => void;
  onBack?: () => void;
}

export const MTProtoCredentialsForm: React.FC<MTProtoCredentialsFormProps> = ({
  onSuccess,
  onBack,
}) => {
  const { setup, isSettingUp } = useMTProtoStore();
  const [showApiHash, setShowApiHash] = useState(false);
  const [formData, setFormData] = useState<MTProtoSetupRequest>({
    telegram_api_id: 0,
    telegram_api_hash: '',
    telegram_phone: '',
  });
  const [errors, setErrors] = useState<Partial<Record<keyof MTProtoSetupRequest, string>>>({});

  const handleChange = (field: keyof MTProtoSetupRequest) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = field === 'telegram_api_id' ? parseInt(e.target.value) || 0 : e.target.value;
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof MTProtoSetupRequest, string>> = {};

    if (!formData.telegram_api_id || formData.telegram_api_id <= 0) {
      newErrors.telegram_api_id = 'API ID is required and must be positive';
    }

    if (!formData.telegram_api_hash || formData.telegram_api_hash.length < 32) {
      newErrors.telegram_api_hash = 'API Hash must be at least 32 characters';
    }

    if (!formData.telegram_phone || !formData.telegram_phone.match(/^\+\d{10,15}$/)) {
      newErrors.telegram_phone = 'Phone must start with + and contain 10-15 digits';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      const result = await setup(formData);
      if (result) {
        onSuccess();
      }
    } catch (error) {
      // Error already handled by store
      console.error('Setup failed:', error);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          <strong>Get your Telegram API credentials:</strong>
        </Typography>
        <ol style={{ marginTop: 8, marginBottom: 0, paddingLeft: 20 }}>
          <li>
            Visit{' '}
            <Link
              href="https://my.telegram.org/apps"
              target="_blank"
              rel="noopener noreferrer"
            >
              my.telegram.org/apps
            </Link>
          </li>
          <li>Log in with your phone number</li>
          <li>Click "API development tools"</li>
          <li>Fill out the form (App title, Short name, Platform, Description)</li>
          <li>
            Copy your <strong>api_id</strong> and <strong>api_hash</strong>
          </li>
        </ol>
      </Alert>

      <TextField
        fullWidth
        label="Telegram API ID"
        type="number"
        value={formData.telegram_api_id || ''}
        onChange={handleChange('telegram_api_id')}
        error={!!errors.telegram_api_id}
        helperText={errors.telegram_api_id || 'Numeric ID from my.telegram.org'}
        margin="normal"
        required
      />

      <TextField
        fullWidth
        label="Telegram API Hash"
        type={showApiHash ? 'text' : 'password'}
        value={formData.telegram_api_hash}
        onChange={handleChange('telegram_api_hash')}
        error={!!errors.telegram_api_hash}
        helperText={errors.telegram_api_hash || '32+ character hash from my.telegram.org'}
        margin="normal"
        required
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={() => setShowApiHash(!showApiHash)}
                edge="end"
              >
                {showApiHash ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />

      <TextField
        fullWidth
        label="Phone Number"
        placeholder="+1234567890"
        value={formData.telegram_phone}
        onChange={handleChange('telegram_phone')}
        error={!!errors.telegram_phone}
        helperText={
          errors.telegram_phone || 'Your Telegram phone number with country code'
        }
        margin="normal"
        required
      />

      <Box display="flex" justifyContent="space-between" mt={3}>
        {onBack && (
          <Button onClick={onBack} disabled={isSettingUp}>
            Back
          </Button>
        )}
        <Button
          type="submit"
          variant="contained"
          disabled={isSettingUp}
          startIcon={isSettingUp && <CircularProgress size={20} />}
          sx={{ ml: 'auto' }}
        >
          {isSettingUp ? 'Sending Code...' : 'Send Verification Code'}
        </Button>
      </Box>
    </Box>
  );
};
