/**
 * MTProto Monitoring Page
 * Comprehensive MTProto status and management dashboard
 *
 * Displays:
 * - Account info with management actions (disconnect, remove, toggle)
 * - Active MTProto Power-Ups (subscribed services)
 * - Available MTProto Upgrades (services to purchase)
 * - Session health metrics
 * - Collection progress
 * - Worker status
 * - Interval boost purchase
 * - Per-channel statistics
 * - Quick Actions
 */
import React, { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Paper,
  alpha,
} from '@mui/material';
import { Refresh, Wifi, WifiOff, SignalCellular4Bar } from '@mui/icons-material';
import { apiClient } from '@/api/client';
import toast from 'react-hot-toast';
import type { MonitoringData } from './types';
import { formatDate } from './utils';
import {
  AccountInfoCard,
  SessionHealthCard,
  CollectionProgressCard,
  CollectionControlCard,
  ChannelStatisticsCard,
  ActiveMTProtoServicesCard,
  AvailableMTProtoUpgradesCard,
} from './components';
import { useMTProtoServices, useMTProtoConnection } from './hooks';

export const MTProtoMonitoringPage: React.FC = () => {
  const { t } = useTranslation(['mtproto', 'common']);
  const navigate = useNavigate();
  
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [removeDialogOpen, setRemoveDialogOpen] = useState(false);
  const [isRemoving, setIsRemoving] = useState(false);

  // Fetch MTProto services (subscriptions and catalog)
  const {
    activeServices,
    availableServices,
    activeServiceKeys,
    isLoading: isLoadingServices,
  } = useMTProtoServices();

  // MTProto connection testing
  const { isTesting, checkConnection } = useMTProtoConnection();

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

  // Quick Actions handlers
  const handleCheckStatus = async () => {
    try {
      await checkConnection();
      toast.success(t('mtproto:quickActions.checkSuccess', '✅ MTProto connection is working!'));
    } catch (err) {
      toast.error(t('mtproto:quickActions.checkFailed', '❌ Connection check failed'));
    }
  };

  const handleBrowsePowerUps = () => {
    navigate('/marketplace?tab=services&category=mtproto_services');
  };

  const handleRemoveMTProto = async () => {
    try {
      setIsRemoving(true);
      await apiClient.delete('/user-mtproto/remove');
      toast.success(t('mtproto:quickActions.removeSuccess', 'MTProto configuration removed'));
      setRemoveDialogOpen(false);
      fetchMonitoringData(false);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || t('mtproto:quickActions.removeFailed', 'Failed to remove MTProto'));
    } finally {
      setIsRemoving(false);
    }
  };

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
      {/* Enhanced Header */}
      <Paper
        elevation={0}
        sx={{
          mb: 4,
          p: 3,
          background: data.mtproto_enabled
            ? 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(103, 58, 183, 0.1) 100%)'
            : 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(158, 158, 158, 0.1) 100%)',
          border: data.mtproto_enabled
            ? '1px solid rgba(33, 150, 243, 0.2)'
            : '1px solid rgba(255, 152, 0, 0.2)',
          borderRadius: 2,
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 1.5,
                  bgcolor: data.mtproto_enabled ? alpha('#2196F3', 0.15) : alpha('#ff9800', 0.15),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: data.mtproto_enabled ? '#2196F3' : '#ff9800',
                }}
              >
                {data.mtproto_enabled ? <Wifi sx={{ fontSize: 28 }} /> : <WifiOff sx={{ fontSize: 28 }} />}
              </Box>
              <Box>
                <Typography variant="h4" component="h1" fontWeight={700}>
                  {t('mtproto:title', 'MTProto Monitoring')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('mtproto:subtitle', 'Real-time collection status and session health')}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mt: 2 }}>
              {/* Live Indicator */}
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                  px: 1,
                  py: 0.25,
                  borderRadius: 1,
                  bgcolor: 'background.paper',
                }}
              >
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
                />
                <Typography variant="caption" color="text.secondary">
                  {isRefreshing ? t('common:updating', 'Updating...') : t('common:live', 'Live')}
                </Typography>
              </Box>
              {lastUpdate && (
                <Typography variant="caption" color="text.secondary">
                  • {t('common:lastUpdate', 'Last update')}: {lastUpdate.toLocaleTimeString()}
                </Typography>
              )}
            </Box>
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
              label={t('common:liveUpdates', 'Live updates')}
            />
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={() => fetchMonitoringData(false)}
              sx={{
                background: 'linear-gradient(135deg, #2196F3 0%, #673AB7 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #1976D2 0%, #5E35B1 100%)',
                },
              }}
            >
              {t('common:refresh', 'Refresh')}
            </Button>
          </Box>
        </Box>
      </Paper>
      {/* MTProto Status Alert */}
      {!data.mtproto_enabled && (
        <Alert 
          severity="warning" 
          sx={{ 
            mb: 3,
            background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 193, 7, 0.05) 100%)',
            border: '1px solid rgba(255, 152, 0, 0.3)',
          }}
        >
          <AlertTitle sx={{ fontWeight: 600 }}>{t('mtproto:status.disabled', 'MTProto Disabled')}</AlertTitle>
          {t('mtproto:status.disabledDesc', 'MTProto is currently disabled. Enable it in the Account section below to start collecting data.')}
        </Alert>
      )}

      {/* Account Info Card - TOP PRIORITY: Shows configuration and management */}
      <Box id="account-info-card">
        <AccountInfoCard onStatusChange={handleAccountStatusChange} />
      </Box>

      {/* Active MTProto Power-Ups Section */}
      <ActiveMTProtoServicesCard
        services={activeServices}
        isLoading={isLoadingServices}
      />

      {/* Available MTProto Upgrades Section */}
      <AvailableMTProtoUpgradesCard
        services={availableServices}
        activeServiceKeys={activeServiceKeys}
        isLoading={isLoadingServices}
      />

      {/* Session Health Card */}
      <SessionHealthCard sessionHealth={data.session_health} />

      {/* Collection Progress Card */}
      <CollectionProgressCard collectionProgress={data.collection_progress} />

      {/* Collection Control Card - Combined Worker Status + Boost Options */}
      <CollectionControlCard
        workerStatus={data.worker_status}
        onBoostPurchased={() => fetchMonitoringData(false)}
      />

      {/* Channel Statistics Card */}
      <ChannelStatisticsCard channels={data.channels} />

      {/* Quick Actions Bar */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          mb: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 2,
          flexWrap: 'wrap',
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.06) 0%, rgba(139, 92, 246, 0.06) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.15)',
          borderRadius: 2,
        }}
      >
        <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
          {t('mtproto:quickActions.title', 'Quick Actions')}:
        </Typography>
        <Button
          variant="contained"
          size="small"
          startIcon={<Refresh />}
          onClick={handleCheckStatus}
          disabled={isTesting}
          sx={{
            background: 'linear-gradient(135deg, #4CAF50 0%, #2196F3 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #2196F3 0%, #4CAF50 100%)',
            },
          }}
        >
          {isTesting 
            ? t('mtproto:quickActions.checking', 'Checking...')
            : t('mtproto:quickActions.checkStatus', 'Check Status')
          }
        </Button>
        <Button
          variant="contained"
          size="small"
          startIcon={<SignalCellular4Bar />}
          onClick={handleBrowsePowerUps}
          sx={{
            background: 'linear-gradient(135deg, #9C27B0 0%, #E91E63 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #E91E63 0%, #9C27B0 100%)',
            },
          }}
        >
          {t('mtproto:quickActions.browsePowerUps', 'Browse Power-Ups')}
        </Button>
      </Paper>

      {/* Remove MTProto Confirmation Dialog */}
      <Dialog
        open={removeDialogOpen}
        onClose={() => setRemoveDialogOpen(false)}
      >
        <DialogTitle>{t('mtproto:quickActions.removeConfirmTitle', 'Remove MTProto Configuration?')}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {t('mtproto:quickActions.removeConfirmDesc', 'This will permanently delete your MTProto configuration including your session. You will need to set it up again to use MTProto features.')}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRemoveDialogOpen(false)}>
            {t('common:cancel', 'Cancel')}
          </Button>
          <Button 
            onClick={handleRemoveMTProto} 
            color="error" 
            variant="contained"
            disabled={isRemoving}
          >
            {isRemoving ? t('common:removing', 'Removing...') : t('common:remove', 'Remove')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Footer Info */}
      <Paper
        elevation={0}
        sx={{
          mt: 3,
          p: 2,
          textAlign: 'center',
          background: 'linear-gradient(135deg, rgba(158, 158, 158, 0.05) 0%, rgba(158, 158, 158, 0.02) 100%)',
          border: '1px solid rgba(158, 158, 158, 0.1)',
          borderRadius: 2,
        }}
      >
        <Typography variant="caption" color="text.secondary">
          {t('common:lastUpdate', 'Last update')}: {formatDate(data.timestamp)} • {t('mtproto:footer.refreshEvery', 'Auto-refresh every 10 seconds')}
        </Typography>
      </Paper>
    </Container>
  );
};

export default MTProtoMonitoringPage;
