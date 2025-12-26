import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  LinearProgress,
  alpha,
  useTheme,
  IconButton,
  Tooltip,
  Alert,
  Divider,
  Stack,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Storage as DatabaseIcon,
  Memory as MemoryIcon,
  Speed as CpuIcon,
  Router as ApiIcon,
  SmartToy as BotIcon,
  Refresh as RefreshIcon,
  Computer as ServerIcon,
  Dns as HostnameIcon,
  Schedule as UptimeIcon,
  SdStorage as DiskIcon,
  Telegram as TelegramIcon,
  TrendingUp as PerformanceIcon,
  Timer as TimerIcon,
  Assessment as MetricsIcon,
} from '@mui/icons-material';
import { ownerApi } from '@api/ownerApi';

interface SystemInfo {
  cpu: {
    percent: number;
    cores_physical: number;
    cores_logical: number;
    frequency_mhz: number | null;
    load_avg_1m: number;
    load_avg_5m: number;
    load_avg_15m: number;
  };
  memory: {
    percent: number;
    total_gb: number;
    used_gb: number;
    available_gb: number;
    swap_percent: number;
    swap_total_gb: number;
  };
  disk: {
    percent: number;
    total_gb: number;
    used_gb: number;
    free_gb: number;
  };
  uptime_hours: number;
  platform: string;
  hostname: string;
}

interface PerformanceMetrics {
  uptime_seconds: number;
  total_requests: number;
  requests_per_minute: number;
  avg_response_time_ms: number;
  error_rate_percent: number;
  cache_hit_rate_percent: number;
  slow_endpoints: Array<{
    endpoint: string;
    count: number;
    avg_time_ms: number;
    max_time_ms: number;
    min_time_ms: number;
    errors: number;
  }>;
  slow_queries: Array<{
    query: string;
    duration_ms: number;
    timestamp: string;
  }>;
  recent_db_query_avg_ms: number;
}

interface HealthStatus {
  status: string;
  timestamp: string;
  database: { status: string; latency_ms: number; connections?: number };
  redis: { status: string; latency_ms: number; memory?: { used_mb: number; peak_mb: number } };
  api: { status: string; uptime_hours: number };
  user_bots?: { status: string; active_count: number; total_count: number };
  user_mtproto?: { status: string; active_sessions: number; total_configured: number };
  performance?: PerformanceMetrics;
  system: SystemInfo;
  issues?: string[];
}

