import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Alert,
  AlertTitle,
  Switch,
  FormControlLabel,
  Paper,
  Container,
  Divider,
  CircularProgress,
  Button
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Schedule,
  TrendingUp,
  Refresh,
  Wifi,
  WifiOff,
  Storage,
  SignalCellular4Bar
} from '@mui/icons-material';
import { apiClient } from '@/api/client';

interface SessionHealth {
  session_valid: boolean;
  session_connected: boolean;
  session_last_used: string | null;
  api_calls_today: number;
  rate_limit_hits_today: number;
  connection_errors_today: number;
  health_score: number;
}

interface CollectionProgress {
  total_channels: number;
  active_channels: number;
  total_posts_collected: number;
  collection_active: boolean;
  last_collection_time: string | null;
  next_collection_eta: string | null;
  estimated_completion_percent: number;
}

interface WorkerStatus {
  worker_running: boolean;
  worker_interval_minutes: number;
  last_run: string | null;
  next_run: string | null;
  runs_today: number;
  errors_today: number;
  currently_collecting: boolean;
  current_channel: string | null;
  channels_processed: number;
  channels_total: number;
  messages_collected_current_run: number;
  errors_current_run: number;
  collection_start_time: string | null;
  estimated_time_remaining: number | null;
}

interface ChannelStats {
  channel_id: number;
  channel_name: string;
  total_posts: number;
  latest_post_date: string | null;
  oldest_post_date: string | null;
  last_collected: string | null;
  collection_enabled: boolean;
}

interface MonitoringData {
  user_id: number;
  mtproto_enabled: boolean;
  session_health: SessionHealth;
  collection_progress: CollectionProgress;
  worker_status: WorkerStatus;
  channels: ChannelStats[];
  timestamp: string;
}

