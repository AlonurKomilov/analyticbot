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
    Chip,
    Alert,
    Fab,
    SpeedDial,
    SpeedDialAction,
    SpeedDialIcon,
    Breadcrumbs,
    Link,
    Collapse,
    IconButton
} from '@mui/material';
import {
    Dashboard as DashboardIcon,
    Analytics as AnalyticsIcon,
    Schedule as ScheduleIcon,
    TrendingUp as TrendingIcon,
    Refresh as RefreshIcon,
    Download as DownloadIcon,
    Settings as SettingsIcon,
    Share as ShareIcon,
    Print as PrintIcon,
    Home as HomeIcon,
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon,
    NavigateNext as NavigateNextIcon
} from '@mui/icons-material';

// Import our chart components
import PostViewDynamicsChart from './PostViewDynamicsChart';
import TopPostsTable from './TopPostsTable';
import BestTimeRecommender from './BestTimeRecommender';
import DataSourceSettings from './DataSourceSettings';
import { useAppStore } from '../store/appStore';

// Tab Panel Component
const TabPanel = ({ children, value, index, ...other }) => (
    <div
        role="tabpanel"
        hidden={value !== index}
        id={`analytics-tabpanel-${index}`}
        aria-labelledby={`analytics-tab-${index}`}
        {...other}
    >
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
);

