/**
 * MTProto Setup Page Component
 * Main wizard for setting up MTProto user client
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
} from '@mui/material';
import { MTProtoStatusCard } from './MTProtoStatusCard';
import { MTProtoCredentialsForm } from './MTProtoCredentialsForm';
import { MTProtoVerificationForm } from './MTProtoVerificationForm';
import { useMTProtoStore } from '../hooks';

const steps = ['Get API Credentials', 'Enter Credentials', 'Verify Phone', 'Complete'];

export const MTProtoSetupPage: React.FC = () => {
  const { status, isLoading, fetchStatus } = useMTProtoStore();
  const [activeStep, setActiveStep] = useState(0);

  // Fetch status on mount
  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  // Determine initial step based on status
  useEffect(() => {
    if (status) {
      if (status.verified) {
        setActiveStep(3); // Complete
      } else if (status.configured) {
        setActiveStep(2); // Need verification
      } else {
        setActiveStep(1); // Need credentials
      }
    }
  }, [status]);

  const handleCredentialsSuccess = () => {
    setActiveStep(2); // Move to verification
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
            <Box>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="subtitle2" gutterBottom>
                  <strong>Step 1: Get Telegram API Credentials</strong>
                </Typography>
                <Typography variant="body2">
                  You need to obtain API credentials from Telegram:
                </Typography>
                <ol style={{ marginTop: 8, marginBottom: 8 }}>
                  <li>
                    Visit{' '}
                    <a
                      href="https://my.telegram.org/apps"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      my.telegram.org/apps
                    </a>
                  </li>
                  <li>Log in with your phone number</li>
                  <li>Click "API development tools"</li>
                  <li>
                    Fill out the form (App title, Short name, Platform, Description)
                  </li>
                  <li>
                    Copy your <strong>api_id</strong> and <strong>api_hash</strong>
                  </li>
                </ol>
              </Alert>

              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button variant="contained" onClick={() => setActiveStep(1)}>
                  I Have My Credentials
                </Button>
              </Box>
            </Box>
          )}

          {activeStep === 1 && (
            <MTProtoCredentialsForm
              onSuccess={handleCredentialsSuccess}
              onBack={() => setActiveStep(0)}
            />
          )}

          {activeStep === 2 && (
            <MTProtoVerificationForm
              onSuccess={handleVerificationSuccess}
              onBack={() => setActiveStep(1)}
            />
          )}

          {activeStep === 3 && (
            <Box>
              <Alert severity="success">
                <Typography variant="subtitle2" gutterBottom>
                  <strong>✅ MTProto Setup Complete!</strong>
                </Typography>
                <Typography variant="body2">
                  Your MTProto user client is now configured and connected. You can now:
                </Typography>
                <ul style={{ marginTop: 8, marginBottom: 0 }}>
                  <li>Read channel message history</li>
                  <li>Analyze existing posts</li>
                  <li>Fetch detailed channel analytics</li>
                  <li>Monitor channel updates in real-time</li>
                </ul>
              </Alert>

              <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
                <Button variant="outlined" href="/channels">
                  Go to Channels
                </Button>
                <Button variant="contained" href="/analytics">
                  View Analytics
                </Button>
              </Box>
            </Box>
          )}
        </Paper>

        {/* Help Section */}
        <Paper sx={{ p: 3, mt: 3, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            What is MTProto?
          </Typography>
          <Typography variant="body2" paragraph>
            MTProto is Telegram's protocol that allows your application to act as a real
            Telegram user. This is different from your bot:
          </Typography>
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2 }}>
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
              <Paper sx={{ p: 2 }}>
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
      </Box>
    </Container>
  );
};