export const MTProtoMonitoringPage: React.FC = () => {
  const [data, setData] = useState<MonitoringData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchMonitoringData = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('📊 Fetching MTProto monitoring data...');
      const response: any = await apiClient.get('/api/user-mtproto/monitoring/overview');
      console.log('📊 Monitoring response:', response);

      // apiClient.get() returns the data directly, not wrapped in response.data
      if (!response) {
        console.error('❌ Empty response received');
        setError('No monitoring data received from server');
        setData(null);
        return;
      }

      setData(response as MonitoringData);
      console.log('✅ Monitoring data loaded successfully');
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to fetch monitoring data';
      console.error('❌ Monitoring fetch error:', err);
      console.error('❌ Error details:', errorMsg);
      setError(errorMsg);
      setData(null);
    } finally {
      console.log('📊 Setting loading to false');
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMonitoringData();

    if (autoRefresh) {
      const interval = setInterval(fetchMonitoringData, 300000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
    return undefined;
  }, [autoRefresh]);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  const formatTimeAgo = (dateStr: string | null) => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const getHealthColor = (score: number): "success" | "warning" | "error" => {
    if (score >= 80) return 'success';
    if (score >= 50) return 'warning';
    return 'error';
  };

  const getHealthChip = (score: number) => {
    if (score >= 80) return <Chip label="Healthy" color="success" size="small" />;
    if (score >= 50) return <Chip label="Degraded" color="warning" size="small" />;
    return <Chip label="Unhealthy" color="error" size="small" />;
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
          <Button variant="contained" onClick={fetchMonitoringData}>
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
          <Button variant="outlined" onClick={fetchMonitoringData}>
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
          <Typography variant="h4" component="h1" gutterBottom>
            MTProto Monitoring
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time collection status and session health
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
            label="Auto-refresh"
          />
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchMonitoringData}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* MTProto Status Alert */}
      {!data.mtproto_enabled && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <AlertTitle>MTProto Disabled</AlertTitle>
          MTProto is currently disabled. Enable it in settings to start collecting data.
        </Alert>
      )}

      {/* Session Health Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            {data.session_health.session_connected ? (
              <Wifi color="success" />
            ) : (
              <WifiOff color="error" />
            )}
            <Typography variant="h6">Session Health</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            MTProto connection and performance metrics
          </Typography>
          <Divider sx={{ my: 2 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Overall Health</Typography>
                <Box display="flex" alignItems="center" gap={1} mt={1}>
                  <Typography variant="h3" color={getHealthColor(data.session_health.health_score)}>
                    {data.session_health.health_score.toFixed(0)}%
                  </Typography>
                  {getHealthChip(data.session_health.health_score)}
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={data.session_health.health_score}
                  color={getHealthColor(data.session_health.health_score)}
                  sx={{ mt: 1, height: 8, borderRadius: 1 }}
                />
              </Box>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Connection Status</Typography>
                <Box display="flex" alignItems="center" gap={1} mt={1}>
                  {data.session_health.session_connected ? (
                    <>
                      <CheckCircle color="success" />
                      <Typography variant="h6">Connected</Typography>
                    </>
                  ) : (
                    <>
                      <Cancel color="error" />
                      <Typography variant="h6">Disconnected</Typography>
                    </>
                  )}
                </Box>
                <Typography variant="caption" color="text.secondary">
                  Last used: {formatTimeAgo(data.session_health.session_last_used)}
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">API Calls Today</Typography>
                <Typography variant="h4" mt={1}>{data.session_health.api_calls_today}</Typography>
                <Typography variant="caption" color="text.secondary">
                  Rate limits: {data.session_health.rate_limit_hits_today}
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Connection Errors</Typography>
                <Typography variant="h4" color="error" mt={1}>
                  {data.session_health.connection_errors_today}
                </Typography>
                <Typography variant="caption" color="text.secondary">Today</Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Collection Progress Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Storage color="primary" />
            <Typography variant="h6">Collection Progress</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Data collection statistics across all channels
          </Typography>
          <Divider sx={{ my: 2 }} />

          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Completion</Typography>
                <Typography variant="h3" color="primary" mt={1}>
                  {data.collection_progress.estimated_completion_percent.toFixed(0)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={data.collection_progress.estimated_completion_percent}
                  sx={{ mt: 1, height: 8, borderRadius: 1 }}
                />
              </Box>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Active Channels</Typography>
                <Typography variant="h4" mt={1}>
                  {data.collection_progress.active_channels} / {data.collection_progress.total_channels}
                </Typography>
                {data.collection_progress.collection_active ? (
                  <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
                    <SignalCellular4Bar color="success" fontSize="small" />
                    <Typography variant="caption" color="success.main">Collecting now</Typography>
                  </Box>
                ) : (
                  <Typography variant="caption" color="text.secondary">Idle</Typography>
                )}
              </Box>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Total Posts</Typography>
                <Typography variant="h4" mt={1}>
                  {data.collection_progress.total_posts_collected.toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary">Collected</Typography>
              </Box>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Last Collection</Typography>
                <Typography variant="body1" fontWeight="medium" mt={1}>
                  {formatTimeAgo(data.collection_progress.last_collection_time)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Next: {formatTimeAgo(data.collection_progress.next_collection_eta)}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Worker Status Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <Schedule color="primary" />
            <Typography variant="h6">Automatic Worker Status</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Background collection service information
          </Typography>
          <Divider sx={{ my: 2 }} />

          {/* Active Collection Progress */}
          {data.worker_status.currently_collecting && (
            <Alert severity="info" sx={{ mb: 3 }}>
              <AlertTitle>Collection in Progress</AlertTitle>
              <Box>
                {data.worker_status.current_channel && (
                  <Typography variant="body2" gutterBottom>
                    Currently collecting: <strong>{data.worker_status.current_channel}</strong>
                  </Typography>
                )}
                {data.worker_status.collection_start_time && (
                  <Typography variant="body2" gutterBottom>
                    Running for: <strong>{formatTimeAgo(data.worker_status.collection_start_time)}</strong>
                  </Typography>
                )}
                <Typography variant="body2" gutterBottom>
                  Progress: <strong>{data.worker_status.channels_processed} / {data.worker_status.channels_total}</strong> channels
                  {' '}({((data.worker_status.channels_processed / data.worker_status.channels_total) * 100).toFixed(0)}%)
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={(data.worker_status.channels_processed / data.worker_status.channels_total) * 100}
                  sx={{ my: 1, height: 6, borderRadius: 1 }}
                />
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="caption" color="text.secondary">
                    Messages collected: {data.worker_status.messages_collected_current_run}
                    {data.worker_status.errors_current_run > 0 && (
                      <span style={{ color: '#f44336', marginLeft: 8 }}>
                        • Errors: {data.worker_status.errors_current_run}
                      </span>
                    )}
                  </Typography>
                  {data.worker_status.estimated_time_remaining && (
                    <Typography variant="caption" color="text.secondary">
                      ETA: ~{Math.ceil(data.worker_status.estimated_time_remaining / 60)}min remaining
                    </Typography>
                  )}
                </Box>
              </Box>
            </Alert>
          )}

          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Worker Status</Typography>
                <Box display="flex" alignItems="center" gap={1} mt={1}>
                  {data.worker_status.worker_running ? (
                    <>
                      <CheckCircle color="success" />
                      <Typography variant="h6" color="success.main">
                        {data.worker_status.currently_collecting ? 'Collecting' : 'Running'}
                      </Typography>
                    </>
                  ) : (
                    <>
                      <Cancel color="error" />
                      <Typography variant="h6" color="error.main">Stopped</Typography>
                    </>
                  )}
                </Box>
              </Box>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Collection Interval</Typography>
                <Typography variant="h4" mt={1}>{data.worker_status.worker_interval_minutes}min</Typography>
                <Typography variant="caption" color="text.secondary">Between runs</Typography>
              </Box>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Runs Today</Typography>
                <Typography variant="h4" mt={1}>{data.worker_status.runs_today}</Typography>
                <Typography variant="caption" color="error.main">
                  Errors: {data.worker_status.errors_today}
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Box>
                <Typography variant="body2" color="text.secondary">Next Run</Typography>
                <Typography variant="body1" fontWeight="medium" mt={1}>
                  {formatTimeAgo(data.worker_status.next_run)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Last: {formatTimeAgo(data.worker_status.last_run)}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Channels Statistics */}
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <TrendingUp color="primary" />
            <Typography variant="h6">Channel Collection Statistics</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Per-channel collection progress
          </Typography>
          <Divider sx={{ my: 2 }} />

          {data.channels.length === 0 ? (
            <Box textAlign="center" py={4}>
              <Typography color="text.secondary">No channels configured yet</Typography>
            </Box>
          ) : (
            <Box>
              {data.channels.map((channel) => (
                <Paper
                  key={channel.channel_id}
                  variant="outlined"
                  sx={{ p: 2, mb: 2, '&:hover': { bgcolor: 'action.hover' } }}
                >
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={4}>
                      <Box>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="subtitle1" fontWeight="medium">
                            {channel.channel_name}
                          </Typography>
                          {channel.collection_enabled ? (
                            <Chip label="Active" color="success" size="small" />
                          ) : (
                            <Chip label="Disabled" size="small" />
                          )}
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          ID: {channel.channel_id}
                        </Typography>
                      </Box>
                    </Grid>

                    <Grid item xs={4} md={2}>
                      <Box textAlign="center">
                        <Typography variant="h5">{channel.total_posts}</Typography>
                        <Typography variant="caption" color="text.secondary">Posts</Typography>
                      </Box>
                    </Grid>

                    <Grid item xs={4} md={3}>
                      <Box textAlign="center">
                        <Typography variant="body2" fontWeight="medium">
                          {formatTimeAgo(channel.latest_post_date)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">Latest</Typography>
                      </Box>
                    </Grid>

                    <Grid item xs={4} md={3}>
                      <Box textAlign="center">
                        <Typography variant="body2" fontWeight="medium">
                          {formatTimeAgo(channel.last_collected)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">Last collected</Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Paper>
              ))}
            </Box>
          )}
        </CardContent>
      </Card>

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
