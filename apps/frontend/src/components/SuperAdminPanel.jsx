import React, { useState, useEffect } from 'react';
import {
    Box,
    Grid,
    Paper,
    Typography,
    Card,
    CardContent,
    CardHeader,
    Button,
    IconButton,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Chip,
    TextField,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Alert,
    LinearProgress,
    Avatar,
    Tooltip,
    Tabs,
    Tab,
    AppBar,
    Toolbar,
    Drawer,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Divider,
    Badge,
    Switch,
    FormControlLabel
} from '@mui/material';

import {
    Dashboard as DashboardIcon,
    People as PeopleIcon,
    Settings as SettingsIcon,
    Security as SecurityIcon,
    Analytics as AnalyticsIcon,
    Payment as PaymentIcon,
    GetApp as ExportIcon,
    Visibility as ViewIcon,
    Edit as EditIcon,
    Delete as DeleteIcon,
    Block as BlockIcon,
    CheckCircle as CheckCircleIcon,
    Warning as WarningIcon,
    Error as ErrorIcon,
    Refresh as RefreshIcon,
    Menu as MenuIcon,
    Notifications as NotificationsIcon,
    ExitToApp as LogoutIcon,
    Search as SearchIcon,
    FilterList as FilterIcon
} from '@mui/icons-material';

const drawerWidth = 240;

// Mock API service
const adminAPI = {
    getDashboard: async () => {
        await new Promise(resolve => setTimeout(resolve, 1000));
        return {
            total_users: 1250,
            active_users_24h: 89,
            total_channels: 456,
            total_payments: 15420.50,
            revenue_30d: 4280.75,
            api_requests_24h: 12450,
            system_uptime: "15d 4h 23m",
            version: "2.6.0"
        };
    },
    
    getUsers: async (/* filters = {} */) => {
        await new Promise(resolve => setTimeout(resolve, 800));
        return [
            {
                id: "1",
                username: "john_doe",
                email: "john@example.com",
                role: "user",
                status: "active",
                created_at: new Date('2024-07-25'),
                last_login: new Date('2025-08-26T08:00:00Z'),
                is_mfa_enabled: true,
                failed_login_attempts: 0
            },
            {
                id: "2",
                username: "jane_smith",
                email: "jane@example.com",
                role: "analyst",
                status: "active",
                created_at: new Date('2024-08-10'),
                last_login: new Date('2025-08-26T02:00:00Z'),
                is_mfa_enabled: false,
                failed_login_attempts: 1
            },
            {
                id: "3",
                username: "admin_user",
                email: "admin@example.com",
                role: "admin",
                status: "active",
                created_at: new Date('2024-06-01'),
                last_login: new Date('2025-08-26T10:00:00Z'),
                is_mfa_enabled: true,
                failed_login_attempts: 0
            }
        ];
    },

    getPaymentSummary: async () => {
        await new Promise(resolve => setTimeout(resolve, 600));
        return {
            total_revenue: 15420.50,
            revenue_this_month: 4280.75,
            revenue_last_month: 3850.25,
            active_subscriptions: 234,
            failed_payments: 12,
            refunds_count: 3,
            refunds_amount: 149.97
        };
    },

    getSystemHealth: async () => {
        await new Promise(resolve => setTimeout(resolve, 500));
        return {
            status: "healthy",
            services: {
                database: { status: "up", response_time: "12ms" },
                redis: { status: "up", response_time: "3ms" },
                api: { status: "up", requests_per_sec: 45.2 },
                bot: { status: "up", active_connections: 234 },
                payment_gateway: { status: "up", success_rate: "99.7%" }
            },
            resources: {
                cpu_usage: "23%",
                memory_usage: "67%",
                disk_usage: "45%"
            }
        };
    }
};

// Role and status display helpers
const getRoleColor = (role) => {
    const colors = {
        admin: 'error',
        moderator: 'warning',
        analyst: 'info',
        user: 'primary',
        readonly: 'secondary',
        guest: 'default'
    };
    return colors[role] || 'default';
};

const getStatusColor = (status) => {
    const colors = {
        active: 'success',
        inactive: 'default',
        suspended: 'warning',
        blocked: 'error',
        pending_verification: 'info'
    };
    return colors[status] || 'default';
};

