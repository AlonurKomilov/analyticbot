/**
 * MTProto Setup Page Component
 * Main wizard for setting up MTProto user client
 * Now uses simplified setup (phone only) by default
 * Includes risk warning and QR code login option
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  Alert,
  Button,
  Grid,
  Collapse,
  Link,
  Chip,
} from '@mui/material';
import { ExpandMore, ExpandLess, CheckCircle, Settings, Analytics, ListAlt } from '@mui/icons-material';
import { MTProtoStatusCard } from './MTProtoStatusCard';
import { MTProtoRiskWarning } from './MTProtoRiskWarning';
import { MTProtoSimpleSetupForm } from './MTProtoSimpleSetupForm';
import { MTProtoCredentialsForm } from './MTProtoCredentialsForm';
import { MTProtoVerificationForm } from './MTProtoVerificationForm';
import { MTProtoQRCodeLogin } from './MTProtoQRCodeLogin';
import { useMTProtoStore } from '../hooks';

// Steps now include risk warning first
const steps = ['Read Warning', 'Enter Phone / QR', 'Verify Code', 'Complete'];

export const MTProtoSetupPage: React.FC = () => {
  const { status, isLoading, fetchStatus } = useMTProtoStore();
  const [activeStep, setActiveStep] = useState(0);
  const [showAdvanced, setShowAdvanced] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_hasAcceptedRisk, setHasAcceptedRisk] = useState(false);
  const [useQRLogin, setUseQRLogin] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState(''); // Shared phone for simple and advanced forms

  // Fetch status on mount
  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Determine initial step based on status
  useEffect(() => {
    if (status) {
      if (status.verified) {
        setActiveStep(3); // Complete (step index 3 in new 4-step flow)
        setHasAcceptedRisk(true); // Already set up, no need for warning
      } else if (status.configured) {
        setActiveStep(2); // Need verification
        setHasAcceptedRisk(true); // Already started setup
      } else {
        setActiveStep(0); // Start from warning
      }
    }
  }, [status]);

  const handleRiskAccepted = () => {
    setHasAcceptedRisk(true);
    setActiveStep(1); // Move to phone/QR entry
  };

  const handleRiskDeclined = () => {
    // Go back to channels or previous page
    window.history.back();
  };

  const handlePhoneSuccess = () => {
    setActiveStep(2); // Move to verification
  };

  const handleCredentialsSuccess = () => {
    setActiveStep(2); // Move to verification (for advanced mode)
  };

  const handleQRSuccess = () => {
    setActiveStep(3); // QR login completes directly
  };

  const handleVerificationSuccess = () => {
    setActiveStep(3); // Move to complete
  };

  if (isLoading) {
    return (
      <Container maxWidth="md">
        <Box sx={{ py: 4, textAlign: 'center' }}>
          <Typography>Loading...</Typography>
        </Box>
      </Container>
    );
  }

  // If MTProto is verified, show the clean completed view
  if (status?.verified) {
    return (
      <Container maxWidth="md">
        <Box sx={{ py: 4 }}>
          {/* Success Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
            <Typography variant="h4" gutterBottom>
              MTProto Connected
            </Typography>
            <Chip
              label="Active"
              color="success"
              size="small"
              sx={{ mb: 2 }}
            />
            <Typography variant="body1" color="text.secondary">
              Your Telegram account is connected and ready to use
            </Typography>
          </Box>

          {/* Status Card */}
          <Box sx={{ mb: 4 }}>
            <MTProtoStatusCard />
          </Box>

          {/* Quick Actions */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              What you can do now
            </Typography>

            <Grid container spacing={3} sx={{ mt: 1 }}>
              <Grid item xs={12} md={4}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    textAlign: 'center',
                    bgcolor: 'action.hover',
                    borderRadius: 2,
                    height: '100%',
                  }}
                >
                  <ListAlt sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Channel History
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Read full message history from your channels
                  </Typography>
                  <Button variant="outlined" size="small" href="/channels">
                    Go to Channels
                  </Button>
                </Paper>
              </Grid>

              <Grid item xs={12} md={4}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    textAlign: 'center',
                    bgcolor: 'action.hover',
                    borderRadius: 2,
                    height: '100%',
                  }}
                >
                  <Analytics sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Analytics
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    View detailed post and channel analytics
                  </Typography>
                  <Button variant="contained" size="small" href="/analytics">
                    View Analytics
                  </Button>
                </Paper>
              </Grid>

              <Grid item xs={12} md={4}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    textAlign: 'center',
                    bgcolor: 'action.hover',
                    borderRadius: 2,
                    height: '100%',
                  }}
                >
                  <Settings sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Settings
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Manage MTProto connection settings
                  </Typography>
                  <Button variant="text" size="small" href="/settings">
                    Open Settings
                  </Button>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        </Box>
      </Container>
    );
  }

  // Show setup wizard for unconfigured users
  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          MTProto Setup
        </Typography>

        <Typography variant="body1" color="text.secondary" paragraph>
          Configure MTProto to enable reading channel history and analyzing posts.
        </Typography>

        {/* Current Status */}
        <Box sx={{ mb: 3 }}>
          <MTProtoStatusCard />
        </Box>

        {/* Setup Wizard */}
        <Paper sx={{ p: 3 }}>
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Step Content */}
          {activeStep === 0 && (
            <MTProtoRiskWarning
              onAccept={handleRiskAccepted}
              onDecline={handleRiskDeclined}
            />
          )}

          {activeStep === 1 && (
            <Box>
              {/* Login Method Tabs */}
              <Box sx={{ mb: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant={!useQRLogin ? 'contained' : 'outlined'}
                  onClick={() => setUseQRLogin(false)}
                >
                  📱 Phone Number
                </Button>
                <Button
                  variant={useQRLogin ? 'contained' : 'outlined'}
                  onClick={() => setUseQRLogin(true)}
                >
                  📷 QR Code
                </Button>
              </Box>

              {!useQRLogin ? (
                <>
                  <MTProtoSimpleSetupForm
                    onSuccess={handlePhoneSuccess}
                    onPhoneChange={setPhoneNumber}
                  />

                  {/* Advanced Option - Hidden by default */}
                  <Box sx={{ mt: 3, borderTop: 1, borderColor: 'divider', pt: 2 }}>
                    <Button
                      size="small"
                      startIcon={showAdvanced ? <ExpandLess /> : <ExpandMore />}
                      onClick={() => setShowAdvanced(!showAdvanced)}
                      sx={{ color: 'text.secondary' }}
                    >
                      {showAdvanced ? 'Hide' : 'Show'} Advanced Options
                    </Button>

                    <Collapse in={showAdvanced}>
                      <Alert severity="info" sx={{ mt: 2 }}>
                        <Typography variant="body2">
                          <strong>Advanced: Use Your Own API Credentials</strong>
                          <br />
                          If you prefer to use your own Telegram API credentials, you can get them from{' '}
                          <Link href="https://my.telegram.org/apps" target="_blank" rel="noopener noreferrer">
                            my.telegram.org/apps
                          </Link>
                        </Typography>
                      </Alert>
                      <Box sx={{ mt: 2 }}>
                        <MTProtoCredentialsForm
                          onSuccess={handleCredentialsSuccess}
                          phone={phoneNumber}
                        />
                      </Box>
                    </Collapse>
                  </Box>
                </>
              ) : (
                <MTProtoQRCodeLogin onSuccess={handleQRSuccess} />
              )}
            </Box>
          )}

          {activeStep === 2 && (
            <MTProtoVerificationForm
              onSuccess={handleVerificationSuccess}
              onBack={() => setActiveStep(1)}
            />
          )}

          {activeStep === 3 && (
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Setup Complete!
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Redirecting to your MTProto dashboard...
              </Typography>
              <Button
                variant="contained"
                onClick={() => window.location.reload()}
              >
                View Dashboard
              </Button>
            </Box>
          )}
        </Paper>

        {/* Help Section - Only show during initial steps (0 or 1) */}
        {activeStep <= 1 && (
          <Paper sx={{ p: 3, mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              What is MTProto?
            </Typography>
            <Typography variant="body2" paragraph>
              MTProto is Telegram's protocol that allows your application to act as a real
              Telegram user. This is different from your bot:
            </Typography>
            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, bgcolor: 'action.hover' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    🤖 Telegram Bot
                  </Typography>
                  <Typography variant="body2">
                    • Send messages
                    <br />
                    • Receive commands
                    <br />
                    • Manage channels
                    <br />• ❌ Cannot read history
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, bgcolor: 'action.hover' }}>
                  <Typography variant="subtitle2" gutterBottom>
                    👤 MTProto Client
                  </Typography>
                  <Typography variant="body2">
                    • Read all messages
                    <br />
                    • Access full history
                    <br />
                    • Get detailed analytics
                    <br />• ✅ Full channel access
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        )}
      </Box>
    </Container>
  );
};
