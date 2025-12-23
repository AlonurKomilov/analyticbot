/**
 * MTProto History Access Service Configuration
 * 
 * Service: mtproto_history_access
 * Price: 100 credits/month
 * 
 * Allows users to configure:
 * - Default message fetch limits
 * - Date range preferences  
 * - Media inclusion settings
 * - Export format preferences
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Switch,
  FormControlLabel,
  FormGroup,
  Slider,
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
} from '@mui/material';
import {
  History as HistoryIcon,
  Save as SaveIcon,
  Settings as SettingsIcon,
  PhotoLibrary as MediaIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface HistoryAccessSettings {
  enabled: boolean;
  default_limit: number;
  include_media_metadata: boolean;
  include_reactions: boolean;
  include_replies: boolean;
  date_range_days: number | null;
  export_format: 'json' | 'csv';
  auto_pagination: boolean;
  rate_limit_delay_ms: number;
}

interface Props {
  chatId?: number; // Optional - MTProto configs are user-level, not per-chat
}

const MESSAGE_LIMITS = [
  { value: 100, label: '100 messages' },
  { value: 500, label: '500 messages' },
  { value: 1000, label: '1,000 messages' },
  { value: 2000, label: '2,000 messages' },
  { value: 5000, label: '5,000 messages (max)' },
];

const DATE_RANGE_OPTIONS = [
  { value: null, label: 'All time (no limit)' },
  { value: 7, label: 'Last 7 days' },
  { value: 30, label: 'Last 30 days' },
  { value: 90, label: 'Last 90 days' },
  { value: 180, label: 'Last 6 months' },
  { value: 365, label: 'Last year' },
];

export const HistoryAccessConfig: React.FC<Props> = () => {
  const [settings, setSettings] = useState<HistoryAccessSettings>({
    enabled: true,
    default_limit: 1000,
    include_media_metadata: true,
    include_reactions: true,
    include_replies: true,
    date_range_days: null,
    export_format: 'json',
    auto_pagination: true,
    rate_limit_delay_ms: 500,
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Usage stats
  const [usageStats, setUsageStats] = useState({
    messages_today: 0,
    messages_month: 0,
    daily_limit: 1000,
    monthly_limit: 20000,
  });

  useEffect(() => {
    const fetchSettings = async () => {
      setIsLoading(true);
      try {
        // Fetch user's MTProto settings
        const response = await apiClient.get('/user-mtproto/monitoring/overview') as Record<string, any>;
        
        // Get settings from response or use defaults
        if (response) {
          // Load from local storage or use defaults (settings not stored on server yet)
          const savedSettings = localStorage.getItem('mtproto_history_settings');
          if (savedSettings) {
            setSettings(prev => ({ ...prev, ...JSON.parse(savedSettings) }));
          }
          
          // Set usage stats from monitoring data
          if (response.collection_progress) {
            setUsageStats(prev => ({
              ...prev,
              messages_today: response.session_health?.api_calls_today || 0,
            }));
          }
        }
      } catch (err: any) {
        // If 404, user doesn't have MTProto configured
        if (err.response?.status === 404) {
          setError('MTProto is not configured. Please set up your MTProto connection first.');
        } else {
          setError(err.message || 'Failed to load settings');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);
    try {
      // Save to local storage (user preferences)
      localStorage.setItem('mtproto_history_settings', JSON.stringify(settings));
      
      // In future: save to backend API
      // await apiClient.patch('/user-mtproto/settings/history-access', settings);
      
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" py={4}>
        <CircularProgress />
      </Box>
    );
  }

  const dailyUsagePercent = (usageStats.messages_today / usageStats.daily_limit) * 100;
  const monthlyUsagePercent = (usageStats.messages_month / usageStats.monthly_limit) * 100;

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}

      {/* Service Header */}
      <Card sx={{ mb: 3, bgcolor: alpha('#2196F3', 0.05), border: '1px solid', borderColor: alpha('#2196F3', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <HistoryIcon sx={{ color: '#2196F3', fontSize: 40 }} />
              <Box>
                <Typography variant="h6">MTProto History Access</Typography>
                <Typography variant="body2" color="text.secondary">
                  Configure how message history is fetched from your channels via MTProto
                </Typography>
              </Box>
            </Box>
            <Chip 
              label="Premium Service" 
              color="primary" 
              size="small"
              sx={{ bgcolor: alpha('#2196F3', 0.1) }}
            />
          </Box>
        </CardContent>
      </Card>

      {/* Usage Stats */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="subtitle1" mb={2}>
            <SpeedIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Usage Quota
          </Typography>
          
          <Stack spacing={2}>
            <Box>
              <Box display="flex" justifyContent="space-between" mb={0.5}>
                <Typography variant="body2">Daily Usage</Typography>
                <Typography variant="body2" color="text.secondary">
                  {usageStats.messages_today.toLocaleString()} / {usageStats.daily_limit.toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1, height: 8 }}>
                <Box 
                  sx={{ 
                    width: `${Math.min(dailyUsagePercent, 100)}%`, 
                    bgcolor: dailyUsagePercent > 80 ? 'warning.main' : 'primary.main',
                    borderRadius: 1, 
                    height: '100%',
                    transition: 'width 0.3s ease',
                  }} 
                />
              </Box>
            </Box>

            <Box>
              <Box display="flex" justifyContent="space-between" mb={0.5}>
                <Typography variant="body2">Monthly Usage</Typography>
                <Typography variant="body2" color="text.secondary">
                  {usageStats.messages_month.toLocaleString()} / {usageStats.monthly_limit.toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ width: '100%', bgcolor: 'grey.200', borderRadius: 1, height: 8 }}>
                <Box 
                  sx={{ 
                    width: `${Math.min(monthlyUsagePercent, 100)}%`, 
                    bgcolor: monthlyUsagePercent > 80 ? 'warning.main' : 'success.main',
                    borderRadius: 1, 
                    height: '100%',
                    transition: 'width 0.3s ease',
                  }} 
                />
              </Box>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      {/* Default Fetch Settings */}
      <Typography variant="subtitle1" mb={2}>
        <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Default Fetch Settings
      </Typography>

      <Box mb={4}>
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Default Message Limit</InputLabel>
          <Select
            value={settings.default_limit}
            label="Default Message Limit"
            onChange={(e) => setSettings(prev => ({ ...prev, default_limit: e.target.value as number }))}
          >
            {MESSAGE_LIMITS.map(option => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Default Date Range</InputLabel>
          <Select
            value={settings.date_range_days ?? 'null'}
            label="Default Date Range"
            onChange={(e) => setSettings(prev => ({ 
              ...prev, 
              date_range_days: e.target.value === 'null' ? null : e.target.value as number 
            }))}
          >
            {DATE_RANGE_OPTIONS.map(option => (
              <MenuItem key={option.value ?? 'null'} value={option.value ?? 'null'}>
                {option.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Export Format</InputLabel>
          <Select
            value={settings.export_format}
            label="Export Format"
            onChange={(e) => setSettings(prev => ({ ...prev, export_format: e.target.value as 'json' | 'csv' }))}
          >
            <MenuItem value="json">JSON (Full data)</MenuItem>
            <MenuItem value="csv">CSV (Tabular)</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Divider sx={{ my: 3 }} />

      {/* Data Inclusion Options */}
      <Typography variant="subtitle1" mb={2}>
        <MediaIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Data Inclusion
      </Typography>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.include_media_metadata}
                onChange={(e) => setSettings(prev => ({ ...prev, include_media_metadata: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Include Media Metadata</Typography>
                <Typography variant="caption" color="text.secondary">
                  Fetch information about photos, videos, and documents in messages
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
                checked={settings.include_reactions}
                onChange={(e) => setSettings(prev => ({ ...prev, include_reactions: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Include Reactions</Typography>
                <Typography variant="caption" color="text.secondary">
                  Fetch emoji reactions data for each message
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
                checked={settings.include_replies}
                onChange={(e) => setSettings(prev => ({ ...prev, include_replies: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Include Reply Information</Typography>
                <Typography variant="caption" color="text.secondary">
                  Fetch data about which messages are replies and their threads
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>
      </FormGroup>

      <Divider sx={{ my: 3 }} />

      {/* Performance Settings */}
      <Typography variant="subtitle1" mb={2}>
        <StorageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Performance Settings
      </Typography>

      <FormGroup>
        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default', mb: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={settings.auto_pagination}
                onChange={(e) => setSettings(prev => ({ ...prev, auto_pagination: e.target.checked }))}
              />
            }
            label={
              <Box>
                <Typography>Auto-Pagination</Typography>
                <Typography variant="caption" color="text.secondary">
                  Automatically fetch multiple pages when requesting more messages than limit
                </Typography>
              </Box>
            }
            sx={{ alignItems: 'flex-start', m: 0 }}
          />
        </Box>

        <Box sx={{ p: 2, borderRadius: 2, bgcolor: 'background.default' }}>
          <Typography variant="body2" mb={2}>
            Rate Limit Delay: <strong>{settings.rate_limit_delay_ms}ms</strong>
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block" mb={2}>
            Delay between API calls to avoid rate limiting (lower = faster but more risky)
          </Typography>
          <Slider
            value={settings.rate_limit_delay_ms}
            onChange={(_, value) => setSettings(prev => ({ ...prev, rate_limit_delay_ms: value as number }))}
            min={100}
            max={2000}
            step={100}
            marks={[
              { value: 100, label: '100ms' },
              { value: 500, label: '500ms' },
              { value: 1000, label: '1s' },
              { value: 2000, label: '2s' },
            ]}
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value}ms`}
          />
        </Box>
      </FormGroup>

      {/* Save Button */}
      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
          size="large"
          sx={{ bgcolor: '#2196F3', '&:hover': { bgcolor: '#1976D2' } }}
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};
