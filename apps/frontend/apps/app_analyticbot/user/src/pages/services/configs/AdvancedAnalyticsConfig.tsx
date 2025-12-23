/**
 * Advanced Analytics Configuration
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Switch,
  Alert,
  Button,
  CircularProgress,
  Divider,
  alpha,
  Card,
  CardContent,
  Paper,
  Grid,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  Save as SaveIcon,
  TrendingUp as GrowthIcon,
  People as UsersIcon,
  Message as MessagesIcon,
  Timeline as TimelineIcon,
  PictureAsPdf as PdfIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface AnalyticsSettings {
  analytics_enabled: boolean;
  track_messages: boolean;
  track_user_activity: boolean;
  track_commands: boolean;
  track_media: boolean;
  weekly_report_enabled: boolean;
  monthly_report_enabled: boolean;
}

interface AnalyticsStats {
  total_messages: number;
  total_users: number;
  active_users_today: number;
  messages_today: number;
  growth_rate: number;
  top_hours: number[];
}

interface Props {
  chatId: number;
}

export const AdvancedAnalyticsConfig: React.FC<Props> = ({ chatId }) => {
  const [settings, setSettings] = useState<AnalyticsSettings>({
    analytics_enabled: false,
    track_messages: true,
    track_user_activity: true,
    track_commands: true,
    track_media: false,
    weekly_report_enabled: false,
    monthly_report_enabled: false,
  });
  const [stats, setStats] = useState<AnalyticsStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [isNewConfig, setIsNewConfig] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const settingsResponse = await apiClient.get(`/user-bot/service/settings/${chatId}`) as AnalyticsSettings;
        if (settingsResponse) {
          setSettings(prev => ({
            ...prev,
            analytics_enabled: settingsResponse.analytics_enabled ?? false,
            track_messages: settingsResponse.track_messages ?? true,
            track_user_activity: settingsResponse.track_user_activity ?? true,
            track_commands: settingsResponse.track_commands ?? true,
            track_media: settingsResponse.track_media ?? false,
            weekly_report_enabled: settingsResponse.weekly_report_enabled ?? false,
            monthly_report_enabled: settingsResponse.monthly_report_enabled ?? false,
          }));
        }

        // Fetch analytics stats
        if (settingsResponse?.analytics_enabled) {
          await fetchStats();
        }
      } catch (err: any) {
        // 404 means settings don't exist yet - this is normal for new chats
        if (err.message?.includes('not found') || err.status === 404) {
          setIsNewConfig(true);
        } else {
          setError(err.message || 'Failed to load settings');
        }
      } finally {
        setIsLoading(false);
      }
    };

    if (chatId) {
      fetchData();
    }
  }, [chatId]);

  const fetchStats = async () => {
    setIsLoadingStats(true);
    try {
      // TODO: Backend endpoint /user-bot/service/analytics/{chatId}/summary not yet implemented
      // Analytics stats display feature coming soon
      console.log('Analytics summary endpoint not yet available');
      setStats(null);
    } catch {
      // Stats may not exist yet
      setStats(null);
    } finally {
      setIsLoadingStats(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);
    try {
      await apiClient.post(`/user-bot/service/settings/${chatId}`, settings);
      setSuccess(true);
      setIsNewConfig(false);
      setTimeout(() => setSuccess(false), 3000);
      
      if (settings.analytics_enabled) {
        await fetchStats();
      }
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

  return (
    <Box>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>Settings saved successfully!</Alert>}
      {isNewConfig && !success && (
        <Alert severity="info" sx={{ mb: 3 }}>
          This chat hasn't been configured yet. Customize your settings and save to get started!
        </Alert>
      )}

      {/* Main Toggle */}
      <Card sx={{ mb: 3, bgcolor: alpha('#14b8a6', 0.05), border: '1px solid', borderColor: alpha('#14b8a6', 0.2) }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <Box
                sx={{
                  width: 50,
                  height: 50,
                  borderRadius: 2,
                  bgcolor: alpha('#14b8a6', 0.2),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <AnalyticsIcon sx={{ color: '#14b8a6', fontSize: 28 }} />
              </Box>
              <Box>
                <Typography variant="h6">Advanced Analytics</Typography>
                <Typography variant="body2" color="text.secondary">
                  Comprehensive analytics dashboard with engagement metrics and growth tracking
                </Typography>
              </Box>
            </Box>
            <Switch
              checked={settings.analytics_enabled}
              onChange={(e) => setSettings(prev => ({ ...prev, analytics_enabled: e.target.checked }))}
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': {
                  color: '#14b8a6',
                },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                  backgroundColor: '#14b8a6',
                },
              }}
              size="medium"
            />
          </Box>
        </CardContent>
      </Card>

      {settings.analytics_enabled && (
        <>
          {/* Stats Overview */}
          {isLoadingStats ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress size={24} />
            </Box>
          ) : stats ? (
            <Grid container spacing={2} sx={{ mb: 4 }}>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <UsersIcon sx={{ color: '#3b82f6', fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" fontWeight={600}>
                    {stats.total_users.toLocaleString()}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Total Users
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <MessagesIcon sx={{ color: '#8b5cf6', fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" fontWeight={600}>
                    {stats.total_messages.toLocaleString()}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Total Messages
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <TimelineIcon sx={{ color: '#f59e0b', fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" fontWeight={600}>
                    {stats.active_users_today}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Active Today
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <GrowthIcon sx={{ color: '#10b981', fontSize: 32, mb: 1 }} />
                  <Typography variant="h5" fontWeight={600}>
                    {stats.growth_rate > 0 ? '+' : ''}{stats.growth_rate}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Growth Rate
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          ) : (
            <Alert severity="info" sx={{ mb: 3 }}>
              Analytics data will appear here once tracking begins.
            </Alert>
          )}

          <Divider sx={{ my: 3 }} />

          {/* Tracking Options */}
          <Paper variant="outlined" sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle1" mb={2}>
              Data Tracking Options
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              Choose what data to track for analytics. More data provides better insights but uses more storage.
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={settings.track_messages}
                      onChange={(e) => setSettings(prev => ({ ...prev, track_messages: e.target.checked }))}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2">Message Activity</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Track message counts and timing
                      </Typography>
                    </Box>
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={settings.track_user_activity}
                      onChange={(e) => setSettings(prev => ({ ...prev, track_user_activity: e.target.checked }))}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2">User Activity</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Track when users are active
                      </Typography>
                    </Box>
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={settings.track_commands}
                      onChange={(e) => setSettings(prev => ({ ...prev, track_commands: e.target.checked }))}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2">Command Usage</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Track bot command usage
                      </Typography>
                    </Box>
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={settings.track_media}
                      onChange={(e) => setSettings(prev => ({ ...prev, track_media: e.target.checked }))}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2">Media Statistics</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Track photos, videos, documents
                      </Typography>
                    </Box>
                  }
                />
              </Grid>
            </Grid>
          </Paper>

          {/* Automated Reports */}
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="subtitle1" mb={2}>
              <ScheduleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Automated Reports
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={3}>
              Receive periodic analytics reports automatically.
            </Typography>

            <Box display="flex" gap={3} flexWrap="wrap">
              <Card
                sx={{
                  flex: 1,
                  minWidth: 200,
                  p: 2,
                  cursor: 'pointer',
                  border: settings.weekly_report_enabled ? '2px solid' : '1px solid',
                  borderColor: settings.weekly_report_enabled ? '#14b8a6' : 'divider',
                  bgcolor: settings.weekly_report_enabled ? alpha('#14b8a6', 0.05) : 'transparent',
                }}
                onClick={() => setSettings(prev => ({ ...prev, weekly_report_enabled: !prev.weekly_report_enabled }))}
              >
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box display="flex" alignItems="center" gap={1}>
                    <PdfIcon color={settings.weekly_report_enabled ? 'primary' : 'action'} />
                    <Box>
                      <Typography variant="subtitle2">Weekly Report</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Sent every Monday
                      </Typography>
                    </Box>
                  </Box>
                  <Checkbox checked={settings.weekly_report_enabled} />
                </Box>
              </Card>

              <Card
                sx={{
                  flex: 1,
                  minWidth: 200,
                  p: 2,
                  cursor: 'pointer',
                  border: settings.monthly_report_enabled ? '2px solid' : '1px solid',
                  borderColor: settings.monthly_report_enabled ? '#14b8a6' : 'divider',
                  bgcolor: settings.monthly_report_enabled ? alpha('#14b8a6', 0.05) : 'transparent',
                }}
                onClick={() => setSettings(prev => ({ ...prev, monthly_report_enabled: !prev.monthly_report_enabled }))}
              >
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box display="flex" alignItems="center" gap={1}>
                    <PdfIcon color={settings.monthly_report_enabled ? 'primary' : 'action'} />
                    <Box>
                      <Typography variant="subtitle2">Monthly Report</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Sent on the 1st
                      </Typography>
                    </Box>
                  </Box>
                  <Checkbox checked={settings.monthly_report_enabled} />
                </Box>
              </Card>
            </Box>
          </Paper>
        </>
      )}

      {/* Save Button */}
      <Box mt={4} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={isSaving ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          onClick={handleSave}
          disabled={isSaving}
          size="large"
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </Button>
      </Box>
    </Box>
  );
};
