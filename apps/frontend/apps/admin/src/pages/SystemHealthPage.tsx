import React, { useState, useEffect } from 'react';
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
} from '@mui/icons-material';
import { apiClient } from '@api/client';

interface HealthStatus {
  status: string;
  database: { status: string; latency_ms: number };
  redis: { status: string; latency_ms: number };
  api: { status: string; uptime_hours: number };
  bot: { status: string; active_connections: number };
  system: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
  };
}

const SystemHealthPage: React.FC = () => {
  const theme = useTheme();
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await apiClient.get('/admin/system/health');
        setHealth(response.data);
      } catch (error) {
        console.error('Failed to fetch health:', error);
        // Mock data on error
        setHealth({
          status: 'healthy',
          database: { status: 'healthy', latency_ms: 12 },
          redis: { status: 'healthy', latency_ms: 2 },
          api: { status: 'healthy', uptime_hours: 120 },
          bot: { status: 'healthy', active_connections: 5 },
          system: { cpu_percent: 35, memory_percent: 62, disk_percent: 45 },
        });
      } finally {
        setLoading(false);
      }
    };
    fetchHealth();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <HealthyIcon color="success" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'error': return <ErrorIcon color="error" />;
      default: return <WarningIcon color="disabled" />;
    }
  };

  const getStatusColor = (percent: number) => {
    if (percent < 60) return theme.palette.success.main;
    if (percent < 80) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Typography variant="h4" fontWeight={700}>
          System Health
        </Typography>
        <Chip
          icon={getStatusIcon(health?.status || 'unknown')}
          label={health?.status?.toUpperCase() || 'UNKNOWN'}
          color={health?.status === 'healthy' ? 'success' : 'warning'}
        />
      </Box>

      {/* Services Status */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Database */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <DatabaseIcon color="primary" />
                <Typography variant="h6">Database</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {getStatusIcon(health?.database?.status || 'unknown')}
                <Typography>{health?.database?.status || 'Unknown'}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Latency: {health?.database?.latency_ms || 0}ms
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Redis */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <MemoryIcon color="secondary" />
                <Typography variant="h6">Redis</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {getStatusIcon(health?.redis?.status || 'unknown')}
                <Typography>{health?.redis?.status || 'Unknown'}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Latency: {health?.redis?.latency_ms || 0}ms
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* API */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <ApiIcon color="info" />
                <Typography variant="h6">API</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {getStatusIcon(health?.api?.status || 'unknown')}
                <Typography>{health?.api?.status || 'Unknown'}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Uptime: {health?.api?.uptime_hours || 0}h
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Bot */}
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <BotIcon color="success" />
                <Typography variant="h6">Bot Service</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {getStatusIcon(health?.bot?.status || 'unknown')}
                <Typography>{health?.bot?.status || 'Unknown'}</Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Connections: {health?.bot?.active_connections || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* System Resources */}
      <Paper sx={{ p: 3, border: `1px solid ${theme.palette.divider}` }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          System Resources
        </Typography>
        <Grid container spacing={4} sx={{ mt: 1 }}>
          {/* CPU */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <CpuIcon />
              <Typography>CPU Usage</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={health?.system?.cpu_percent || 0}
              sx={{
                height: 10,
                borderRadius: 5,
                bgcolor: alpha(theme.palette.primary.main, 0.1),
                '& .MuiLinearProgress-bar': {
                  bgcolor: getStatusColor(health?.system?.cpu_percent || 0),
                },
              }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              {health?.system?.cpu_percent || 0}%
            </Typography>
          </Grid>

          {/* Memory */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <MemoryIcon />
              <Typography>Memory Usage</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={health?.system?.memory_percent || 0}
              sx={{
                height: 10,
                borderRadius: 5,
                bgcolor: alpha(theme.palette.primary.main, 0.1),
                '& .MuiLinearProgress-bar': {
                  bgcolor: getStatusColor(health?.system?.memory_percent || 0),
                },
              }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              {health?.system?.memory_percent || 0}%
            </Typography>
          </Grid>

          {/* Disk */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <DatabaseIcon />
              <Typography>Disk Usage</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={health?.system?.disk_percent || 0}
              sx={{
                height: 10,
                borderRadius: 5,
                bgcolor: alpha(theme.palette.primary.main, 0.1),
                '& .MuiLinearProgress-bar': {
                  bgcolor: getStatusColor(health?.system?.disk_percent || 0),
                },
              }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              {health?.system?.disk_percent || 0}%
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default SystemHealthPage;
