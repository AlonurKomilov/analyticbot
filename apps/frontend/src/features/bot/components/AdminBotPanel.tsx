/**
 * Admin Bot Panel Component
 * Admin interface to manage all user bots
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControl,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  Block,
  PlayArrow,
  Settings,
  Refresh,
  AdminPanelSettings,
} from '@mui/icons-material';
import { useUserBotStore } from '@/store';
import { BotStatus, type AdminBotListItem } from '@/types';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

export const AdminBotPanel: React.FC = () => {
  const {
    allBots,
    totalBots,
    fetchAllBots,
    suspendUserBot,
    activateUserBot,
    updateUserBotRateLimits,
    isLoadingBots,
    isSuspending,
    isActivating,
    isUpdating,
  } = useUserBotStore();

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [statusFilter, setStatusFilter] = useState<string>('');

  // Dialog states
  const [suspendDialog, setSuspendDialog] = useState<{ open: boolean; userId: number | null }>({
    open: false,
    userId: null,
  });
  const [suspendReason, setSuspendReason] = useState('');

  const [rateLimitDialog, setRateLimitDialog] = useState<{
    open: boolean;
    userId: number | null;
    currentRps: number;
    currentConcurrent: number;
  }>({
    open: false,
    userId: null,
    currentRps: 0,
    currentConcurrent: 0,
  });
  const [newRps, setNewRps] = useState('');
  const [newConcurrent, setNewConcurrent] = useState('');

  useEffect(() => {
    loadBots();
  }, [page, rowsPerPage, statusFilter]);

  const loadBots = () => {
    fetchAllBots({
      limit: rowsPerPage,
      offset: page * rowsPerPage,
      status: statusFilter || undefined,
    });
  };

  const handleRefresh = () => {
    loadBots();
    toast.success('Bot list refreshed');
  };

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSuspendClick = (userId: number) => {
    setSuspendDialog({ open: true, userId });
    setSuspendReason('');
  };

  const handleSuspendConfirm = async () => {
    if (!suspendDialog.userId) return;

    if (suspendReason.trim().length < 5) {
      toast.error('Suspension reason must be at least 5 characters');
      return;
    }

    try {
      await suspendUserBot(suspendDialog.userId, suspendReason);
      toast.success('Bot suspended successfully');
      setSuspendDialog({ open: false, userId: null });
      setSuspendReason('');
    } catch (err) {
      toast.error('Failed to suspend bot');
    }
  };

  const handleActivate = async (userId: number) => {
    try {
      await activateUserBot(userId);
      toast.success('Bot activated successfully');
    } catch (err) {
      toast.error('Failed to activate bot');
    }
  };

  const handleRateLimitClick = (bot: AdminBotListItem) => {
    setRateLimitDialog({
      open: true,
      userId: bot.user_id,
      currentRps: bot.max_requests_per_second,
      currentConcurrent: bot.max_concurrent_requests,
    });
    setNewRps(bot.max_requests_per_second.toString());
    setNewConcurrent(bot.max_concurrent_requests.toString());
  };

  const handleRateLimitConfirm = async () => {
    if (!rateLimitDialog.userId) return;

    const rps = parseFloat(newRps);
    const concurrent = parseInt(newConcurrent);

    if (isNaN(rps) || rps <= 0) {
      toast.error('RPS must be a positive number');
      return;
    }

    if (isNaN(concurrent) || concurrent <= 0) {
      toast.error('Max concurrent must be a positive integer');
      return;
    }

    try {
      await updateUserBotRateLimits(rateLimitDialog.userId, {
        max_requests_per_second: rps,
        max_concurrent_requests: concurrent,
      });
      toast.success('Rate limits updated successfully');
      setRateLimitDialog({ open: false, userId: null, currentRps: 0, currentConcurrent: 0 });
    } catch (err) {
      toast.error('Failed to update rate limits');
    }
  };

  const getStatusColor = (status: BotStatus): 'success' | 'error' | 'warning' | 'info' | 'default' => {
    switch (status) {
      case BotStatus.ACTIVE:
        return 'success';
      case BotStatus.SUSPENDED:
        return 'error';
      case BotStatus.RATE_LIMITED:
        return 'warning';
      case BotStatus.PENDING:
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center">
          <AdminPanelSettings sx={{ mr: 1, fontSize: 32 }} />
          <Typography variant="h4" component="h1">
            Bot Management (Admin)
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <FormControl sx={{ minWidth: 150 }} size="small">
            <InputLabel>Status Filter</InputLabel>
            <Select
              value={statusFilter}
              label="Status Filter"
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(0);
              }}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="suspended">Suspended</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="rate_limited">Rate Limited</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={handleRefresh} disabled={isLoadingBots}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>User ID</TableCell>
                  <TableCell>Bot Username</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>RPS</TableCell>
                  <TableCell>Max Concurrent</TableCell>
                  <TableCell>Total Requests</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoadingBots ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : allBots.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Typography color="text.secondary">No bots found</Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  allBots.map((bot) => (
                    <TableRow key={bot.user_id} hover>
                      <TableCell>{bot.user_id}</TableCell>
                      <TableCell>@{bot.bot_username || 'Unknown'}</TableCell>
                      <TableCell>
                        <Chip
                          label={bot.status.toUpperCase()}
                          color={getStatusColor(bot.status)}
                          size="small"
                        />
                        {bot.is_verified && (
                          <Chip label="VERIFIED" color="success" size="small" sx={{ ml: 1 }} />
                        )}
                      </TableCell>
                      <TableCell>{bot.max_requests_per_second}</TableCell>
                      <TableCell>{bot.max_concurrent_requests}</TableCell>
                      <TableCell>{bot.total_requests.toLocaleString()}</TableCell>
                      <TableCell>
                        {format(new Date(bot.created_at), 'PP')}
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={1}>
                          {bot.status === BotStatus.SUSPENDED ? (
                            <Tooltip title="Activate Bot">
                              <IconButton
                                size="small"
                                color="success"
                                onClick={() => handleActivate(bot.user_id)}
                                disabled={isActivating}
                              >
                                <PlayArrow />
                              </IconButton>
                            </Tooltip>
                          ) : (
                            <Tooltip title="Suspend Bot">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleSuspendClick(bot.user_id)}
                                disabled={isSuspending}
                              >
                                <Block />
                              </IconButton>
                            </Tooltip>
                          )}
                          <Tooltip title="Update Rate Limits">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleRateLimitClick(bot)}
                              disabled={isUpdating}
                            >
                              <Settings />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>

          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={totalBots}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </CardContent>
      </Card>

      {/* Suspend Bot Dialog */}
      <Dialog
        open={suspendDialog.open}
        onClose={() => setSuspendDialog({ open: false, userId: null })}
      >
        <DialogTitle>Suspend Bot</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Please provide a reason for suspending this bot (minimum 5 characters):
          </DialogContentText>
          <TextField
            fullWidth
            label="Suspension Reason"
            value={suspendReason}
            onChange={(e) => setSuspendReason(e.target.value)}
            multiline
            rows={3}
            autoFocus
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSuspendDialog({ open: false, userId: null })}>Cancel</Button>
          <Button
            onClick={handleSuspendConfirm}
            color="error"
            variant="contained"
            disabled={isSuspending}
          >
            {isSuspending ? 'Suspending...' : 'Suspend'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Update Rate Limits Dialog */}
      <Dialog
        open={rateLimitDialog.open}
        onClose={() =>
          setRateLimitDialog({ open: false, userId: null, currentRps: 0, currentConcurrent: 0 })
        }
      >
        <DialogTitle>Update Rate Limits</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Current: {rateLimitDialog.currentRps} RPS, {rateLimitDialog.currentConcurrent} concurrent
          </DialogContentText>
          <TextField
            fullWidth
            label="Requests Per Second (RPS)"
            value={newRps}
            onChange={(e) => setNewRps(e.target.value)}
            type="number"
            sx={{ mb: 2 }}
          />
          <TextField
            fullWidth
            label="Max Concurrent Requests"
            value={newConcurrent}
            onChange={(e) => setNewConcurrent(e.target.value)}
            type="number"
          />
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() =>
              setRateLimitDialog({ open: false, userId: null, currentRps: 0, currentConcurrent: 0 })
            }
          >
            Cancel
          </Button>
          <Button onClick={handleRateLimitConfirm} variant="contained" disabled={isUpdating}>
            {isUpdating ? 'Updating...' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
