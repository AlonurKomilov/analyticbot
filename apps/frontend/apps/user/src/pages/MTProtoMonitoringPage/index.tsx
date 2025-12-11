/**
 * MTProto Monitoring Page
 * Comprehensive MTProto status and management dashboard
 *
 * Displays:
 * - Account info with management actions (disconnect, remove, toggle)
 * - Session health metrics
 * - Collection progress
 * - Worker status
 * - Interval boost purchase
 * - Per-channel statistics
 */
import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Alert,
  AlertTitle,
  Switch,
  FormControlLabel,
  Container,
  CircularProgress,
  Button,
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { apiClient } from '@/api/client';
import type { MonitoringData } from './types';
import { formatDate } from './utils';
import {
  AccountInfoCard,
  SessionHealthCard,
  CollectionProgressCard,
  WorkerStatusCard,
  ChannelStatisticsCard,
  IntervalBoostCard,
} from './components';

export const MTProtoMonitoringPage: React.FC = () => {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const fetchMonitoringData = useCallback(async (isBackgroundRefresh = false) => {
    if (!isBackgroundRefresh) {
      setLoading(true);
    } else {
      setIsRefreshing(true);
    }

    if (!isBackgroundRefresh) {
      setError(null);
    }

    try {
      console.log(`📊 ${isBackgroundRefresh ? 'Background' : 'Initial'} fetch MTProto monitoring data...`);
      const response = await apiClient.get<MonitoringData>('/user-mtproto/monitoring/overview');

      if (!response) {
        console.error('❌ Empty response received');
        if (!isBackgroundRefresh) {
          setError('No monitoring data received from server');
          setData(null);
        }
        return;
      }

      setData(response);
      setLastUpdate(new Date());

      if (error) {
        setError(null);
      }

      console.log('✅ Monitoring data updated successfully');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch monitoring data';
      console.error('❌ Monitoring fetch error:', err);

      if (!isBackgroundRefresh || !data) {
        setError(errorMsg);
        setData(null);
      } else {
        console.warn('Background refresh failed, keeping existing data');
      }
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [data, error]);

  useEffect(() => {
    fetchMonitoringData(false);
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchMonitoringData(true);
    }, 10000);

    return () => clearInterval(interval);
  }, [autoRefresh, fetchMonitoringData]);

  // Callback when account status changes (toggle, disconnect, remove)
  const handleAccountStatusChange = useCallback(() => {
    fetchMonitoringData(false);
  }, [fetchMonitoringData]);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="400px">
          <CircularProgress size={60} />
          <Typography variant="body1" sx={{ mt: 2 }}>Loading monitoring data...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">
          <AlertTitle>Error</AlertTitle>
          {error}
        </Alert>
        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
          <Button variant="contained" onClick={() => fetchMonitoringData(false)}>
            Retry
          </Button>
          <Button variant="outlined" onClick={() => window.open(import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:11400', '_blank')}>
            Open API
          </Button>
          <Button variant="text" onClick={() => window.location.reload()}>
            Reload App
          </Button>
        </Box>
      </Container>
    );
  }

  if (!data) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="warning">
          <AlertTitle>No Data</AlertTitle>
          No monitoring data available. Please ensure MTProto is configured.
        </Alert>
        <Box sx={{ mt: 2 }}>
          <Button variant="outlined" onClick={() => fetchMonitoringData(false)}>
            Retry
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Typography variant="h4" component="h1">
              MTProto Monitoring
            </Typography>
            {/* Live indicator */}
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: isRefreshing ? 'primary.main' : 'success.main',
                animation: isRefreshing ? 'pulse 1s ease-in-out infinite' : 'none',
                boxShadow: isRefreshing
                  ? '0 0 8px rgba(25, 118, 210, 0.6)'
                  : '0 0 6px rgba(46, 125, 50, 0.4)',
                '@keyframes pulse': {
                  '0%, 100%': { opacity: 1, transform: 'scale(1)' },
                  '50%': { opacity: 0.6, transform: 'scale(1.2)' },
                },
              }}
              title={isRefreshing ? 'Updating data...' : 'Live - Connected'}
            />
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Real-time collection status and session health
            {lastUpdate && ` • Last updated: ${lastUpdate.toLocaleTimeString()}`}
          </Typography>
        </Box>
        <Box display="flex" gap={2} alignItems="center">
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                color="primary"
              />
            }
            label="Live updates"
          />
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => fetchMonitoringData(false)}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* MTProto Status Alert */}
      {!data.mtproto_enabled && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <AlertTitle>MTProto Disabled</AlertTitle>
          MTProto is currently disabled. Enable it in the Account section below to start collecting data.
        </Alert>
      )}

      {/* Account Info Card - TOP PRIORITY: Shows configuration and management */}
      <AccountInfoCard onStatusChange={handleAccountStatusChange} />

      {/* Session Health Card */}
      <SessionHealthCard sessionHealth={data.session_health} />
      
      {/* Collection Progress Card */}
      <CollectionProgressCard collectionProgress={data.collection_progress} />
      
      {/* Worker Status Card */}
      <WorkerStatusCard workerStatus={data.worker_status} />
      
      {/* Interval Boost Card - Purchase faster collection */}
      <IntervalBoostCard
        currentInterval={data.worker_status.worker_interval_minutes}
        planName={data.worker_status.plan_name || 'free'}
        onBoostPurchased={() => fetchMonitoringData(false)}
      />
      
      {/* Channel Statistics Card */}
      <ChannelStatisticsCard channels={data.channels} />

      {/* Footer Info */}
      <Box textAlign="center" mt={3}>
        <Typography variant="caption" color="text.secondary">
          Last updated: {formatDate(data.timestamp)}
        </Typography>
      </Box>
    </Container>
  );
};

export default MTProtoMonitoringPage;
