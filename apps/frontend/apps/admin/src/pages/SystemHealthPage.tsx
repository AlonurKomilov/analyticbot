import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid2 as Grid,
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
} from '@mui/icons-material';
import { apiClient } from '@api/client';
import { API_ENDPOINTS } from '@config/api';

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

interface HealthStatus {
  status: string;
  timestamp: string;
  database: { status: string; latency_ms: number; connections?: number };
  redis: { status: string; latency_ms: number; memory?: { used_mb: number; peak_mb: number } };
  api: { status: string; uptime_hours: number };
  user_bots?: { status: string; active_count: number; total_count: number };
  user_mtproto?: { status: string; active_sessions: number; total_configured: number };
  system: SystemInfo;
  issues?: string[];
}

// Helper to normalize system data from old or new format
const normalizeSystemData = (data: any): SystemInfo => {
  // Check if it's the new nested format
  if (data?.system?.cpu?.percent !== undefined) {
    return data.system;
  }
  
  // Handle old flat format
  return {
    cpu: {
      percent: data?.system?.cpu_percent ?? data?.cpu_percent ?? 0,
      cores_physical: data?.system?.cores_physical ?? 1,
      cores_logical: data?.system?.cores_logical ?? 1,
      frequency_mhz: data?.system?.frequency_mhz ?? null,
      load_avg_1m: data?.system?.load_avg_1m ?? 0,
      load_avg_5m: data?.system?.load_avg_5m ?? 0,
      load_avg_15m: data?.system?.load_avg_15m ?? 0,
    },
    memory: {
      percent: data?.system?.memory_percent ?? data?.memory_percent ?? 0,
      total_gb: data?.system?.memory_total_gb ?? 0,
      used_gb: data?.system?.memory_used_gb ?? 0,
      available_gb: data?.system?.memory_available_gb ?? 0,
      swap_percent: data?.system?.swap_percent ?? 0,
      swap_total_gb: data?.system?.swap_total_gb ?? 0,
    },
    disk: {
      percent: data?.system?.disk_percent ?? data?.disk_percent ?? 0,
      total_gb: data?.system?.disk_total_gb ?? 0,
      used_gb: data?.system?.disk_used_gb ?? 0,
      free_gb: data?.system?.disk_free_gb ?? 0,
    },
    uptime_hours: data?.system?.uptime_hours ?? 0,
    platform: data?.system?.platform ?? 'Unknown',
    hostname: data?.system?.hostname ?? 'Unknown',
  };
};