const AnalyticsDashboard = () => {
    const [activeTab, setActiveTab] = useState(0);
    const [lastUpdated, setLastUpdated] = useState(new Date());
    const [isLoading, setIsLoading] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    
    // Store integration
    const { dataSource, setDataSource, fetchData, isUsingRealAPI } = useAppStore();

    // Auto-refresh functionality
    useEffect(() => {
        const interval = setInterval(() => {
            setLastUpdated(new Date());
        }, 60000); // Update every minute

        return () => clearInterval(interval);
    }, []);

    // Handle data source change
    const handleDataSourceChange = async (newSource) => {
        setDataSource(newSource);
        setIsLoading(true);
        
        try {
            await fetchData(newSource);
            setLastUpdated(new Date());
        } catch (error) {
            console.error('Error switching data source:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    const handleRefresh = async () => {
        setIsLoading(true);
        // Simulate refresh delay
        setTimeout(() => {
            setLastUpdated(new Date());
            setIsLoading(false);
        }, 1000);
    };

    const speedDialActions = [
        { icon: <RefreshIcon />, name: 'Yangilash', action: handleRefresh },
        { icon: <DownloadIcon />, name: 'Eksport', action: () => console.log('Export') },
        { icon: <ShareIcon />, name: 'Ulashish', action: () => console.log('Share') },
        { icon: <PrintIcon />, name: 'Chop etish', action: () => console.log('Print') },
        { icon: <SettingsIcon />, name: 'Sozlamalar', action: () => setShowSettings(!showSettings) }
    ];

    return (
        <Container maxWidth="xl" sx={{ py: 3 }}>
            {/* Breadcrumbs */}
            <Breadcrumbs 
                separator={<NavigateNextIcon fontSize="small" />} 
                sx={{ mb: 2 }}
            >
                <Link 
                    underline="hover" 
                    color="inherit" 
                    href="/"
                    sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                >
                    <HomeIcon fontSize="small" />
                    Bosh sahifa
                </Link>
                <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <AnalyticsIcon fontSize="small" />
                    Analytics Dashboard
                </Typography>
            </Breadcrumbs>

            {/* Header */}
            <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                        <Typography variant="h4" sx={{ mb: 1, fontWeight: 'bold' }}>
                            📊 Rich Analytics Dashboard
                        </Typography>
                        <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                            Telegram kanalining to'liq tahlili va AI tavsiyalari
                        </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Card sx={{ bgcolor: 'rgba(255,255,255,0.1)', color: 'white' }}>
                            <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                <Typography variant="caption" sx={{ opacity: 0.8 }}>
                                    So'ngi yangilash
                                </Typography>
                                <Typography variant="body2" fontWeight="bold">
                                    {lastUpdated.toLocaleTimeString()}
                                </Typography>
                            </CardContent>
                        </Card>
                        
                        <Chip 
                            icon={<TrendingIcon />} 
                            label={isUsingRealAPI() ? "Live API" : "Demo Data"} 
                            color="primary" 
                            sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                        />
                        
                        <IconButton
                            onClick={() => setShowSettings(!showSettings)}
                            sx={{ color: 'white' }}
                            title="Data Source Settings"
                        >
                            {showSettings ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                    </Box>
                </Box>
            </Paper>

            {/* Data Source Settings - Collapsible */}
            <Collapse in={showSettings}>
                <DataSourceSettings onDataSourceChange={handleDataSourceChange} />
            </Collapse>

            {/* Alert for Phase 2.1 Status */}
            <Alert 
                severity="info" 
                sx={{ mb: 3 }}
                icon={<AnalyticsIcon />}
            >
                <strong>Phase 2.1 - Week 2:</strong> Rich Analytics Dashboard va AI Best Time recommendations faol. 
                Barcha ma'lumotlar real-time rejimida yangilanmoqda.
            </Alert>

            {/* Main Tabs */}
            <Paper sx={{ mb: 3 }}>
                <Tabs
                    value={activeTab}
                    onChange={handleTabChange}
                    sx={{ 
                        borderBottom: 1, 
                        borderColor: 'divider',
                        '& .MuiTab-root': { minHeight: 64 }
                    }}
                    variant="fullWidth"
                >
                    <Tab 
                        icon={<TrendingIcon />} 
                        label="Post Dynamics" 
                        sx={{ fontSize: '0.9rem', fontWeight: 'bold' }}
                    />
                    <Tab 
                        icon={<DashboardIcon />} 
                        label="Top Posts" 
                        sx={{ fontSize: '0.9rem', fontWeight: 'bold' }}
                    />
                    <Tab 
                        icon={<ScheduleIcon />} 
                        label="AI Time Recommendations" 
                        sx={{ fontSize: '0.9rem', fontWeight: 'bold' }}
                    />
                </Tabs>

                {/* Tab Panels */}
                <TabPanel value={activeTab} index={0}>
                    <PostViewDynamicsChart />
                </TabPanel>

                <TabPanel value={activeTab} index={1}>
                    <TopPostsTable />
                </TabPanel>

                <TabPanel value={activeTab} index={2}>
                    <BestTimeRecommender />
                </TabPanel>
            </Paper>

            {/* Summary Stats Row */}
            <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <Card variant="outlined" sx={{ textAlign: 'center', py: 2 }}>
                        <CardContent>
                            <Typography variant="h4" color="primary" gutterBottom>
                                24/7
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Real-time Monitoring
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card variant="outlined" sx={{ textAlign: 'center', py: 2 }}>
                        <CardContent>
                            <Typography variant="h4" color="success.main" gutterBottom>
                                AI
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Machine Learning Predictions
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card variant="outlined" sx={{ textAlign: 'center', py: 2 }}>
                        <CardContent>
                            <Typography variant="h4" color="warning.main" gutterBottom>
                                📈
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Advanced Analytics
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Card variant="outlined" sx={{ textAlign: 'center', py: 2 }}>
                        <CardContent>
                            <Typography variant="h4" color="info.main" gutterBottom>
                                🎯
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Smart Recommendations
                            </Typography>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Phase 2.1 Features Showcase */}
            <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AnalyticsIcon color="primary" />
                    Phase 2.1 Week 2 - Key Features
                </Typography>
                
                <Grid container spacing={2}>
                    <Grid item xs={12} md={4}>
                        <Card variant="outlined" sx={{ height: '100%' }}>
                            <CardContent>
                                <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                                    📊 Interactive Charts
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    • Real-time post view dynamics
                                    <br />• Area charts with multiple metrics
                                    <br />• 24-hour heatmap visualization
                                    <br />• Auto-refresh capabilities
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} md={4}>
                        <Card variant="outlined" sx={{ height: '100%' }}>
                            <CardContent>
                                <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', color: 'success.main' }}>
                                    🏆 Top Posts Analysis
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    • Comprehensive posts ranking
                                    <br />• Engagement rate calculations
                                    <br />• Performance badges
                                    <br />• Detailed metrics table
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>

                    <Grid item xs={12} md={4}>
                        <Card variant="outlined" sx={{ height: '100%' }}>
                            <CardContent>
                                <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                                    🤖 AI Recommendations
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    • Machine learning time predictions
                                    <br />• Confidence-based scoring
                                    <br />• Weekly performance insights
                                    <br />• Smart posting schedule
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            </Paper>

            {/* Floating Action Button */}
            <SpeedDial
                ariaLabel="Analytics Actions"
                sx={{ position: 'fixed', bottom: 16, right: 16 }}
                icon={<SpeedDialIcon />}
                open={false}
            >
                {speedDialActions.map((action) => (
                    <SpeedDialAction
                        key={action.name}
                        icon={action.icon}
                        tooltipTitle={action.name}
                        onClick={action.action}
                    />
                ))}
            </SpeedDial>

            {/* Loading Overlay */}
            {isLoading && (
                <Box
                    sx={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        bgcolor: 'rgba(0,0,0,0.3)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 9999
                    }}
                >
                    <Card sx={{ p: 3, textAlign: 'center' }}>
                        <RefreshIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2, animation: 'spin 1s linear infinite' }} />
                        <Typography variant="h6">
                            Ma'lumotlar yangilanmoqda...
                        </Typography>
                    </Card>
                </Box>
            )}

            {/* Custom CSS for animations */}
            <style jsx>{`
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </Container>
    );
};

export default AnalyticsDashboard;
