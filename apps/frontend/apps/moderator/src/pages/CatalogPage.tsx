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
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Avatar,
  Snackbar,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Sync as SyncIcon,
  Refresh as RefreshIcon,
  Star as StarIcon,
  StarOutline as StarOutlineIcon,
  Verified as VerifiedIcon,
  LibraryBooks as CatalogIcon,
} from '@mui/icons-material';
import { apiClient } from '@api/client';
import { API_ENDPOINTS } from '@config/api';
import { format } from 'date-fns';
import { useDebounce } from '@hooks/useDebounce';
import { PageSkeleton } from '@components/Skeletons';

interface CatalogEntry {
  id: number;
  telegram_id: number;
  username: string | null;
  title: string;
  description: string | null;
  avatar_url: string | null;
  category_id: number | null;
  category_name: string | null;
  country_code: string | null;
  language_code: string | null;
  is_featured: boolean;
  is_verified: boolean;
  is_active: boolean;
  added_by: number | null;
  added_at: string;
  last_synced_at: string | null;
  subscriber_count: number | null;
}

interface Category {
  id: number;
  name: string;
  slug: string;
  icon: string | null;
  color: string | null;
  channel_count: number;
}

interface CatalogStats {
  total_channels: number;
  featured_channels: number;
  verified_channels: number;
  total_categories: number;
  active_channels: number;
  inactive_channels: number;
}