// Dashboard Overview Component
const DashboardOverview = ({ stats, loading }) => {
    if (loading) return <LinearProgress />;
    
    return (
        <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
                <Card>
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box>
                                <Typography color="textSecondary" variant="body2">
                                    Total Users
                                </Typography>
                                <Typography variant="h4">
                                    {stats.total_users?.toLocaleString() || 0}
                                </Typography>
                            </Box>
                            <PeopleIcon color="primary" sx={{ fontSize: 40 }} />
                        </Box>
                        <Typography variant="body2" color="success.main">
                            +{stats.active_users_24h} active today
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
                <Card>
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box>
                                <Typography color="textSecondary" variant="body2">
                                    Total Revenue
                                </Typography>
                                <Typography variant="h4">
                                    ${stats.total_payments?.toFixed(2) || 0}
                                </Typography>
                            </Box>
                            <PaymentIcon color="success" sx={{ fontSize: 40 }} />
                        </Box>
                        <Typography variant="body2" color="success.main">
                            ${stats.revenue_30d?.toFixed(2)} this month
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
                <Card>
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box>
                                <Typography color="textSecondary" variant="body2">
                                    API Requests
                                </Typography>
                                <Typography variant="h4">
                                    {stats.api_requests_24h?.toLocaleString() || 0}
                                </Typography>
                            </Box>
                            <AnalyticsIcon color="info" sx={{ fontSize: 40 }} />
                        </Box>
                        <Typography variant="body2" color="textSecondary">
                            Last 24 hours
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
                <Card>
                    <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box>
                                <Typography color="textSecondary" variant="body2">
                                    System Uptime
                                </Typography>
                                <Typography variant="h4">
                                    {stats.system_uptime || "N/A"}
                                </Typography>
                            </Box>
                            <CheckCircleIcon color="success" sx={{ fontSize: 40 }} />
                        </Box>
                        <Typography variant="body2" color="success.main">
                            Version {stats.version}
                        </Typography>
                    </CardContent>
                </Card>
            </Grid>
        </Grid>
    );
};

