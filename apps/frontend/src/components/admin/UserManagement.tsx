/**
 * User Management Component
 * 
 * Admin dashboard for user oversight and management.
 * Integrates with admin/usersService.ts
 */

import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Button,
    IconButton,
    TextField,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Alert,
    Chip,
    CircularProgress,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    TablePagination,
    Paper,
    Avatar,
    Menu,
    MenuItem,
    Divider,
    FormControl,
    InputLabel,
    Select
} from '@mui/material';
import {
    MoreVert as MoreIcon,
    Block as BlockIcon,
    CheckCircle as ActiveIcon,
    Delete as DeleteIcon,
    Search as SearchIcon,
    Refresh as RefreshIcon,
    History as HistoryIcon,
    Assessment as StatsIcon,
    Email as EmailIcon,
    Person as PersonIcon,
    AdminPanelSettings as AdminIcon
} from '@mui/icons-material';
import { 
    adminUsersService, 
    type AdminUserInfo, 
    type UserStatistics,
    type UserAuditLog
} from '@/services/admin/usersService';

/**
 * User Role Type (5-tier hierarchy)
 * viewer < user < moderator < admin < owner
 */
type UserRole = 'viewer' | 'user' | 'moderator' | 'admin' | 'owner';

export interface UserManagementProps {
    onUserUpdated?: () => void;
}

