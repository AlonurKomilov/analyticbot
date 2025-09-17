/**
 * 🔒 MFA Setup Component
 * 
 * Two-factor authentication setup interface with QR code generation,
 * backup codes, and verification workflow.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Alert,
  Stepper,  
  Step,
  StepLabel,
  CircularProgress,
  Card,
  CardContent,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Security as SecurityIcon,
  QrCode as QrCodeIcon,
  FileCopy as CopyIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';

const MFASetup = ({ onComplete }) => {
  const { user } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [setupData, setSetupData] = useState(null);
  const [verificationToken, setVerificationToken] = useState('');
  const [error, setError] = useState('');
  const [backupCodesDialog, setBackupCodesDialog] = useState(false);

  const steps = [
    'Setup MFA',
    'Scan QR Code', 
    'Verify Setup',
    'Save Backup Codes'
  ];

  // Start MFA setup
  const initiateSetup = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/mfa/setup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok) {
        setSetupData(data);
        setActiveStep(1);
      } else {
        setError(data.detail || 'Failed to setup MFA');
      }
    } catch (err) {
      console.error('MFA setup error:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Verify setup token
  const verifySetup = async () => {
    if (!verificationToken || verificationToken.length !== 6) {
      setError('Please enter a 6-digit code');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/mfa/verify-setup', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token: verificationToken })
      });

      const data = await response.json();

      if (response.ok) {
        setActiveStep(3);
        setBackupCodesDialog(true);
      } else {
        setError(data.detail || 'Invalid verification code');
      }
    } catch (err) {
      console.error('MFA verification error:', err);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Copy to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  // Download backup codes
  const downloadBackupCodes = () => {
    if (!setupData?.backup_codes) return;

    const content = [
      'AnalyticBot MFA Backup Codes',
      `Generated: ${new Date().toLocaleDateString()}`,
      `User: ${user?.email}`,
      '',
      'Keep these codes safe! Each code can only be used once.',
      '',
      ...setupData.backup_codes.map((code, index) => `${index + 1}. ${code}`)
    ].join('\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'analyticbot-backup-codes.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Complete setup
  const completeSetup = () => {
    setBackupCodesDialog(false);
    if (onComplete) {
      onComplete();
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <SecurityIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Enable Two-Factor Authentication
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Add an extra layer of security to your account
          </Typography>
        </Box>

        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Step 1: Introduction */}
        {activeStep === 0 && (
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Secure Your Account
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Two-factor authentication (2FA) adds an extra layer of security by requiring 
              a code from your mobile device in addition to your password.
            </Typography>
            
            <Alert severity="info" sx={{ mb: 3, textAlign: 'left' }}>
              You'll need an authenticator app like Google Authenticator, Authy, or Microsoft Authenticator.
            </Alert>

            <Button
              variant="contained"
              size="large"
              onClick={initiateSetup}
              disabled={loading}
              sx={{ minWidth: 200 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Start Setup'}
            </Button>
          </Box>
        )}

        {/* Step 2: QR Code */}
        {activeStep === 1 && setupData && (
          <Box>
            <Typography variant="h6" gutterBottom sx={{ textAlign: 'center' }}>
              Scan QR Code
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center' }}>
              Open your authenticator app and scan this QR code
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                {/* QR Code */}
                <Card>
                  <CardContent sx={{ textAlign: 'center' }}>
                    <QrCodeIcon sx={{ fontSize: 48, mb: 2, color: 'primary.main' }} />
                    {setupData.qr_code ? (
                      <img 
                        src={setupData.qr_code} 
                        alt="MFA QR Code"
                        style={{ maxWidth: '100%', height: 'auto' }}
                      />
                    ) : (
                      <Typography>QR Code will appear here</Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                {/* Manual Entry */}
                <Card>
                  <CardContent>
                    <Typography variant="subtitle1" gutterBottom>
                      Can't scan? Enter manually:
                    </Typography>
                    <Box sx={{ 
                      p: 2, 
                      bgcolor: 'grey.100', 
                      borderRadius: 1, 
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
                        {setupData.secret}
                      </Typography>
                      <Tooltip title="Copy Secret">
                        <IconButton size="small" onClick={() => copyToClipboard(setupData.secret)}>
                          <CopyIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Box sx={{ textAlign: 'center', mt: 3 }}>
              <Button variant="contained" onClick={() => setActiveStep(2)}>
                I've Added the Account
              </Button>
            </Box>
          </Box>
        )}

        {/* Step 3: Verification */}
        {activeStep === 2 && (
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Verify Setup
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Enter the 6-digit code from your authenticator app
            </Typography>

            <TextField
              label="Verification Code"
              value={verificationToken}
              onChange={(e) => setVerificationToken(e.target.value.replace(/\D/g, '').slice(0, 6))}
              inputProps={{ 
                maxLength: 6,
                style: { textAlign: 'center', fontSize: '1.5rem', letterSpacing: '0.5rem' }
              }}
              sx={{ mb: 3, minWidth: 200 }}
              placeholder="000000"
            />

            <Box>
              <Button
                variant="contained"
                onClick={verifySetup}
                disabled={loading || verificationToken.length !== 6}
                sx={{ minWidth: 150 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Verify'}
              </Button>
            </Box>
          </Box>
        )}

        {/* Backup Codes Dialog */}
        <Dialog
          open={backupCodesDialog}
          onClose={completeSetup}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle sx={{ textAlign: 'center' }}>
            <CheckIcon sx={{ color: 'success.main', fontSize: 48, mb: 1 }} />
            <Typography variant="h5">
              MFA Successfully Enabled!
            </Typography>
          </DialogTitle>
          
          <DialogContent>
            <Alert severity="warning" sx={{ mb: 3 }}>
              Save these backup codes in a safe place. Each code can only be used once and 
              will help you regain access if you lose your device.
            </Alert>

            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Backup Codes:
              </Typography>
              <Grid container spacing={1}>
                {setupData?.backup_codes?.map((code, index) => (
                  <Grid item xs={6} key={index}>
                    <Chip
                      label={code}
                      variant="outlined"
                      sx={{ fontFamily: 'monospace', width: '100%' }}
                    />
                  </Grid>
                ))}
              </Grid>
            </Box>

            <Box sx={{ textAlign: 'center' }}>
              <Button
                startIcon={<DownloadIcon />}
                onClick={downloadBackupCodes}
                variant="outlined"
                sx={{ mr: 2 }}
              >
                Download Codes
              </Button>
              <Button
                startIcon={<CopyIcon />}
                onClick={() => copyToClipboard(setupData?.backup_codes?.join('\n'))}
                variant="outlined"
              >
                Copy All Codes
              </Button>
            </Box>
          </DialogContent>

          <DialogActions sx={{ justifyContent: 'center', pb: 3 }}>
            <Button variant="contained" onClick={completeSetup} size="large">
              I've Saved My Backup Codes
            </Button>
          </DialogActions>
        </Dialog>
      </Paper>
    </Box>
  );
};

export default MFASetup;