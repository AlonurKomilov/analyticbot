import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    Grid,
    Chip,
    Alert,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Tabs,
    Tab,
    Badge,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Switch,
    FormControlLabel
} from '@mui/material';
import {
    Security as SecurityIcon,
    Warning as WarningIcon,
    CheckCircle as SafeIcon,
    Error as CriticalIcon,
    Shield as ShieldIcon,
    Settings as SettingsIcon,
    Notifications as NotificationsIcon
} from '@mui/icons-material';

import { useUIStore } from '../stores';

// Mock data will be imported dynamically only in demo mode
// Removed top-level imports to prevent loading in real API mode

interface SecurityAlert {
    id: number | string;
    type: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    timestamp: string;
    source: string;
    action?: string;
    description: string;
}

interface SecurityMetric {
    metric: string;
    score?: number;
    value?: string;
    status: 'excellent' | 'good' | 'needs-attention' | 'poor';
}

interface ActiveMonitor {
    name: string;
    status: 'active' | 'maintenance' | 'offline';
    lastUpdate: string;
}

interface TabPanelProps {
    children: React.ReactNode;
    value: number;
    index: number;
}

type SeverityLevel = 'critical' | 'high' | 'medium' | 'low';
type MonitorStatus = 'active' | 'maintenance' | 'offline';
type ScoreStatus = 'excellent' | 'good' | 'needs-attention' | 'poor';

/**
 * Security Monitoring Service Page
 * Real-time security analysis and threat detection
 */