// System Health Component
const SystemHealth = ({ health, loading }) => {
    if (loading) return <LinearProgress />;
    
    return (
        <Card sx={{ mt: 3 }}>
            <CardHeader 
                title="System Health" 
                avatar={<SecurityIcon color="primary" />}
                action={
                    <Chip 
                        label={health.status || "unknown"} 
                        color={health.status === "healthy" ? "success" : "error"}
                        size="small"
                    />
                }
            />
            <CardContent>
                <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                        <Typography variant="h6" gutterBottom>Services</Typography>
                        {Object.entries(health.services || {}).map(([service, info]) => (
                            <Box key={service} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Typography variant="body2">{service.replace('_', ' ')}</Typography>
                                <Box sx={{ display: 'flex', gap: 1 }}>
                                    <Chip 
                                        label={info.status} 
                                        color={info.status === 'up' ? 'success' : 'error'} 
                                        size="small"
                                    />
                                    <Typography variant="body2" color="textSecondary">
                                        {info.response_time || info.requests_per_sec || info.active_connections || info.success_rate}
                                    </Typography>
                                </Box>
                            </Box>
                        ))}
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Typography variant="h6" gutterBottom>Resources</Typography>
                        {Object.entries(health.resources || {}).map(([resource, usage]) => (
                            <Box key={resource} sx={{ mb: 1 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <Typography variant="body2">{resource.replace('_', ' ')}</Typography>
                                    <Typography variant="body2" color="textSecondary">{usage}</Typography>
                                </Box>
                                <LinearProgress 
                                    variant="determinate" 
                                    value={parseInt(usage) || 0} 
                                    color={parseInt(usage) > 80 ? 'error' : parseInt(usage) > 60 ? 'warning' : 'primary'}
                                />
                            </Box>
                        ))}
                    </Grid>
                </Grid>
            </CardContent>
        </Card>
    );
};

// User Management Component
const UserManagement = ({ users, loading, onRefresh }) => {
    const [roleFilter, setRoleFilter] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    
    const filteredUsers = users.filter(user => {
        const matchesRole = !roleFilter || user.role === roleFilter;
        const matchesStatus = !statusFilter || user.status === statusFilter;
        const matchesSearch = !searchTerm || 
            user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
            user.email.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesRole && matchesStatus && matchesSearch;
    });
    
    return (
        <Card>
            <CardHeader 
                title="User Management" 
                avatar={<PeopleIcon color="primary" />}
                action={
                    <Button onClick={onRefresh} startIcon={<RefreshIcon />}>
                        Refresh
                    </Button>
                }
            />
            <CardContent>
                <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <TextField
                        placeholder="Search users..."
                        size="small"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        InputProps={{
                            startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />
                        }}
                    />
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Role</InputLabel>
                        <Select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
                            <MenuItem value="">All Roles</MenuItem>
                            <MenuItem value="admin">Admin</MenuItem>
                            <MenuItem value="moderator">Moderator</MenuItem>
                            <MenuItem value="analyst">Analyst</MenuItem>
                            <MenuItem value="user">User</MenuItem>
                            <MenuItem value="readonly">ReadOnly</MenuItem>
                            <MenuItem value="guest">Guest</MenuItem>
                        </Select>
                    </FormControl>
                    <FormControl size="small" sx={{ minWidth: 120 }}>
                        <InputLabel>Status</InputLabel>
                        <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                            <MenuItem value="">All Status</MenuItem>
                            <MenuItem value="active">Active</MenuItem>
                            <MenuItem value="inactive">Inactive</MenuItem>
                            <MenuItem value="suspended">Suspended</MenuItem>
                            <MenuItem value="blocked">Blocked</MenuItem>
                        </Select>
                    </FormControl>
                </Box>

                {loading ? (
                    <LinearProgress />
                ) : (
                    <TableContainer>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>User</TableCell>
                                    <TableCell>Role</TableCell>
                                    <TableCell>Status</TableCell>
                                    <TableCell>Last Login</TableCell>
                                    <TableCell>MFA</TableCell>
                                    <TableCell>Failed Attempts</TableCell>
                                    <TableCell>Actions</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {filteredUsers.map((user) => (
                                    <TableRow key={user.id}>
                                        <TableCell>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                                                <Avatar sx={{ width: 32, height: 32 }}>
                                                    {user.username[0].toUpperCase()}
                                                </Avatar>
                                                <Box>
                                                    <Typography variant="body2" fontWeight="medium">
                                                        {user.username}
                                                    </Typography>
                                                    <Typography variant="body2" color="textSecondary">
                                                        {user.email}
                                                    </Typography>
                                                </Box>
                                            </Box>
                                        </TableCell>
                                        <TableCell>
                                            <Chip 
                                                label={user.role} 
                                                color={getRoleColor(user.role)} 
                                                size="small"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Chip 
                                                label={user.status} 
                                                color={getStatusColor(user.status)} 
                                                size="small"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Typography variant="body2">
                                                {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
                                            </Typography>
                                        </TableCell>
                                        <TableCell>
                                            <Chip 
                                                label={user.is_mfa_enabled ? "Enabled" : "Disabled"} 
                                                color={user.is_mfa_enabled ? "success" : "default"} 
                                                size="small"
                                            />
                                        </TableCell>
                                        <TableCell>
                                            <Typography variant="body2" color={user.failed_login_attempts > 0 ? "error" : "inherit"}>
                                                {user.failed_login_attempts}
                                            </Typography>
                                        </TableCell>
                                        <TableCell>
                                            <Box sx={{ display: 'flex', gap: 1 }}>
                                                <Tooltip title="View Details">
                                                    <IconButton size="small">
                                                        <ViewIcon />
                                                    </IconButton>
                                                </Tooltip>
                                                <Tooltip title="Edit User">
                                                    <IconButton size="small">
                                                        <EditIcon />
                                                    </IconButton>
                                                </Tooltip>
                                                <Tooltip title="Block User">
                                                    <IconButton size="small" color="error">
                                                        <BlockIcon />
                                                    </IconButton>
                                                </Tooltip>
                                            </Box>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                )}
                
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="textSecondary">
                        Showing {filteredUsers.length} of {users.length} users
                    </Typography>
                    <Button startIcon={<ExportIcon />} size="small">
                        Export Data
                    </Button>
                </Box>
            </CardContent>
        </Card>
    );
};

// Main SuperAdmin Panel Component
const SuperAdminPanel = () => {
    const [currentTab, setCurrentTab] = useState(0);
    const [mobileOpen, setMobileOpen] = useState(false);
    const [dashboardStats, setDashboardStats] = useState({});
    const [users, setUsers] = useState([]);
    const [_paymentSummary, setPaymentSummary] = useState({});
    const [systemHealth, setSystemHealth] = useState({});
    const [loading, setLoading] = useState({
        dashboard: false,
        users: false,
        payments: false,
        health: false
    });

    const menuItems = [
        { label: 'Dashboard', icon: <DashboardIcon />, value: 0 },
        { label: 'Users', icon: <PeopleIcon />, value: 1 },
        { label: 'Payments', icon: <PaymentIcon />, value: 2 },
        { label: 'System Health', icon: <SecurityIcon />, value: 3 },
        { label: 'Settings', icon: <SettingsIcon />, value: 4 }
    ];

    const handleDrawerToggle = () => {
        setMobileOpen(!mobileOpen);
    };

    const loadDashboard = async () => {
        setLoading(prev => ({ ...prev, dashboard: true }));
        try {
            const stats = await adminAPI.getDashboard();
            setDashboardStats(stats);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        } finally {
            setLoading(prev => ({ ...prev, dashboard: false }));
        }
    };

    const loadUsers = async () => {
        setLoading(prev => ({ ...prev, users: true }));
        try {
            const userData = await adminAPI.getUsers();
            setUsers(userData);
        } catch (error) {
            console.error('Failed to load users:', error);
        } finally {
            setLoading(prev => ({ ...prev, users: false }));
        }
    };

    const loadPayments = async () => {
        setLoading(prev => ({ ...prev, payments: true }));
        try {
            const payments = await adminAPI.getPaymentSummary();
            setPaymentSummary(payments);
        } catch (error) {
            console.error('Failed to load payments:', error);
        } finally {
            setLoading(prev => ({ ...prev, payments: false }));
        }
    };

    const loadSystemHealth = async () => {
        setLoading(prev => ({ ...prev, health: true }));
        try {
            const health = await adminAPI.getSystemHealth();
            setSystemHealth(health);
        } catch (error) {
            console.error('Failed to load system health:', error);
        } finally {
            setLoading(prev => ({ ...prev, health: false }));
        }
    };

    useEffect(() => {
        loadDashboard();
        loadUsers();
        loadPayments();
        loadSystemHealth();
    }, []);

    const drawer = (
        <div>
            <Toolbar>
                <Typography variant="h6" noWrap component="div">
                    SuperAdmin
                </Typography>
            </Toolbar>
            <Divider />
            <List>
                {menuItems.map((item) => (
                    <ListItem 
                        button 
                        key={item.value}
                        selected={currentTab === item.value}
                        onClick={() => setCurrentTab(item.value)}
                    >
                        <ListItemIcon>{item.icon}</ListItemIcon>
                        <ListItemText primary={item.label} />
                    </ListItem>
                ))}
            </List>
            <Divider />
            <List>
                <ListItem button>
                    <ListItemIcon><LogoutIcon /></ListItemIcon>
                    <ListItemText primary="Logout" />
                </ListItem>
            </List>
        </div>
    );

    const renderTabContent = () => {
        switch (currentTab) {
            case 0:
                return (
                    <Box>
                        <DashboardOverview stats={dashboardStats} loading={loading.dashboard} />
                        <SystemHealth health={systemHealth} loading={loading.health} />
                    </Box>
                );
            case 1:
                return (
                    <UserManagement 
                        users={users} 
                        loading={loading.users} 
                        onRefresh={loadUsers}
                    />
                );
            case 2:
                return (
                    <Card>
                        <CardHeader title="Payment Management" avatar={<PaymentIcon />} />
                        <CardContent>
                            <Typography>Payment management features coming soon...</Typography>
                        </CardContent>
                    </Card>
                );
            case 3:
                return (
                    <SystemHealth health={systemHealth} loading={loading.health} />
                );
            case 4:
                return (
                    <Card>
                        <CardHeader title="System Settings" avatar={<SettingsIcon />} />
                        <CardContent>
                            <Typography>System configuration panel coming soon...</Typography>
                        </CardContent>
                    </Card>
                );
            default:
                return null;
        }
    };

    return (
        <Box sx={{ display: 'flex' }}>
            <AppBar
                position="fixed"
                sx={{
                    width: { sm: `calc(100% - ${drawerWidth}px)` },
                    ml: { sm: `${drawerWidth}px` },
                }}
            >
                <Toolbar>
                    <IconButton
                        color="inherit"
                        edge="start"
                        onClick={handleDrawerToggle}
                        sx={{ mr: 2, display: { sm: 'none' } }}
                    >
                        <MenuIcon />
                    </IconButton>
                    <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                        AnalyticBot SuperAdmin Panel
                    </Typography>
                    <Badge badgeContent={4} color="error">
                        <NotificationsIcon />
                    </Badge>
                </Toolbar>
            </AppBar>
            <Box
                component="nav"
                sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
            >
                <Drawer
                    variant="temporary"
                    open={mobileOpen}
                    onClose={handleDrawerToggle}
                    ModalProps={{
                        keepMounted: true,
                    }}
                    sx={{
                        display: { xs: 'block', sm: 'none' },
                        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                    }}
                >
                    {drawer}
                </Drawer>
                <Drawer
                    variant="permanent"
                    sx={{
                        display: { xs: 'none', sm: 'block' },
                        '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
                    }}
                    open
                >
                    {drawer}
                </Drawer>
            </Box>
            <Box
                component="main"
                sx={{ flexGrow: 1, p: 3, width: { sm: `calc(100% - ${drawerWidth}px)` } }}
            >
                <Toolbar />
                {renderTabContent()}
            </Box>
        </Box>
    );
};

export default SuperAdminPanel;
