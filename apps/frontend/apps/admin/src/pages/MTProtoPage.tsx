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
  IconButton,
  Tooltip,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Menu,
} from '@mui/material';
import {
  Telegram as TelegramIcon,
  Refresh as RefreshIcon,
  CheckCircle as EnabledIcon,
  Cancel as DisabledIcon,
  Person as UserIcon,
  LiveTv as ChannelIcon,
  History as HistoryIcon,
  Close as CloseIcon,
  MoreVert as MoreVertIcon,
  Visibility as ViewIcon,
  PlayArrow as EnableIcon,
  Stop as DisableIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { apiClient } from '../api/client';
import { PageSkeleton } from '../components/Skeletons';

interface MTProtoSession {
  id: number;
  user_id: number;
  user_email: string | null;
  user_name: string | null;
  mtproto_id: number | null;  // Telegram user ID from MTProto authentication
  mtproto_username: string | null;  // Telegram username from MTProto authentication
  channel_id: number;
  channel_name: string | null;
  channel_username: string | null;
  mtproto_enabled: boolean;  // User toggle
  session_active: boolean;  // Actually has working session
  created_at: string;
  updated_at: string;
}

interface MTProtoStats {
  total_sessions: number;
  active_sessions: number;  // Actually working
  not_setup_sessions: number;  // Enabled but not completed
  disabled_sessions: number;
  users_with_mtproto: number;
}

interface SessionListResponse {
  total: number;
  page: number;
  page_size: number;
  sessions: MTProtoSession[];
}

interface ConnectedChannel {
  mtproto_id: number;
  channel_id: number;
  channel_name: string;
  channel_username: string | null;
  mtproto_enabled: boolean;
  connected_at: string | null;
}

interface SessionDetails {
  id: number;
  user_id: number;
  user_email: string | null;
  user_name: string | null;
  user_telegram_id: number | null;
  mtproto_id: number | null;
  mtproto_username: string | null;
  channel_name: string | null;
  channel_username: string | null;
  mtproto_enabled: boolean;
  created_at: string | null;
  updated_at: string | null;
  connected_channels: ConnectedChannel[];
  stats: {
    total_runs: number;
    first_run_at: string | null;
    last_run_at: string | null;
    avg_interval_minutes: number | null;
    total_errors: number;
  };
  recent_status_changes: Array<{
    action: string;
    timestamp: string | null;
    channel_id: number | null;
  }>;
}

const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'Never';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

const getActionIcon = (action: string) => {
  switch (action) {
    case 'collection_progress':
      return <EnabledIcon color="success" fontSize="small" />;
    case 'collection_start':
      return <EnabledIcon color="success" fontSize="small" />;
    case 'collection_end':
      return <HistoryIcon color="info" fontSize="small" />;
    case 'enabled':
      return <EnabledIcon color="success" fontSize="small" />;
    case 'disabled':
      return <DisabledIcon color="error" fontSize="small" />;
    default:
      return <HistoryIcon color="action" fontSize="small" />;
  }
};

const getActionLabel = (action: string): string => {
  switch (action) {
    case 'collection_progress':
      return 'Collection Completed';
    case 'collection_start':
      return 'Collection Started';
    case 'collection_end':
      return 'Collection Ended';
    case 'enabled':
      return 'MTProto Enabled';
    case 'disabled':
      return 'MTProto Disabled';
    default:
      return action;
  }
};

const MTProtoPage: React.FC = () => {
  const [sessions, setSessions] = useState<MTProtoSession[]>([]);
  const [stats, setStats] = useState<MTProtoStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  
  // Details dialog state
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState<SessionDetails | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);

  // Actions menu state
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [menuSession, setMenuSession] = useState<MTProtoSession | null>(null);

  // Delete confirmation state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteSession, setDeleteSession] = useState<MTProtoSession | null>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, session: MTProtoSession) => {
    setMenuAnchor(event.currentTarget);
    setMenuSession(session);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setMenuSession(null);
  };

  const handleDeleteSession = async () => {
    if (!deleteSession) return;
    
    setActionLoading(deleteSession.id);
    try {
      await apiClient.delete(`/admin/system/mtproto/sessions/${deleteSession.user_id}`);
      setDeleteDialogOpen(false);
      setDeleteSession(null);
      fetchStats();
      fetchSessions();
    } catch (err) {
      console.error('Delete error:', err);
      setError('Failed to delete MTProto session');
    } finally {
      setActionLoading(null);
    }
  };

  const fetchStats = useCallback(async () => {
    try {
      const response = await apiClient.get<MTProtoStats>('/admin/system/mtproto/stats');
      setStats(response.data);
    } catch (err) {
      console.error('Stats fetch error:', err);
    }
  }, []);

  const fetchSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        page: (page + 1).toString(),
        page_size: rowsPerPage.toString(),
      });

      if (statusFilter) {
        params.append('status_filter', statusFilter);
      }

      const response = await apiClient.get<SessionListResponse>(
        `/admin/system/mtproto/sessions?${params.toString()}`
      );
      setSessions(response.data.sessions || []);
      setTotal(response.data.total || 0);
    } catch (err) {
      setError('Failed to load MTProto sessions. Please try again.');
      console.error('Session fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, statusFilter]);

  useEffect(() => {
    fetchStats();
    fetchSessions();
  }, [fetchStats, fetchSessions]);

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleToggleSession = async (session: MTProtoSession) => {
    setActionLoading(session.id);
    try {
      await apiClient.patch(`/admin/system/mtproto/sessions/${session.id}/toggle`);
      await fetchSessions();
      await fetchStats();
    } catch (err) {
      setError('Failed to toggle MTProto session');
      console.error('Toggle error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleViewDetails = async (session: MTProtoSession) => {
    setDetailsOpen(true);
    setDetailsLoading(true);
    try {
      const response = await apiClient.get<SessionDetails>(
        `/admin/system/mtproto/sessions/${session.id}/details`
      );
      setSelectedSession(response.data);
    } catch (err) {
      console.error('Details fetch error:', err);
      setError('Failed to load session details');
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleCloseDetails = () => {
    setDetailsOpen(false);
    setSelectedSession(null);
  };

  const handleRefresh = () => {
    fetchStats();
    fetchSessions();
  };

  // Show skeleton on initial load
  if (loading && sessions.length === 0) {
    return (
      <PageSkeleton
        hasTitle={true}
        hasStats={true}
        statsCount={4}
        hasFilters={true}
        hasTable={true}
        tableRows={10}
        tableColumns={7}
      />
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            MTProto Management
          </Typography>
          <Typography color="text.secondary">
            Manage MTProto data collection sessions across all users
          </Typography>
        </Box>
        <Tooltip title="Refresh">
          <IconButton onClick={handleRefresh} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" fontWeight={700} color="primary">
                {stats?.total_sessions || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Sessions
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" fontWeight={700} color="success.main">
                {stats?.active_sessions || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" fontWeight={700} color="warning.main">
                {stats?.not_setup_sessions || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Not Setup
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" fontWeight={700} color="text.secondary">
                {stats?.disabled_sessions || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Disabled
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Status Filter</InputLabel>
          <Select
            value={statusFilter}
            label="Status Filter"
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(0);
            }}
          >
            <MenuItem value="">All Sessions</MenuItem>
            <MenuItem value="active">Active Only</MenuItem>
            <MenuItem value="not_setup">Not Setup Only</MenuItem>
            <MenuItem value="disabled">Disabled Only</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Paper>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>MTProto</TableCell>
                <TableCell>User</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Updated</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <CircularProgress size={32} />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Loading sessions...
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : sessions.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <TelegramIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                    <Typography color="text.secondary">No MTProto sessions found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                sessions.map((session) => (
                  <TableRow key={session.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <TelegramIcon fontSize="small" color="primary" />
                        <Box>
                          <Typography variant="body2" fontWeight={500}>
                            {session.mtproto_username ? `@${session.mtproto_username}` : '@pending'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            ID: {session.mtproto_id || 'Not set'}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <UserIcon fontSize="small" color="action" />
                        <Box>
                          <Typography variant="body2" fontWeight={500}>
                            {session.user_name || session.user_email || 'Unknown User'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            ID: {session.user_id}{session.user_email && ` • ${session.user_email}`}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={session.session_active ? <EnabledIcon /> : <DisabledIcon />}
                        label={session.session_active ? 'Active' : session.mtproto_enabled ? 'Not Setup' : 'Disabled'}
                        size="small"
                        color={session.session_active ? 'success' : session.mtproto_enabled ? 'warning' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDate(session.updated_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDate(session.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, session)}
                      >
                        <MoreVertIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={total}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[10, 25, 50, 100]}
        />
      </Paper>

      {/* Actions Menu */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuItem onClick={() => {
          if (menuSession) handleViewDetails(menuSession);
          handleMenuClose();
        }}>
          <ListItemIcon><ViewIcon fontSize="small" /></ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={() => {
            if (menuSession) handleToggleSession(menuSession);
            handleMenuClose();
          }}
          disabled={actionLoading === menuSession?.id}
        >
          <ListItemIcon>
            {menuSession?.mtproto_enabled ? (
              <DisableIcon fontSize="small" color="error" />
            ) : (
              <EnableIcon fontSize="small" color="success" />
            )}
          </ListItemIcon>
          <ListItemText sx={{ color: menuSession?.mtproto_enabled ? 'error.main' : 'success.main' }}>
            {menuSession?.mtproto_enabled ? 'Disable Collection' : 'Enable Collection'}
          </ListItemText>
        </MenuItem>
        <Divider />
        <MenuItem 
          onClick={() => {
            if (menuSession) {
              setDeleteSession(menuSession);
              setDeleteDialogOpen(true);
            }
            handleMenuClose();
          }}
          disabled={actionLoading === menuSession?.id}
        >
          <ListItemIcon><DeleteIcon fontSize="small" color="error" /></ListItemIcon>
          <ListItemText sx={{ color: 'error.main' }}>Delete MTProto</ListItemText>
        </MenuItem>
      </Menu>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete MTProto Session</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the MTProto session for{' '}
            <strong>{deleteSession?.mtproto_username ? `@${deleteSession.mtproto_username}` : `User ID ${deleteSession?.user_id}`}</strong>?
          </Typography>
          <Typography variant="body2" color="error" sx={{ mt: 2 }}>
            This will remove the MTProto configuration and all connected channel settings for this user. This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={() => handleDeleteSession()} 
            color="error" 
            variant="contained"
            disabled={actionLoading === deleteSession?.id}
          >
            {actionLoading === deleteSession?.id ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <TelegramIcon color="primary" />
              <Typography variant="h6">MTProto Session Details</Typography>
            </Box>
            <IconButton onClick={handleCloseDetails} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {detailsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : selectedSession ? (
            <Box>
              {/* Session Info */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      MTProto Account
                    </Typography>
                    <Typography variant="h6" fontWeight={600} color="primary">
                      {selectedSession.mtproto_username ? `@${selectedSession.mtproto_username}` : '@pending'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      ID: {selectedSession.mtproto_id || 'Not set'}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      User
                    </Typography>
                    <Typography variant="body1" fontWeight={500}>
                      {selectedSession.user_name || selectedSession.user_email || 'Unknown'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      ID: {selectedSession.user_id}{selectedSession.user_email && ` • ${selectedSession.user_email}`}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Connected Channels */}
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                Connected Channels ({selectedSession.connected_channels?.length || 0}/5)
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                {(selectedSession.connected_channels || []).map((channel) => (
                  <Grid item xs={12} sm={6} key={channel.channel_id}>
                    <Card variant="outlined">
                      <CardContent sx={{ py: 1.5 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                          <ChannelIcon fontSize="small" color="action" />
                          <Typography variant="body2" fontWeight={500}>
                            {channel.channel_name}
                          </Typography>
                          <Chip 
                            label={channel.mtproto_enabled ? "Active" : "Disabled"}
                            color={channel.mtproto_enabled ? "success" : "default"}
                            size="small"
                            sx={{ ml: 'auto' }}
                          />
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          {channel.channel_username && <span>@{channel.channel_username} • </span>}
                          ID: {channel.channel_id}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
                {(!selectedSession.connected_channels || selectedSession.connected_channels.length === 0) && (
                  <Grid item xs={12}>
                    <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                      No channels connected
                    </Typography>
                  </Grid>
                )}
              </Grid>

              {/* System Resource Stats */}
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                Resource Usage
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                      <Typography variant="h5" fontWeight={700} color="primary">
                        {selectedSession.stats.total_runs}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Total Runs
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                      <Typography variant="h5" fontWeight={700} color={selectedSession.stats.total_errors > 0 ? "error.main" : "success.main"}>
                        {selectedSession.stats.total_errors}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Total Errors
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                      <Typography variant="h5" fontWeight={700} color="info.main">
                        {selectedSession.stats.avg_interval_minutes ? `${selectedSession.stats.avg_interval_minutes}m` : '-'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Avg Interval
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                      <Chip 
                        label={selectedSession.mtproto_enabled ? "Enabled" : "Disabled"}
                        color={selectedSession.mtproto_enabled ? "success" : "default"}
                        size="small"
                      />
                      <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                        Status
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Timeline Info */}
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                Timeline
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={4}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      First Run
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      {formatDate(selectedSession.stats.first_run_at)}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      Last Run
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      {formatDate(selectedSession.stats.last_run_at)}
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      Session Created
                    </Typography>
                    <Typography variant="body2" fontWeight={500}>
                      {formatDate(selectedSession.created_at)}
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>

              {/* Status Changes */}
              <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 2 }}>
                Recent Status Changes
              </Typography>
              {(selectedSession.recent_status_changes?.length || 0) > 0 ? (
                <List dense sx={{ bgcolor: 'background.paper', borderRadius: 1 }}>
                  {selectedSession.recent_status_changes.map((change, index) => (
                    <React.Fragment key={index}>
                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          {getActionIcon(change.action)}
                        </ListItemIcon>
                        <ListItemText
                          primary={getActionLabel(change.action)}
                          secondary={formatDate(change.timestamp)}
                        />
                      </ListItem>
                      {index < selectedSession.recent_status_changes.length - 1 && <Divider component="li" />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary" sx={{ py: 2, textAlign: 'center' }}>
                  No status changes recorded
                </Typography>
              )}
            </Box>
          ) : (
            <Typography color="text.secondary" sx={{ py: 4, textAlign: 'center' }}>
              Failed to load session details
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MTProtoPage;
