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
  Settings as SettingsIcon,
  TrendingUp as TrendingUpIcon,
  History as HistoryIcon,
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

interface AuditLogEntry {
  id: number;
  service_key: string;
  action: string;
  old_limit: number | null;
  new_limit: number | null;
  old_period: string | null;
  new_period: string | null;
  old_enabled: boolean | null;
  new_enabled: boolean | null;
  changed_by: string;
  changed_by_username: string | null;
  changed_by_ip: string | null;
  change_reason: string | null;
  created_at: string;
}

interface HistoryDialogState {
  open: boolean;
  service: string;
  entries: AuditLogEntry[];
  loading: boolean;
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
  const [historyDialog, setHistoryDialog] = useState<HistoryDialogState>({
    open: false,
    service: '',
    entries: [],
    loading: false,
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
      await fetchDashboard();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  // Open history dialog and fetch audit trail
  const handleHistoryClick = async (service: string) => {
    setHistoryDialog({ open: true, service, entries: [], loading: true });
    try {
      const response = await apiClient.get('/admin/rate-limits/audit-trail', {
        params: { service_key: service, limit: 50 },
      });
      setHistoryDialog(prev => ({ ...prev, entries: response.data.entries, loading: false }));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch audit trail');
      setHistoryDialog(prev => ({ ...prev, loading: false }));
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
                          >
                            {stat.remaining}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {stat.reset_at
                              ? new Date(stat.reset_at).toLocaleTimeString()
                              : '-'}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                            <Tooltip title="View History">
                              <IconButton
                                size="small"
                                onClick={() => handleHistoryClick(stat.service)}
                                color="info"
                              >
                                <HistoryIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
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
                          </Box>
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
              Last updated: {dashboard?.timestamp ? new Date(dashboard.timestamp).toLocaleString() : 'N/A'}
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

      {/* History/Audit Trail Dialog */}
      <Dialog 
        open={historyDialog.open} 
        onClose={() => setHistoryDialog({ ...historyDialog, open: false })} 
        maxWidth="md" 
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <HistoryIcon />
            Change History: {formatServiceName(historyDialog.service)}
          </Box>
        </DialogTitle>
        <DialogContent>
          {historyDialog.loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : historyDialog.entries.length === 0 ? (
            <Box sx={{ textAlign: 'center', p: 4 }}>
              <Typography color="text.secondary">
                No change history available for this service
              </Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Date & Time</TableCell>
                    <TableCell>Action</TableCell>
                    <TableCell>Changed By</TableCell>
                    <TableCell>Before</TableCell>
                    <TableCell>After</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {historyDialog.entries.map((entry) => (
                    <TableRow key={entry.id} hover>
                      <TableCell>
                        <Typography variant="caption">
                          {new Date(entry.created_at).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={entry.action}
                          size="small"
                          color={
                            entry.action === 'create' ? 'success' :
                            entry.action === 'update' ? 'primary' :
                            entry.action === 'delete' ? 'error' :
                            'default'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {entry.changed_by_username || entry.changed_by}
                        </Typography>
                        {entry.changed_by_ip && (
                          <Typography variant="caption" color="text.secondary">
                            {entry.changed_by_ip}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {entry.old_limit !== null && (
                          <Typography variant="body2">
                            {entry.old_limit}/{entry.old_period}
                            {entry.old_enabled === false && ' (disabled)'}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {entry.new_limit !== null && (
                          <Typography variant="body2" fontWeight="medium">
                            {entry.new_limit}/{entry.new_period}
                            {entry.new_enabled === false && ' (disabled)'}
                          </Typography>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryDialog({ ...historyDialog, open: false })}>
            Close
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
