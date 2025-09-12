import React, { useState, useEffect } from 'react';
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
    Chip,
    Button
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import PostCreator from './components/PostCreator';
import ScheduledPostsList from './components/ScheduledPostsList';
import MediaPreview from './components/MediaPreview';
import AddChannel from './components/AddChannel';
import EnhancedMediaUploader from './components/EnhancedMediaUploader.jsx';
import StorageFileBrowser from './components/StorageFileBrowser.jsx';
import AnalyticsDashboard from './components/AnalyticsDashboard.jsx';
import { useAppStore } from './store/appStore.js';
import { Icon, StatusChip } from './components/common/IconSystem.jsx';
import { TouchTargetProvider } from './components/common/TouchTargetCompliance.jsx';
import {
    AutoFixHigh as ContentIcon,
    TrendingUp as PredictiveIcon,
    PersonRemove as ChurnIcon,
    Security as SecurityIcon,
    Launch as LaunchIcon
} from '@mui/icons-material';

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
            <Stack spacing={3}>
                <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 2 }} />
                <Grid container spacing={2}>
                    {[...Array(4)].map((_, i) => (
                        <Grid item xs={6} key={i}>
                            <Skeleton variant="rectangular" height={120} sx={{ borderRadius: 2 }} />
                        </Grid>
                    ))}
                </Grid>
            </Stack>
            
            {/* Sidebar content */}
            <Stack spacing={3}>
                <Skeleton variant="rectangular" height={250} sx={{ borderRadius: 2 }} />
                <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2 }} />
            </Stack>
        </Box>
    </Stack>
);

/**
 * Main Dashboard Component
 * Professional dashboard with AI services quick access
 */
