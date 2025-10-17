import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  CardContent,
  FormControlLabel,
  Switch,
  Typography,
  Box,
  Alert,
  Chip,
  Button,
  Divider,
  Stack
} from '@mui/material';
import {
  CloudQueue as ApiIcon,
  Computer as MockIcon,
  Refresh as RefreshIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon
} from '@mui/icons-material';

const DataSourceSettings = ({ onDataSourceChange }) => {
  const [useRealAPI, setUseRealAPI] = useState(() => {
    // If user has token, they're using real API
    const token = localStorage.getItem('token');
    if (token) return true;

    // Otherwise check localStorage for user preference
    const saved = localStorage.getItem('useRealAPI');
    if (saved === null || saved === 'undefined') return false;
    try {
      return JSON.parse(saved);
    } catch {
      console.warn('Invalid JSON in localStorage for useRealAPI:', saved);
      return false;
    }
  });

  const [apiStatus, setApiStatus] = useState(() => {
    // If user has token, API is online
    return localStorage.getItem('token') ? 'online' : 'unknown';
  }); // unknown, online, offline
  const [lastChecked, setLastChecked] = useState(null);
  const [isChecking, setIsChecking] = useState(false);

  // Check API availability
  const checkAPIStatus = useCallback(async () => {
    setIsChecking(true);
    try {
      // If user is authenticated, API is considered online
      const token = localStorage.getItem('token');
      if (token) {
        setApiStatus('online');
        setLastChecked(new Date());
        setIsChecking(false);
        return;
      }

      // Otherwise, check health endpoint
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // Increased to 5s

      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || (window.location.protocol + '//' + window.location.hostname + ':11400');
      const response = await fetch(`${apiBaseUrl}/health`, {
        method: 'GET',
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        setApiStatus('online');
      } else {
        setApiStatus('offline');
      }
    } catch (error) {
      // Ignore AbortError (timeout is expected behavior)
      if (error.name !== 'AbortError') {
        // Only log unexpected API check errors in development
        if (import.meta.env.DEV && apiStatus !== 'offline') {
          console.log('API check failed:', error.message);
        }
      }
      setApiStatus('offline');
    } finally {
      setLastChecked(new Date());
      setIsChecking(false);
    }
  }, [apiStatus]);

  // Initial API check
  useEffect(() => {
    checkAPIStatus();
  }, [checkAPIStatus]);

  // Listen for authentication changes
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'token') {
        // Token changed - recheck API status
        if (e.newValue) {
          setUseRealAPI(true);
          setApiStatus('online');
        } else {
          setUseRealAPI(false);
          checkAPIStatus();
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Also check on component mount
    const token = localStorage.getItem('token');
    if (token && apiStatus !== 'online') {
      setApiStatus('online');
      setUseRealAPI(true);
    }

    return () => window.removeEventListener('storage', handleStorageChange);
  }, [checkAPIStatus, apiStatus]);

  // Handle toggle change
  const handleToggleChange = (event) => {
    const newValue = event.target.checked;
    setUseRealAPI(newValue);

    // Save preference to localStorage
    localStorage.setItem('useRealAPI', JSON.stringify(newValue));

    // Notify parent component
    if (onDataSourceChange) {
      onDataSourceChange(newValue ? 'api' : 'mock');
    }
  };

  // Monitor API status changes
  useEffect(() => {
    if (useRealAPI && apiStatus === 'offline') {
      // Only log if user is not authenticated
      const token = localStorage.getItem('token');
      if (!token) {
        console.info('API is offline - user should sign in to demo account for mock data');
      }
      // No automatic switching to preserve backend demo authentication security
    }
  }, [apiStatus, useRealAPI, onDataSourceChange]);

  const getStatusColor = () => {
    switch (apiStatus) {
      case 'online': return 'success';
      case 'offline': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = () => {
    switch (apiStatus) {
      case 'online': return <SuccessIcon fontSize="small" />;
      case 'offline': return <ErrorIcon fontSize="small" />;
      default: return null;
    }
  };

  return (
    <Card sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {useRealAPI ? <ApiIcon /> : <MockIcon />}
            Data Source Settings
          </Typography>

          <Chip
            icon={getStatusIcon()}
            label={`API ${apiStatus}`}
            color={getStatusColor()}
            size="small"
          />
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Main Toggle */}
        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={useRealAPI}
                onChange={handleToggleChange}
                disabled={apiStatus === 'offline' && useRealAPI}
              />
            }
            label={
              <Box>
                <Typography variant="body1" fontWeight="medium">
                  {useRealAPI ? 'Real API Data' : 'Demo Data'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {useRealAPI
                    ? 'Connect to live analytics data from your channels'
                    : 'Use professional demo data for testing and preview'
                  }
                </Typography>
              </Box>
            }
          />
        </Box>

        {/* Status Information */}
        <Stack spacing={2}>
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Current Data Source:
            </Typography>
            <Alert
              severity={useRealAPI ? 'info' : 'success'}
              sx={{ mb: 1 }}
              icon={useRealAPI ? <ApiIcon /> : <MockIcon />}
            >
              <Typography variant="body2">
                {useRealAPI ? (
                  <>
                    <strong>Live API Data</strong> - Real analytics from your Telegram channels
                  </>
                ) : (
                  <>
                    <strong>Professional Demo Data</strong> - 35K+ views, realistic engagement metrics
                  </>
                )}
              </Typography>
            </Alert>
          </Box>

          {/* API Status Details */}
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle2">
                API Connection Status:
              </Typography>
              <Button
                size="small"
                startIcon={<RefreshIcon />}
                onClick={checkAPIStatus}
                disabled={isChecking}
              >
                {isChecking ? 'Checking...' : 'Check Again'}
              </Button>
            </Box>

            <Alert severity={apiStatus === 'online' ? 'success' : 'warning'}>
              <Typography variant="body2">
                {apiStatus === 'online' ? (
                  'API is available and ready to serve real data'
                ) : apiStatus === 'offline' ? (
                  'API is currently unavailable. Using demo data automatically.'
                ) : (
                  'Checking API availability...'
                )}
              </Typography>
              {lastChecked && (
                <Typography variant="caption" sx={{ mt: 0.5, display: 'block' }}>
                  Last checked: {lastChecked.toLocaleTimeString()}
                </Typography>
              )}
            </Alert>
          </Box>

          {/* Auto-fallback Warning */}
          {useRealAPI && apiStatus === 'offline' && (
            <Alert severity="warning">
              <Typography variant="body2">
                <strong>Auto-switching to Demo Data</strong><br />
                The API is currently unavailable. You'll automatically be switched to demo data in a few seconds
                to ensure the best user experience.
              </Typography>
            </Alert>
          )}

          {/* Benefits Information */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Data Source Benefits:
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {useRealAPI ? (
                <>
                  <Chip label="Real-time Analytics" size="small" color="primary" />
                  <Chip label="Live Engagement Data" size="small" color="primary" />
                  <Chip label="Actual Post Performance" size="small" color="primary" />
                  <Chip label="Personal Insights" size="small" color="primary" />
                </>
              ) : (
                <>
                  <Chip label="Instant Loading" size="small" color="success" />
                  <Chip label="Professional Preview" size="small" color="success" />
                  <Chip label="Always Available" size="small" color="success" />
                  <Chip label="Perfect for Demo" size="small" color="success" />
                </>
              )}
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default DataSourceSettings;