const CatalogPage: React.FC = () => {
  const [entries, setEntries] = useState<CatalogEntry[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [stats, setStats] = useState<CatalogStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  
  // Filters
  const [categoryFilter, setCategoryFilter] = useState<number | ''>('');
  const [featuredFilter, setFeaturedFilter] = useState<boolean | ''>('');
  
  // Dialogs
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<CatalogEntry | null>(null);
  
  // Add form
  const [addForm, setAddForm] = useState({
    username: '',
    category_id: 1,
    country_code: '',
    language_code: '',
    is_featured: false,
  });
  
  // Edit form
  const [editForm, setEditForm] = useState({
    category_id: 1,
    country_code: '',
    language_code: '',
    is_featured: false,
    is_verified: false,
    is_active: true,
  });

  const fetchCategories = useCallback(async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.PUBLIC.CATEGORIES);
      setCategories(response.data.categories || []);
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.CATALOG.STATS);
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, []);

  const fetchEntries = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, unknown> = {
        page: page + 1,
        per_page: rowsPerPage,
      };
      if (categoryFilter) params.category_id = categoryFilter;
      if (featuredFilter !== '') params.is_featured = featuredFilter;
      
      const response = await apiClient.get(API_ENDPOINTS.CATALOG.LIST, { params });
      setEntries(response.data.entries || []);
      setTotal(response.data.total || 0);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load catalog entries';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [page, rowsPerPage, categoryFilter, featuredFilter]);

  useEffect(() => {
    fetchCategories();
    fetchStats();
  }, [fetchCategories, fetchStats]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  const handleAddChannel = async () => {
    if (!addForm.username.trim()) {
      setError('Please enter a channel username');
      return;
    }
    
    setActionLoading(-1);
    try {
      await apiClient.post(API_ENDPOINTS.CATALOG.ADD, {
        username: addForm.username.replace('@', ''),
        category_id: addForm.category_id,
        country_code: addForm.country_code || null,
        language_code: addForm.language_code || null,
        is_featured: addForm.is_featured,
      });
      setSuccess('Channel added successfully!');
      setAddDialogOpen(false);
      setAddForm({
        username: '',
        category_id: 1,
        country_code: '',
        language_code: '',
        is_featured: false,
      });
      fetchEntries();
      fetchStats();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to add channel');
    } finally {
      setActionLoading(null);
    }
  };

  const handleUpdateEntry = async () => {
    if (!selectedEntry) return;
    
    setActionLoading(selectedEntry.id);
    try {
      await apiClient.put(API_ENDPOINTS.CATALOG.ENTRY(selectedEntry.id), {
        category_id: editForm.category_id,
        country_code: editForm.country_code || null,
        language_code: editForm.language_code || null,
        is_featured: editForm.is_featured,
        is_verified: editForm.is_verified,
        is_active: editForm.is_active,
      });
      setSuccess('Channel updated successfully!');
      setEditDialogOpen(false);
      setSelectedEntry(null);
      fetchEntries();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to update channel');
    } finally {
      setActionLoading(null);
    }
  };

  const handleDeleteEntry = async (entry: CatalogEntry) => {
    if (!window.confirm(`Are you sure you want to remove "${entry.title}" from the catalog?`)) {
      return;
    }
    
    setActionLoading(entry.id);
    try {
      await apiClient.delete(API_ENDPOINTS.CATALOG.ENTRY(entry.id));
      setSuccess('Channel removed from catalog');
      fetchEntries();
      fetchStats();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to remove channel');
    } finally {
      setActionLoading(null);
    }
  };

  const handleToggleFeatured = async (entry: CatalogEntry) => {
    setActionLoading(entry.id);
    try {
      await apiClient.post(API_ENDPOINTS.CATALOG.FEATURE(entry.id), null, {
        params: { featured: !entry.is_featured },
      });
      setSuccess(`Channel ${!entry.is_featured ? 'featured' : 'unfeatured'} successfully!`);
      fetchEntries();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to update featured status');
    } finally {
      setActionLoading(null);
    }
  };

  const handleToggleVerified = async (entry: CatalogEntry) => {
    setActionLoading(entry.id);
    try {
      await apiClient.post(API_ENDPOINTS.CATALOG.VERIFY(entry.id), null, {
        params: { verified: !entry.is_verified },
      });
      setSuccess(`Channel ${!entry.is_verified ? 'verified' : 'unverified'} successfully!`);
      fetchEntries();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to update verified status');
    } finally {
      setActionLoading(null);
    }
  };

  const handleSyncChannel = async (entry: CatalogEntry) => {
    setActionLoading(entry.id);
    try {
      await apiClient.post(API_ENDPOINTS.CATALOG.SYNC(entry.id));
      setSuccess('Channel synced successfully!');
      fetchEntries();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to sync channel');
    } finally {
      setActionLoading(null);
    }
  };

  const openEditDialog = (entry: CatalogEntry) => {
    setSelectedEntry(entry);
    setEditForm({
      category_id: entry.category_id || 1,
      country_code: entry.country_code || '',
      language_code: entry.language_code || '',
      is_featured: entry.is_featured,
      is_verified: entry.is_verified,
      is_active: entry.is_active,
    });
    setEditDialogOpen(true);
  };

  const formatNumber = (num: number | null): string => {
    if (num === null) return '-';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  if (loading && entries.length === 0) {
    return <PageSkeleton />;
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            <CatalogIcon sx={{ mr: 1, verticalAlign: 'bottom' }} />
            Channel Catalog
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage channels in the public analytics catalog
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setAddDialogOpen(true)}
        >
          Add Channel
        </Button>
      </Box>

      {/* Stats Cards */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} sm={4} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="h4" color="primary">
                  {stats.total_channels}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="h4" color="warning.main">
                  {stats.featured_channels}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Featured
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="h4" color="success.main">
                  {stats.verified_channels}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Verified
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="h4" color="info.main">
                  {stats.total_categories}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Categories
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="h4" color="text.primary">
                  {stats.active_channels || stats.total_channels}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={6} sm={4} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="h4" color="error.main">
                  {stats.inactive_channels || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Inactive
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Alerts */}
      <Snackbar
        open={!!success}
        autoHideDuration={3000}
        onClose={() => setSuccess(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Paper sx={{ mb: 2, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Category</InputLabel>
              <Select
                value={categoryFilter}
                label="Category"
                onChange={(e) => setCategoryFilter(e.target.value as number | '')}
              >
                <MenuItem value="">All Categories</MenuItem>
                {categories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.id}>
                    {cat.icon} {cat.name} ({cat.channel_count})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth size="small">
              <InputLabel>Featured</InputLabel>
              <Select
                value={featuredFilter}
                label="Featured"
                onChange={(e) => setFeaturedFilter(e.target.value as boolean | '')}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value={true as unknown as string}>Featured Only</MenuItem>
                <MenuItem value={false as unknown as string}>Non-Featured</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={fetchEntries}
              disabled={loading}
            >
              Refresh
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Channel</TableCell>
              <TableCell>Category</TableCell>
              <TableCell align="right">Subscribers</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell>Added</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {entries.map((entry) => (
              <TableRow key={entry.id} hover>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Avatar
                      src={entry.avatar_url || undefined}
                      sx={{ width: 40, height: 40 }}
                    >
                      {entry.title?.[0] || '?'}
                    </Avatar>
                    <Box>
                      <Typography variant="subtitle2">
                        {entry.title}
                        {entry.is_verified && (
                          <VerifiedIcon
                            sx={{ ml: 0.5, fontSize: 16, color: 'primary.main' }}
                          />
                        )}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        @{entry.username || 'private'}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>
                  {entry.category_name ? (
                    <Chip
                      label={entry.category_name}
                      size="small"
                      variant="outlined"
                    />
                  ) : (
                    '-'
                  )}
                </TableCell>
                <TableCell align="right">
                  {formatNumber(entry.subscriber_count)}
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                    {entry.is_featured && (
                      <Tooltip title="Featured">
                        <StarIcon sx={{ color: 'warning.main', fontSize: 20 }} />
                      </Tooltip>
                    )}
                    {entry.is_active ? (
                      <Chip label="Active" color="success" size="small" />
                    ) : (
                      <Chip label="Inactive" color="default" size="small" />
                    )}
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {format(new Date(entry.added_at), 'MMM d, yyyy')}
                  </Typography>
                  {entry.last_synced_at && (
                    <Typography variant="caption" color="text.secondary" display="block">
                      Synced: {format(new Date(entry.last_synced_at), 'MMM d, HH:mm')}
                    </Typography>
                  )}
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                    <Tooltip title={entry.is_featured ? 'Remove from featured' : 'Add to featured'}>
                      <IconButton
                        size="small"
                        onClick={() => handleToggleFeatured(entry)}
                        disabled={actionLoading === entry.id}
                      >
                        {entry.is_featured ? (
                          <StarIcon color="warning" />
                        ) : (
                          <StarOutlineIcon />
                        )}
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={entry.is_verified ? 'Remove verification' : 'Verify channel'}>
                      <IconButton
                        size="small"
                        onClick={() => handleToggleVerified(entry)}
                        disabled={actionLoading === entry.id}
                      >
                        <VerifiedIcon color={entry.is_verified ? 'primary' : 'disabled'} />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Sync from Telegram">
                      <IconButton
                        size="small"
                        onClick={() => handleSyncChannel(entry)}
                        disabled={actionLoading === entry.id}
                      >
                        {actionLoading === entry.id ? (
                          <CircularProgress size={20} />
                        ) : (
                          <SyncIcon />
                        )}
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => openEditDialog(entry)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Remove">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteEntry(entry)}
                        disabled={actionLoading === entry.id}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
            {entries.length === 0 && !loading && (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">
                    No channels in catalog yet. Click "Add Channel" to get started.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={total}
          page={page}
          rowsPerPage={rowsPerPage}
          onPageChange={(_, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
          rowsPerPageOptions={[10, 25, 50]}
        />
      </TableContainer>

      {/* Add Channel Dialog */}
      <Dialog
        open={addDialogOpen}
        onClose={() => setAddDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Channel to Catalog</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              label="Channel Username"
              value={addForm.username}
              onChange={(e) => setAddForm({ ...addForm, username: e.target.value })}
              placeholder="@channelname or channelname"
              helperText="Enter the Telegram channel username (without https://t.me/)"
            />
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={addForm.category_id}
                label="Category"
                onChange={(e) => setAddForm({ ...addForm, category_id: e.target.value as number })}
              >
                {categories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.id}>
                    {cat.icon} {cat.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Country Code"
                  value={addForm.country_code}
                  onChange={(e) => setAddForm({ ...addForm, country_code: e.target.value })}
                  placeholder="US, UK, RU, etc."
                  inputProps={{ maxLength: 2 }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Language Code"
                  value={addForm.language_code}
                  onChange={(e) => setAddForm({ ...addForm, language_code: e.target.value })}
                  placeholder="en, ru, es, etc."
                  inputProps={{ maxLength: 5 }}
                />
              </Grid>
            </Grid>
            <FormControlLabel
              control={
                <Switch
                  checked={addForm.is_featured}
                  onChange={(e) => setAddForm({ ...addForm, is_featured: e.target.checked })}
                />
              }
              label="Feature this channel"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleAddChannel}
            disabled={actionLoading === -1}
          >
            {actionLoading === -1 ? (
              <CircularProgress size={20} sx={{ mr: 1 }} />
            ) : null}
            Add Channel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Channel Dialog */}
      <Dialog
        open={editDialogOpen}
        onClose={() => setEditDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Edit Channel: {selectedEntry?.title}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={editForm.category_id}
                label="Category"
                onChange={(e) => setEditForm({ ...editForm, category_id: e.target.value as number })}
              >
                {categories.map((cat) => (
                  <MenuItem key={cat.id} value={cat.id}>
                    {cat.icon} {cat.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Country Code"
                  value={editForm.country_code}
                  onChange={(e) => setEditForm({ ...editForm, country_code: e.target.value })}
                  placeholder="US, UK, RU, etc."
                  inputProps={{ maxLength: 2 }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Language Code"
                  value={editForm.language_code}
                  onChange={(e) => setEditForm({ ...editForm, language_code: e.target.value })}
                  placeholder="en, ru, es, etc."
                  inputProps={{ maxLength: 5 }}
                />
              </Grid>
            </Grid>
            <FormControlLabel
              control={
                <Switch
                  checked={editForm.is_featured}
                  onChange={(e) => setEditForm({ ...editForm, is_featured: e.target.checked })}
                />
              }
              label="Featured"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={editForm.is_verified}
                  onChange={(e) => setEditForm({ ...editForm, is_verified: e.target.checked })}
                />
              }
              label="Verified"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={editForm.is_active}
                  onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                />
              }
              label="Active"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleUpdateEntry}
            disabled={actionLoading === selectedEntry?.id}
          >
            {actionLoading === selectedEntry?.id ? (
              <CircularProgress size={20} sx={{ mr: 1 }} />
            ) : null}
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CatalogPage;
