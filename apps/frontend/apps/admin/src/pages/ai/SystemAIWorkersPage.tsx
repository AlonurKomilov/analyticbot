/**
 * System AI Workers Page
 * 
 * Manage AI-monitored workers:
 * - Worker list and status
 * - Start/stop/restart controls
 * - Resource monitoring
 * - Scaling controls
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
  CardActions,
  Chip,
  alpha,
  useTheme,
  IconButton,
  Tooltip,
  LinearProgress,
  Divider,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Skeleton,
  Alert,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  SmartToy as AIIcon,
  Memory as MemoryIcon,
  Speed as CpuIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as RestartIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  Settings as ConfigIcon,
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Telegram as TelegramIcon,
  Api as ApiIcon,
  Schedule as CeleryIcon,
  MoreVert as MoreIcon,
  TrendingUp as ScaleUpIcon,
  TrendingDown as ScaleDownIcon,
} from '@mui/icons-material';

interface Worker {
  id: string;
  name: string;
  type: 'mtproto' | 'bot' | 'api' | 'celery';
  status: 'running' | 'stopped' | 'error' | 'starting' | 'stopping';
  instances: number;
  max_instances: number;
  cpu_percent: number;
  memory_mb: number;
  memory_limit_mb: number;
  uptime_hours: number;
  last_health_check: string;
  auto_scale_enabled: boolean;
}

const SystemAIWorkersPage: React.FC = () => {
  const theme = useTheme();
  
  const [loading, setLoading] = useState(true);
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [selectedWorker, setSelectedWorker] = useState<Worker | null>(null);
  const [scaleDialogOpen, setScaleDialogOpen] = useState(false);
  const [scaleValue, setScaleValue] = useState(1);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWorkers = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setWorkers([
          {
            id: '1',
            name: 'MTProto Pool',
            type: 'mtproto',
            status: 'running',
            instances: 3,
            max_instances: 10,
            cpu_percent: 15,
            memory_mb: 512,
            memory_limit_mb: 1024,
            uptime_hours: 72,
            last_health_check: new Date().toISOString(),
            auto_scale_enabled: true,
          },
          {
            id: '2',
            name: 'Bot Handler',
            type: 'bot',
            status: 'running',
            instances: 2,
            max_instances: 5,
            cpu_percent: 8,
            memory_mb: 256,
            memory_limit_mb: 512,
            uptime_hours: 72,
            last_health_check: new Date().toISOString(),
            auto_scale_enabled: true,
          },
          {
            id: '3',
            name: 'API Server',
            type: 'api',
            status: 'running',
            instances: 4,
            max_instances: 8,
            cpu_percent: 22,
            memory_mb: 384,
            memory_limit_mb: 768,
            uptime_hours: 72,
            last_health_check: new Date().toISOString(),
            auto_scale_enabled: false,
          },
          {
            id: '4',
            name: 'Celery Workers',
            type: 'celery',
            status: 'running',
            instances: 5,
            max_instances: 20,
            cpu_percent: 35,
            memory_mb: 768,
            memory_limit_mb: 2048,
            uptime_hours: 48,
            last_health_check: new Date().toISOString(),
            auto_scale_enabled: true,
          },
        ]);
      } catch (err) {
        setError('Failed to load workers');
      } finally {
        setLoading(false);
      }
    };
    
    fetchWorkers();
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'success';
      case 'stopped': return 'default';
      case 'error': return 'error';
      case 'starting': return 'info';
      case 'stopping': return 'warning';
      default: return 'default';
    }
  };

  const handleAction = async (workerId: string, action: 'start' | 'stop' | 'restart') => {
    // TODO: API call
    console.log(`${action} worker ${workerId}`);
  };

  const handleScale = async () => {
    if (!selectedWorker) return;
    // TODO: API call
    console.log(`Scale ${selectedWorker.name} to ${scaleValue} instances`);
    setScaleDialogOpen(false);
  };

  const handleToggleAutoScale = async (workerId: string, enabled: boolean) => {
    setWorkers(prev => prev.map(w => 
      w.id === workerId ? { ...w, auto_scale_enabled: enabled } : w
    ));
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="text" width={300} height={40} />
        <Skeleton variant="rounded" height={400} sx={{ mt: 3 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight={700} gutterBottom>
            Managed Workers
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-monitored infrastructure components
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" startIcon={<RestartIcon />}>
            Refresh All
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[
          { label: 'Total Workers', value: workers.length, color: theme.palette.primary.main },
          { label: 'Running', value: workers.filter(w => w.status === 'running').length, color: theme.palette.success.main },
          { label: 'Total Instances', value: workers.reduce((sum, w) => sum + w.instances, 0), color: theme.palette.info.main },
          { label: 'Auto-scale Enabled', value: workers.filter(w => w.auto_scale_enabled).length, color: theme.palette.warning.main },
        ].map((stat) => (
          <Grid size={{ xs: 6, md: 3 }} key={stat.label}>
            <Card sx={{ border: `1px solid ${theme.palette.divider}` }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h3" fontWeight={700} sx={{ color: stat.color }}>
                  {stat.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {stat.label}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Workers Table */}
      <TableContainer component={Paper} sx={{ border: `1px solid ${theme.palette.divider}` }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Worker</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Instances</TableCell>
              <TableCell>CPU</TableCell>
              <TableCell>Memory</TableCell>
              <TableCell>Auto-scale</TableCell>
              <TableCell>Uptime</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {workers.map((worker) => (
              <TableRow key={worker.id} hover>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Box
                      sx={{
                        p: 1,
                        borderRadius: 1,
                        bgcolor: alpha(theme.palette.primary.main, 0.1),
                        color: theme.palette.primary.main,
                      }}
                    >
                      {getWorkerIcon(worker.type)}
                    </Box>
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600}>
                        {worker.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {worker.type}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                
                <TableCell>
                  <Chip
                    label={worker.status}
                    size="small"
                    color={getStatusColor(worker.status) as any}
                  />
                </TableCell>
                
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2">
                      {worker.instances}/{worker.max_instances}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Tooltip title="Scale Up">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedWorker(worker);
                            setScaleValue(worker.instances + 1);
                            setScaleDialogOpen(true);
                          }}
                          disabled={worker.instances >= worker.max_instances}
                        >
                          <ScaleUpIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Scale Down">
                        <IconButton
                          size="small"
                          onClick={() => {
                            setSelectedWorker(worker);
                            setScaleValue(Math.max(1, worker.instances - 1));
                            setScaleDialogOpen(true);
                          }}
                          disabled={worker.instances <= 1}
                        >
                          <ScaleDownIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                </TableCell>
                
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={worker.cpu_percent}
                      sx={{ width: 60, height: 6, borderRadius: 3 }}
                      color={worker.cpu_percent > 80 ? 'error' : 'primary'}
                    />
                    <Typography variant="body2">{worker.cpu_percent}%</Typography>
                  </Box>
                </TableCell>
                
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={(worker.memory_mb / worker.memory_limit_mb) * 100}
                      sx={{ width: 60, height: 6, borderRadius: 3 }}
                      color={worker.memory_mb / worker.memory_limit_mb > 0.8 ? 'warning' : 'info'}
                    />
                    <Typography variant="body2">
                      {worker.memory_mb}/{worker.memory_limit_mb}MB
                    </Typography>
                  </Box>
                </TableCell>
                
                <TableCell>
                  <Switch
                    checked={worker.auto_scale_enabled}
                    onChange={(e) => handleToggleAutoScale(worker.id, e.target.checked)}
                    size="small"
                  />
                </TableCell>
                
                <TableCell>
                  <Typography variant="body2">{worker.uptime_hours}h</Typography>
                </TableCell>
                
                <TableCell align="right">
                  <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
                    {worker.status === 'running' ? (
                      <>
                        <Tooltip title="Restart">
                          <IconButton
                            size="small"
                            onClick={() => handleAction(worker.id, 'restart')}
                          >
                            <RestartIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Stop">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleAction(worker.id, 'stop')}
                          >
                            <StopIcon />
                          </IconButton>
                        </Tooltip>
                      </>
                    ) : (
                      <Tooltip title="Start">
                        <IconButton
                          size="small"
                          color="success"
                          onClick={() => handleAction(worker.id, 'start')}
                        >
                          <StartIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Scale Dialog */}
      <Dialog open={scaleDialogOpen} onClose={() => setScaleDialogOpen(false)}>
        <DialogTitle>Scale {selectedWorker?.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Current instances: {selectedWorker?.instances} / Max: {selectedWorker?.max_instances}
            </Typography>
            <TextField
              fullWidth
              type="number"
              label="Target Instances"
              value={scaleValue}
              onChange={(e) => setScaleValue(Number(e.target.value))}
              inputProps={{
                min: 1,
                max: selectedWorker?.max_instances || 10,
              }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScaleDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleScale}>
            Scale
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SystemAIWorkersPage;