const SystemHealthPage: React.FC = () => {
  const theme = useTheme();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval] = useState(5); // seconds

  const fetchHealth = useCallback(async (showRefreshSpinner = false) => {
    if (showRefreshSpinner) {
      setRefreshing(true);
    }
    setError(null);
    
    try {
      const response = await apiClient.get(API_ENDPOINTS.ADMIN.HEALTH);
      const data = response.data;
      
      // Normalize system data
      const normalizedSystem = normalizeSystemData(data);
      
      setHealth({
        ...data,
        system: normalizedSystem,
      });
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

  // Auto-refresh with configurable interval
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

  const getStatusColor = (percent: number) => {
    if (percent < 60) return theme.palette.success.main;
    if (percent < 80) return theme.palette.warning.main;
    return theme.palette.error.main;
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
    <Box>
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
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Database */}
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
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
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
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
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
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
                Session Uptime: {health?.api?.uptime_hours || 0}h
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* User Bots */}
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
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
        <Grid size={{ xs: 12, sm: 6, md: 2.4 }}>
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

      {/* System Resources - Enhanced */}
      <Paper sx={{ p: 3, border: `1px solid ${theme.palette.divider}` }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h6" fontWeight={600}>
            System Resources
          </Typography>
          {autoRefresh && (
            <Chip 
              label="Live" 
              size="small" 
              color="success" 
              sx={{ 
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.6 },
                  '100%': { opacity: 1 },
                },
              }} 
            />
          )}
        </Box>
        
        <Grid container spacing={4}>
          {/* CPU Section */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Paper sx={{ p: 2, bgcolor: alpha(theme.palette.primary.main, 0.03) }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <CpuIcon color="primary" />
                <Typography variant="subtitle1" fontWeight={600}>CPU</Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">Usage</Typography>
                  <Typography variant="body2" fontWeight={600} color={getStatusColor(sys?.cpu.percent || 0)}>
                    {sys?.cpu.percent || 0}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={sys?.cpu.percent || 0}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    bgcolor: alpha(theme.palette.primary.main, 0.1),
                    '& .MuiLinearProgress-bar': {
                      bgcolor: getStatusColor(sys?.cpu.percent || 0),
                      borderRadius: 4,
                    },
                  }}
                />
              </Box>
              
              <Divider sx={{ my: 1.5 }} />
              
              <Stack spacing={0.5}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="text.secondary">Cores (Physical/Logical)</Typography>
                  <Typography variant="caption">{sys?.cpu.cores_physical} / {sys?.cpu.cores_logical}</Typography>
                </Box>
                {sys?.cpu.frequency_mhz && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="caption" color="text.secondary">Frequency</Typography>
                    <Typography variant="caption">{sys.cpu.frequency_mhz} MHz</Typography>
                  </Box>
                )}
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="text.secondary">Load Avg (1/5/15m)</Typography>
                  <Typography variant="caption">
                    {sys?.cpu.load_avg_1m} / {sys?.cpu.load_avg_5m} / {sys?.cpu.load_avg_15m}
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>

          {/* Memory Section */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Paper sx={{ p: 2, bgcolor: alpha(theme.palette.secondary.main, 0.03) }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <MemoryIcon color="secondary" />
                <Typography variant="subtitle1" fontWeight={600}>Memory</Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">RAM Usage</Typography>
                  <Typography variant="body2" fontWeight={600} color={getStatusColor(sys?.memory.percent || 0)}>
                    {sys?.memory.used_gb || 0} / {sys?.memory.total_gb || 0} GB ({sys?.memory.percent || 0}%)
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={sys?.memory.percent || 0}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    bgcolor: alpha(theme.palette.secondary.main, 0.1),
                    '& .MuiLinearProgress-bar': {
                      bgcolor: getStatusColor(sys?.memory.percent || 0),
                      borderRadius: 4,
                    },
                  }}
                />
              </Box>
              
              <Divider sx={{ my: 1.5 }} />
              
              <Stack spacing={0.5}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="text.secondary">Total RAM</Typography>
                  <Typography variant="caption">{sys?.memory.total_gb} GB</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="text.secondary">Used / Available</Typography>
                  <Typography variant="caption">{sys?.memory.used_gb} GB / {sys?.memory.available_gb} GB</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="text.secondary">Swap</Typography>
                  <Typography variant="caption">{sys?.memory.swap_percent}% of {sys?.memory.swap_total_gb} GB</Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>

          {/* Disk Section */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Paper sx={{ p: 2, bgcolor: alpha(theme.palette.info.main, 0.03) }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <DiskIcon color="info" />
                <Typography variant="subtitle1" fontWeight={600}>Disk</Typography>
              </Box>
              
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Typography variant="body2">Storage Usage</Typography>
                  <Typography variant="body2" fontWeight={600} color={getStatusColor(sys?.disk.percent || 0)}>
                    {sys?.disk.used_gb || 0} / {sys?.disk.total_gb || 0} GB ({sys?.disk.percent || 0}%)
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={sys?.disk.percent || 0}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    bgcolor: alpha(theme.palette.info.main, 0.1),
                    '& .MuiLinearProgress-bar': {
                      bgcolor: getStatusColor(sys?.disk.percent || 0),
                      borderRadius: 4,
                    },
                  }}
                />
              </Box>
              
              <Divider sx={{ my: 1.5 }} />
              
              <Stack spacing={0.5}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="text.secondary">Total Space</Typography>
                  <Typography variant="caption">{sys?.disk.total_gb} GB</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="text.secondary">Used Space</Typography>
                  <Typography variant="caption">{sys?.disk.used_gb} GB</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="caption" color="text.secondary">Free Space</Typography>
                  <Typography variant="caption">{sys?.disk.free_gb} GB</Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default SystemHealthPage;
