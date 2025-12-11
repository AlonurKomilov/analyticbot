import React, { useState, useEffect } from 'react';
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
  DialogContentText,
  DialogActions,
  Button,
  Alert,
  Snackbar,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Checkbox,
  Toolbar,
  CircularProgress,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as ViewIcon,
  Block as BlockIcon,
  Delete as DeleteIcon,
  CheckCircle as ActivateIcon,
  Telegram as TelegramIcon,
  Google as GoogleIcon,
  Email as EmailIcon,
  MoreVert as MoreVertIcon,
  MonetizationOn as CreditsIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { apiClient } from '@api/client';
import { API_ENDPOINTS } from '@config/api';
import { format } from 'date-fns';
import { useDebounce } from '../hooks/useDebounce';
import { PageSkeleton } from '../components/Skeletons';
import { exportTableData, generateExportFilename } from '../utils/export';

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
  last_login: string | null;
  channels_count?: number;
  auth_provider?: string;
  credit_balance?: number;
}

interface UserDetail {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  role: string;
  status: string;
  created_at: string;
  last_login: string | null;
  channels_count: number;
  total_posts: number;
  total_views: number;
  auth_provider: string;
}

const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Dialog states
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [suspendDialogOpen, setSuspendDialogOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userDetail, setUserDetail] = useState<UserDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [suspendReason, setSuspendReason] = useState('');
  const [suspendLoading, setSuspendLoading] = useState(false);

  // Snackbar state
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Menu state for actions
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [menuUser, setMenuUser] = useState<User | null>(null);

  // Credit adjustment state
  const [creditDialogOpen, setCreditDialogOpen] = useState(false);
  const [creditAmount, setCreditAmount] = useState<string>('');
  const [creditReason, setCreditReason] = useState('');
  const [creditLoading, setCreditLoading] = useState(false);
  const [userCredits, setUserCredits] = useState<{ balance: number; lifetime_earned: number; lifetime_spent: number } | null>(null);

  // Bulk selection state
  const [selected, setSelected] = useState<number[]>([]);
  const [bulkActionLoading, setBulkActionLoading] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_bulkSuspendDialogOpen, setBulkSuspendDialogOpen] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [_bulkDeleteDialogOpen, setBulkDeleteDialogOpen] = useState(false);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, user: User) => {
    setMenuAnchorEl(event.currentTarget);
    setMenuUser(user);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setMenuUser(null);
  };

  const fetchUsers = async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.ADMIN.USERS);
      setUsers(response.data.users || response.data || []);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleViewUser = async (user: User) => {
    setSelectedUser(user);
    setViewDialogOpen(true);
    setDetailLoading(true);
    try {
      const response = await apiClient.get(API_ENDPOINTS.ADMIN.USER_DETAIL(user.id));
      setUserDetail(response.data);
    } catch (error) {
      console.error('Failed to fetch user details:', error);
      setSnackbar({ open: true, message: 'Failed to fetch user details', severity: 'error' });
    } finally {
      setDetailLoading(false);
    }
  };

  const handleSuspendUser = async (user: User) => {
    if (user.role === 'admin' || user.role === 'owner') {
      setSnackbar({ open: true, message: 'Cannot suspend admin users', severity: 'error' });
      return;
    }

    if (user.status === 'suspended') {
      // Unsuspend - no reason needed
      try {
        await apiClient.post(API_ENDPOINTS.ADMIN.USER_UNSUSPEND(user.id));
        setSnackbar({ open: true, message: 'User unsuspended successfully. Their channels and data collection have been re-enabled.', severity: 'success' });
        fetchUsers();
      } catch (error: any) {
        const message = error.response?.data?.detail || 'Failed to unsuspend user';
        setSnackbar({ open: true, message, severity: 'error' });
      }
    } else {
      // Suspend - open dialog to get reason
      setSelectedUser(user);
      setSuspendReason('');
      setSuspendDialogOpen(true);
    }
  };

  const handleSuspendConfirm = async () => {
    if (!selectedUser || !suspendReason.trim()) {
      setSnackbar({ open: true, message: 'Please provide a suspension reason', severity: 'error' });
      return;
    }

    if (suspendReason.trim().length < 5) {
      setSnackbar({ open: true, message: 'Suspension reason must be at least 5 characters', severity: 'error' });
      return;
    }

    setSuspendLoading(true);
    try {
      await apiClient.post(API_ENDPOINTS.ADMIN.USER_SUSPEND(selectedUser.id), {
        reason: suspendReason.trim(),
      });
      setSnackbar({
        open: true,
        message: 'User suspended successfully. Their channels have been disabled and data collection stopped.',
        severity: 'success'
      });
      setSuspendDialogOpen(false);
      setSelectedUser(null);
      setSuspendReason('');
      fetchUsers();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to suspend user';
      setSnackbar({ open: true, message, severity: 'error' });
    } finally {
      setSuspendLoading(false);
    }
  };

  const handleDeleteClick = (user: User) => {
    if (user.role === 'admin' || user.role === 'owner') {
      setSnackbar({ open: true, message: 'Cannot delete admin users', severity: 'error' });
      return;
    }
    setSelectedUser(user);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedUser) return;

    try {
      await apiClient.delete(API_ENDPOINTS.ADMIN.USER_DELETE(selectedUser.id));
      setSnackbar({ open: true, message: 'User deleted successfully', severity: 'success' });
      setDeleteDialogOpen(false);
      setSelectedUser(null);
      fetchUsers(); // Refresh the list
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to delete user';
      setSnackbar({ open: true, message, severity: 'error' });
    }
  };

  // Credit management handlers
  const handleCreditClick = async (user: User) => {
    setSelectedUser(user);
    setCreditAmount('');
    setCreditReason('');
    setUserCredits(null);
    setCreditDialogOpen(true);

    // Fetch user's current credit info
    try {
      const response = await apiClient.get(API_ENDPOINTS.ADMIN.USER_CREDITS(user.id));
      setUserCredits({
        balance: response.data.credit_balance || 0,
        lifetime_earned: response.data.lifetime_earned || 0,
        lifetime_spent: response.data.lifetime_spent || 0,
      });
    } catch (error) {
      console.error('Failed to fetch user credits:', error);
      setUserCredits({ balance: user.credit_balance || 0, lifetime_earned: 0, lifetime_spent: 0 });
    }
  };

  const handleCreditAdjust = async (isAdd: boolean) => {
    if (!selectedUser) return;

    const amount = parseFloat(creditAmount);
    if (isNaN(amount) || amount <= 0) {
      setSnackbar({ open: true, message: 'Please enter a valid positive amount', severity: 'error' });
      return;
    }

    if (!creditReason.trim() || creditReason.trim().length < 5) {
      setSnackbar({ open: true, message: 'Please provide a reason (min 5 characters)', severity: 'error' });
      return;
    }

    setCreditLoading(true);
    try {
      const adjustAmount = isAdd ? amount : -amount;
      const response = await apiClient.post(API_ENDPOINTS.ADMIN.USER_CREDITS_ADJUST(selectedUser.id), {
        amount: adjustAmount,
        reason: creditReason.trim(),
      });

      setSnackbar({
        open: true,
        message: `Credits ${isAdd ? 'added' : 'removed'} successfully. New balance: ${response.data.new_balance}`,
        severity: 'success'
      });

      // Update local state
      setUserCredits(prev => prev ? { ...prev, balance: response.data.new_balance } : null);
      setCreditAmount('');
      setCreditReason('');

      // Update user in list
      setUsers(prevUsers =>
        prevUsers.map(u =>
          u.id === selectedUser.id
            ? { ...u, credit_balance: response.data.new_balance }
            : u
        )
      );
    } catch (error: any) {
      const message = error.response?.data?.detail || `Failed to ${isAdd ? 'add' : 'remove'} credits`;
      setSnackbar({ open: true, message, severity: 'error' });
    } finally {
      setCreditLoading(false);
    }
  };

  // Bulk selection handlers
  const handleSelectAll = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      // Only select non-admin users
      const selectableUsers = filteredUsers.filter(u => u.role !== 'admin' && u.role !== 'owner');
      setSelected(selectableUsers.map(u => u.id));
    } else {
      setSelected([]);
    }
  };

  const handleSelectOne = (userId: number) => {
    setSelected(prev => 
      prev.includes(userId) 
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const handleBulkSuspend = async () => {
    setBulkActionLoading(true);
    let successCount = 0;
    let failCount = 0;

    for (const userId of selected) {
      try {
        await apiClient.post(API_ENDPOINTS.ADMIN.USER_SUSPEND(userId), {
          reason: 'Bulk suspension by admin',
        });
        successCount++;
      } catch {
        failCount++;
      }
    }

    setBulkActionLoading(false);
    setBulkSuspendDialogOpen(false);
    setSelected([]);
    fetchUsers();
    
    if (failCount === 0) {
      setSnackbar({ open: true, message: `Successfully suspended ${successCount} users`, severity: 'success' });
    } else {
      setSnackbar({ open: true, message: `Suspended ${successCount} users, ${failCount} failed`, severity: 'warning' as 'success' });
    }
  };

  const handleBulkDelete = async () => {
    setBulkActionLoading(true);
    let successCount = 0;
    let failCount = 0;

    for (const userId of selected) {
      try {
        await apiClient.delete(API_ENDPOINTS.ADMIN.USER_DELETE(userId));
        successCount++;
      } catch {
        failCount++;
      }
    }

    setBulkActionLoading(false);
    setBulkDeleteDialogOpen(false);
    setSelected([]);
    fetchUsers();
    
    if (failCount === 0) {
      setSnackbar({ open: true, message: `Successfully deleted ${successCount} users`, severity: 'success' });
    } else {
      setSnackbar({ open: true, message: `Deleted ${successCount} users, ${failCount} failed`, severity: 'warning' as 'success' });
    }
  };

  const handleExportCSV = () => {
    const exportData = filteredUsers.map(user => ({
      ID: user.id,
      Username: user.username,
      Email: user.email,
      Role: user.role,
      Status: user.status,
      'Auth Provider': user.auth_provider || 'email',
      'Credit Balance': user.credit_balance || 0,
      'Created At': user.created_at,
      'Last Login': user.last_login || 'Never',
    }));
    
    exportTableData(exportData, generateExportFilename('users'), 'csv');
    setSnackbar({ open: true, message: 'Users exported successfully', severity: 'success' });
  };

  // Debounce search for better performance
  const debouncedSearch = useDebounce(search, 300);

  const filteredUsers = users.filter(
    (user) =>
      user.id?.toString().includes(debouncedSearch) ||
      user.username?.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
      user.email?.toLowerCase().includes(debouncedSearch.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'suspended': return 'error';
      case 'pending_verification': return 'warning';
      default: return 'default';
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin': return 'primary';
      case 'owner': return 'secondary';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <PageSkeleton
        hasTitle={true}
        hasStats={false}
        hasFilters={true}
        hasTable={true}
        tableRows={10}
        tableColumns={11}
      />
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          User Management
        </Typography>
        <Typography color="text.secondary">
          Manage all registered users
        </Typography>
      </Box>

      {/* Search and Bulk Actions */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
          <TextField
            placeholder="Search users..."
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
      {selected.length > 0 && (
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
            {selected.length} user(s) selected
          </Typography>
          <Tooltip title="Suspend Selected">
            <IconButton
              color="inherit"
              onClick={handleBulkSuspend}
              disabled={bulkActionLoading}
            >
              <BlockIcon />
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

      {/* Users Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  indeterminate={selected.length > 0 && selected.length < filteredUsers.length}
                  checked={filteredUsers.length > 0 && selected.length === filteredUsers.length}
                  onChange={handleSelectAll}
                  color="primary"
                />
              </TableCell>
              <TableCell>ID</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Auth</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Credits</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Last Login</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredUsers
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((user) => (
                <TableRow 
                  key={user.id} 
                  hover
                  selected={selected.includes(user.id)}
                >
                  <TableCell padding="checkbox">
                    <Checkbox
                      checked={selected.includes(user.id)}
                      onChange={() => handleSelectOne(user.id)}
                      color="primary"
                    />
                  </TableCell>
                  <TableCell>{user.id}</TableCell>
                  <TableCell sx={{ fontWeight: 500 }}>{user.username || '-'}</TableCell>
                  <TableCell>{user.email || '-'}</TableCell>
                  <TableCell>
                    <Tooltip title={user.auth_provider === 'telegram' ? 'Telegram Login' : user.auth_provider === 'google' ? 'Google Login' : 'Email/Password'}>
                      <span>
                        {user.auth_provider === 'telegram' ? (
                          <TelegramIcon sx={{ color: '#0088cc', fontSize: 20 }} />
                        ) : user.auth_provider === 'google' ? (
                          <GoogleIcon sx={{ color: '#4285f4', fontSize: 20 }} />
                        ) : (
                          <EmailIcon sx={{ color: '#888', fontSize: 20 }} />
                        )}
                      </span>
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.role}
                      size="small"
                      color={getRoleColor(user.role) as any}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={user.status}
                      size="small"
                      color={getStatusColor(user.status) as any}
                    />
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Click to manage credits">
                      <Chip
                        icon={<CreditsIcon sx={{ fontSize: 16 }} />}
                        label={(user.credit_balance ?? 0).toLocaleString()}
                        size="small"
                        onClick={() => handleCreditClick(user)}
                        sx={{
                          cursor: 'pointer',
                          bgcolor: 'rgba(255, 193, 7, 0.15)',
                          color: '#F9A825',
                          fontWeight: 600,
                          '&:hover': { bgcolor: 'rgba(255, 193, 7, 0.25)' },
                        }}
                      />
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    {user.created_at
                      ? format(new Date(user.created_at), 'MMM d, yyyy')
                      : '-'}
                  </TableCell>
                  <TableCell>
                    {user.last_login
                      ? format(new Date(user.last_login), 'MMM d, yyyy HH:mm')
                      : 'Never'}
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={(e) => handleMenuOpen(e, user)}
                    >
                      <MoreVertIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={filteredUsers.length}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>

      {/* Actions Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuItem onClick={() => { if (menuUser) handleViewUser(menuUser); handleMenuClose(); }}>
          <ListItemIcon>
            <ViewIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => { if (menuUser) handleCreditClick(menuUser); handleMenuClose(); }}>
          <ListItemIcon>
            <CreditsIcon fontSize="small" sx={{ color: '#FFD700' }} />
          </ListItemIcon>
          <ListItemText>Manage Credits</ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() => { if (menuUser) handleSuspendUser(menuUser); handleMenuClose(); }}
          disabled={menuUser?.role === 'admin' || menuUser?.role === 'owner'}
        >
          <ListItemIcon>
            {menuUser?.status === 'suspended' ? (
              <ActivateIcon fontSize="small" color="success" />
            ) : (
              <BlockIcon fontSize="small" color="warning" />
            )}
          </ListItemIcon>
          <ListItemText>
            {menuUser?.status === 'suspended' ? 'Unsuspend User' : 'Suspend User'}
          </ListItemText>
        </MenuItem>
        <MenuItem
          onClick={() => { if (menuUser) handleDeleteClick(menuUser); handleMenuClose(); }}
          disabled={menuUser?.role === 'admin' || menuUser?.role === 'owner'}
          sx={{ color: 'error.main' }}
        >
          <ListItemIcon>
            <DeleteIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Delete User</ListItemText>
        </MenuItem>
      </Menu>

      {/* View User Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>User Details</DialogTitle>
        <DialogContent>
          {detailLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : userDetail ? (
            <Box sx={{ pt: 1 }}>
              <Typography variant="body2" color="text.secondary">ID</Typography>
              <Typography variant="body1" gutterBottom>{userDetail.id}</Typography>

              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>Username</Typography>
              <Typography variant="body1" gutterBottom>{userDetail.username || '-'}</Typography>

              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>Email</Typography>
              <Typography variant="body1" gutterBottom>{userDetail.email || '-'}</Typography>

              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>Full Name</Typography>
              <Typography variant="body1" gutterBottom>{userDetail.full_name || '-'}</Typography>

              <Box sx={{ display: 'flex', gap: 4, mt: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Role</Typography>
                  <Chip label={userDetail.role} size="small" color={userDetail.role === 'admin' ? 'primary' : 'default'} />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip label={userDetail.status} size="small" color={userDetail.status === 'active' ? 'success' : userDetail.status === 'suspended' ? 'error' : 'warning'} />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Auth Provider</Typography>
                  <Chip
                    icon={userDetail.auth_provider === 'telegram' ? <TelegramIcon /> : userDetail.auth_provider === 'google' ? <GoogleIcon /> : <EmailIcon />}
                    label={userDetail.auth_provider === 'telegram' ? 'Telegram' : userDetail.auth_provider === 'google' ? 'Google' : 'Email/Password'}
                    size="small"
                    color={userDetail.auth_provider === 'telegram' ? 'info' : userDetail.auth_provider === 'google' ? 'error' : 'default'}
                    variant="outlined"
                  />
                </Box>
              </Box>

              <Box sx={{ display: 'flex', gap: 4, mt: 3 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Channels</Typography>
                  <Typography variant="h6">{userDetail.channels_count}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Posts</Typography>
                  <Typography variant="h6">{userDetail.total_posts.toLocaleString()}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Total Views</Typography>
                  <Typography variant="h6">{userDetail.total_views.toLocaleString()}</Typography>
                </Box>
              </Box>

              <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>Created</Typography>
              <Typography variant="body1" gutterBottom>
                {userDetail.created_at ? format(new Date(userDetail.created_at), 'PPpp') : '-'}
              </Typography>

              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>Last Login</Typography>
              <Typography variant="body1">
                {userDetail.last_login ? format(new Date(userDetail.last_login), 'PPpp') : 'Never'}
              </Typography>
            </Box>
          ) : (
            <Typography>No user data available</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete User</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to permanently delete user <strong>{selectedUser?.username}</strong> (ID: {selectedUser?.id})?
            <br /><br />
            This action cannot be undone and will also delete all their channels and associated data.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Suspend User Dialog */}
      <Dialog open={suspendDialogOpen} onClose={() => setSuspendDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BlockIcon color="warning" />
          Suspend User
        </DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            You are about to suspend user <strong>{selectedUser?.username}</strong> (ID: {selectedUser?.id}).
          </DialogContentText>

          <Alert severity="warning" sx={{ mb: 2 }}>
            <strong>This will:</strong>
            <ul style={{ margin: '8px 0 0 0', paddingLeft: '20px' }}>
              <li>Block the user from logging in</li>
              <li>Disable all their channels</li>
              <li>Stop MTProto data collection</li>
              <li>Pause all scheduled posts</li>
            </ul>
          </Alert>

          <TextField
            autoFocus
            label="Suspension Reason"
            placeholder="e.g., Violation of terms of service, Suspicious activity, etc."
            fullWidth
            multiline
            rows={3}
            value={suspendReason}
            onChange={(e) => setSuspendReason(e.target.value)}
            helperText="This reason will be shown to the user when they try to log in. Minimum 5 characters."
            required
            error={suspendReason.length > 0 && suspendReason.length < 5}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSuspendDialogOpen(false)} disabled={suspendLoading}>
            Cancel
          </Button>
          <Button
            onClick={handleSuspendConfirm}
            color="warning"
            variant="contained"
            disabled={suspendLoading || suspendReason.trim().length < 5}
            startIcon={suspendLoading ? <CircularProgress size={16} /> : <BlockIcon />}
          >
            {suspendLoading ? 'Suspending...' : 'Suspend User'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Credit Management Dialog */}
      <Dialog open={creditDialogOpen} onClose={() => setCreditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CreditsIcon sx={{ color: '#FFD700' }} />
          Manage Credits - {selectedUser?.username || `User #${selectedUser?.id}`}
        </DialogTitle>
        <DialogContent>
          {/* Current Balance Display */}
          <Box sx={{ mb: 3, p: 2, bgcolor: 'rgba(255, 193, 7, 0.1)', borderRadius: 2 }}>
            <Typography variant="h4" fontWeight="bold" sx={{ color: '#F9A825' }}>
              {userCredits?.balance?.toLocaleString() ?? '...'}
              <Typography component="span" variant="body1" color="text.secondary" sx={{ ml: 1 }}>
                credits
              </Typography>
            </Typography>
            <Box sx={{ display: 'flex', gap: 3, mt: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Earned: {userCredits?.lifetime_earned?.toLocaleString() ?? 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Spent: {userCredits?.lifetime_spent?.toLocaleString() ?? 0}
              </Typography>
            </Box>
          </Box>

          {/* Adjustment Form */}
          <Typography variant="subtitle2" gutterBottom>
            Adjust Credits
          </Typography>
          <TextField
            label="Amount"
            type="number"
            fullWidth
            value={creditAmount}
            onChange={(e) => setCreditAmount(e.target.value)}
            sx={{ mb: 2 }}
            InputProps={{
              startAdornment: <InputAdornment position="start"><CreditsIcon sx={{ color: '#FFD700' }} /></InputAdornment>,
            }}
          />
          <TextField
            label="Reason"
            placeholder="e.g., Promotional bonus, Customer support credit, Refund, etc."
            fullWidth
            multiline
            rows={2}
            value={creditReason}
            onChange={(e) => setCreditReason(e.target.value)}
            helperText="Required - minimum 5 characters"
          />
        </DialogContent>
        <DialogActions sx={{ p: 2, gap: 1 }}>
          <Button onClick={() => setCreditDialogOpen(false)} disabled={creditLoading}>
            Cancel
          </Button>
          <Button
            variant="outlined"
            color="error"
            onClick={() => handleCreditAdjust(false)}
            disabled={creditLoading || !creditAmount || !creditReason.trim()}
            startIcon={creditLoading ? <CircularProgress size={16} /> : <RemoveIcon />}
          >
            Remove
          </Button>
          <Button
            variant="contained"
            color="success"
            onClick={() => handleCreditAdjust(true)}
            disabled={creditLoading || !creditAmount || !creditReason.trim()}
            startIcon={creditLoading ? <CircularProgress size={16} /> : <AddIcon />}
          >
            Add Credits
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default UsersPage;
