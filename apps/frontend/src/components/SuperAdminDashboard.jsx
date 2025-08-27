import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Grid,
    Paper,
    Tabs,
    Tab,
    Card,
    CardContent,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Button,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Alert,
    CircularProgress,
    Avatar,
    List,
    ListItem,
    ListItemText,
    ListItemAvatar,
    Divider
} from '@mui/material';
import {
    Dashboard as DashboardIcon,
    People as PeopleIcon,
    Security as SecurityIcon,
    Settings as SettingsIcon,
    Block as BlockIcon,
    CheckCircle as CheckCircleIcon,
    Warning as WarningIcon,
    AdminPanelSettings as AdminIcon
} from '@mui/icons-material';

// Tab Panel Component
const TabPanel = ({ children, value, index, ...other }) => (
    <div
        role="tabpanel"
        hidden={value !== index}
        id={`admin-tabpanel-${index}`}
        aria-labelledby={`admin-tab-${index}`}
        {...other}
    >
        {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
);

const SuperAdminDashboard = () => {
    const [activeTab, setActiveTab] = useState(0);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState(null);
    const [users, setUsers] = useState([]);
    const [auditLogs, setAuditLogs] = useState([]);
    const [suspendDialog, setSuspendDialog] = useState({ open: false, user: null });
    const [suspensionReason, setSuspensionReason] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            
            // Fetch system statistics
            const statsResponse = await fetch('/api/v1/superadmin/stats', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                }
            });
            
            if (statsResponse.ok) {
                const statsData = await statsResponse.json();
                setStats(statsData);
            }

            // Fetch users
            const usersResponse = await fetch('/api/v1/superadmin/users?limit=100', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                }
            });
            
            if (usersResponse.ok) {
                const usersData = await usersResponse.json();
                setUsers(usersData);
            }

            // Fetch audit logs
            const auditResponse = await fetch('/api/v1/superadmin/audit-logs?limit=50', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                }
            });
            
            if (auditResponse.ok) {
                const auditData = await auditResponse.json();
                setAuditLogs(auditData);
            }

        } catch (err) {
            setError('Failed to fetch dashboard data');
            console.error('Dashboard fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleSuspendUser = async () => {
        if (!suspendDialog.user || !suspensionReason.trim()) {
            setError('Please provide a suspension reason');
            return;
        }

        try {
            const response = await fetch(`/api/v1/superadmin/users/${suspendDialog.user.id}/suspend`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                },
                body: JSON.stringify({ reason: suspensionReason })
            });

            if (response.ok) {
                setSuccess('User suspended successfully');
                setSuspendDialog({ open: false, user: null });
                setSuspensionReason('');
                fetchDashboardData(); // Refresh data
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to suspend user');
            }
        } catch (err) {
            setError('Network error occurred');
            console.error('Suspend user error:', err);
        }
    };

    const handleReactivateUser = async (userId) => {
        try {
            const response = await fetch(`/api/v1/superadmin/users/${userId}/reactivate`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('adminToken')}`
                }
            });

            if (response.ok) {
                setSuccess('User reactivated successfully');
                fetchDashboardData(); // Refresh data
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Failed to reactivate user');
            }
        } catch (err) {
            setError('Network error occurred');
            console.error('Reactivate user error:', err);
        }
    };

    const getStatusColor = (status) => {
        switch (status.toLowerCase()) {
            case 'active': return 'success';
            case 'suspended': return 'error';
            case 'inactive': return 'warning';
            default: return 'default';
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString();
    };

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ mt: 4, mb: 4, display: 'flex', justifyContent: 'center' }}>
                <CircularProgress size={60} />
            </Container>
        );
    }

    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            {/* Header */}
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <AdminIcon sx={{ mr: 2, fontSize: 40, color: 'primary.main' }} />
                    SuperAdmin Management Panel
                </Typography>
                <Typography variant="subtitle1" color="text.secondary">
                    Enterprise-grade system administration and monitoring
                </Typography>
            </Box>

            {/* Alerts */}
            {error && (
                <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}
            {success && (
                <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
                    {success}
                </Alert>
            )}

            {/* System Stats Cards */}
            {stats && (
                <Grid container spacing={3} sx={{ mb: 4 }}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card>
                            <CardContent sx={{ textAlign: 'center' }}>
                                <PeopleIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
                                <Typography variant="h4" color="primary">
                                    {stats.users.total}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Total Users
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card>
                            <CardContent sx={{ textAlign: 'center' }}>
                                <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                                <Typography variant="h4" color="success.main">
                                    {stats.users.active}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Active Users
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card>
                            <CardContent sx={{ textAlign: 'center' }}>
                                <BlockIcon sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
                                <Typography variant="h4" color="error.main">
                                    {stats.users.suspended}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Suspended Users
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card>
                            <CardContent sx={{ textAlign: 'center' }}>
                                <SecurityIcon sx={{ fontSize: 40, color: 'info.main', mb: 1 }} />
                                <Typography variant="h4" color="info.main">
                                    {stats.activity.admin_logins_24h}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Admin Logins (24h)
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            )}

            {/* Main Content Tabs */}
            <Paper sx={{ width: '100%' }}>
                <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
                        <Tab 
                            icon={<DashboardIcon />} 
                            label="Overview" 
                            iconPosition="start"
                        />
                        <Tab 
                            icon={<PeopleIcon />} 
                            label="User Management" 
                            iconPosition="start"
                        />
                        <Tab 
                            icon={<SecurityIcon />} 
                            label="Audit Logs" 
                            iconPosition="start"
                        />
                        <Tab 
                            icon={<SettingsIcon />} 
                            label="System Config" 
                            iconPosition="start"
                        />
                    </Tabs>
                </Box>

                {/* Overview Tab */}
                <TabPanel value={activeTab} index={0}>
                    <Typography variant="h6" gutterBottom>System Overview</Typography>
                    <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>Recent Activity</Typography>
                                    <List>
                                        {auditLogs.slice(0, 5).map((log, index) => (
                                            <React.Fragment key={log.id}>
                                                <ListItem>
                                                    <ListItemAvatar>
                                                        <Avatar sx={{ bgcolor: log.success ? 'success.main' : 'error.main' }}>
                                                            {log.success ? <CheckCircleIcon /> : <WarningIcon />}
                                                        </Avatar>
                                                    </ListItemAvatar>
                                                    <ListItemText
                                                        primary={`${log.admin_username} - ${log.action}`}
                                                        secondary={formatDate(log.created_at)}
                                                    />
                                                </ListItem>
                                                {index < 4 && <Divider />}
                                            </React.Fragment>
                                        ))}
                                    </List>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Card>
                                <CardContent>
                                    <Typography variant="h6" gutterBottom>System Health</Typography>
                                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                        <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                                        <Typography>Database: Operational</Typography>
                                    </Box>
                                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                        <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                                        <Typography>API Services: Healthy</Typography>
                                    </Box>
                                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                        <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                                        <Typography>Security System: Active</Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </TabPanel>

                {/* User Management Tab */}
                <TabPanel value={activeTab} index={1}>
                    <Typography variant="h6" gutterBottom>System Users</Typography>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>User ID</TableCell>
                                    <TableCell>Username</TableCell>
                                    <TableCell>Full Name</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell>Subscription</TableCell>
                                    <TableCell>Channels</TableCell>
                                    <TableCell>Posts</TableCell>
                                    <TableCell>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {users.map((user) => (
                                    <TableRow key={user.id}>
                                        <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                                            {user.telegram_id}
                                        </TableCell>
                                        <TableCell>{user.username || 'N/A'}</TableCell>
                                        <TableCell>{user.full_name || 'N/A'}</TableCell>
                                        <TableCell>
                                            <Chip 
                                                label={user.status} 
                                                color={getStatusColor(user.status)}
                                                size="small"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Chip 
                                                label={user.subscription_tier || 'free'} 
                                                variant="outlined"
                                                size="small"
                                            />
                                        </TableCell>
                                        <TableCell>{user.total_channels}</TableCell>
                                        <TableCell>{user.total_posts}</TableCell>
                                        <TableCell>
                                            {user.status === 'active' ? (
                                                <Button
                                                    variant="outlined"
                                                    color="error"
                                                    size="small"
                                                    onClick={() => setSuspendDialog({ open: true, user })}
                                                >
                                                    Suspend
                                                </Button>
                                            ) : user.status === 'suspended' ? (
                                                <Button
                                                    variant="outlined"
                                                    color="success"
                                                    size="small"
                                                    onClick={() => handleReactivateUser(user.id)}
                                                >
                                                    Reactivate
                                                </Button>
                                            ) : null}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </TabPanel>

                {/* Audit Logs Tab */}
                <TabPanel value={activeTab} index={2}>
                    <Typography variant="h6" gutterBottom>Administrative Audit Trail</Typography>
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Timestamp</TableCell>
                                    <TableCell>Admin</TableCell>
                                    <TableCell>Action</TableCell>
                                    <TableCell>Resource</TableCell>
                                    <TableCell>IP Address</TableCell>
                                    <TableCell>Status</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {auditLogs.map((log) => (
                                    <TableRow key={log.id}>
                                        <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                                            {formatDate(log.created_at)}
                                        </TableCell>
                                        <TableCell>{log.admin_username}</TableCell>
                                        <TableCell>{log.action}</TableCell>
                                        <TableCell>{log.resource_type}</TableCell>
                                        <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}>
                                            {log.ip_address}
                                        </TableCell>
                                        <TableCell>
                                            <Chip 
                                                label={log.success ? 'Success' : 'Failed'} 
                                                color={log.success ? 'success' : 'error'}
                                                size="small"
                                            />
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                </TabPanel>

                {/* System Configuration Tab */}
                <TabPanel value={activeTab} index={3}>
                    <Typography variant="h6" gutterBottom>System Configuration</Typography>
                    <Alert severity="info">
                        System configuration management coming soon. This will allow runtime configuration 
                        of security settings, feature flags, and operational parameters.
                    </Alert>
                </TabPanel>
            </Paper>

            {/* User Suspension Dialog */}
            <Dialog open={suspendDialog.open} onClose={() => setSuspendDialog({ open: false, user: null })}>
                <DialogTitle>Suspend User</DialogTitle>
                <DialogContent>
                    <Typography gutterBottom>
                        Are you sure you want to suspend user: <strong>{suspendDialog.user?.username || suspendDialog.user?.full_name || 'Unknown'}</strong>?
                    </Typography>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Suspension Reason"
                        fullWidth
                        variant="outlined"
                        multiline
                        rows={3}
                        value={suspensionReason}
                        onChange={(e) => setSuspensionReason(e.target.value)}
                        placeholder="Please provide a detailed reason for suspension..."
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setSuspendDialog({ open: false, user: null })}>
                        Cancel
                    </Button>
                    <Button onClick={handleSuspendUser} color="error" variant="contained">
                        Suspend User
                    </Button>
                </DialogActions>
            </Dialog>
        </Container>
    );
};

export default SuperAdminDashboard;
