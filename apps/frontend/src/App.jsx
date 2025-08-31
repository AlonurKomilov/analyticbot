import React, { useState } from 'react';
import { 
    Container, 
    Box, 
    Typography, 
    Skeleton, 
    Stack, 
    Tabs, 
    Tab, 
    Paper,
    Grid,
    Card,
    CardContent,
    Chip
} from '@mui/material';
import PostCreator from './components/PostCreator';
import ScheduledPostsList from './components/ScheduledPostsList';
import MediaPreview from './components/MediaPreview';
import AddChannel from './components/AddChannel';
import EnhancedMediaUploader from './components/EnhancedMediaUploader.jsx'; // NEW for Phase 2.1
import StorageFileBrowser from './components/StorageFileBrowser.jsx'; // NEW for Phase 2.1
import AnalyticsDashboard from './components/AnalyticsDashboard.jsx'; // NEW Week 2 Analytics
import { useAppStore } from './store/appStore.js';

const AppSkeleton = () => (
    <Stack spacing={3} sx={{ mt: 2 }}>
        {/* Header skeleton */}
        <Paper sx={{ p: 3, borderRadius: 2 }}>
            <Skeleton variant="text" width="60%" height={40} sx={{ mx: 'auto' }} />
            <Skeleton variant="text" width="40%" height={20} sx={{ mx: 'auto', mt: 1 }} />
            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', mt: 2 }}>
                {[...Array(5)].map((_, i) => (
                    <Skeleton key={i} variant="rounded" width={80} height={32} />
                ))}
            </Box>
        </Paper>
        
        {/* Tabs skeleton */}
        <Paper sx={{ borderRadius: 2 }}>
            <Box sx={{ display: 'flex', borderBottom: '1px solid #e0e0e0' }}>
                {[...Array(3)].map((_, i) => (
                    <Skeleton key={i} variant="rectangular" width="33.33%" height={64} />
                ))}
            </Box>
        </Paper>
        
        {/* Dashboard content skeleton */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 3 }}>
            {/* Main chart area */}
            <Paper sx={{ p: 3, borderRadius: 2 }}>
                <Skeleton variant="text" width="50%" height={30} />
                <Box sx={{ display: 'flex', gap: 2, mt: 2, mb: 3 }}>
                    {[...Array(4)].map((_, i) => (
                        <Skeleton key={i} variant="rounded" width={120} height={80} />
                    ))}
                </Box>
                <Skeleton variant="rectangular" width="100%" height={300} sx={{ borderRadius: 1 }} />
            </Paper>
            
            {/* Sidebar */}
            <Paper sx={{ p: 3, borderRadius: 2 }}>
                <Skeleton variant="text" width="70%" height={30} />
                <Stack spacing={2} sx={{ mt: 2 }}>
                    {[...Array(6)].map((_, i) => (
                        <Box key={i} sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                            <Skeleton variant="circular" width={40} height={40} />
                            <Box sx={{ flex: 1 }}>
                                <Skeleton variant="text" width="80%" />
                                <Skeleton variant="text" width="60%" />
                            </Box>
                            <Skeleton variant="rounded" width={50} height={24} />
                        </Box>
                    ))}
                </Stack>
            </Paper>
        </Box>
        
        {/* Bottom summary cards */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' }, gap: 2 }}>
            {[...Array(4)].map((_, i) => (
                <Paper key={i} sx={{ p: 2, borderRadius: 2 }}>
                    <Skeleton variant="text" width="60%" />
                    <Skeleton variant="text" width="40%" height={30} />
                    <Skeleton variant="rectangular" width="100%" height={4} sx={{ mt: 1, borderRadius: 2 }} />
                </Paper>
            ))}
        </Box>
    </Stack>
);

// Tab Panel Component
const TabPanel = ({ children, value, index, ...other }) => (
    <div
        role="tabpanel"
        hidden={value !== index}
        id={`main-tabpanel-${index}`}
        aria-labelledby={`main-tab-${index}`}
        {...other}
    >
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
);

