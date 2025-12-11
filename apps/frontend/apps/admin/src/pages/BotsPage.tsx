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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Menu,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  SmartToy as BotsIcon,
  Refresh as RefreshIcon,
  PlayArrow as ActivateIcon,
  Pause as SuspendIcon,
  Visibility as ViewIcon,
  Speed as RateLimitIcon,
  CheckCircle as VerifiedIcon,
  Warning as WarningIcon,
  MoreVert as MoreVertIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { apiClient } from '../api/client';
import { API_ENDPOINTS } from '../config/api';
import { PageSkeleton } from '../components/Skeletons';

interface BotInfo {
  id: number;
  user_id: number;
  bot_username: string;
  bot_id: number;
  status: 'active' | 'suspended' | 'inactive';
  is_verified: boolean;
  max_requests_per_second: number;
  max_concurrent_requests: number;
  total_requests: number;
  last_used_at: string | null;
  created_at: string;
  updated_at: string | null;
  suspension_reason: string | null;
}

interface BotListResponse {
  total: number;
  page: number;
  page_size: number;
  bots: BotInfo[];
}

const STATUS_COLORS: Record<string, 'success' | 'error' | 'warning' | 'default'> = {
  active: 'success',
  suspended: 'error',
  inactive: 'warning',
};

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

