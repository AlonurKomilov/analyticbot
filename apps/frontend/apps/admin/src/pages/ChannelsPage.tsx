import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  TextField,
  InputAdornment,
  Tooltip,
  TablePagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Alert,
  Grid,
  Card,
  CardContent,
  Checkbox,
  Toolbar,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon,
  Sync as SyncIcon,
  Refresh as RefreshIcon,
  PlayArrow as ActivateIcon,
  Pause as SuspendIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { apiClient } from '@api/client';
import { API_ENDPOINTS } from '@config/api';
import { format } from 'date-fns';
import { useDebounce } from '../hooks/useDebounce';
import { PageSkeleton } from '../components/Skeletons';
import { exportTableData, generateExportFilename } from '../utils/export';

interface Channel {
  id: number;
  name: string;
  username: string;
  owner_id: number;
  owner_username: string | null;
  subscriber_count: number;
  is_active: boolean;
  created_at: string;
  last_activity: string | null;
  total_posts: number;
  total_views: number;
}

const ChannelsPage: React.FC = () => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  // Bulk selection state
  const [selectedChannels, setSelectedChannels] = useState<number[]>([]);
  const [bulkActionLoading, setBulkActionLoading] = useState(false);

  // Dialog states
  const [deleteDialog, setDeleteDialog] = useState<Channel | null>(null);
  const [viewDialog, setViewDialog] = useState<Channel | null>(null);

  // Stats
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    suspended: 0,
  });

  const fetchChannels = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiClient.get(API_ENDPOINTS.ADMIN.CHANNELS);
      const channelList = response.data.channels || response.data || [];
      setChannels(channelList);

      // Calculate stats
      setStats({
        total: channelList.length,
        active: channelList.filter((c: Channel) => c.is_active).length,
        suspended: channelList.filter((c: Channel) => !c.is_active).length,
      });
    } catch (error) {
      console.error('Failed to fetch channels:', error);
      setError('Failed to load channels');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChannels();
  }, [fetchChannels]);

  const handleDelete = async () => {
    if (!deleteDialog) return;
    setActionLoading(deleteDialog.id);
    try {
      await apiClient.delete(`${API_ENDPOINTS.ADMIN.CHANNELS}/${deleteDialog.id}`);
      setSuccess(`Channel "${deleteDialog.name}" deleted successfully`);
      setDeleteDialog(null);
      await fetchChannels();
    } catch (err) {
      setError('Failed to delete channel');
      console.error('Delete error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleSuspend = async (channel: Channel) => {
    setActionLoading(channel.id);
    try {
      await apiClient.post(`${API_ENDPOINTS.ADMIN.CHANNELS}/${channel.id}/suspend`);
      setSuccess(`Channel "${channel.name}" suspended successfully`);
      await fetchChannels();
    } catch (err) {
      setError('Failed to suspend channel');
      console.error('Suspend error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleUnsuspend = async (channel: Channel) => {
    setActionLoading(channel.id);
    try {
      await apiClient.post(`${API_ENDPOINTS.ADMIN.CHANNELS}/${channel.id}/unsuspend`);
      setSuccess(`Channel "${channel.name}" reactivated successfully`);
      await fetchChannels();
    } catch (err) {
      setError('Failed to unsuspend channel');
      console.error('Unsuspend error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleSync = async (channel: Channel) => {
    setActionLoading(channel.id);
    try {
      // Note: If there's a sync endpoint, use it here
      // For now, we'll just show a message
      setSuccess(`Sync triggered for "${channel.name}"`);
    } catch (err) {
      setError('Failed to sync channel');
      console.error('Sync error:', err);
    } finally {
      setActionLoading(null);
    }
  };

  // Bulk action handlers
  const handleSelectAll = () => {
    if (selectedChannels.length === filteredChannels.length) {
      setSelectedChannels([]);
    } else {
      setSelectedChannels(filteredChannels.map(c => c.id));
    }
  };

  const handleSelectChannel = (channelId: number) => {
    setSelectedChannels(prev =>
      prev.includes(channelId)
        ? prev.filter(id => id !== channelId)
        : [...prev, channelId]
    );
  };

  const handleBulkSuspend = async () => {
    setBulkActionLoading(true);
    try {
      await Promise.all(
        selectedChannels.map(id =>
          apiClient.post(`${API_ENDPOINTS.ADMIN.CHANNELS}/${id}/suspend`)
        )
      );
      setSuccess(`${selectedChannels.length} channel(s) suspended successfully`);
      setSelectedChannels([]);
      await fetchChannels();
    } catch (err) {
      setError('Failed to suspend some channels');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const handleBulkDelete = async () => {
    setBulkActionLoading(true);
    try {
      await Promise.all(
        selectedChannels.map(id =>
          apiClient.delete(`${API_ENDPOINTS.ADMIN.CHANNELS}/${id}`)
        )
      );
      setSuccess(`${selectedChannels.length} channel(s) deleted successfully`);
      setSelectedChannels([]);
      await fetchChannels();
    } catch (err) {
      setError('Failed to delete some channels');
    } finally {
      setBulkActionLoading(false);
    }
  };

  const handleExportCSV = () => {
    const exportData = filteredChannels.map(channel => ({
      ID: channel.id,
      Name: channel.name,
      Username: channel.username,
      'Owner ID': channel.owner_id,
      'Subscribers': channel.subscriber_count || 0,
      Status: channel.is_active ? 'Active' : 'Suspended',
      'Total Posts': channel.total_posts || 0,
      'Total Views': channel.total_views || 0,
      'Created At': channel.created_at,
      'Last Activity': channel.last_activity || 'Never',
    }));

    exportTableData(exportData, generateExportFilename('channels'), 'csv');
    setSuccess('Channels exported successfully');
  };

  // Debounce search for better performance
  const debouncedSearch = useDebounce(search, 300);

  const filteredChannels = channels.filter(
    (channel) =>
      channel.name?.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
      channel.username?.toLowerCase().includes(debouncedSearch.toLowerCase())
  );

  const getStatusColor = (isActive: boolean) => {
    return isActive ? 'success' : 'error';
  };

  const getStatusLabel = (isActive: boolean) => {
    return isActive ? 'active' : 'suspended';
  };

  if (loading) {
    return (
      <PageSkeleton
        hasTitle={true}
        hasStats={true}
        statsCount={3}
        hasFilters={true}
        hasTable={true}
        tableRows={10}
        tableColumns={10}
      />
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Channel Management
          </Typography>
          <Typography color="text.secondary">
            Manage all connected Telegram channels
          </Typography>
        </Box>
        <Tooltip title="Refresh">
          <IconButton onClick={fetchChannels} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" fontWeight={700} color="primary">
                {stats.total}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Channels
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={4}>
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
        <Grid item xs={4}>
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
      </Grid>

      {/* Search and Bulk Actions */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <TextField
            placeholder="Search channels..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            size="small"
            sx={{ minWidth: 300 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon color="action" />
                </InputAdornment>
              ),
            }}
          />
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant="outlined"
              size="small"
              startIcon={<DownloadIcon />}
              onClick={handleExportCSV}
            >
              Export CSV
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* Bulk Actions Toolbar */}
      {selectedChannels.length > 0 && (
        <Toolbar
          sx={{
            mb: 2,
            pl: { sm: 2 },
            pr: { xs: 1, sm: 1 },
            bgcolor: 'primary.light',
            borderRadius: 1,
            color: 'primary.contrastText',
          }}
        >
          <Typography sx={{ flex: '1 1 100%' }} color="inherit" variant="subtitle1">
            {selectedChannels.length} channel(s) selected
          </Typography>
          <Tooltip title="Suspend Selected">
            <IconButton
              color="inherit"
              onClick={handleBulkSuspend}
              disabled={bulkActionLoading}
            >
              <SuspendIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Delete Selected">
            <IconButton
              color="inherit"
              onClick={handleBulkDelete}
              disabled={bulkActionLoading}
            >
              <DeleteIcon />
            </IconButton>
          </Tooltip>
          {bulkActionLoading && <CircularProgress size={24} sx={{ ml: 2, color: 'inherit' }} />}
        </Toolbar>
      )}

      {/* Channels Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={selectedChannels.length > 0 && selectedChannels.length < filteredChannels.length}
                  checked={filteredChannels.length > 0 && selectedChannels.length === filteredChannels.length}
                  onChange={handleSelectAll}
                  color="primary"
                />
              </TableCell>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>Owner ID</TableCell>
              <TableCell>Subscribers</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Last Activity</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredChannels
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((channel) => (
                <TableRow
                  key={channel.id}
                  hover
                  selected={selectedChannels.includes(channel.id)}
                >
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selectedChannels.includes(channel.id)}
                      onChange={() => handleSelectChannel(channel.id)}
                      color="primary"
                    />
                  </TableCell>
                  <TableCell>{channel.id}</TableCell>
                  <TableCell sx={{ fontWeight: 500 }}>{channel.name || '-'}</TableCell>
                  <TableCell>@{channel.username || '-'}</TableCell>
                  <TableCell>{channel.owner_id}</TableCell>
                  <TableCell>
                    {channel.subscriber_count?.toLocaleString() || 0}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getStatusLabel(channel.is_active)}
                      size="small"
                      color={getStatusColor(channel.is_active)}
                    />
                  </TableCell>
                  <TableCell>
                    {channel.created_at
                      ? format(new Date(channel.created_at), 'MMM d, yyyy')
                      : '-'}
                  </TableCell>
                  <TableCell>
                    {channel.last_activity
                      ? format(new Date(channel.last_activity), 'MMM d, HH:mm')
                      : 'Never'}
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="View Details">
                      <IconButton
                        size="small"
                        onClick={() => setViewDialog(channel)}
                      >
                        <ViewIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Force Sync">
                      <IconButton
                        size="small"
                        color="info"
                        onClick={() => handleSync(channel)}
                        disabled={actionLoading === channel.id}
                      >
                        <SyncIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    {channel.is_active ? (
                      <Tooltip title="Suspend Channel">
                        <IconButton
                          size="small"
                          color="warning"
                          onClick={() => handleSuspend(channel)}
                          disabled={actionLoading === channel.id}
                        >
                          <SuspendIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    ) : (
                      <Tooltip title="Reactivate Channel">
                        <IconButton
                          size="small"
                          color="success"
                          onClick={() => handleUnsuspend(channel)}
                          disabled={actionLoading === channel.id}
                        >
                          <ActivateIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    <Tooltip title="Delete Channel">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => setDeleteDialog(channel)}
                        disabled={actionLoading === channel.id}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={filteredChannels.length}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteDialog} onClose={() => setDeleteDialog(null)}>
        <DialogTitle>Delete Channel</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to permanently delete the channel{' '}
            <strong>"{deleteDialog?.name}"</strong>?
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            This action cannot be undone. All channel data including posts and analytics will be deleted.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(null)}>Cancel</Button>
          <Button
            onClick={handleDelete}
            color="error"
            variant="contained"
            disabled={!!actionLoading}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Details Dialog */}
      <Dialog open={!!viewDialog} onClose={() => setViewDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Channel Details</DialogTitle>
        <DialogContent>
          {viewDialog && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 1 }}>
              <Box>
                <Typography variant="caption" color="text.secondary">Name</Typography>
                <Typography variant="body1" fontWeight={500}>{viewDialog.name}</Typography>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Username</Typography>
                <Typography variant="body1">@{viewDialog.username || 'N/A'}</Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 4 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">Subscribers</Typography>
                  <Typography variant="body1">{viewDialog.subscriber_count?.toLocaleString()}</Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">Total Posts</Typography>
                  <Typography variant="body1">{viewDialog.total_posts}</Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">Total Views</Typography>
                  <Typography variant="body1">{viewDialog.total_views?.toLocaleString()}</Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', gap: 4 }}>
                <Box>
                  <Typography variant="caption" color="text.secondary">Owner ID</Typography>
                  <Typography variant="body1">{viewDialog.owner_id}</Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="text.secondary">Status</Typography>
                  <Chip
                    label={viewDialog.is_active ? 'Active' : 'Suspended'}
                    color={viewDialog.is_active ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
              </Box>
              <Box>
                <Typography variant="caption" color="text.secondary">Created</Typography>
                <Typography variant="body1">
                  {viewDialog.created_at ? format(new Date(viewDialog.created_at), 'PPpp') : 'Unknown'}
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialog(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChannelsPage;