const MainDashboard = () => {
    const navigate = useNavigate();
    const [selectedTab, setSelectedTab] = useState(0);
    const { 
        isGlobalLoading,
        isLoading,
        fetchData,
        posts, 
        scheduledPosts, 
        selectedMedia, 
        channels,
        addPost, 
        schedulePost, 
        setSelectedMedia, 
        addChannel, 
        removeChannel 
    } = useAppStore();
    
    // Check for global loading state or specific fetchData loading
    const isLoadingData = isGlobalLoading() || isLoading('fetchData');
    
    // Initialize app data on component mount
    useEffect(() => {
        console.log('MainDashboard: Initializing app data');
        fetchData();
    }, [fetchData]);

    const aiServices = [
        {
            name: 'Content Optimizer',
            description: 'AI-powered content enhancement for maximum engagement',
            status: 'active',
            icon: ContentIcon,
            path: '/services/content-optimizer',
            metrics: { optimized: 1247, improvement: '+34%' }
        },
        {
            name: 'Predictive Analytics',
            description: 'Future performance predictions and trend analysis',
            status: 'active',
            icon: PredictiveIcon,
            path: '/services/predictive-analytics',
            metrics: { accuracy: '94.2%', predictions: 156 }
        },
        {
            name: 'Churn Predictor',
            description: 'Customer retention insights and risk assessment',
            status: 'beta',
            icon: ChurnIcon,
            path: '/services/churn-predictor',
            metrics: { atRisk: 47, saved: 23 }
        },
        {
            name: 'Security Monitoring',
            description: 'Real-time security analysis and threat detection',
            status: 'active',
            icon: SecurityIcon,
            path: '/services/security-monitoring',
            metrics: { blocked: 156, score: '87%' }
        }
    ];

    const getStatusColor = (status) => {
        switch (status) {
            case 'active': return 'success';
            case 'beta': return 'warning';
            case 'maintenance': return 'error';
            default: return 'default';
        }
    };

    // Show loading skeleton if still loading
    if (isLoadingData) {
        return (
            <TouchTargetProvider>
                <Container maxWidth="xl" sx={{ py: 3, minHeight: '100vh' }}>
                    <AppSkeleton />
                </Container>
            </TouchTargetProvider>
        );
    }

    return (
        <TouchTargetProvider>
            <Container maxWidth="xl" sx={{ py: 3, minHeight: '100vh' }}>
                {/* System Status Overview */}
                <Paper 
                    elevation={1}
                    sx={{ 
                        p: 3, 
                        mb: 4, 
                        borderRadius: 2,
                        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
                        border: '1px solid',
                        borderColor: 'divider'
                    }}
                >
                    <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                        System Status
                    </Typography>
                    <Stack 
                        direction="row" 
                        spacing={2} 
                        sx={{ flexWrap: 'wrap', gap: 1 }}
                    >
                        <StatusChip label="Analytics Active" status="success" />
                        <StatusChip label="AI Services Running" status="success" />
                        <StatusChip label="Real-time Monitoring" status="info" />
                        <StatusChip label="Security Enabled" status="success" />
                        <StatusChip label="Performance Optimized" status="warning" />
                    </Stack>
                </Paper>

                {/* AI Services Quick Access */}
                <Paper sx={{ mb: 4, p: 3, borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                        <Typography variant="h5" fontWeight={600}>
                            AI Services
                        </Typography>
                        <Button
                            variant="outlined"
                            endIcon={<LaunchIcon />}
                            onClick={() => navigate('/services')}
                            sx={{ minHeight: 44 }}
                        >
                            View All Services
                        </Button>
                    </Box>
                    
                    <Grid container spacing={3}>
                        {aiServices.map((service) => {
                            const IconComponent = service.icon;
                            return (
                                <Grid item xs={12} sm={6} md={3} key={service.name}>
                                    <Card 
                                        sx={{ 
                                            height: '100%',
                                            cursor: 'pointer',
                                            transition: 'all 0.3s ease',
                                            '&:hover': {
                                                transform: 'translateY(-4px)',
                                                boxShadow: 4
                                            }
                                        }}
                                        onClick={() => navigate(service.path)}
                                    >
                                        <CardContent sx={{ p: 3 }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                                <IconComponent 
                                                    sx={{ 
                                                        fontSize: 28, 
                                                        color: 'primary.main',
                                                        mr: 1
                                                    }} 
                                                />
                                                <Chip 
                                                    label={service.status} 
                                                    color={getStatusColor(service.status)}
                                                    size="small"
                                                />
                                            </Box>
                                            
                                            <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
                                                {service.name}
                                            </Typography>
                                            
                                            <Typography 
                                                variant="body2" 
                                                color="text.secondary" 
                                                sx={{ mb: 2, minHeight: 40 }}
                                            >
                                                {service.description}
                                            </Typography>
                                            
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                                                {Object.entries(service.metrics).map(([key, value]) => (
                                                    <Box key={key} sx={{ textAlign: 'center' }}>
                                                        <Typography variant="caption" color="text.secondary">
                                                            {key}
                                                        </Typography>
                                                        <Typography variant="body2" fontWeight={600}>
                                                            {value}
                                                        </Typography>
                                                    </Box>
                                                ))}
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            );
                        })}
                    </Grid>
                </Paper>

                {/* Main Content Tabs */}
                <Paper sx={{ borderRadius: 2 }}>
                    <Tabs 
                        value={selectedTab} 
                        onChange={(_, newValue) => setSelectedTab(newValue)}
                        sx={{ 
                            borderBottom: '1px solid',
                            borderColor: 'divider',
                            px: 2
                        }}
                    >
                        <Tab 
                            label="Dashboard" 
                            icon={<Icon name="dashboard" />} 
                            sx={{ minHeight: 64, fontSize: '1rem' }}
                        />
                        <Tab 
                            label="Create Post" 
                            icon={<Icon name="create" />} 
                            sx={{ minHeight: 64, fontSize: '1rem' }}
                        />
                        <Tab 
                            label="Analytics" 
                            icon={<Icon name="analytics" />} 
                            sx={{ minHeight: 64, fontSize: '1rem' }}
                        />
                    </Tabs>

                    <Box sx={{ p: 3 }}>
                        {selectedTab === 0 && (
                            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 3 }}>
                                {/* Main Content */}
                                <Box>
                                    <AnalyticsDashboard />
                                </Box>
                                
                                {/* Sidebar */}
                                <Stack spacing={3}>
                                    <ScheduledPostsList posts={scheduledPosts} />
                                    <AddChannel 
                                        channels={channels} 
                                        onAdd={addChannel} 
                                        onRemove={removeChannel} 
                                    />
                                </Stack>
                            </Box>
                        )}
                        
                        {selectedTab === 1 && (
                            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 3 }}>
                                <Box>
                                    <PostCreator onSubmit={addPost} onSchedule={schedulePost} />
                                </Box>
                                <Box>
                                    <Stack spacing={3}>
                                        <EnhancedMediaUploader onMediaSelect={setSelectedMedia} />
                                        {selectedMedia.length > 0 && (
                                            <MediaPreview 
                                                media={selectedMedia} 
                                                onRemove={(index) => {
                                                    const newMedia = [...selectedMedia];
                                                    newMedia.splice(index, 1);
                                                    setSelectedMedia(newMedia);
                                                }}
                                            />
                                        )}
                                        <StorageFileBrowser onFileSelect={setSelectedMedia} />
                                    </Stack>
                                </Box>
                            </Box>
                        )}
                        
                        {selectedTab === 2 && (
                            <AnalyticsDashboard />
                        )}
                    </Box>
                </Paper>
            </Container>
        </TouchTargetProvider>
    );
};

export default MainDashboard;