const SystemHealthPage: React.FC = () => {
  const theme = useTheme();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval] = useState(5);

  const fetchHealth = useCallback(async (showRefreshSpinner = false) => {
    if (showRefreshSpinner) {
      setRefreshing(true);
    }
    setError(null);

    try {
      const response = await ownerApi.getSystemHealth();
      setHealth(response.data);
      setLastUpdated(new Date());
    } catch (err: any) {
      console.error('Failed to fetch health:', err);
      setError(err.response?.data?.detail || 'Failed to fetch system health');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => fetchHealth(), refreshInterval * 1000);
    return () => clearInterval(interval);
  }, [fetchHealth, autoRefresh, refreshInterval]);

  const handleRefresh = () => {
    fetchHealth(true);
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'healthy': return <HealthyIcon color="success" />;
      case 'warning':
      case 'degraded': return <WarningIcon color="warning" />;
      case 'error':
      case 'unhealthy': return <ErrorIcon color="error" />;
      default: return <WarningIcon color="disabled" />;
    }
  };

  const getStatusChipColor = (status: string): 'success' | 'warning' | 'error' | 'default' => {
    switch (status?.toLowerCase()) {
      case 'healthy': return 'success';
      case 'warning':
      case 'degraded': return 'warning';
      case 'error':
      case 'unhealthy': return 'error';
      default: return 'default';
    }
  };

  const capitalizeStatus = (status: string) => {
    if (!status) return 'Unknown';
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  const formatUptime = (hours: number) => {
    if (hours < 24) return `${hours.toFixed(1)}h`;
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `${days}d ${remainingHours.toFixed(0)}h`;
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  const sys = health?.system;

  return (
    <Box sx={{ maxWidth: '100%', overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="h4" fontWeight={700}>
            System Health
          </Typography>
          <Chip
            icon={getStatusIcon(health?.status || 'unknown')}
            label={(health?.status || 'UNKNOWN').toUpperCase()}
            color={getStatusChipColor(health?.status || 'unknown')}
          />
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                size="small"
              />
            }
            label={
              <Typography variant="body2" color="text.secondary">
                Auto-refresh ({refreshInterval}s)
              </Typography>
            }
          />
          {lastUpdated && (
            <Typography variant="caption" color="text.secondary">
              Updated: {lastUpdated.toLocaleTimeString()}
            </Typography>
          )}
          <Tooltip title="Refresh Now">
            <IconButton onClick={handleRefresh} disabled={refreshing} size="small">
              {refreshing ? <CircularProgress size={20} /> : <RefreshIcon />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Server Info Banner */}
      {sys && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: alpha(theme.palette.primary.main, 0.05), border: `1px solid ${theme.palette.divider}` }}>
          <Stack direction="row" spacing={4} flexWrap="wrap" useFlexGap>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ServerIcon fontSize="small" color="primary" />
              <Typography variant="body2"><strong>Platform:</strong> {sys.platform}</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <HostnameIcon fontSize="small" color="primary" />
              <Typography variant="body2"><strong>Hostname:</strong> {sys.hostname}</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <UptimeIcon fontSize="small" color="primary" />
              <Typography variant="body2"><strong>Uptime:</strong> {formatUptime(sys.uptime_hours)}</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CpuIcon fontSize="small" color="primary" />
              <Typography variant="body2"><strong>CPU:</strong> {sys.cpu.cores_physical} cores ({sys.cpu.cores_logical} threads)</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <MemoryIcon fontSize="small" color="primary" />
              <Typography variant="body2"><strong>RAM:</strong> {sys.memory.total_gb} GB</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <DiskIcon fontSize="small" color="primary" />
              <Typography variant="body2"><strong>Disk:</strong> {sys.disk.total_gb} GB</Typography>
            </Box>
          </Stack>
        </Paper>
      )}

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Issues List */}
      {health?.issues && health.issues.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>System Issues Detected:</Typography>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {health.issues.map((issue, index) => (
              <li key={index}><Typography variant="body2">{issue}</Typography></li>
            ))}
          </ul>
        </Alert>
      )}

      {/* Services Status */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {/* Database */}
        <Grid item xs={12} sm={6} lg={2.4}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}`, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <DatabaseIcon color="primary" />
                <Typography variant="h6">Database</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {getStatusIcon(health?.database?.status || 'unknown')}
                <Typography>{capitalizeStatus(health?.database?.status || 'unknown')}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" display="block">
                Latency: {health?.database?.latency_ms || 0}ms
              </Typography>
              {health?.database?.connections !== undefined && (
                <Typography variant="caption" color="text.secondary" display="block">
                  Connections: {health.database.connections}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Redis */}
        <Grid item xs={12} sm={6} lg={2.4}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}`, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <MemoryIcon color="secondary" />
                <Typography variant="h6">Redis</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {getStatusIcon(health?.redis?.status || 'unknown')}
                <Typography>{capitalizeStatus(health?.redis?.status || 'unknown')}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" display="block">
                Latency: {health?.redis?.latency_ms || 0}ms
              </Typography>
              {health?.redis?.memory && (
                <Typography variant="caption" color="text.secondary" display="block">
                  Memory: {health.redis.memory.used_mb}MB / Peak: {health.redis.memory.peak_mb}MB
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* API */}
        <Grid item xs={12} sm={6} lg={2.4}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}`, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <ApiIcon color="info" />
                <Typography variant="h6">API</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {getStatusIcon(health?.api?.status || 'unknown')}
                <Typography>{capitalizeStatus(health?.api?.status || 'unknown')}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" display="block">
                Session Uptime: {formatUptime(health?.api?.uptime_hours || 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* User Bots */}
        <Grid item xs={12} sm={6} lg={2.4}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}`, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <BotIcon color="success" />
                <Typography variant="h6">User Bots</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {getStatusIcon(health?.user_bots?.status || 'unknown')}
                <Typography>{capitalizeStatus(health?.user_bots?.status || 'unknown')}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" display="block">
                Active: {health?.user_bots?.active_count || 0} / {health?.user_bots?.total_count || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* User MTProto */}
        <Grid item xs={12} sm={6} lg={2.4}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}`, height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TelegramIcon sx={{ color: '#0088cc' }} />
                <Typography variant="h6">User MTProto</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {getStatusIcon(health?.user_mtproto?.status || 'unknown')}
                <Typography>{capitalizeStatus(health?.user_mtproto?.status || 'unknown')}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" display="block">
                Active: {health?.user_mtproto?.active_sessions || 0} sessions
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block">
                Configured: {health?.user_mtproto?.total_configured || 0} channels
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Metrics Section */}
      {health?.performance && (
        <Paper sx={{ p: 3, mb: 4, border: `1px solid ${theme.palette.divider}` }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
            <PerformanceIcon color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Performance Metrics
            </Typography>
            <Chip
              label={`${health.performance.requests_per_minute} req/min`}
              size="small"
              color="primary"
              variant="outlined"
            />
          </Box>

          {/* Key Metrics Grid */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6} sm={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: alpha(theme.palette.primary.main, 0.05) }}>
                <Typography variant="h4" color="primary" fontWeight={600}>
                  {health.performance.total_requests.toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Requests
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={6} sm={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: alpha(theme.palette.success.main, 0.05) }}>
                <Typography variant="h4" color="success.main" fontWeight={600}>
                  {health.performance.requests_per_minute}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Requests / Minute
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={6} sm={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: alpha(theme.palette.info.main, 0.05) }}>
                <Typography variant="h4" color="info.main" fontWeight={600}>
                  {health.performance.avg_response_time_ms.toFixed(0)}ms
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Avg Response Time
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={6} sm={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: alpha(
                health.performance.error_rate_percent > 5 ? theme.palette.error.main : theme.palette.success.main,
                0.05
              )}}>
                <Typography 
                  variant="h4" 
                  color={health.performance.error_rate_percent > 5 ? 'error.main' : 'success.main'}
                  fontWeight={600}
                >
                  {health.performance.error_rate_percent.toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Error Rate
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          {/* Additional Metrics Row */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, bgcolor: alpha(theme.palette.secondary.main, 0.03) }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <MetricsIcon fontSize="small" color="secondary" />
                  <Typography variant="subtitle2">Cache Performance</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h5" color="secondary" fontWeight={600}>
                    {health.performance.cache_hit_rate_percent.toFixed(1)}%
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Hit Rate
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={health.performance.cache_hit_rate_percent}
                  sx={{
                    mt: 1,
                    height: 6,
                    borderRadius: 3,
                    bgcolor: alpha(theme.palette.secondary.main, 0.1),
                    '& .MuiLinearProgress-bar': {
                      bgcolor: theme.palette.secondary.main,
                      borderRadius: 3,
                    },
                  }}
                />
              </Paper>
            </Grid>

            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, bgcolor: alpha(theme.palette.info.main, 0.03) }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <DatabaseIcon fontSize="small" color="info" />
                  <Typography variant="subtitle2">Database Queries</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h5" color="info.main" fontWeight={600}>
                    {health.performance.recent_db_query_avg_ms.toFixed(1)}ms
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Avg Time
                  </Typography>
                </Box>
              </Paper>
            </Grid>

            <Grid item xs={12} sm={4}>
              <Paper sx={{ p: 2, bgcolor: alpha(theme.palette.success.main, 0.03) }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TimerIcon fontSize="small" color="success" />
                  <Typography variant="subtitle2">API Uptime</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h5" color="success.main" fontWeight={600}>
                    {formatUptime(health.performance.uptime_seconds / 3600)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Current Session
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          </Grid>

          {/* Slow Endpoints */}
          {health.performance.slow_endpoints && health.performance.slow_endpoints.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <WarningIcon fontSize="small" color="warning" />
                <Typography variant="subtitle1" fontWeight={600}>
                  Slow Endpoints (Top 5)
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {health.performance.slow_endpoints.slice(0, 5).map((endpoint, index) => (
                  <Paper 
                    key={index} 
                    sx={{ 
                      p: 1.5, 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      bgcolor: alpha(theme.palette.warning.main, 0.05),
                    }}
                  >
                    <Box>
                      <Typography variant="body2" fontWeight={500}>{endpoint.endpoint}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {endpoint.count} requests • {endpoint.errors} errors
                      </Typography>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography variant="body2" color="warning.main" fontWeight={600}>
                        Avg: {endpoint.avg_time_ms.toFixed(0)}ms
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Max: {endpoint.max_time_ms.toFixed(0)}ms
                      </Typography>
                    </Box>
                  </Paper>
                ))}
              </Box>
            </>
          )}
        </Paper>
      )}

      {/* Resource Usage */}
      {sys && (
        <Grid container spacing={2}>
          {/* CPU Usage */}
          <Grid item xs={12} md={4}>
            <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <CpuIcon color="primary" />
                  <Typography variant="h6">CPU Usage</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                    <CircularProgress
                      variant="determinate"
                      value={sys.cpu.percent}
                      size={80}
                      thickness={6}
                      sx={{
                        color: sys.cpu.percent > 80 ? theme.palette.error.main : sys.cpu.percent > 60 ? theme.palette.warning.main : theme.palette.success.main,
                      }}
                    />
                    <Box
                      sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="body1" fontWeight={600}>
                        {sys.cpu.percent}%
                      </Typography>
                    </Box>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Load: {sys.cpu.load_avg_1m} / {sys.cpu.load_avg_5m} / {sys.cpu.load_avg_15m}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {sys.cpu.frequency_mhz ? `${sys.cpu.frequency_mhz} MHz` : 'Frequency N/A'}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Memory Usage */}
          <Grid item xs={12} md={4}>
            <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <MemoryIcon color="secondary" />
                  <Typography variant="h6">Memory Usage</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                    <CircularProgress
                      variant="determinate"
                      value={sys.memory.percent}
                      size={80}
                      thickness={6}
                      sx={{
                        color: sys.memory.percent > 90 ? theme.palette.error.main : sys.memory.percent > 75 ? theme.palette.warning.main : theme.palette.success.main,
                      }}
                    />
                    <Box
                      sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="body1" fontWeight={600}>
                        {sys.memory.percent}%
                      </Typography>
                    </Box>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {sys.memory.used_gb} / {sys.memory.total_gb} GB
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Swap: {sys.memory.swap_percent}% ({sys.memory.swap_total_gb} GB)
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Disk Usage */}
          <Grid item xs={12} md={4}>
            <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <DiskIcon color="info" />
                  <Typography variant="h6">Disk Usage</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                    <CircularProgress
                      variant="determinate"
                      value={sys.disk.percent}
                      size={80}
                      thickness={6}
                      sx={{
                        color: sys.disk.percent > 90 ? theme.palette.error.main : sys.disk.percent > 75 ? theme.palette.warning.main : theme.palette.success.main,
                      }}
                    />
                    <Box
                      sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="body1" fontWeight={600}>
                        {sys.disk.percent}%
                      </Typography>
                    </Box>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {sys.disk.used_gb} / {sys.disk.total_gb} GB
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Free: {sys.disk.free_gb} GB
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default SystemHealthPage;
