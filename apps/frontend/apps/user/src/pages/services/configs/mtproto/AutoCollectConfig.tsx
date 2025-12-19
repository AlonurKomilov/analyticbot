/**
 * MTProto Auto-Collect Service Configuration
 * 
 * Service: mtproto_auto_collect
 * Price: 150 credits/month
 * 
 * Allows users to configure:
 * - Automatic collection scheduling
 * - Worker settings
 * - Channel-specific collection rules
 * - Collection frequency and timing
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  FormGroup,
  Alert,
  Button,
  CircularProgress,
  Divider,
  alpha,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Stack,
  Grid,
  Paper,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Schedule as ScheduleIcon,
  Save as SaveIcon,
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingIcon,
  AccessTime as TimeIcon,
  Memory as MemoryIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface WorkerStatus {
  id: string;
  status: 'running' | 'paused' | 'stopped' | 'idle';
  last_run: string | null;
  next_run: string | null;
  channels_count: number;
  messages_collected: number;
  errors_count: number;
}

interface AutoCollectSettings {
  enabled: boolean;
  collection_interval_hours: number;
  batch_size: number;
  max_channels_per_run: number;
  priority_mode: 'round_robin' | 'activity_based' | 'custom';
  pause_during_hours: number[];
  auto_retry_on_error: boolean;
  retry_delay_minutes: number;
  collect_on_startup: boolean;
}

const INTERVAL_OPTIONS = [
  { value: 1, label: 'Every hour' },
  { value: 2, label: 'Every 2 hours' },
  { value: 4, label: 'Every 4 hours' },
  { value: 6, label: 'Every 6 hours' },
  { value: 12, label: 'Every 12 hours' },
  { value: 24, label: 'Once daily' },
];

const BATCH_SIZE_OPTIONS = [
  { value: 100, label: '100 messages' },
  { value: 250, label: '250 messages' },
  { value: 500, label: '500 messages' },
  { value: 1000, label: '1,000 messages' },
];

const PRIORITY_MODES = [
  { value: 'round_robin', label: 'Round Robin', description: 'Collect from all channels equally' },
  { value: 'activity_based', label: 'Activity Based', description: 'Prioritize channels with more activity' },
  { value: 'custom', label: 'Custom Order', description: 'Use your custom channel priority list' },
];

export const AutoCollectConfig: React.FC = () => {
  const [settings, setSettings] = useState<AutoCollectSettings>({
    enabled: true,
    collection_interval_hours: 4,
    batch_size: 500,
    max_channels_per_run: 10,
    priority_mode: 'activity_based',
    pause_during_hours: [],
    auto_retry_on_error: true,
    retry_delay_minutes: 15,
    collect_on_startup: false,
  });

  const [workerStatus, setWorkerStatus] = useState<WorkerStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const fetchWorkerStatus = async () => {
    try {
      const response = await apiClient.get('/user-mtproto/monitoring/worker') as Record<string, any>;
      setWorkerStatus(response.worker || {
        id: 'mtproto-worker',
        status: 'idle',
        last_run: null,
        next_run: null,
        channels_count: 0,
        messages_collected: 0,
        errors_count: 0,
      });
    } catch (err: any) {
      // Worker might not exist yet
      setWorkerStatus({
        id: 'mtproto-worker',
        status: 'stopped',
        last_run: null,
        next_run: null,
        channels_count: 0,
        messages_collected: 0,
        errors_count: 0,
      });
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        await fetchWorkerStatus();
        
        // Load saved settings from localStorage
        const savedSettings = localStorage.getItem('mtproto_autocollect_settings');
        if (savedSettings) {
          setSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }));
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load settings');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
    
    // Refresh worker status every 30 seconds
    const interval = setInterval(fetchWorkerStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);
    try {
      localStorage.setItem('mtproto_autocollect_settings', JSON.stringify(settings));
      
      // TODO: Save to backend when API is ready
      // await apiClient.patch('/user-mtproto/settings/auto-collect', settings);
      
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleWorker = async () => {
    setIsToggling(true);
    setError(null);
    try {
      const action = workerStatus?.status === 'running' ? 'pause' : 'start';
      await apiClient.post(`/user-mtproto/monitoring/worker/${action}`);
      await fetchWorkerStatus();
    } catch (err: any) {
      setError(err.message || `Failed to ${workerStatus?.status === 'running' ? 'pause' : 'start'} worker`);
    } finally {
      setIsToggling(false);
    }
  };

  const handleTriggerRun = async () => {
    setError(null);
    try {
      await apiClient.post('/user-mtproto/monitoring/worker/trigger');
      await fetchWorkerStatus();
    } catch (err: any) {
      setError(err.message || 'Failed to trigger collection run');
    }
  };

  const formatTime = (dateStr: string | null) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'success';
      case 'paused': return 'warning';
      case 'stopped': return 'error';
      default: return 'default';
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}

      {/* Service Header */}
      <Card sx={{ mb: 3, bgcolor: alpha('#FF9800', 0.05), border: '1px solid', borderColor: alpha('#FF9800', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <ScheduleIcon sx={{ color: '#FF9800', fontSize: 40 }} />
              <Box>
                <Typography variant="h6">MTProto Auto-Collect</Typography>
                <Typography variant="body2" color="text.secondary">
                  Automatically collect messages from your channels on a schedule
                </Typography>
              </Box>
            </Box>
            <Chip 
              label="Premium Service" 
              color="warning" 
              size="small"
              sx={{ bgcolor: alpha('#FF9800', 0.1) }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Worker Status Panel */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="subtitle1">
              <MemoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Worker Status
            </Typography>
            <Box display="flex" gap={1}>
              <Tooltip title="Refresh status">
                <IconButton size="small" onClick={fetchWorkerStatus}>
                  <RefreshIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Chip 
                label={workerStatus?.status || 'unknown'} 
                color={getStatusColor(workerStatus?.status || 'unknown') as any}
                size="small"
              />
            </Box>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="caption" color="text.secondary">Last Run</Typography>
                <Typography variant="body2">{formatTime(workerStatus?.last_run || null)}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="caption" color="text.secondary">Next Run</Typography>
                <Typography variant="body2">{formatTime(workerStatus?.next_run || null)}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="caption" color="text.secondary">Channels</Typography>
                <Typography variant="body2">{workerStatus?.channels_count || 0}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, bgcolor: 'background.default' }}>
                <Typography variant="caption" color="text.secondary">Messages Collected</Typography>
                <Typography variant="body2">{(workerStatus?.messages_collected || 0).toLocaleString()}</Typography>
              </Paper>
            </Grid>
          </Grid>

          <Box display="flex" gap={2} mt={2}>
            <Button
              variant="outlined"
              size="small"
              startIcon={isToggling ? <CircularProgress size={16} /> : (workerStatus?.status === 'running' ? <PauseIcon /> : <PlayIcon />)}
              onClick={handleToggleWorker}
              disabled={isToggling}
              color={workerStatus?.status === 'running' ? 'warning' : 'success'}
            >
              {workerStatus?.status === 'running' ? 'Pause' : 'Start'}
            </Button>
            <Button
              variant="outlined"
              size="small"
              startIcon={<PlayIcon />}
              onClick={handleTriggerRun}
              disabled={workerStatus?.status === 'running'}
            >
              Run Now
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Schedule Settings */}
      <Typography variant="subtitle1" mb={2}>
        <TimeIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Schedule Configuration
      </Typography>

      <Box mb={4}>
        <FormGroup>
          <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.enabled}
                  onChange={(e) => setSettings(prev => ({ ...prev, enabled: e.target.checked }))}
                />
              }
              label={
                <Box>
                  <Typography>Enable Auto-Collection</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Automatically collect messages on the configured schedule
                  </Typography>
                </Box>
              }
              sx={{ alignItems: 'flex-start', m: 0 }}
            />
          </Box>
        </FormGroup>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Collection Interval</InputLabel>
              <Select
                value={settings.collection_interval_hours}
                label="Collection Interval"
                onChange={(e) => setSettings(prev => ({ ...prev, collection_interval_hours: e.target.value as number }))}
              >
                {INTERVAL_OPTIONS.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Messages Per Channel</InputLabel>
              <Select
                value={settings.batch_size}
                label="Messages Per Channel"
                onChange={(e) => setSettings(prev => ({ ...prev, batch_size: e.target.value as number }))}
              >
                {BATCH_SIZE_OPTIONS.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* Priority Settings */}
      <Typography variant="subtitle1" mb={2}>
        <TrendingIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Collection Priority
      </Typography>

      <Stack spacing={2} mb={3}>
        {PRIORITY_MODES.map(mode => (
          <Paper
            key={mode.value}
            sx={{
              p: 2,
              cursor: 'pointer',
              border: '2px solid',
              borderColor: settings.priority_mode === mode.value ? 'primary.main' : 'transparent',
              bgcolor: settings.priority_mode === mode.value ? alpha('#FF9800', 0.05) : 'background.default',
              transition: 'all 0.2s ease',
              '&:hover': {
                borderColor: 'primary.light',
              },
            }}
            onClick={() => setSettings(prev => ({ ...prev, priority_mode: mode.value as any }))}
          >
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="subtitle2">{mode.label}</Typography>
                <Typography variant="caption" color="text.secondary">{mode.description}</Typography>
              </Box>
              {settings.priority_mode === mode.value && (
                <Chip label="Active" color="primary" size="small" />
              )}
            </Box>
          </Paper>
        ))}
      </Stack>

      <FormControl fullWidth sx={{ mb: 3 }}>
        <InputLabel>Max Channels Per Run</InputLabel>
        <Select
          value={settings.max_channels_per_run}
          label="Max Channels Per Run"
          onChange={(e) => setSettings(prev => ({ ...prev, max_channels_per_run: e.target.value as number }))}
        >
          {[5, 10, 15, 20, 25, 30, 50].map(value => (
            <MenuItem key={value} value={value}>
              {value} channels
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      <Divider sx={{ my: 3 }} />

      {/* Error Handling */}
      <Typography variant="subtitle1" mb={2}>
        <InfoIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Error Handling
      </Typography>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.auto_retry_on_error}
                onChange={(e) => setSettings(prev => ({ ...prev, auto_retry_on_error: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Auto-Retry on Error</Typography>
                <Typography variant="caption" color="text.secondary">
                  Automatically retry collection if an error occurs
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>

        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.collect_on_startup}
                onChange={(e) => setSettings(prev => ({ ...prev, collect_on_startup: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Collect on Session Start</Typography>
                <Typography variant="caption" color="text.secondary">
                  Trigger a collection run when MTProto session connects
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      {settings.auto_retry_on_error && (
        <FormControl fullWidth sx={{ mt: 2 }}>
          <InputLabel>Retry Delay</InputLabel>
          <Select
            value={settings.retry_delay_minutes}
            label="Retry Delay"
            onChange={(e) => setSettings(prev => ({ ...prev, retry_delay_minutes: e.target.value as number }))}
          >
            {[5, 10, 15, 30, 60].map(value => (
              <MenuItem key={value} value={value}>
                {value} minutes
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {/* Save Button */}
      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
          size="large"
          sx={{ bgcolor: '#FF9800', '&:hover': { bgcolor: '#F57C00' } }}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};
