/**
 * Bot Setup Wizard Component
 * Multi-step form for creating and configuring user bots
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Step,
  StepLabel,
  Stepper,
  TextField,
  Typography,
  Paper,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  Link,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  SmartToy,
  Settings,
  CheckCircle,
  Info,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useUserBotStore } from '@/store';
import type { CreateBotRequest } from '@/types';
import toast from 'react-hot-toast';

const steps = ['Bot Credentials', 'Rate Limits', 'Verification'];

interface BotWizardFormData {
  bot_token: string;
  rate_limit_rps: string;
  max_concurrent_requests: string;
  test_message: string;
}

export const BotSetupWizard: React.FC = () => {
  const navigate = useNavigate();
  const { createBot, verifyBot, isCreating, isVerifying, error, clearError, bot } = useUserBotStore();

  const [activeStep, setActiveStep] = useState(0);
  const [showBotToken, setShowBotToken] = useState(false);
  const [formData, setFormData] = useState<BotWizardFormData>({
    bot_token: '',
    rate_limit_rps: '30',
    max_concurrent_requests: '10',
    test_message: 'Hello! Your bot is now configured.',
  });
  const [formErrors, setFormErrors] = useState<Partial<Record<keyof BotWizardFormData, string>>>({});

  // If bot already exists (parent page already checked), redirect to dashboard
  // This handles the case where BotSetupWizard is rendered directly or via BotSetupPage
  useEffect(() => {
    if (bot) {
      toast.success('✅ You already have a bot configured! Redirecting to dashboard...', {
        duration: 3000,
      });
      const timer = setTimeout(() => {
        navigate('/bot/dashboard');
      }, 2000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [bot, navigate]);

  const handleNext = async () => {
    // Validate current step
    if (!validateStep(activeStep)) {
      return;
    }

    // If last step, create and verify bot
    if (activeStep === steps.length - 1) {
      await handleSubmit();
      return;
    }

    // Move to next step
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
    clearError();
  };

  const validateStep = (step: number): boolean => {
    const errors: Partial<Record<keyof BotWizardFormData, string>> = {};

    switch (step) {
      case 0: // Bot Credentials
        if (!formData.bot_token.trim()) {
          errors.bot_token = 'Bot token is required';
        } else if (!formData.bot_token.match(/^\d+:[A-Za-z0-9_-]+$/)) {
          errors.bot_token = 'Invalid bot token format';
        }
        break;

      case 1: // Rate Limits
        const rps = parseFloat(formData.rate_limit_rps);
        if (isNaN(rps) || rps <= 0) {
          errors.rate_limit_rps = 'RPS must be a positive number';
        }

        const concurrent = parseInt(formData.max_concurrent_requests);
        if (isNaN(concurrent) || concurrent <= 0) {
          errors.max_concurrent_requests = 'Max concurrent must be a positive integer';
        }
        break;
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async () => {
    try {
      // Create bot
      const createData: CreateBotRequest = {
        bot_token: formData.bot_token,
        max_requests_per_second: parseFloat(formData.rate_limit_rps),
        max_concurrent_requests: parseInt(formData.max_concurrent_requests),
      };

      await createBot(createData);
      toast.success('🎉 Bot created successfully!');

      // Verify bot
      await verifyBot({ test_message: formData.test_message || undefined });
      toast.success('✅ Bot verified and connected!');

      // Navigate to bot dashboard
      setTimeout(() => {
        navigate('/bot/dashboard');
      }, 1500);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to create bot';

      // Handle specific error cases with helpful messages
      if (errorMessage.includes('already has a bot')) {
        toast.success('✅ You already have a bot configured! Redirecting to dashboard...', {
          duration: 3000,
        });
        setTimeout(() => {
          navigate('/bot/dashboard');
        }, 2000);
      } else if (errorMessage.includes('Invalid bot token')) {
        toast.error('❌ Invalid bot token. Please check your token from @BotFather');
      } else if (errorMessage.includes('Unauthorized')) {
        toast.error('❌ Bot token unauthorized. Make sure it\'s a valid token from @BotFather');
      } else {
        toast.error(`❌ ${errorMessage}`);
      }
    }
  };

  const handleChange = (field: keyof BotWizardFormData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setFormData({ ...formData, [field]: event.target.value });
    // Clear error for this field
    if (formErrors[field]) {
      setFormErrors({ ...formErrors, [field]: undefined });
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Enter Your Bot Token
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Get your bot token from{' '}
              <a href="https://t.me/BotFather" target="_blank" rel="noopener noreferrer">
                @BotFather
              </a>{' '}
              on Telegram
            </Typography>
            <TextField
              fullWidth
              label="Bot Token"
              value={formData.bot_token}
              onChange={handleChange('bot_token')}
              error={!!formErrors.bot_token}
              helperText={formErrors.bot_token || 'Format: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'}
              type={showBotToken ? 'text' : 'password'}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SmartToy />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowBotToken(!showBotToken)} edge="end">
                      {showBotToken ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Alert severity="info" sx={{ mt: 3 }} icon={<Info />}>
              <Typography variant="body2">
                <strong>Need MTProto for advanced features?</strong>
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                MTProto API setup is now separate and optional. Configure it later in{' '}
                <Link href="/settings/mtproto-setup" underline="hover">
                  Settings → MTProto Setup
                </Link>
                {' '}to enable features like:
              </Typography>
              <ul style={{ marginTop: '4px', marginBottom: 0, paddingLeft: '20px' }}>
                <li>Access to private channels/groups</li>
                <li>User account authentication</li>
                <li>Advanced Telegram features</li>
              </ul>
            </Alert>
          </Box>
        );

      case 1:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Configure Rate Limits
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Set request limits for your bot
            </Typography>
            <TextField
              fullWidth
              label="Requests Per Second (RPS)"
              value={formData.rate_limit_rps}
              onChange={handleChange('rate_limit_rps')}
              error={!!formErrors.rate_limit_rps}
              helperText={formErrors.rate_limit_rps || 'Maximum requests per second (default: 30)'}
              type="number"
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Settings />
                  </InputAdornment>
                ),
              }}
            />
            <TextField
              fullWidth
              label="Max Concurrent Requests"
              value={formData.max_concurrent_requests}
              onChange={handleChange('max_concurrent_requests')}
              error={!!formErrors.max_concurrent_requests}
              helperText={
                formErrors.max_concurrent_requests || 'Maximum concurrent requests (default: 10)'
              }
              type="number"
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Settings />
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        );

      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Test Your Bot
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Optional: Send a test message to verify your bot is working
            </Typography>
            <TextField
              fullWidth
              label="Test Message (Optional)"
              value={formData.test_message}
              onChange={handleChange('test_message')}
              multiline
              rows={3}
              helperText="We'll send this message from your bot to verify it works"
            />
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2" component="div">
                Once you click "Create & Verify Bot", we will:
              </Typography>
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                <li>Create your bot with the provided credentials</li>
                <li>Initialize the bot instance</li>
                <li>Send the test message (if provided)</li>
                <li>Mark your bot as verified</li>
              </ul>
            </Alert>
          </Box>
        );

      default:
        return null;
    }
  };

  const isLastStep = activeStep === steps.length - 1;
  const isLoading = isCreating || isVerifying;

  return (
    <Paper sx={{ p: 4, maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Setup Your Bot
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph align="center">
        Follow these steps to create and configure your multi-tenant bot
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mt: 4, mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={clearError}>
          {error}
        </Alert>
      )}

      <Box sx={{ minHeight: 300, mb: 4 }}>{renderStepContent(activeStep)}</Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button disabled={activeStep === 0 || isLoading} onClick={handleBack}>
          Back
        </Button>
        <Button
          variant="contained"
          onClick={handleNext}
          disabled={isLoading}
          startIcon={isLoading ? <CircularProgress size={20} /> : isLastStep ? <CheckCircle /> : null}
        >
          {isLoading ? 'Processing...' : isLastStep ? 'Create & Verify Bot' : 'Next'}
        </Button>
      </Box>
    </Paper>
  );
};