const SecurityMonitoringService: React.FC = () => {
    const dataSource = useUIStore((state) => state.dataSource);
    const [currentTab, setCurrentTab] = useState<number>(0);
    const [realTimeMonitoring, setRealTimeMonitoring] = useState<boolean>(true);
    const [threats, setThreats] = useState<SecurityAlert[]>([]);
    const [serviceStats, setServiceStats] = useState<any>({
        status: 'loading',
        threatsBlocked: 0,
        activeMonitors: 0,
        securityScore: 0
    });
    const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
    const [metrics, setMetrics] = useState<SecurityMetric[]>([]);

    const activeMonitors: ActiveMonitor[] = [
        { name: 'Brute Force Detection', status: 'active', lastUpdate: '30s ago' },
        { name: 'SQL Injection Scanner', status: 'active', lastUpdate: '45s ago' },
        { name: 'DDoS Protection', status: 'active', lastUpdate: '1m ago' },
        { name: 'Malware Scanner', status: 'active', lastUpdate: '2m ago' },
        { name: 'Anomaly Detection', status: 'active', lastUpdate: '3m ago' },
        { name: 'Data Leak Monitor', status: 'maintenance', lastUpdate: '5m ago' }
    ];

    // Load service data based on data source
    useEffect(() => {
        const loadSecurityData = async () => {
            try {
                if (dataSource === 'mock') {
                    // Dynamic import in demo mode only
                    const {
                        securityStats,
                        mockSecurityAlerts,
                        securityMetrics
                    } = await import('../__mocks__/aiServices/securityMonitor');
                    
                    setServiceStats(securityStats);
                    setAlerts(mockSecurityAlerts as any);
                    setMetrics(securityMetrics as any);
                } else {
                    // Real API mode - fetch live security data
                    // TODO: Implement real API call when security monitoring endpoint is ready
                    console.log('Real security monitoring API not yet implemented');
                }
            } catch (err) {
                console.error('Failed to load security data:', err);
            }
        };

        loadSecurityData();
    }, [dataSource]);

    useEffect(() => {
        // Simulate real-time threat updates
        const interval = setInterval(() => {
            if (realTimeMonitoring && Math.random() > 0.8) {
                const newThreat: SecurityAlert = {
                    id: Date.now(),
                    type: 'System Scan',
                    severity: 'low',
                    timestamp: 'Just now',
                    source: 'Auto Scanner',
                    action: 'Monitored',
                    description: 'Routine security check completed'
                };
                setThreats(prev => [newThreat, ...prev.slice(0, 4)]);
            }
        }, 10000);

        return () => clearInterval(interval);
    }, [realTimeMonitoring]);

    const getSeverityColor = (severity: SeverityLevel): 'error' | 'warning' | 'info' | 'success' | 'default' => {
        switch (severity) {
            case 'critical': return 'error';
            case 'high': return 'warning';
            case 'medium': return 'info';
            case 'low': return 'success';
            default: return 'default';
        }
    };

    const getSeverityIcon = (severity: SeverityLevel): React.ReactNode => {
        switch (severity) {
            case 'critical': return <CriticalIcon color="error" />;
            case 'high': return <WarningIcon color="warning" />;
            case 'medium': return <NotificationsIcon color="info" />;
            case 'low': return <SafeIcon color="success" />;
            default: return <SafeIcon />;
        }
    };

    const getScoreColor = (status: ScoreStatus): string => {
        switch (status) {
            case 'excellent': return 'success.main';
            case 'good': return 'info.main';
            case 'needs-attention': return 'warning.main';
            case 'poor': return 'error.main';
            default: return 'text.secondary';
        }
    };

    const getMonitorIcon = (status: MonitorStatus): React.ReactNode => {
        switch (status) {
            case 'active': return <SafeIcon color="success" />;
            case 'maintenance': return <WarningIcon color="warning" />;
            case 'offline': return <CriticalIcon color="error" />;
            default: return <SafeIcon />;
        }
    };

    const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
        <div hidden={value !== index}>
            {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
        </div>
    );

    return (
        <Box>
            {/* Service Header */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <SecurityIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                    <Typography variant="h4" component="h1" fontWeight={600}>
                        Security Monitoring
                    </Typography>
                    <Chip
                        label="Active"
                        color="success"
                        variant="filled"
                        sx={{ ml: 'auto' }}
                    />
                </Box>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                    Real-time security analysis and threat detection for comprehensive platform protection
                </Typography>

                {/* Quick Stats */}
                <Grid container spacing={3}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="success.main" fontWeight={600}>
                                {serviceStats.threatsBlocked}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Threats Blocked
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="primary.main" fontWeight={600}>
                                {serviceStats.securityScore}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Security Score
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="info.main" fontWeight={600}>
                                {activeMonitors.filter(m => m.status === 'active').length}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Active Monitors
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2, bgcolor: realTimeMonitoring ? 'success.light' : 'grey.100' }}>
                            <Badge
                                variant="dot"
                                color={realTimeMonitoring ? 'success' : 'default'}
                                sx={{
                                    '& .MuiBadge-badge': {
                                        right: '50%',
                                        top: 8,
                                        animation: realTimeMonitoring ? 'pulse 2s infinite' : 'none'
                                    },
                                    '@keyframes pulse': {
                                        '0%': { opacity: 1 },
                                        '50%': { opacity: 0.5 },
                                        '100%': { opacity: 1 }
                                    }
                                }}
                            >
                                <ShieldIcon
                                    sx={{
                                        fontSize: 40,
                                        color: realTimeMonitoring ? 'success.main' : 'grey.500',
                                        mb: 1
                                    }}
                                />
                            </Badge>
                            <Typography variant="body2" color="text.secondary">
                                {realTimeMonitoring ? 'Monitoring Active' : 'Monitoring Paused'}
                            </Typography>
                        </Card>
                    </Grid>
                </Grid>
            </Box>

            {/* Service Tabs */}
            <Card>
                <Tabs
                    value={currentTab}
                    onChange={(_e, newValue: number) => setCurrentTab(newValue)}
                    sx={{ borderBottom: 1, borderColor: 'divider' }}
                >
                    <Tab
                        label={
                            <Badge badgeContent={alerts.length} color="error">
                                Threat Alerts
                            </Badge>
                        }
                        icon={<WarningIcon />}
                    />
                    <Tab label="Security Metrics" icon={<ShieldIcon />} />
                    <Tab label="Active Monitors" icon={<NotificationsIcon />} />
                    <Tab label="Settings" icon={<SettingsIcon />} />
                </Tabs>

                {/* Threat Alerts Tab */}
                <TabPanel value={currentTab} index={0}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 3 }}>
                            Recent Security Alerts
                        </Typography>

                        {alerts.length === 0 ? (
                            <Alert severity="success">
                                No security threats detected. Your system is secure.
                            </Alert>
                        ) : (
                            <List>
                                {[...alerts, ...threats].map((alert) => (
                                    <ListItem
                                        key={alert.id}
                                        sx={{
                                            border: 1,
                                            borderColor: 'divider',
                                            borderRadius: 2,
                                            mb: 2,
                                            borderLeftColor: getSeverityColor(alert.severity) + '.main',
                                            borderLeftWidth: 4
                                        }}
                                    >
                                        <ListItemIcon>
                                            {getSeverityIcon(alert.severity)}
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    <Typography variant="subtitle1" fontWeight={600}>
                                                        {alert.type}
                                                    </Typography>
                                                    <Chip
                                                        label={alert.severity.toUpperCase()}
                                                        color={getSeverityColor(alert.severity)}
                                                        size="small"
                                                    />
                                                    {alert.action && (
                                                        <Chip
                                                            label={alert.action}
                                                            variant="outlined"
                                                            size="small"
                                                        />
                                                    )}
                                                </Box>
                                            }
                                            secondary={
                                                <Box sx={{ mt: 1 }}>
                                                    <Typography variant="body2" color="text.secondary">
                                                        {alert.description}
                                                    </Typography>
                                                    <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                                                        Source: {alert.source} • {alert.timestamp}
                                                    </Typography>
                                                </Box>
                                            }
                                        />
                                    </ListItem>
                                ))}
                            </List>
                        )}
                    </CardContent>
                </TabPanel>

                {/* Security Metrics Tab */}
                <TabPanel value={currentTab} index={1}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 3 }}>
                            Security Score Breakdown
                        </Typography>

                        <TableContainer component={Paper} variant="outlined">
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell><strong>Security Area</strong></TableCell>
                                        <TableCell><strong>Score</strong></TableCell>
                                        <TableCell><strong>Status</strong></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {metrics.map((metric, index) => (
                                        <TableRow key={index}>
                                            <TableCell>{metric.metric}</TableCell>
                                            <TableCell>
                                                <Typography
                                                    variant="h6"
                                                    sx={{ color: getScoreColor(metric.status) }}
                                                >
                                                    {metric.score || metric.value || 'N/A'}
                                                </Typography>
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={metric.status.replace('-', ' ')}
                                                    color={
                                                        metric.status === 'excellent' ? 'success' :
                                                        metric.status === 'good' ? 'info' :
                                                        metric.status === 'needs-attention' ? 'warning' : 'error'
                                                    }
                                                    size="small"
                                                />
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </CardContent>
                </TabPanel>

                {/* Active Monitors Tab */}
                <TabPanel value={currentTab} index={2}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 3 }}>
                            Security Monitor Status
                        </Typography>

                        <List>
                            {activeMonitors.map((monitor, index) => (
                                <ListItem
                                    key={index}
                                    sx={{
                                        border: 1,
                                        borderColor: 'divider',
                                        borderRadius: 1,
                                        mb: 1
                                    }}
                                >
                                    <ListItemIcon>
                                        {getMonitorIcon(monitor.status)}
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={monitor.name}
                                        secondary={`Last update: ${monitor.lastUpdate}`}
                                    />
                                    <Chip
                                        label={monitor.status}
                                        color={
                                            monitor.status === 'active' ? 'success' :
                                            monitor.status === 'maintenance' ? 'warning' : 'error'
                                        }
                                        size="small"
                                        variant="outlined"
                                    />
                                </ListItem>
                            ))}
                        </List>
                    </CardContent>
                </TabPanel>

                {/* Settings Tab */}
                <TabPanel value={currentTab} index={3}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 3 }}>
                            Security Monitoring Settings
                        </Typography>

                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={realTimeMonitoring}
                                        onChange={(e) => setRealTimeMonitoring(e.target.checked)}
                                    />
                                }
                                label="Real-time Threat Monitoring"
                            />

                            <FormControlLabel
                                control={<Switch defaultChecked />}
                                label="Email Alert Notifications"
                            />

                            <FormControlLabel
                                control={<Switch defaultChecked />}
                                label="Auto-block Suspicious IPs"
                            />

                            <FormControlLabel
                                control={<Switch />}
                                label="Advanced Threat Detection"
                            />

                            <FormControlLabel
                                control={<Switch defaultChecked />}
                                label="Security Audit Logging"
                            />
                        </Box>
                    </CardContent>
                </TabPanel>
            </Card>
        </Box>
    );
};

export default SecurityMonitoringService;
