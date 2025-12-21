/**
 * System AI Dashboard Page
 * 
 * Admin overview of the AI system:
 * - System status
 * - Worker overview
 * - Recent decisions
 * - Resource usage
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid2 as Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Chip,
  alpha,
  useTheme,
  IconButton,
  Tooltip,
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Button,
  CircularProgress,
  Skeleton,
  Alert,
} from '@mui/material';
import {
  SmartToy as AIIcon,
  Memory as MemoryIcon,
  Speed as CpuIcon,
  Storage as StorageIcon,
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  PlayArrow as RunningIcon,
  Pause as PausedIcon,
  Settings as ConfigIcon,
  History as HistoryIcon,
  TrendingUp as MetricsIcon,
  AutoMode as AutoIcon,
  Telegram as TelegramIcon,
  Api as ApiIcon,
  Schedule as CeleryIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface SystemAIStatus {
  enabled: boolean;
  auto_scale: boolean;
  dry_run: boolean;
  approval_level: 'auto' | 'review' | 'approval';
  uptime_hours: number;
  last_action_at: string | null;
}

interface WorkerSummary {
  id: string;
  name: string;
  type: 'mtproto' | 'bot' | 'api' | 'celery';
  status: 'running' | 'stopped' | 'error';
  cpu_percent: number;
  memory_mb: number;
}

interface RecentDecision {
  id: string;
  type: string;
  description: string;
  status: 'approved' | 'pending' | 'rejected' | 'executed';
  created_at: string;
}

interface ResourceUsage {
  cpu_percent: number;
  memory_percent: number;
  memory_used_gb: number;
  memory_total_gb: number;
  disk_percent: number;
}

const SystemAIDashboardPage: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<SystemAIStatus | null>(null);
  const [workers, setWorkers] = useState<WorkerSummary[]>([]);
  const [decisions, setDecisions] = useState<RecentDecision[]>([]);
  const [resources, setResources] = useState<ResourceUsage | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API calls
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setStatus({
          enabled: true,
          auto_scale: true,
          dry_run: false,
          approval_level: 'review',
          uptime_hours: 72.5,
          last_action_at: new Date(Date.now() - 1800000).toISOString(),
        });
        
        setWorkers([
          { id: '1', name: 'MTProto Pool', type: 'mtproto', status: 'running', cpu_percent: 15, memory_mb: 512 },
          { id: '2', name: 'Bot Handler', type: 'bot', status: 'running', cpu_percent: 8, memory_mb: 256 },
          { id: '3', name: 'API Server', type: 'api', status: 'running', cpu_percent: 12, memory_mb: 384 },
          { id: '4', name: 'Celery Workers', type: 'celery', status: 'running', cpu_percent: 25, memory_mb: 768 },
        ]);
        
        setDecisions([
          { id: '1', type: 'scale_up', description: 'Scale MTProto workers from 3 to 5', status: 'pending', created_at: new Date().toISOString() },
          { id: '2', type: 'config_change', description: 'Adjust rate limit for API', status: 'approved', created_at: new Date(Date.now() - 3600000).toISOString() },
          { id: '3', type: 'health_check', description: 'Routine health verification', status: 'executed', created_at: new Date(Date.now() - 7200000).toISOString() },
        ]);
        
        setResources({
          cpu_percent: 35,
          memory_percent: 62,
          memory_used_gb: 5.0,
          memory_total_gb: 8.0,
          disk_percent: 45,
        });
      } catch (err) {
        setError('Failed to load system AI data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const getWorkerIcon = (type: string) => {
    switch (type) {
      case 'mtproto': return <TelegramIcon />;
      case 'bot': return <AIIcon />;
      case 'api': return <ApiIcon />;
      case 'celery': return <CeleryIcon />;
      default: return <AIIcon />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <RunningIcon color="success" />;
      case 'stopped': return <PausedIcon color="warning" />;
      case 'error': return <ErrorIcon color="error" />;
      default: return <WarningIcon />;
    }
  };

  const getDecisionStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      case 'executed': return 'info';
      default: return 'default';
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const diff = Date.now() - new Date(dateString).getTime();
    const hours = Math.floor(diff / 3600000);
    if (hours < 1) return 'Just now';
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    return `${Math.floor(hours / 24)} days ago`;
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="text" width={300} height={40} />
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {[1, 2, 3, 4].map((i) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={i}>
              <Skeleton variant="rounded" height={150} />
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <AIIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />
            <Typography variant="h4" component="h1" fontWeight={700}>
              System AI Dashboard
            </Typography>
            {status?.enabled && (
              <Chip
                icon={<HealthyIcon />}
                label="Active"
                color="success"
                size="small"
              />
            )}
          </Box>
          <Typography variant="body1" color="text.secondary">
            AI-powered infrastructure management and monitoring
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton onClick={() => setLoading(true)}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="outlined"
            startIcon={<ConfigIcon />}
            onClick={() => navigate('/ai/config')}
          >
            Configuration
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Status Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: alpha(theme.palette.primary.main, 0.15),
                    color: theme.palette.primary.main,
                  }}
                >
                  <AIIcon />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    AI Status
                  </Typography>
                  <Typography variant="h5" fontWeight={700}>
                    {status?.enabled ? 'Active' : 'Disabled'}
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ mt: 2 }}>
                <Chip
                  label={`Auto-scale: ${status?.auto_scale ? 'ON' : 'OFF'}`}
                  size="small"
                  color={status?.auto_scale ? 'success' : 'default'}
                  sx={{ mr: 1 }}
                />
                <Chip
                  label={`Mode: ${status?.approval_level}`}
                  size="small"
                  variant="outlined"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: alpha(theme.palette.success.main, 0.15),
                    color: theme.palette.success.main,
                  }}
                >
                  <CpuIcon />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    CPU Usage
                  </Typography>
                  <Typography variant="h5" fontWeight={700}>
                    {resources?.cpu_percent}%
                  </Typography>
                </Box>
              </Box>
              <LinearProgress
                variant="determinate"
                value={resources?.cpu_percent || 0}
                sx={{ mt: 2, height: 6, borderRadius: 3 }}
                color={resources?.cpu_percent && resources.cpu_percent > 80 ? 'error' : 'primary'}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: alpha(theme.palette.info.main, 0.15),
                    color: theme.palette.info.main,
                  }}
                >
                  <MemoryIcon />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Memory
                  </Typography>
                  <Typography variant="h5" fontWeight={700}>
                    {resources?.memory_used_gb.toFixed(1)}/{resources?.memory_total_gb}GB
                  </Typography>
                </Box>
              </Box>
              <LinearProgress
                variant="determinate"
                value={resources?.memory_percent || 0}
                sx={{ mt: 2, height: 6, borderRadius: 3 }}
                color={resources?.memory_percent && resources.memory_percent > 80 ? 'warning' : 'info'}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    bgcolor: alpha(theme.palette.warning.main, 0.15),
                    color: theme.palette.warning.main,
                  }}
                >
                  <HistoryIcon />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Uptime
                  </Typography>
                  <Typography variant="h5" fontWeight={700}>
                    {status?.uptime_hours.toFixed(1)}h
                  </Typography>
                </Box>
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                Last action: {status?.last_action_at ? formatTimeAgo(status.last_action_at) : 'Never'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Workers */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardHeader
              avatar={<AutoIcon color="primary" />}
              title="Managed Workers"
              subheader={`${workers.filter(w => w.status === 'running').length}/${workers.length} running`}
              action={
                <Button size="small" onClick={() => navigate('/ai/workers')}>
                  View All
                </Button>
              }
            />
            <Divider />
            <List disablePadding>
              {workers.map((worker, index) => (
                <React.Fragment key={worker.id}>
                  {index > 0 && <Divider />}
                  <ListItem>
                    <ListItemIcon>
                      <Box
                        sx={{
                          p: 1,
                          borderRadius: 1,
                          bgcolor: alpha(theme.palette.primary.main, 0.1),
                        }}
                      >
                        {getWorkerIcon(worker.type)}
                      </Box>
                    </ListItemIcon>
                    <ListItemText
                      primary={worker.name}
                      secondary={`CPU: ${worker.cpu_percent}% | RAM: ${worker.memory_mb}MB`}
                    />
                    <ListItemSecondaryAction>
                      {getStatusIcon(worker.status)}
                    </ListItemSecondaryAction>
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          </Card>
        </Grid>

        {/* Recent Decisions */}
        <Grid size={{ xs: 12, md: 6 }}>
          <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
            <CardHeader
              avatar={<MetricsIcon color="primary" />}
              title="Recent AI Decisions"
              subheader={`${decisions.filter(d => d.status === 'pending').length} pending approval`}
              action={
                <Button size="small" onClick={() => navigate('/ai/decisions')}>
                  View All
                </Button>
              }
            />
            <Divider />
            <List disablePadding>
              {decisions.map((decision, index) => (
                <React.Fragment key={decision.id}>
                  {index > 0 && <Divider />}
                  <ListItem>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" fontWeight={500}>
                            {decision.description}
                          </Typography>
                          <Chip
                            label={decision.status}
                            size="small"
                            color={getDecisionStatusColor(decision.status) as any}
                          />
                        </Box>
                      }
                      secondary={formatTimeAgo(decision.created_at)}
                    />
                    {decision.status === 'pending' && (
                      <ListItemSecondaryAction>
                        <Button size="small" color="primary">
                          Review
                        </Button>
                      </ListItemSecondaryAction>
                    )}
                  </ListItem>
                </React.Fragment>
              ))}
            </List>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemAIDashboardPage;
