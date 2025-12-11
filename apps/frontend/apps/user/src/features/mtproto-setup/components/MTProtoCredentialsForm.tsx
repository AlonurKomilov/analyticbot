/**
 * MTProto Credentials Form Component
 * Form for entering API ID, API Hash, and Phone Number
 */

import React, { useState, useEffect } from 'react';
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
import { logger } from '@/utils/logger';

interface MTProtoCredentialsFormProps {
  onSuccess: () => void;
  onBack?: () => void;
  phone: string; // Phone number from simple form
}

export const MTProtoCredentialsForm: React.FC<MTProtoCredentialsFormProps> = ({
  onSuccess,
  onBack,
  phone,
}) => {
  const { setup, isSettingUp } = useMTProtoStore();
  const [showApiHash, setShowApiHash] = useState(false);
  const [formData, setFormData] = useState<MTProtoSetupRequest>({
    mtproto_api_id: 0,
    telegram_api_hash: '',
    mtproto_phone: phone, // Use phone from prop
  });
  const [errors, setErrors] = useState<Partial<Record<keyof MTProtoSetupRequest, string>>>({});

  const handleChange = (field: keyof MTProtoSetupRequest) => (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = field === 'mtproto_api_id' ? parseInt(e.target.value) || 0 : e.target.value;
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  // Sync phone from prop
  useEffect(() => {
    setFormData(prev => ({ ...prev, mtproto_phone: phone }));
  }, [phone]);

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof MTProtoSetupRequest, string>> = {};

    if (!formData.mtproto_api_id || formData.mtproto_api_id <= 0) {
      newErrors.mtproto_api_id = 'API ID is required and must be positive';
    }

    if (!formData.telegram_api_hash || formData.telegram_api_hash.length < 32) {
      newErrors.telegram_api_hash = 'API Hash must be at least 32 characters';
    }

    if (!phone || !phone.match(/^\+?\d{10,15}$/)) {
      newErrors.mtproto_phone = 'Please enter phone number in the field above first';
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
      logger.error('Setup failed:', error);
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
        label="MTProto API ID"
        type="number"
        value={formData.mtproto_api_id || ''}
        onChange={handleChange('mtproto_api_id')}
        error={!!errors.mtproto_api_id}
        helperText={errors.mtproto_api_id || 'Numeric ID from my.telegram.org'}
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

      {/* Phone number info - using phone from simple form above */}
      {phone ? (
        <Alert severity="success" sx={{ mt: 2 }}>
          Using phone number: <strong>{phone}</strong>
        </Alert>
      ) : (
        <Alert severity="warning" sx={{ mt: 2 }}>
          Please enter your phone number in the "Quick Setup" form above first
        </Alert>
      )}

      {errors.mtproto_phone && (
        <Alert severity="error" sx={{ mt: 1 }}>
          {errors.mtproto_phone}
        </Alert>
      )}

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
