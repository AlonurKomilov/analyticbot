/**
 * MTProto QR Code Login Component
 * Allows users to login by scanning QR code with Telegram app
 * Supports 2FA password entry when required
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Alert,
  Button,
  CircularProgress,
  Fade,
  TextField,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { QrCode2, Refresh, CheckCircle, Error, Lock, Visibility, VisibilityOff } from '@mui/icons-material';
import { useMTProtoStore } from '../hooks';

interface MTProtoQRCodeLoginProps {
  onSuccess: () => void;
}

export const MTProtoQRCodeLogin: React.FC<MTProtoQRCodeLoginProps> = ({
  onSuccess,
}) => {
  const { requestQRLogin, checkQRStatus, submitQR2FA, isVerifying } = useMTProtoStore();
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);
  const [qrCodeBase64, setQrCodeBase64] = useState<string | null>(null);
  const [expiresIn, setExpiresIn] = useState<number>(0);
  const [status, setStatus] = useState<'idle' | 'loading' | 'waiting' | 'success' | 'error' | '2fa'>('idle');
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const countdownRef = useRef<NodeJS.Timeout | null>(null);
  const hasRequestedRef = useRef(false); // Prevent double requests

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, []);

  // Request QR code
  const requestQR = useCallback(async () => {
    // Prevent multiple simultaneous requests
    if (isRefreshing) return;
    
    setIsRefreshing(true);
    setStatus('loading');
    setStatusMessage('Generating QR code...');
    
    // Clear any existing intervals
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    if (countdownRef.current) {
      clearInterval(countdownRef.current);
      countdownRef.current = null;
    }
    
    try {
      const result = await requestQRLogin();
      
      if (result) {
        setQrCodeUrl(result.qr_code_url);
        setQrCodeBase64(result.qr_code_base64);
        setExpiresIn(result.expires_in);
        setStatus('waiting');
        setStatusMessage('Scan with Telegram app');
        setIsRefreshing(false); // Reset after successful load
        
        // Start countdown
        countdownRef.current = setInterval(() => {
          setExpiresIn(prev => {
            if (prev <= 1) {
              if (countdownRef.current) clearInterval(countdownRef.current);
              if (pollingRef.current) clearInterval(pollingRef.current);
              setStatus('error');
              setStatusMessage('QR code expired. Click refresh to get a new one.');
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
        
        // Start polling for status
        pollingRef.current = setInterval(async () => {
          try {
            const statusResult = await checkQRStatus();
            
            if (statusResult) {
              if (statusResult.status === 'success') {
                // Success!
                if (pollingRef.current) clearInterval(pollingRef.current);
                if (countdownRef.current) clearInterval(countdownRef.current);
                setStatus('success');
                setStatusMessage('Login successful!');
                setTimeout(() => {
                  onSuccess();
                }, 1500);
              } else if (statusResult.status === 'expired') {
                // Expired
                if (pollingRef.current) clearInterval(pollingRef.current);
                if (countdownRef.current) clearInterval(countdownRef.current);
                setStatus('error');
                setStatusMessage('QR code expired. Click refresh to get a new one.');
              } else if (statusResult.status === '2fa_required') {
                // 2FA needed - show password form
                if (pollingRef.current) clearInterval(pollingRef.current);
                if (countdownRef.current) clearInterval(countdownRef.current);
                setStatus('2fa');
                setStatusMessage('Two-factor authentication required');
              }
              // Otherwise keep polling (status === 'pending')
            }
          } catch {
            // Ignore polling errors
          }
        }, 2500); // Poll every 2.5 seconds
      } else {
        setStatus('error');
        setStatusMessage('Failed to generate QR code');
        setIsRefreshing(false);
      }
    } catch (e) {
      setStatus('error');
      setStatusMessage(String((e as { message?: string })?.message || 'Unknown error'));
      setIsRefreshing(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [requestQRLogin, checkQRStatus, onSuccess, isRefreshing]);

  // Auto-request QR on mount - only once
  useEffect(() => {
    if (!hasRequestedRef.current) {
      hasRequestedRef.current = true;
      requestQR();
    }
  }, []); // Empty dependency array - only run on mount

  // Handle 2FA password submission
  const handle2FASubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!password.trim()) {
      setPasswordError('Please enter your password');
      return;
    }
    
    setPasswordError(null);
    
    const result = await submitQR2FA(password);
    
    if (result) {
      if (result.status === 'success') {
        setStatus('success');
        setStatusMessage('Login successful!');
        setTimeout(() => {
          onSuccess();
        }, 1500);
      } else if (result.status === '2fa_required' && result.message.includes('Invalid')) {
        setPasswordError('Invalid password. Please try again.');
      } else {
        setPasswordError(result.message);
      }
    }
  };

  // 2FA Form view
  if (status === '2fa') {
    return (
      <Box>
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>🔐 Two-Factor Authentication Required</strong>
            <br />
            Your Telegram account has 2FA enabled. Please enter your password to complete login.
          </Typography>
        </Alert>

        <Paper sx={{ p: 4 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
            <Lock sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Enter 2FA Password
            </Typography>
            <Typography variant="body2" color="text.secondary" textAlign="center">
              Enter the password you set up in Telegram's Two-Step Verification settings
            </Typography>
          </Box>

          <Box component="form" onSubmit={handle2FASubmit}>
            <TextField
              fullWidth
              label="2FA Password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setPasswordError(null);
              }}
              error={!!passwordError}
              helperText={passwordError}
              disabled={isVerifying}
              autoFocus
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock />
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
              sx={{ mb: 3 }}
            />

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                onClick={() => {
                  setStatus('error');
                  setStatusMessage('Login cancelled. Click refresh to try again.');
                  setPassword('');
                }}
                disabled={isVerifying}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={isVerifying || !password.trim()}
                startIcon={isVerifying ? <CircularProgress size={16} color="inherit" /> : <Lock />}
              >
                {isVerifying ? 'Verifying...' : 'Verify Password'}
              </Button>
            </Box>
          </Box>
        </Paper>
      </Box>
    );
  }

  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Scan QR Code with Telegram</strong>
          <br />
          Open Telegram on your phone → Settings → Devices → Link Desktop Device → Scan QR Code
        </Typography>
      </Alert>

      <Paper 
        sx={{ 
          p: 4, 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          bgcolor: status === 'success' ? 'success.50' : 'background.paper',
          transition: 'background-color 0.3s',
        }}
      >
        {/* QR Code Display */}
        <Box
          sx={{
            width: 256,
            height: 256,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'white',
            borderRadius: 2,
            border: '2px solid',
            borderColor: status === 'success' ? 'success.main' : 'grey.300',
            mb: 2,
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {status === 'loading' && (
            <CircularProgress size={60} />
          )}
          
          {status === 'waiting' && qrCodeBase64 && (
            <Fade in>
              <img 
                src={`data:image/png;base64,${qrCodeBase64}`}
                alt="Telegram Login QR Code"
                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
              />
            </Fade>
          )}
          
          {status === 'waiting' && !qrCodeBase64 && qrCodeUrl && (
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <QrCode2 sx={{ fontSize: 64, color: 'grey.400', mb: 1 }} />
              <Typography variant="caption" color="text.secondary">
                QR image not available.
                <br />
                Please scan: {qrCodeUrl}
              </Typography>
            </Box>
          )}
          
          {status === 'success' && (
            <Fade in>
              <CheckCircle sx={{ fontSize: 100, color: 'success.main' }} />
            </Fade>
          )}
          
          {status === 'error' && (
            <Fade in>
              <Error sx={{ fontSize: 100, color: 'error.main' }} />
            </Fade>
          )}
        </Box>

        {/* Status Message */}
        <Typography 
          variant="body1" 
          color={status === 'success' ? 'success.main' : status === 'error' ? 'error.main' : 'text.secondary'}
          sx={{ mb: 1 }}
        >
          {statusMessage}
        </Typography>

        {/* Countdown */}
        {status === 'waiting' && expiresIn > 0 && (
          <Typography variant="caption" color="text.secondary" sx={{ mb: 2 }}>
            Expires in {expiresIn} seconds
          </Typography>
        )}

        {/* Refresh Button */}
        {(status === 'error' || (status === 'waiting' && expiresIn < 10)) && (
          <Button
            variant="outlined"
            startIcon={isRefreshing ? <CircularProgress size={16} /> : <Refresh />}
            onClick={() => requestQR()}
            disabled={isRefreshing}
          >
            {isRefreshing ? 'Loading...' : 'Get New QR Code'}
          </Button>
        )}

        {/* Loading indicator for success transition */}
        {status === 'success' && (
          <Typography variant="body2" color="success.main">
            Redirecting...
          </Typography>
        )}
      </Paper>

      {/* Instructions */}
      <Box sx={{ mt: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          How to scan:
        </Typography>
        <Typography variant="body2" component="ol" sx={{ pl: 2 }}>
          <li>Open <strong>Telegram</strong> on your phone</li>
          <li>Go to <strong>Settings</strong> → <strong>Devices</strong></li>
          <li>Tap <strong>Link Desktop Device</strong></li>
          <li>Point your camera at this QR code</li>
        </Typography>
      </Box>
    </Box>
  );
};