function App() {
    const store = useAppStore();
    const [activeTab, setActiveTab] = useState(1); // Start with Analytics Dashboard
    const [isInitialized, setIsInitialized] = useState(false);

    // Initialize app data when component mounts
    React.useEffect(() => {
        const initializeApp = async () => {
            try {
                // Load initial data, but don't block UI if it fails
                await store.fetchData();
            } catch (error) {
                console.warn('Failed to fetch initial data, using demo mode:', error);
                // Continue with mock data for demo purposes
            } finally {
                // Always mark as initialized to show the UI
                setIsInitialized(true);
            }
        };

        // Show content immediately with minimal delay for better UX
        setTimeout(() => {
            setIsInitialized(true); // Show UI immediately
            initializeApp(); // Load data in background
        }, 500); // Optimized loading timeout
    }, [store]);

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    // Show loading only for first 2 seconds or if critical operations are running
    const shouldShowLoading = !isInitialized;

    return (
        <Container maxWidth="xl">
            <Box sx={{ my: 2, textAlign: 'center' }}>
                <Typography variant="h4" component="h1" gutterBottom sx={{ 
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)', 
                    backgroundClip: 'text', 
                    WebkitBackgroundClip: 'text', 
                    color: 'transparent',
                    fontWeight: 'bold',
                    mb: 1
                }}>
                    🤖 AnalyticBot Dashboard
                </Typography>
                <Typography variant="subtitle1" color="text.secondary" gutterBottom sx={{ mb: 2 }}>
                    PROFESSIONAL TELEGRAM ANALYTICS • REAL-TIME DATA • AI INSIGHTS
                </Typography>
                
                {/* Enhanced Service Status Cards */}
                <Box sx={{ 
                    display: 'flex', 
                    gap: 1, 
                    justifyContent: 'center', 
                    flexWrap: 'wrap', 
                    mb: 3,
                    p: 2,
                    borderRadius: 2,
                    bgcolor: 'background.paper',
                    boxShadow: 1
                }}>
                    <Chip icon={<span>✅</span>} label="Bot Online" color="success" size="medium" sx={{ fontSize: '0.9rem' }} />
                    <Chip icon={<span>�</span>} label="Analytics Ready" color="primary" size="medium" sx={{ fontSize: '0.9rem' }} />
                    <Chip icon={<span>🛡️</span>} label="Secure" color="secondary" size="medium" sx={{ fontSize: '0.9rem' }} />
                    <Chip icon={<span>🧠</span>} label="AI Active" color="warning" size="medium" sx={{ fontSize: '0.9rem' }} />
                    <Chip icon={<span>⚡</span>} label="Real-time" color="info" size="medium" sx={{ fontSize: '0.9rem' }} />
                </Box>
            </Box>

            {shouldShowLoading ? (
                <AppSkeleton />
            ) : (
                <Box>
                    {/* Main Navigation Tabs */}
                    <Paper sx={{ mb: 3, borderRadius: 2, overflow: 'hidden' }}>
                        <Tabs
                            value={activeTab}
                            onChange={handleTabChange}
                            sx={{ 
                                borderBottom: 1, 
                                borderColor: 'divider',
                                '& .MuiTab-root': {
                                    fontWeight: 'bold',
                                    fontSize: '1rem',
                                    textTransform: 'none',
                                    minHeight: 64,
                                    '&.Mui-selected': {
                                        color: 'primary.main'
                                    }
                                }
                            }}
                            variant="fullWidth"
                            TabIndicatorProps={{
                                style: {
                                    height: 4,
                                    borderRadius: '4px 4px 0 0'
                                }
                            }}
                        >
                            <Tab 
                                label={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        📝 <span>Post Management</span>
                                    </Box>
                                } 
                            />
                            <Tab 
                                label={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        📊 <span>Analytics Dashboard</span>
                                    </Box>
                                } 
                            />
                            <Tab 
                                label={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        🧠 <span>AI Services</span>
                                    </Box>
                                } 
                            />
                        </Tabs>
                    </Paper>

                    {/* Post Management Tab */}
                    <TabPanel value={activeTab} index={0}>
                        <Container maxWidth="sm">
                            <AddChannel />
                            <EnhancedMediaUploader /> {/* NEW Enhanced uploader */}
                            <MediaPreview /> {/* Keep existing for compatibility */}
                            <PostCreator />
                            <ScheduledPostsList />
                            <StorageFileBrowser /> {/* NEW File browser */}
                        </Container>
                    </TabPanel>

                    {/* Analytics Dashboard Tab */}
                    <TabPanel value={activeTab} index={1}>
                        <AnalyticsDashboard /> {/* NEW Week 2 Analytics Dashboard */}
                    </TabPanel>

                    {/* AI Services Tab */}
                    <TabPanel value={activeTab} index={2}>
                        <Container maxWidth="lg">
                            <Grid container spacing={3}>
                                <Grid item xs={12}>
                                    <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        🧠 AI & Machine Learning Xizmatlari
                                    </Typography>
                                </Grid>
                                
                                {/* AI Service Cards */}
                                <Grid item xs={12} md={6}>
                                    <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
                                        <CardContent>
                                            <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>
                                                🎯 Content Optimizer
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                                Matn va hashtag optimallashtirish, sentiment analysis
                                            </Typography>
                                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                                <Chip label="✅ Sentiment Analysis" size="small" color="success" />
                                                <Chip label="✅ Hashtag AI" size="small" color="success" />
                                                <Chip label="✅ Readability" size="small" color="success" />
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>

                                <Grid item xs={12} md={6}>
                                    <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
                                        <CardContent>
                                            <Typography variant="h6" gutterBottom sx={{ color: 'success.main' }}>
                                                📈 Predictive Analytics
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                                ML algoritmlari orqali post performance prediction
                                            </Typography>
                                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                                <Chip label="✅ Engagement Prediction" size="small" color="success" />
                                                <Chip label="✅ Best Time AI" size="small" color="success" />
                                                <Chip label="✅ Audience Analysis" size="small" color="success" />
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>

                                <Grid item xs={12} md={6}>
                                    <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
                                        <CardContent>
                                            <Typography variant="h6" gutterBottom sx={{ color: 'warning.main' }}>
                                                🔮 Churn Predictor
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                                Obunachilar aktivligini bashorat qilish va saqlash
                                            </Typography>
                                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                                <Chip label="✅ Risk Assessment" size="small" color="success" />
                                                <Chip label="✅ Retention AI" size="small" color="success" />
                                                <Chip label="✅ User Behavior" size="small" color="success" />
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>

                                <Grid item xs={12} md={6}>
                                    <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-4px)' } }}>
                                        <CardContent>
                                            <Typography variant="h6" gutterBottom sx={{ color: 'error.main' }}>
                                                🛡️ Security & Monitoring
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                                OAuth 2.0, MFA, RBAC va xavfsizlik monitoring
                                            </Typography>
                                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                                <Chip label="✅ OAuth 2.0" size="small" color="success" />
                                                <Chip label="✅ Multi-Factor Auth" size="small" color="success" />
                                                <Chip label="✅ Role-Based Access" size="small" color="success" />
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>

                                {/* Technology Stack */}
                                <Grid item xs={12}>
                                    <Paper sx={{ p: 3, mt: 2 }}>
                                        <Typography variant="h6" gutterBottom>
                                            🔧 Technology Stack
                                        </Typography>
                                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                            <Chip label="Python 3.11" color="primary" />
                                            <Chip label="scikit-learn" color="primary" />
                                            <Chip label="pandas" color="primary" />
                                            <Chip label="numpy" color="primary" />
                                            <Chip label="MLflow" color="primary" />
                                            <Chip label="FastAPI" color="secondary" />
                                            <Chip label="aiogram 3.22" color="secondary" />
                                            <Chip label="Redis" color="secondary" />
                                        </Box>
                                    </Paper>
                                </Grid>
                            </Grid>
                        </Container>
                    </TabPanel>
                </Box>
            )}
        </Container>
    );
}

export default App;
