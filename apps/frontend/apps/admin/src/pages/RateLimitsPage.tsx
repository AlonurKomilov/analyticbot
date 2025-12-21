import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid2 as Grid,
  Card,
  CardContent,
  CardHeader,
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
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Speed as SpeedIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  CheckCircle as HealthyIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  RestartAlt as ResetIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingUpIcon,
  Person as PersonIcon,
  Public as PublicIcon,
} from '@mui/icons-material';
import { apiClient } from '@api/client';

interface RateLimitConfig {
  service: string;
  limit: number;
  period: string;
  enabled: boolean;
  description: string | null;
}

interface RateLimitUsage {
  service: string;
  current_usage: number;
  limit: number;
  period: string;
  remaining: number;
  reset_at: string | null;
  utilization_percent: number;
  is_at_limit: boolean;
}

interface DashboardData {
  configs: RateLimitConfig[];
  stats: RateLimitUsage[];
  summary: {
    total_services: number;
    services_at_limit: number;
    high_usage_services: number;
    total_requests_this_period: number;
    enabled_services: number;
  };
  timestamp: string;
}

interface EditDialogState {
  open: boolean;
  service: string;
  limit: number;
  period: string;
  enabled: boolean;
  description: string;
}

const RateLimitsPage: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [editDialog, setEditDialog] = useState<EditDialogState>({
    open: false,
    service: '',
    limit: 100,
    period: 'minute',
    enabled: true,
    description: '',
  });
  const [saving, setSaving] = useState(false);

  // Fetch dashboard data
  const fetchDashboard = useCallback(async (showRefreshing = false) => {
    if (showRefreshing) setRefreshing(true);
    try {
      const response = await apiClient.get('/admin/rate-limits/dashboard');
      setDashboard(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch rate limit data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Initial fetch and auto-refresh
  useEffect(() => {
    fetchDashboard();
    
    if (autoRefresh) {
      const interval = setInterval(() => fetchDashboard(), 30000); // 30 second refresh
      return () => clearInterval(interval);
    }
  }, [fetchDashboard, autoRefresh]);

  // Open edit dialog
  const handleEditClick = (config: RateLimitConfig) => {
    setEditDialog({
      open: true,
      service: config.service,
      limit: config.limit,
      period: config.period,
      enabled: config.enabled,
      description: config.description || '',
    });
  };

  // Save edited config
  const handleSaveConfig = async () => {
    setSaving(true);
    try {
      await apiClient.put(`/admin/rate-limits/configs/${editDialog.service}`, {
        limit: editDialog.limit,
        period: editDialog.period,
        enabled: editDialog.enabled,
        description: editDialog.description || null,
      });
      setEditDialog({ ...editDialog, open: false });
      fetchDashboard(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update configuration');
    } finally {
      setSaving(false);
    }
  };

  // Get status color based on utilization
  const getStatusColor = (utilization: number, isAtLimit: boolean) => {
    if (isAtLimit) return 'error';
    if (utilization > 80) return 'warning';
    if (utilization > 50) return 'info';
    return 'success';
  };

  // Get status icon
  const getStatusIcon = (utilization: number, isAtLimit: boolean) => {
    if (isAtLimit) return <ErrorIcon color="error" />;
    if (utilization > 80) return <WarningIcon color="warning" />;
    return <HealthyIcon color="success" />;
  };

  // Format service name for display
  const formatServiceName = (service: string) => {
    return service
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SpeedIcon fontSize="large" />
            Rate Limits Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Monitor and configure rate limits across all services
          </Typography>
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
            label="Auto-refresh"
          />
          <Tooltip title="Refresh now">
            <IconButton onClick={() => fetchDashboard(true)} disabled={refreshing}>
              <RefreshIcon sx={{ animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {dashboard && (
        <>
          {/* Summary Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        bgcolor: alpha(theme.palette.primary.main, 0.1),
                      }}
                    >
                      <SettingsIcon color="primary" />
                    </Box>
                    <Box>
                      <Typography variant="h4">{dashboard.summary.total_services}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Services
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        bgcolor: alpha(theme.palette.success.main, 0.1),
                      }}
                    >
                      <TrendingUpIcon color="success" />
                    </Box>
                    <Box>
                      <Typography variant="h4">{dashboard.summary.total_requests_this_period}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Requests This Period
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        bgcolor: alpha(theme.palette.warning.main, 0.1),
                      }}
                    >
                      <WarningIcon color="warning" />
                    </Box>
                    <Box>
                      <Typography variant="h4">{dashboard.summary.high_usage_services}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        High Usage ({'>'}80%)
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Card>
                <CardContent>
                  <Stack direction="row" alignItems="center" spacing={2}>
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        bgcolor: alpha(theme.palette.error.main, 0.1),
                      }}
                    >
                      <ErrorIcon color="error" />
                    </Box>
                    <Box>
                      <Typography variant="h4">{dashboard.summary.services_at_limit}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        At Limit
                      </Typography>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Rate Limits Table */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SpeedIcon />
              Service Rate Limits
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Service</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Usage</TableCell>
                    <TableCell>Limit</TableCell>
                    <TableCell>Period</TableCell>
                    <TableCell>Utilization</TableCell>
                    <TableCell>Remaining</TableCell>
                    <TableCell>Reset At</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dashboard.stats.map((stat) => {
                    const config = dashboard.configs.find(c => c.service === stat.service);
                    return (
                      <TableRow key={stat.service} hover>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getStatusIcon(stat.utilization_percent, stat.is_at_limit)}
                            <Box>
                              <Typography variant="body2" fontWeight="medium">
                                {formatServiceName(stat.service)}
                              </Typography>
                              {config?.description && (
                                <Typography variant="caption" color="text.secondary">
                                  {config.description}
                                </Typography>
                              )}
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={stat.is_at_limit ? 'AT LIMIT' : config?.enabled ? 'Active' : 'Disabled'}
                            color={stat.is_at_limit ? 'error' : config?.enabled ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {stat.current_usage}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {stat.limit}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" textTransform="capitalize">
                            {stat.period}
                          </Typography>
                        </TableCell>
                        <TableCell sx={{ minWidth: 150 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={Math.min(stat.utilization_percent, 100)}
                              color={getStatusColor(stat.utilization_percent, stat.is_at_limit)}
                              sx={{ flex: 1, height: 8, borderRadius: 1 }}
                            />
                            <Typography variant="caption" sx={{ minWidth: 45 }}>
                              {stat.utilization_percent.toFixed(1)}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Typography
                            variant="body2"
                            color={stat.remaining === 0 ? 'error' : 'text.secondary'}
                            fontWeight={stat.remaining === 0 ? 'bold' : 'normal'}
                          >
                            {stat.remaining}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="caption" color="text.secondary">
                            {stat.reset_at
                              ? new Date(stat.reset_at).toLocaleTimeString()
                              : '-'}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          {config && (
                            <Tooltip title="Edit Configuration">
                              <IconButton
                                size="small"
                                onClick={() => handleEditClick(config)}
                              >
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {/* Last Updated */}
          <Box sx={{ mt: 2, textAlign: 'right' }}>
            <Typography variant="caption" color="text.secondary">
              Last updated: {new Date(dashboard.timestamp).toLocaleString()}
            </Typography>
          </Box>
        </>
      )}

      {/* Edit Dialog */}
      <Dialog open={editDialog.open} onClose={() => setEditDialog({ ...editDialog, open: false })} maxWidth="sm" fullWidth>
        <DialogTitle>
          Edit Rate Limit: {formatServiceName(editDialog.service)}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={3} sx={{ mt: 2 }}>
            <TextField
              label="Request Limit"
              type="number"
              value={editDialog.limit}
              onChange={(e) => setEditDialog({ ...editDialog, limit: parseInt(e.target.value) || 0 })}
              fullWidth
              inputProps={{ min: 1 }}
              helperText="Maximum number of requests allowed"
            />
            <FormControl fullWidth>
              <InputLabel>Time Period</InputLabel>
              <Select
                value={editDialog.period}
                label="Time Period"
                onChange={(e) => setEditDialog({ ...editDialog, period: e.target.value })}
              >
                <MenuItem value="minute">Per Minute</MenuItem>
                <MenuItem value="hour">Per Hour</MenuItem>
                <MenuItem value="day">Per Day</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Description"
              value={editDialog.description}
              onChange={(e) => setEditDialog({ ...editDialog, description: e.target.value })}
              fullWidth
              multiline
              rows={2}
              helperText="Optional description for this rate limit"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={editDialog.enabled}
                  onChange={(e) => setEditDialog({ ...editDialog, enabled: e.target.checked })}
                />
              }
              label="Rate Limit Enabled"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog({ ...editDialog, open: false })}>
            Cancel
          </Button>
          <Button
            onClick={handleSaveConfig}
            variant="contained"
            disabled={saving || editDialog.limit < 1}
          >
            {saving ? <CircularProgress size={20} /> : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Spin animation */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </Box>
  );
};

export default RateLimitsPage;
