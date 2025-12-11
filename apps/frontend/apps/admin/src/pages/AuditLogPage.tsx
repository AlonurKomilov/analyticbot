import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
  Grid,
  InputAdornment,
} from '@mui/material';
import {
  History as AuditIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Person as PersonIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../config/api';
import { PageSkeleton } from '../components/Skeletons';

interface AuditLogEntry {
  id: number;
  admin_user_id: number;
  admin_username: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  user_agent: string | null;
  timestamp: string;
  success: boolean;
  error_message: string | null;
}

interface AuditLogResponse {
  entries: AuditLogEntry[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const ACTION_COLORS: Record<string, 'success' | 'error' | 'warning' | 'info' | 'default'> = {
  admin_login: 'success',
  admin_logout: 'info',
  admin_login_failed: 'error',
  user_suspend: 'warning',
  user_unsuspend: 'success',
  user_delete: 'error',
  user_credits_adjust: 'info',
  channel_suspend: 'warning',
  channel_unsuspend: 'success',
  channel_delete: 'error',
  channel_force_sync: 'info',
  bot_suspend: 'warning',
  bot_activate: 'success',
  settings_update: 'info',
};

const formatActionName = (action: string): string => {
  return action
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
};

const AuditLogPage: React.FC = () => {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [total, setTotal] = useState(0);
  const [actions, setActions] = useState<string[]>([]);

  // Filters
  const [selectedAction, setSelectedAction] = useState<string>('');
  const [adminFilter, setAdminFilter] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const fetchActions = useCallback(async () => {
    try {
      const response = await apiClient.get<string[]>(`${API_ENDPOINTS.ADMIN.AUDIT_LOG}/actions`);
      setActions(response.data);
    } catch {
      console.error('Failed to fetch action types');
    }
  }, []);

  const fetchAuditLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        page: (page + 1).toString(),
        page_size: rowsPerPage.toString(),
      });

      if (selectedAction) {
        params.append('action', selectedAction);
      }
      if (adminFilter) {
        params.append('admin_id', adminFilter);
      }
      if (startDate) {
        params.append('start_date', startDate);
      }
      if (endDate) {
        params.append('end_date', endDate);
      }

      const response = await apiClient.get<AuditLogResponse>(
        `${API_ENDPOINTS.ADMIN.AUDIT_LOG}?${params.toString()}`
      );
      setEntries(response.data.entries);
      setTotal(response.data.total);
    } catch (err) {
      setError('Failed to load audit logs. Please try again.');
      console.error('Audit log fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, selectedAction, adminFilter, startDate, endDate]);

  useEffect(() => {
    fetchActions();
  }, [fetchActions]);

  useEffect(() => {
    fetchAuditLogs();
  }, [fetchAuditLogs]);

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleClearFilters = () => {
    setSelectedAction('');
    setAdminFilter('');
    setStartDate('');
    setEndDate('');
    setPage(0);
  };

  const hasActiveFilters = selectedAction || adminFilter || startDate || endDate;

  // Show skeleton on initial load
  if (loading && entries.length === 0) {
    return (
      <PageSkeleton
        hasTitle={true}
        hasStats={false}
        hasFilters={true}
        hasTable={true}
        tableRows={15}
        tableColumns={7}
      />
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Audit Log
          </Typography>
          <Typography color="text.secondary">
            Track all administrative actions and system events
          </Typography>
        </Box>
        <Tooltip title="Refresh">
          <IconButton onClick={fetchAuditLogs} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Action Type</InputLabel>
              <Select
                value={selectedAction}
                label="Action Type"
                onChange={(e) => {
                  setSelectedAction(e.target.value);
                  setPage(0);
                }}
              >
                <MenuItem value="">All Actions</MenuItem>
                {actions.map((action) => (
                  <MenuItem key={action} value={action}>
                    {formatActionName(action)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              size="small"
              label="Admin ID"
              value={adminFilter}
              onChange={(e) => {
                setAdminFilter(e.target.value);
                setPage(0);
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <PersonIcon fontSize="small" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2.5}>
            <TextField
              fullWidth
              size="small"
              label="Start Date"
              type="date"
              value={startDate}
              onChange={(e) => {
                setStartDate(e.target.value);
                setPage(0);
              }}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2.5}>
            <TextField
              fullWidth
              size="small"
              label="End Date"
              type="date"
              value={endDate}
              onChange={(e) => {
                setEndDate(e.target.value);
                setPage(0);
              }}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Search">
                <IconButton color="primary" onClick={fetchAuditLogs}>
                  <SearchIcon />
                </IconButton>
              </Tooltip>
              {hasActiveFilters && (
                <Tooltip title="Clear Filters">
                  <IconButton onClick={handleClearFilters}>
                    <ClearIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Admin</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Resource</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>IP Address</TableCell>
                <TableCell>Details</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <CircularProgress size={32} />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Loading audit logs...
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : entries.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <AuditIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                    <Typography color="text.secondary">
                      No audit log entries found
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                entries.map((entry) => (
                  <TableRow key={entry.id} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ whiteSpace: 'nowrap' }}>
                        {formatDate(entry.timestamp)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <PersonIcon fontSize="small" color="action" />
                        <Box>
                          <Typography variant="body2" fontWeight={500}>
                            {entry.admin_username || `User #${entry.admin_user_id}`}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            ID: {entry.admin_user_id}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={formatActionName(entry.action)}
                        size="small"
                        color={ACTION_COLORS[entry.action] || 'default'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      {entry.resource_type ? (
                        <Typography variant="body2">
                          {entry.resource_type}
                          {entry.resource_id && (
                            <Typography component="span" variant="caption" color="text.secondary">
                              {' '}#{entry.resource_id}
                            </Typography>
                          )}
                        </Typography>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          —
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {entry.success ? (
                        <Tooltip title="Success">
                          <SuccessIcon color="success" fontSize="small" />
                        </Tooltip>
                      ) : (
                        <Tooltip title={entry.error_message || 'Failed'}>
                          <ErrorIcon color="error" fontSize="small" />
                        </Tooltip>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                        {entry.ip_address || '—'}
                      </Typography>
                    </TableCell>
                    <TableCell sx={{ maxWidth: 200 }}>
                      {entry.details ? (
                        <Tooltip title={<pre style={{ margin: 0 }}>{JSON.stringify(entry.details, null, 2)}</pre>}>
                          <Typography 
                            variant="body2" 
                            color="text.secondary" 
                            sx={{ 
                              overflow: 'hidden', 
                              textOverflow: 'ellipsis', 
                              whiteSpace: 'nowrap',
                              cursor: 'help',
                            }}
                          >
                            {JSON.stringify(entry.details).slice(0, 50)}...
                          </Typography>
                        </Tooltip>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          —
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={total}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  );
};

export default AuditLogPage;
