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
    NavigateNext as NavigateNextIcon,
    Security as SecurityIcon
} from '@mui/icons-material';

// Import our chart components
import PostViewDynamicsChart from './charts/PostViewDynamics';
import TopPostsTable from './TopPostsTable';
import EnhancedTopPostsTable from './EnhancedTopPostsTable';
import BestTimeRecommender from './BestTimeRecommender';
import DataSourceSettings from './DataSourceSettings';
import ExportButton from './common/ExportButton';
import ShareButton from './common/ShareButton';
import AdvancedAnalyticsDashboard from './analytics/AdvancedAnalyticsDashboard';
import RealTimeAlertsSystem from './analytics/RealTimeAlertsSystem';
import ContentProtectionDashboard from './content/ContentProtectionDashboard';
import { useAppStore } from '../store/appStore';

// Tab Panel Component with improved accessibility
const TabPanel = ({ children, value, index, ...other }) => (
    <section
        role="tabpanel"
        hidden={value !== index}
        id={`analytics-tabpanel-${index}`}
        aria-labelledby={`analytics-tab-${index}`}
        aria-hidden={value !== index}
        tabIndex={value === index ? 0 : -1}
        {...other}
    >
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </section>
);

const AnalyticsDashboard = () => {
    const [activeTab, setActiveTab] = useState(0);
    const [lastUpdated, setLastUpdated] = useState(new Date());
    const [isLoading, setIsLoading] = useState(false);
    const [showSettings, setShowSettings] = useState(false);
    
    // Channel configuration
    const channelId = 'demo_channel'; // Default channel for analytics
    
    // Store integration
    const { dataSource, setDataSource, fetchData, isUsingRealAPI, clearAnalyticsData } = useAppStore();

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
            
            // Clear analytics cache to force components to reload with new data source
            clearAnalyticsData();
            
            setLastUpdated(new Date());
            
            // Force refresh of analytics data with new source
            setTimeout(() => {
                window.dispatchEvent(new CustomEvent('dataSourceChanged', { 
                    detail: { source: newSource } 
                }));
            }, 100);
            
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
        { icon: <RefreshIcon />, name: 'Refresh', action: handleRefresh },
        { icon: <DownloadIcon />, name: 'Export', action: () => console.log('Export') },
        { icon: <ShareIcon />, name: 'Share', action: () => console.log('Share') },
        { icon: <PrintIcon />, name: 'Print', action: () => console.log('Print') },
        { icon: <SettingsIcon />, name: 'Settings', action: () => setShowSettings(!showSettings) }
    ];

    return (
        <Container maxWidth="xl" sx={{ py: 3 }}>
            {/* Breadcrumbs */}
            <nav aria-label="Breadcrumb navigation">
                <Breadcrumbs 
                    separator={<NavigateNextIcon fontSize="small" aria-hidden="true" />} 
                    sx={{ mb: 2 }}
                >
                    <Link 
                        underline="hover" 
                        color="inherit" 
                        href="/"
                        sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                        aria-label="Go to homepage"
                    >
                        <HomeIcon fontSize="small" aria-hidden="true" />
                        Home
                    </Link>
                    <Typography color="text.primary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <AnalyticsIcon fontSize="small" aria-hidden="true" />
                            Analytics Dashboard
                        </Typography>
                    </Breadcrumbs>
                </nav>

                {/* Header */}
                <header>
                    <Paper sx={{ p: 3, mb: 3, background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Box>
                                <Typography variant="h1" sx={{ mb: 1, fontWeight: 'bold', fontSize: '2rem' }}>
                                    <span aria-hidden="true">📊</span> Analytics & Content Protection
                                </Typography>
                                <Typography variant="subtitle1" sx={{ opacity: 0.9 }}>
                                    Complete analysis with Week 5-6 content protection features
                                </Typography>
                            </Box>                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Card sx={{ bgcolor: 'rgba(255,255,255,0.1)', color: 'white' }}>
                                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                                        Last Updated
                                    </Typography>
                                    <Typography variant="body2" fontWeight="bold">
                                        <time dateTime={lastUpdated.toISOString()}>
                                            {lastUpdated.toLocaleTimeString()}
                                        </time>
                                    </Typography>
                                </CardContent>
                            </Card>
                            
                            {/* Quick Actions - Export & Share */}
                            <Box sx={{ display: 'flex', gap: 1 }}>
                                <ExportButton 
                                    channelId="demo_channel"
                                    dataType="engagement"
                                    period="7d"
                                    size="small"
                                    sx={{ 
                                        bgcolor: 'rgba(255,255,255,0.2)', 
                                        color: 'white',
                                        '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' }
                                    }}
                                />
                                <ShareButton 
                                    channelId="demo_channel"
                                    dataType="engagement"
                                    size="small"
                                    sx={{ 
                                        bgcolor: 'rgba(255,255,255,0.2)', 
                                        color: 'white',
                                        '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' }
                                    }}
                                />
                            </Box>
                            
                            <Chip 
                                icon={<TrendingIcon aria-hidden="true" />} 
                                label={isUsingRealAPI() ? "Live API" : "Demo Data"} 
                                color="primary" 
                                sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
                            />
                            
                            <IconButton
                                onClick={() => setShowSettings(!showSettings)}
                                sx={{ color: 'white' }}
                                aria-label={showSettings ? "Hide data source settings" : "Show data source settings"}
                                aria-expanded={showSettings}
                                aria-controls="data-source-settings"
                            >
                                {showSettings ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                            </IconButton>
                        </Box>
                    </Box>
                </Paper>
            </header>

            {/* Live region for announcements */}
            <div aria-live="polite" aria-atomic="true" className="sr-only">
                {isLoading && "Loading analytics data..."}
                {!isLoading && "Analytics data loaded"}
            </div>

            {/* Data Source Settings - Collapsible */}
            <Collapse in={showSettings}>
                <div id="data-source-settings">
                    <DataSourceSettings onDataSourceChange={handleDataSourceChange} />
                </div>
            </Collapse>

            {/* Alert for Current Status */}
            <Alert 
                severity="success" 
                sx={{ mb: 3 }}
                icon={<SecurityIcon />}
                role="status"
            >
                <strong>🛡️ NEW: Week 5-6 Content Protection Available!</strong> Click the "Content Protection" tab below to access watermarking and theft detection tools. 
                Premium features include image watermarking, content scanning, and security tools.
            </Alert>

            {/* Main Tabs */}
            <nav aria-label="Analytics navigation">
                <Paper sx={{ mb: 3 }}>
                    <Tabs
                        value={activeTab}
                        onChange={handleTabChange}
                        sx={{ 
                            borderBottom: 1, 
                            borderColor: 'divider',
                            '& .MuiTab-root': { 
                                minHeight: 64,
                                '&:focus-visible': {
                                    outline: '2px solid #2196F3',
                                    outlineOffset: '2px'
                                }
                            }
                        }}
                        variant="fullWidth"
                        aria-label="Analytics sections"
                    >
                        <Tab 
                            icon={<TrendingIcon />} 
                            label="Post Dynamics" 
                            sx={{ fontSize: '0.9rem', fontWeight: 'bold' }}
                            id="analytics-tab-0"
                            aria-controls="analytics-tabpanel-0"
                        />
                        <Tab 
                            icon={<DashboardIcon />} 
                            label="Top Posts" 
                            sx={{ fontSize: '0.9rem', fontWeight: 'bold' }}
                            id="analytics-tab-1"
                            aria-controls="analytics-tabpanel-1"
                        />
                        <Tab 
                            icon={<ScheduleIcon />} 
                            label="AI Time Recommendations" 
                            sx={{ fontSize: '0.9rem', fontWeight: 'bold' }}
                            id="analytics-tab-2"
                            aria-controls="analytics-tabpanel-2"
                        />
                        <Tab 
                            icon={<AnalyticsIcon />} 
                            label="Advanced Analytics" 
                            sx={{ fontSize: '0.9rem', fontWeight: 'bold' }}
                            id="analytics-tab-3"
                            aria-controls="analytics-tabpanel-3"
                        />
                        <Tab 
                            icon={<SecurityIcon />} 
                            label="🛡️ Content Protection" 
                            sx={{ fontSize: '0.9rem', fontWeight: 'bold', color: 'primary.main' }}
                            id="analytics-tab-4"
                            aria-controls="analytics-tabpanel-4"
                        />
                    </Tabs>
                </Paper>
            </nav>

            {/* TabPanels with proper ARIA */}
            <main role="main">
                <TabPanel 
                    value={activeTab} 
                    index={0}
                    id="analytics-tabpanel-0"
                    aria-labelledby="analytics-tab-0"
                >
                    {/* Summary Stats Row */}
                    <Grid container spacing={3} sx={{ mb: 3 }}>
                        <Grid item xs={12} md={3}>
                            <Card sx={{ textAlign: 'center', height: '100%' }}>
                                <CardContent>
                                    <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                                        248
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Total Posts Analyzed
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={3}>
                            <Card sx={{ textAlign: 'center', height: '100%' }}>
                                <CardContent>
                                    <Typography variant="h4" color="success.main" sx={{ fontWeight: 'bold' }}>
                                        12.4K
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Average Views
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={3}>
                            <Card sx={{ textAlign: 'center', height: '100%' }}>
                                <CardContent>
                                    <Typography variant="h4" color="warning.main" sx={{ fontWeight: 'bold' }}>
                                        18.7%
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Engagement Rate
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item xs={12} md={3}>
                            <Card sx={{ textAlign: 'center', height: '100%' }}>
                                <CardContent>
                                    <Typography variant="h4" color="error.main" sx={{ fontWeight: 'bold' }}>
                                        2.1K
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Peak Views Today
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>

                    {/* Chart Component */}
                    <Paper sx={{ p: 3, mb: 3 }}>
                        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <TrendingIcon color="primary" />
                            Post View Dynamics - Last 30 Days
                        </Typography>
                        <PostViewDynamicsChart />
                    </Paper>

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
                                            <span aria-hidden="true">📊</span> Interactive Charts
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            • Real-time data visualization
                                            <br />• Performance trends analysis
                                            <br />• Custom date range selection
                                            <br />• Multiple chart types support
                                        </Typography>
                                    </CardContent>
                                </Card>
                            </Grid>

                            <Grid item xs={12} md={4}>
                                <Card variant="outlined" sx={{ height: '100%' }}>
                                    <CardContent>
                                        <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold', color: 'success.main' }}>
                                            <span aria-hidden="true">🏆</span> Advanced Analytics
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
                                            <span aria-hidden="true">🤖</span> AI Recommendations
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
                </TabPanel>

                <TabPanel 
                    value={activeTab} 
                    index={1}
                    id="analytics-tabpanel-1"
                    aria-labelledby="analytics-tab-1"
                >
                    <EnhancedTopPostsTable />
                </TabPanel>

                <TabPanel 
                    value={activeTab} 
                    index={2}
                    id="analytics-tabpanel-2"
                    aria-labelledby="analytics-tab-2"
                >
                    <BestTimeRecommender />
                </TabPanel>

                <TabPanel 
                    value={activeTab} 
                    index={3}
                    id="analytics-tabpanel-3"
                    aria-labelledby="analytics-tab-3"
                >
                    {/* Week 3-4 Advanced Analytics & Alerts */}
                    <RealTimeAlertsSystem channelId={channelId} />
                    <AdvancedAnalyticsDashboard channelId={channelId} />
                </TabPanel>

                <TabPanel 
                    value={activeTab} 
                    index={4}
                    id="analytics-tabpanel-4"
                    aria-labelledby="analytics-tab-4"
                >
                    {/* Week 5-6 Content Protection */}
                    <ContentProtectionDashboard />
                </TabPanel>
            </main>

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
                    role="status"
                    aria-live="polite"
                >
                    <Card sx={{ p: 3, textAlign: 'center' }}>
                        <RefreshIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2, animation: 'spin 1s linear infinite' }} />
                        <Typography variant="h6">
                            Loading analytics data...
                        </Typography>
                    </Card>
                </Box>
            )}

            {/* Custom CSS for animations */}
            <style>{`
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </Container>
    );
};

export default AnalyticsDashboard;
