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
import TWAEnhancementDemo from './components/TWAEnhancementDemo.jsx'; // NEW Phase 2.1 Demo
import SuperAdminPanel from './components/SuperAdminPanel.jsx'; // NEW Phase 2.6 SuperAdmin Panel
import DevelopmentTools from './components/DevelopmentTools.jsx'; // Development helper
import { useAppStore } from './store/appStore.js';

const AppSkeleton = () => (
    <Stack spacing={3} sx={{ mt: 2 }}>
        <Skeleton variant="rounded" width="100%" height={110} />
        <Skeleton variant="rounded" width="100%" height={280} />
        <Skeleton variant="rounded" width="100%" height={200} />
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
    const { isLoading } = useAppStore();
    const [activeTab, setActiveTab] = useState(0);

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    return (
        <Container maxWidth="xl">
            <Box sx={{ my: 2, textAlign: 'center' }}>
                <Typography variant="h4" component="h1" gutterBottom sx={{ 
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)', 
                    backgroundClip: 'text', 
                    WebkitBackgroundClip: 'text', 
                    color: 'transparent',
                    fontWeight: 'bold' 
                }}>
                    🤖 AnalyticBot Dashboard
                </Typography>
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                    To'liq Telegram Bot Boshqaruv Tizimi
                </Typography>
                
                {/* Service Status Cards */}
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap', mb: 2 }}>
                    <Chip icon={<span>🤖</span>} label="Bot Active" color="success" size="small" />
                    <Chip icon={<span>🔍</span>} label="Analytics" color="primary" size="small" />
                    <Chip icon={<span>🛡️</span>} label="Security" color="secondary" size="small" />
                    <Chip icon={<span>🧠</span>} label="AI/ML" color="warning" size="small" />
                    <Chip icon={<span>📊</span>} label="Dashboard" color="info" size="small" />
                </Box>
            </Box>

            {isLoading ? (
                <AppSkeleton />
            ) : (
                <Box>
                    {/* Main Navigation Tabs */}
                    <Paper sx={{ mb: 3 }}>
                        <Tabs
                            value={activeTab}
                            onChange={handleTabChange}
                            sx={{ borderBottom: 1, borderColor: 'divider' }}
                            variant="fullWidth"
                        >
                            <Tab 
                                label={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        📝 <span>Post Boshqaruvi</span>
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
                                        🧠 <span>AI Xizmatlari</span>
                                    </Box>
                                } 
                            />
                            <Tab 
                                label={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        🚀 <span>TWA Enhancement Demo</span>
                                    </Box>
                                } 
                            />
                            <Tab 
                                label={
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                        🛡️ <span>SuperAdmin Panel</span>
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

                    {/* TWA Enhancement Demo Tab */}
                    <TabPanel value={activeTab} index={3}>
                        <TWAEnhancementDemo />
                    </TabPanel>

                    {/* SuperAdmin Panel Tab */}
                    <TabPanel value={activeTab} index={4}>
                        <SuperAdminPanel />
                    </TabPanel>
                </Box>
            )}
            
            {/* Development Tools (only visible in development) */}
            <DevelopmentTools />
        </Container>
    );
}

export default App;
