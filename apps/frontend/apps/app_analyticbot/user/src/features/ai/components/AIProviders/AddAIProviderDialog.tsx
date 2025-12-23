/**
 * Add AI Provider Dialog Component
 * Form to add a new AI provider with API key
 */

import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Box,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  Link,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  OpenInNew as ExternalLinkIcon,
} from '@mui/icons-material';
import type { AIProvider, AddProviderRequest } from '../../api/aiProvidersAPI';

interface AddAIProviderDialogProps {
  open: boolean;
  onClose: () => void;
  availableProviders: AIProvider[];
  onSubmit: (data: AddProviderRequest) => Promise<any>;
  isLoading: boolean;
}

export const AddAIProviderDialog: React.FC<AddAIProviderDialogProps> = ({
  open,
  onClose,
  availableProviders,
  onSubmit,
  isLoading,
}) => {
  const theme = useTheme();
  const [formData, setFormData] = useState<AddProviderRequest>({
    provider: '',
    api_key: '',
    model: '',
    monthly_budget: undefined,
  });
  const [showApiKey, setShowApiKey] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedProvider = availableProviders.find((p) => p.name === formData.provider);

  const handleProviderChange = (provider: string) => {
    const providerData = availableProviders.find((p) => p.name === provider);
    setFormData({
      provider,
      api_key: '',
      model: providerData?.default_model || '',
      monthly_budget: undefined,
    });
    setError(null);
  };

  const handleSubmit = async () => {
    setError(null);

    // Validation
    if (!formData.provider) {
      setError('Please select a provider');
      return;
    }
    if (!formData.api_key.trim()) {
      setError('Please enter your API key');
      return;
    }
    if (!formData.model) {
      setError('Please select a model');
      return;
    }

    try {
      await onSubmit(formData);
      handleClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add provider');
    }
  };

  const handleClose = () => {
    setFormData({
      provider: '',
      api_key: '',
      model: '',
      monthly_budget: undefined,
    });
    setError(null);
    setShowApiKey(false);
    onClose();
  };

  const providerLinks: Record<string, string> = {
    openai: 'https://platform.openai.com/api-keys',
    claude: 'https://console.anthropic.com/settings/keys',
    gemini: 'https://aistudio.google.com/app/apikey',
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Add AI Provider</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 1 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {/* Provider Selection */}
          <TextField
            select
            fullWidth
            label="AI Provider"
            value={formData.provider}
            onChange={(e) => handleProviderChange(e.target.value)}
            margin="normal"
            required
          >
            {availableProviders.map((provider) => (
              <MenuItem key={provider.name} value={provider.name}>
                {provider.display_name}
              </MenuItem>
            ))}
          </TextField>

          {/* Provider Info */}
          {selectedProvider && (
            <Box
              sx={{
                mt: 2,
                p: 2,
                bgcolor: alpha(theme.palette.primary.main, 0.05),
                borderRadius: 1,
              }}
            >
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {selectedProvider.description || `Connect your ${selectedProvider.display_name} account`}
              </Typography>
              {providerLinks[selectedProvider.name] && (
                <Link
                  href={providerLinks[selectedProvider.name]}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 0.5,
                    mt: 1,
                    fontSize: '0.875rem',
                  }}
                >
                  Get API Key
                  <ExternalLinkIcon sx={{ fontSize: 14 }} />
                </Link>
              )}
            </Box>
          )}

          {/* API Key Input */}
          <TextField
            fullWidth
            label="API Key"
            type={showApiKey ? 'text' : 'password'}
            value={formData.api_key}
            onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
            margin="normal"
            required
            placeholder={
              formData.provider === 'openai'
                ? 'sk-proj-...'
                : formData.provider === 'claude'
                ? 'sk-ant-...'
                : 'Your API key'
            }
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={() => setShowApiKey(!showApiKey)}
                    edge="end"
                    size="small"
                  >
                    {showApiKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                  </IconButton>
                </InputAdornment>
              ),
            }}
            helperText="Your API key is encrypted and never exposed"
          />

          {/* Model Selection */}
          {selectedProvider && (
            <TextField
              select
              fullWidth
              label="Model"
              value={formData.model}
              onChange={(e) => setFormData({ ...formData, model: e.target.value })}
              margin="normal"
              required
            >
              {selectedProvider.available_models.map((model) => (
                <MenuItem key={model} value={model}>
                  {model}
                </MenuItem>
              ))}
            </TextField>
          )}

          {/* Monthly Budget */}
          <TextField
            fullWidth
            label="Monthly Budget (Optional)"
            type="number"
            value={formData.monthly_budget || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                monthly_budget: e.target.value ? parseFloat(e.target.value) : undefined,
              })
            }
            margin="normal"
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>,
            }}
            helperText="Set a spending limit to prevent overage charges"
          />

          {/* Security Notice */}
          <Alert severity="info" sx={{ mt: 2 }}>
            🔒 Your API key will be encrypted using AES-128 encryption before storage.
            We never store or transmit your key in plain text.
          </Alert>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={isLoading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isLoading || !formData.provider || !formData.api_key}
        >
          {isLoading ? 'Adding...' : 'Add Provider'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