const UserManagement: React.FC<UserManagementProps> = ({ onUserUpdated }) => {
    const [users, setUsers] = useState<AdminUserInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [selectedUser, setSelectedUser] = useState<AdminUserInfo | null>(null);
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [actionDialog, setActionDialog] = useState<{
        open: boolean;
        type: 'suspend' | 'delete' | 'role' | 'stats' | 'audit' | 'notify' | null;
        user: AdminUserInfo | null;
    }>({
        open: false,
        type: null,
        user: null
    });
    const [suspendReason, setSuspendReason] = useState('');
    const [newRole, setNewRole] = useState<UserRole>('user');
    const [notificationMessage, setNotificationMessage] = useState('');
    const [statistics, setStatistics] = useState<UserStatistics | null>(null);
    const [auditLogs, setAuditLogs] = useState<UserAuditLog[]>([]);
    const [actionLoading, setActionLoading] = useState(false);

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await adminUsersService.getAllUsers();
            setUsers(data.users);
        } catch (err: any) {
            setError(err.message || 'Failed to load users');
            console.error('Failed to load users:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSearch = async () => {
        if (!searchTerm.trim()) {
            loadUsers();
            return;
        }

        setLoading(true);
        try {
            const results = await adminUsersService.searchUsers(searchTerm);
            setUsers(results);
        } catch (err: any) {
            setError(err.message || 'Search failed');
        } finally {
            setLoading(false);
        }
    };

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, user: AdminUserInfo) => {
        setAnchorEl(event.currentTarget);
        setSelectedUser(user);
        setNewRole(user.role);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    const openActionDialog = (
        type: 'suspend' | 'delete' | 'role' | 'stats' | 'audit' | 'notify',
        user: AdminUserInfo
    ) => {
        setActionDialog({ open: true, type, user });
        handleMenuClose();
        
        if (type === 'stats') {
            loadStatistics();
        } else if (type === 'audit') {
            loadAuditLogs(user.user_id);
        }
    };

    const closeActionDialog = () => {
        setActionDialog({ open: false, type: null, user: null });
        setSuspendReason('');
        setNotificationMessage('');
        setStatistics(null);
        setAuditLogs([]);
    };

    const loadStatistics = async () => {
        setActionLoading(true);
        try {
            const stats = await adminUsersService.getUserStatistics();
            setStatistics(stats);
        } catch (err) {
            console.error('Failed to load statistics:', err);
        } finally {
            setActionLoading(false);
        }
    };

    const loadAuditLogs = async (userId: number) => {
        setActionLoading(true);
        try {
            const logs = await adminUsersService.getUserAuditLog(userId);
            setAuditLogs(logs);
        } catch (err) {
            console.error('Failed to load audit logs:', err);
        } finally {
            setActionLoading(false);
        }
    };

    const handleSuspendUser = async () => {
        if (!actionDialog.user || !suspendReason.trim()) return;

        setActionLoading(true);
        try {
            await adminUsersService.suspendUser(
                actionDialog.user.user_id,
                {
                    reason: suspendReason,
                    duration_days: 30,
                    notify_user: true
                }
            );
            await loadUsers();
            closeActionDialog();
            onUserUpdated?.();
        } catch (err: any) {
            setError(err.message || 'Failed to suspend user');
        } finally {
            setActionLoading(false);
        }
    };

    const handleUnsuspendUser = async (userId: number) => {
        setActionLoading(true);
        try {
            await adminUsersService.unsuspendUser(userId);
            await loadUsers();
            onUserUpdated?.();
        } catch (err: any) {
            setError(err.message || 'Failed to unsuspend user');
        } finally {
            setActionLoading(false);
        }
    };

    const handleUpdateRole = async () => {
        if (!actionDialog.user) return;

        setActionLoading(true);
        try {
            await adminUsersService.updateUserRole(actionDialog.user.user_id, newRole);
            await loadUsers();
            closeActionDialog();
            onUserUpdated?.();
        } catch (err: any) {
            setError(err.message || 'Failed to update role');
        } finally {
            setActionLoading(false);
        }
    };

    const handleDeleteUser = async () => {
        if (!actionDialog.user) return;

        setActionLoading(true);
        try {
            await adminUsersService.deleteUser(
                actionDialog.user.user_id,
                'Admin deleted user'
            );
            await loadUsers();
            closeActionDialog();
            onUserUpdated?.();
        } catch (err: any) {
            setError(err.message || 'Failed to delete user');
        } finally {
            setActionLoading(false);
        }
    };

    const handleSendNotification = async () => {
        if (!actionDialog.user || !notificationMessage.trim()) return;

        setActionLoading(true);
        try {
            await adminUsersService.sendNotification(
                actionDialog.user.user_id,
                notificationMessage
            );
            closeActionDialog();
        } catch (err: any) {
            setError(err.message || 'Failed to send notification');
        } finally {
            setActionLoading(false);
        }
    };

    const getRoleColor = (role: string): 'default' | 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success' => {
        switch (role) {
            case 'owner': return 'error';      // Highest level - red
            case 'admin': return 'warning';    // Platform admin - orange
            case 'moderator': return 'info';   // Support team - blue
            case 'user': return 'primary';     // Standard user - primary
            case 'viewer': return 'default';   // Read-only - gray
            default: return 'default';
        }
    };

    const getRoleIcon = (role: string) => {
        switch (role) {
            case 'owner':
            case 'admin':
                return <AdminIcon fontSize="small" />;
            case 'moderator':
            case 'user':
            case 'viewer':
            default:
                return <PersonIcon fontSize="small" />;
        }
    };

    const filteredUsers = users.filter(user => 
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (user.full_name && user.full_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (user.telegram_username && user.telegram_username.toLowerCase().includes(searchTerm.toLowerCase())) ||
        user.telegram_id?.toString().includes(searchTerm) ||
        user.role.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const paginatedUsers = filteredUsers.slice(
        page * rowsPerPage,
        page * rowsPerPage + rowsPerPage
    );

    return (
        <Card>
            <CardContent>
                {/* Header */}
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                    <Typography variant="h5" component="h2">
                        User Management
                    </Typography>
                    <Button
                        startIcon={<RefreshIcon />}
                        onClick={loadUsers}
                        disabled={loading}
                        size="small"
                    >
                        Refresh
                    </Button>
                </Box>

                {/* Search Bar */}
                <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
                    <TextField
                        fullWidth
                        size="small"
                        placeholder="Search by username, Telegram ID, or role..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                        InputProps={{
                            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                        }}
                    />
                    <Button variant="contained" onClick={handleSearch}>
                        Search
                    </Button>
                </Box>

                {/* Error Alert */}
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}

                {/* Users Table */}
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                        <CircularProgress />
                    </Box>
                ) : (
                    <>
                        <TableContainer component={Paper} variant="outlined">
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>User</TableCell>
                                        <TableCell>Role</TableCell>
                                        <TableCell>Status</TableCell>
                                        <TableCell align="right">Channels</TableCell>
                                        <TableCell>Last Active</TableCell>
                                        <TableCell align="center">Actions</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {paginatedUsers.map((user) => (
                                        <TableRow key={user.user_id} hover>
                                            <TableCell>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <Avatar sx={{ width: 32, height: 32 }}>
                                                        {(user.full_name || user.email)[0].toUpperCase()}
                                                    </Avatar>
                                                    <Box>
                                                        <Typography variant="body2" fontWeight="medium">
                                                            {user.full_name || user.email}
                                                        </Typography>
                                                        <Typography variant="caption" color="text.secondary">
                                                            {user.telegram_username ? `@${user.telegram_username}` : `TG: ${user.telegram_id || 'N/A'}`}
                                                        </Typography>
                                                    </Box>
                                                </Box>
                                            </TableCell>
                                            <TableCell>
                                                <Chip 
                                                    label={user.role} 
                                                    color={getRoleColor(user.role)}
                                                    size="small"
                                                    icon={getRoleIcon(user.role)}
                                                />
                                            </TableCell>
                                            <TableCell>
                                                {user.status === 'suspended' ? (
                                                    <Chip 
                                                        label="Suspended" 
                                                        color="error" 
                                                        size="small"
                                                        icon={<BlockIcon />}
                                                    />
                                                ) : user.status === 'deleted' ? (
                                                    <Chip 
                                                        label="Deleted" 
                                                        color="default" 
                                                        size="small"
                                                        icon={<DeleteIcon />}
                                                    />
                                                ) : (
                                                    <Chip 
                                                        label="Active" 
                                                        color="success" 
                                                        size="small"
                                                        icon={<ActiveIcon />}
                                                    />
                                                )}
                                            </TableCell>
                                            <TableCell align="right">
                                                {user.total_channels || 0}
                                            </TableCell>
                                            <TableCell>
                                                {user.last_login 
                                                    ? new Date(user.last_login).toLocaleDateString()
                                                    : 'Never'}
                                            </TableCell>
                                            <TableCell align="center">
                                                <IconButton
                                                    size="small"
                                                    onClick={(e) => handleMenuOpen(e, user)}
                                                >
                                                    <MoreIcon />
                                                </IconButton>
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>

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
                    </>
                )}

                {/* Action Menu */}
                <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleMenuClose}
                >
                    <MenuItem onClick={() => selectedUser && openActionDialog('stats', selectedUser)}>
                        <StatsIcon fontSize="small" sx={{ mr: 1 }} />
                        View Statistics
                    </MenuItem>
                    <MenuItem onClick={() => selectedUser && openActionDialog('audit', selectedUser)}>
                        <HistoryIcon fontSize="small" sx={{ mr: 1 }} />
                        Audit Log
                    </MenuItem>
                    <MenuItem onClick={() => selectedUser && openActionDialog('notify', selectedUser)}>
                        <EmailIcon fontSize="small" sx={{ mr: 1 }} />
                        Send Notification
                    </MenuItem>
                    <Divider />
                    <MenuItem onClick={() => selectedUser && openActionDialog('role', selectedUser)}>
                        <AdminIcon fontSize="small" sx={{ mr: 1 }} />
                        Change Role
                    </MenuItem>
                    {selectedUser?.status === 'suspended' ? (
                        <MenuItem onClick={() => selectedUser && handleUnsuspendUser(selectedUser.user_id)}>
                            <ActiveIcon fontSize="small" sx={{ mr: 1 }} />
                            Unsuspend
                        </MenuItem>
                    ) : (
                        <MenuItem onClick={() => selectedUser && openActionDialog('suspend', selectedUser)}>
                            <BlockIcon fontSize="small" sx={{ mr: 1 }} />
                            Suspend
                        </MenuItem>
                    )}
                    <MenuItem 
                        onClick={() => selectedUser && openActionDialog('delete', selectedUser)}
                        sx={{ color: 'error.main' }}
                    >
                        <DeleteIcon fontSize="small" sx={{ mr: 1 }} />
                        Delete
                    </MenuItem>
                </Menu>

                {/* Action Dialogs */}
                <Dialog 
                    open={actionDialog.open} 
                    onClose={closeActionDialog}
                    maxWidth="sm"
                    fullWidth
                >
                    <DialogTitle>
                        {actionDialog.type === 'suspend' && 'Suspend User'}
                        {actionDialog.type === 'delete' && 'Delete User'}
                        {actionDialog.type === 'role' && 'Change User Role'}
                        {actionDialog.type === 'stats' && 'User Statistics'}
                        {actionDialog.type === 'audit' && 'Audit Log'}
                        {actionDialog.type === 'notify' && 'Send Notification'}
                    </DialogTitle>
                    <DialogContent>
                        {/* Suspend Dialog */}
                        {actionDialog.type === 'suspend' && (
                            <Box>
                                <Alert severity="warning" sx={{ mb: 2 }}>
                                    This will suspend the user and prevent further access.
                                </Alert>
                                <TextField
                                    fullWidth
                                    multiline
                                    rows={3}
                                    label="Suspension Reason"
                                    value={suspendReason}
                                    onChange={(e) => setSuspendReason(e.target.value)}
                                    placeholder="Enter reason for suspension..."
                                    required
                                />
                            </Box>
                        )}

                        {/* Delete Dialog */}
                        {actionDialog.type === 'delete' && (
                            <Alert severity="error">
                                Are you sure you want to delete user "{actionDialog.user?.full_name || actionDialog.user?.email}"? 
                                This action cannot be undone.
                            </Alert>
                        )}

                        {/* Role Change Dialog */}
                        {actionDialog.type === 'role' && (
                            <FormControl fullWidth>
                                <InputLabel>New Role</InputLabel>
                                <Select<UserRole>
                                    value={newRole}
                                    label="New Role"
                                    onChange={(e) => setNewRole(e.target.value as UserRole)}
                                >
                                    <MenuItem value="viewer">Viewer (Read-only)</MenuItem>
                                    <MenuItem value="user">User</MenuItem>
                                    <MenuItem value="moderator">Moderator</MenuItem>
                                    <MenuItem value="admin">Admin</MenuItem>
                                    <MenuItem value="owner">Owner</MenuItem>
                                </Select>
                            </FormControl>
                        )}

                        {/* Statistics Dialog */}
                        {actionDialog.type === 'stats' && (
                            <Box>
                                {actionLoading ? (
                                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                                        <CircularProgress />
                                    </Box>
                                ) : statistics ? (
                                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                        <Box>
                                            <Typography variant="caption" color="text.secondary">
                                                Total Users
                                            </Typography>
                                            <Typography variant="h6">
                                                {statistics.total_users.toLocaleString()}
                                            </Typography>
                                        </Box>
                                        <Box>
                                            <Typography variant="caption" color="text.secondary">
                                                Active Users
                                            </Typography>
                                            <Typography variant="h6">
                                                {statistics.active_users.toLocaleString()}
                                            </Typography>
                                        </Box>
                                        <Box>
                                            <Typography variant="caption" color="text.secondary">
                                                Premium Users
                                            </Typography>
                                            <Typography variant="h6">
                                                {statistics.premium_users.toLocaleString()}
                                            </Typography>
                                        </Box>
                                        <Box>
                                            <Typography variant="caption" color="text.secondary">
                                                Logins Today
                                            </Typography>
                                            <Typography variant="h6">
                                                {statistics.total_logins_today.toLocaleString()}
                                            </Typography>
                                        </Box>
                                    </Box>
                                ) : (
                                    <Alert severity="info">No statistics available</Alert>
                                )}
                            </Box>
                        )}

                        {/* Audit Log Dialog */}
                        {actionDialog.type === 'audit' && (
                            <Box>
                                {actionLoading ? (
                                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                                        <CircularProgress />
                                    </Box>
                                ) : auditLogs.length > 0 ? (
                                    <Box sx={{ maxHeight: 400, overflowY: 'auto' }}>
                                        {auditLogs.map((log, index) => (
                                            <Box key={index} sx={{ mb: 2, pb: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
                                                <Typography variant="body2" fontWeight="medium">
                                                    {log.action}
                                                </Typography>
                                                <Typography variant="caption" color="text.secondary">
                                                    by {log.admin_email} • {new Date(log.timestamp).toLocaleString()}
                                                </Typography>
                                                {log.details && Object.keys(log.details).length > 0 && (
                                                    <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                                                        {JSON.stringify(log.details)}
                                                    </Typography>
                                                )}
                                            </Box>
                                        ))}
                                    </Box>
                                ) : (
                                    <Alert severity="info">No audit logs available</Alert>
                                )}
                            </Box>
                        )}

                        {/* Notification Dialog */}
                        {actionDialog.type === 'notify' && (
                            <TextField
                                fullWidth
                                multiline
                                rows={4}
                                label="Notification Message"
                                value={notificationMessage}
                                onChange={(e) => setNotificationMessage(e.target.value)}
                                placeholder="Enter notification message..."
                                required
                            />
                        )}
                    </DialogContent>
                    <DialogActions>
                        <Button onClick={closeActionDialog}>Cancel</Button>
                        {actionDialog.type === 'suspend' && (
                            <Button 
                                onClick={handleSuspendUser} 
                                variant="contained" 
                                color="warning"
                                disabled={!suspendReason.trim() || actionLoading}
                            >
                                {actionLoading ? <CircularProgress size={20} /> : 'Suspend'}
                            </Button>
                        )}
                        {actionDialog.type === 'delete' && (
                            <Button 
                                onClick={handleDeleteUser} 
                                variant="contained" 
                                color="error"
                                disabled={actionLoading}
                            >
                                {actionLoading ? <CircularProgress size={20} /> : 'Delete'}
                            </Button>
                        )}
                        {actionDialog.type === 'role' && (
                            <Button 
                                onClick={handleUpdateRole} 
                                variant="contained"
                                disabled={actionLoading}
                            >
                                {actionLoading ? <CircularProgress size={20} /> : 'Update Role'}
                            </Button>
                        )}
                        {actionDialog.type === 'notify' && (
                            <Button 
                                onClick={handleSendNotification} 
                                variant="contained"
                                disabled={!notificationMessage.trim() || actionLoading}
                            >
                                {actionLoading ? <CircularProgress size={20} /> : 'Send'}
                            </Button>
                        )}
                    </DialogActions>
                </Dialog>
            </CardContent>
        </Card>
    );
};

export default UserManagement;