const BotsPage: React.FC = () => {
  const [bots, setBots] = useState<BotInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  // Dialogs
  const [suspendDialog, setSuspendDialog] = useState<BotInfo | null>(null);
  const [suspendReason, setSuspendReason] = useState('');
  const [rateLimitDialog, setRateLimitDialog] = useState<BotInfo | null>(null);
  const [newRateLimit, setNewRateLimit] = useState<number>(10);
  const [newConcurrent, setNewConcurrent] = useState<number>(5);
  const [deleteDialog, setDeleteDialog] = useState<BotInfo | null>(null);

  // Actions menu state
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [menuBot, setMenuBot] = useState<BotInfo | null>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, bot: BotInfo) => {
    setMenuAnchor(event.currentTarget);
    setMenuBot(bot);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setMenuBot(null);
  };

  // Summary stats
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    suspended: 0,
    inactive: 0,
  });

  const fetchBots = useCallback(async () => {
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

      const response = await apiClient.get<BotListResponse>(
        `${API_ENDPOINTS.BOTS.LIST}/list?${params.toString()}`
      );
      setBots(response.data.bots);
      setTotal(response.data.total);

      // Calculate stats from all bots (paginated properly)
      const statsResponse = await apiClient.get<BotListResponse>(
        `${API_ENDPOINTS.BOTS.LIST}/list?page=1&page_size=100`
      );
      const allBots = statsResponse.data.bots;
      const totalBots = statsResponse.data.total;
      setStats({
        total: totalBots,
        active: allBots.filter((b) => b.status === 'active').length,
        suspended: allBots.filter((b) => b.status === 'suspended').length,
        inactive: allBots.filter((b) => b.status === 'inactive').length,
      });
    } catch (err) {
      setError('Failed to load bots. Please try again.');
      console.error('Bot fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, statusFilter]);

  useEffect(() => {
    fetchBots();
  }, [fetchBots]);

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSuspend = async () => {
    if (!suspendDialog) return;
    setActionLoading(suspendDialog.id);
    try {
      await apiClient.patch(`${API_ENDPOINTS.BOTS.LIST}/${suspendDialog.user_id}/suspend`, {
        reason: suspendReason || 'Suspended by admin',
      });
      await fetchBots();
      setSuspendDialog(null);
      setSuspendReason('');
    } catch (err) {
      setError('Failed to suspend bot');
      console.error('Suspend error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleActivate = async (bot: BotInfo) => {
    setActionLoading(bot.id);
    try {
      await apiClient.patch(`${API_ENDPOINTS.BOTS.LIST}/${bot.user_id}/activate`);
      await fetchBots();
    } catch (err: unknown) {
      // Extract error message from API response
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail 
        || 'Failed to activate bot';
      setError(errorMessage);
      console.error('Activate error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleRateLimitUpdate = async () => {
    if (!rateLimitDialog) return;
    setActionLoading(rateLimitDialog.id);
    try {
      await apiClient.patch(`${API_ENDPOINTS.BOTS.LIST}/${rateLimitDialog.user_id}/rate-limits`, {
        max_requests_per_second: newRateLimit,
        max_concurrent_requests: newConcurrent,
      });
      await fetchBots();
      setRateLimitDialog(null);
    } catch (err) {
      setError('Failed to update rate limits');
      console.error('Rate limit error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteBot = async () => {
    if (!deleteDialog) return;
    setActionLoading(deleteDialog.id);
    try {
      await apiClient.delete(`${API_ENDPOINTS.BOTS.LIST}/${deleteDialog.user_id}/delete`);
      await fetchBots();
      setDeleteDialog(null);
    } catch (err: unknown) {
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail 
        || 'Failed to delete bot';
      setError(errorMessage);
      console.error('Delete error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  // Show skeleton on initial load
  if (loading && bots.length === 0) {
    return (
      <PageSkeleton
        hasTitle={true}
        hasStats={true}
        statsCount={4}
        hasFilters={true}
        hasTable={true}
        tableRows={10}
        tableColumns={8}
      />
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Bot Management
          </Typography>
          <Typography color="text.secondary">
            Manage connected Telegram bots across all users
          </Typography>
        </Box>
        <Tooltip title="Refresh">
          <IconButton onClick={fetchBots} disabled={loading}>
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
                {stats.total}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Bots
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" fontWeight={700} color="success.main">
                {stats.active}
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
              <Typography variant="h4" fontWeight={700} color="error.main">
                {stats.suspended}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Suspended
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" fontWeight={700} color="warning.main">
                {stats.inactive}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Inactive
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
            <MenuItem value="">All Statuses</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="suspended">Suspended</MenuItem>
            <MenuItem value="inactive">Inactive</MenuItem>
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
                <TableCell>Bot</TableCell>
                <TableCell>User ID</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Verified</TableCell>
                <TableCell>Rate Limits</TableCell>
                <TableCell>Total Requests</TableCell>
                <TableCell>Last Used</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <CircularProgress size={32} />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Loading bots...
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : bots.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                    <BotsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                    <Typography color="text.secondary">No bots found</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                bots.map((bot) => (
                  <TableRow key={bot.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <BotsIcon fontSize="small" color="action" />
                        <Box>
                          <Typography variant="body2" fontWeight={500}>
                            @{bot.bot_username}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            ID: {bot.bot_id || 'Not set'}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{bot.user_id}</Typography>
                    </TableCell>
                    <TableCell>
                      {/* Show "Not Setup" for placeholder bots */}
                      {bot.bot_username === 'pending' || bot.bot_id === 0 ? (
                        <Chip
                          label="Not Setup"
                          size="small"
                          color="warning"
                        />
                      ) : (
                        <Chip
                          label={bot.status}
                          size="small"
                          color={STATUS_COLORS[bot.status] || 'default'}
                        />
                      )}
                      {bot.suspension_reason && (
                        <Tooltip title={bot.suspension_reason}>
                          <WarningIcon fontSize="small" color="error" sx={{ ml: 1 }} />
                        </Tooltip>
                      )}
                    </TableCell>
                    <TableCell>
                      {bot.is_verified ? (
                        <VerifiedIcon color="success" fontSize="small" />
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {bot.max_requests_per_second} RPS / {bot.max_concurrent_requests} conc.
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {bot.total_requests.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(bot.last_used_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={(e) => handleMenuOpen(e, bot)}
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
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={total}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
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
        <MenuItem onClick={handleMenuClose}>
          <ListItemIcon><ViewIcon fontSize="small" /></ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => {
          if (menuBot) {
            setRateLimitDialog(menuBot);
            setNewRateLimit(menuBot.max_requests_per_second);
            setNewConcurrent(menuBot.max_concurrent_requests);
          }
          handleMenuClose();
        }}>
          <ListItemIcon><RateLimitIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Manage Credits</ListItemText>
        </MenuItem>
        {menuBot?.status === 'active' ? (
          <MenuItem 
            onClick={() => {
              if (menuBot) setSuspendDialog(menuBot);
              handleMenuClose();
            }}
            disabled={actionLoading === menuBot?.id}
          >
            <ListItemIcon><SuspendIcon fontSize="small" color="error" /></ListItemIcon>
            <ListItemText sx={{ color: 'error.main' }}>Suspend User</ListItemText>
          </MenuItem>
        ) : (
          <MenuItem 
            onClick={() => {
              if (menuBot) handleActivate(menuBot);
              handleMenuClose();
            }}
            disabled={actionLoading === menuBot?.id}
          >
            <ListItemIcon><ActivateIcon fontSize="small" color="success" /></ListItemIcon>
            <ListItemText sx={{ color: 'success.main' }}>Activate User</ListItemText>
          </MenuItem>
        )}
        <MenuItem 
          onClick={() => {
            if (menuBot) setDeleteDialog(menuBot);
            handleMenuClose();
          }}
          disabled={actionLoading === menuBot?.id}
        >
          <ListItemIcon><DeleteIcon fontSize="small" color="error" /></ListItemIcon>
          <ListItemText sx={{ color: 'error.main' }}>Delete Bot</ListItemText>
        </MenuItem>
      </Menu>

      {/* Suspend Dialog */}
      <Dialog open={!!suspendDialog} onClose={() => setSuspendDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Suspend Bot</DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 2 }}>
            Are you sure you want to suspend <strong>@{suspendDialog?.bot_username}</strong>?
          </Typography>
          <TextField
            fullWidth
            label="Suspension Reason"
            value={suspendReason}
            onChange={(e) => setSuspendReason(e.target.value)}
            placeholder="Enter reason for suspension..."
            multiline
            rows={2}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSuspendDialog(null)}>Cancel</Button>
          <Button
            onClick={handleSuspend}
            color="error"
            variant="contained"
            disabled={!!actionLoading}
          >
            Suspend
          </Button>
        </DialogActions>
      </Dialog>

      {/* Rate Limit Dialog */}
      <Dialog
        open={!!rateLimitDialog}
        onClose={() => setRateLimitDialog(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Update Rate Limits</DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 3 }}>
            Update rate limits for <strong>@{rateLimitDialog?.bot_username}</strong>
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              type="number"
              label="Max Requests/Second"
              value={newRateLimit}
              onChange={(e) => setNewRateLimit(parseInt(e.target.value) || 1)}
              inputProps={{ min: 1, max: 100 }}
              fullWidth
            />
            <TextField
              type="number"
              label="Max Concurrent"
              value={newConcurrent}
              onChange={(e) => setNewConcurrent(parseInt(e.target.value) || 1)}
              inputProps={{ min: 1, max: 50 }}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRateLimitDialog(null)}>Cancel</Button>
          <Button
            onClick={handleRateLimitUpdate}
            color="primary"
            variant="contained"
            disabled={!!actionLoading}
          >
            Update
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Bot Dialog */}
      <Dialog open={!!deleteDialog} onClose={() => setDeleteDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ color: 'error.main' }}>Delete Bot</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This action cannot be undone!
          </Alert>
          <Typography>
            Are you sure you want to delete <strong>@{deleteDialog?.bot_username}</strong> for user <strong>{deleteDialog?.user_id}</strong>?
          </Typography>
          <Typography sx={{ mt: 2, color: 'text.secondary' }}>
            This will completely remove the bot credentials from the system. The user will need to set up a new bot from scratch.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(null)}>Cancel</Button>
          <Button
            onClick={handleDeleteBot}
            color="error"
            variant="contained"
            disabled={!!actionLoading}
            startIcon={actionLoading === deleteDialog?.id ? <CircularProgress size={16} /> : <DeleteIcon />}
          >
            Delete Bot
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BotsPage;
