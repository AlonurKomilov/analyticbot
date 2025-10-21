import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    Button,
    Grid,
    Chip,
    LinearProgress,
    Alert,
    Switch,
    FormControlLabel,
    Tabs,
    Tab,
    Divider
} from '@mui/material';
import {
    AutoFixHigh as OptimizeIcon,
    TrendingUp as AnalyticsIcon,
    Schedule as ScheduleIcon,
    Settings as SettingsIcon,
    CheckCircle as SuccessIcon
} from '@mui/icons-material';

import { AIServicesAPI, ContentOptimizerAPI } from './aiServicesAPI';
import { useDemoMode, loadMockData } from '../__mocks__/utils/demoGuard';

// Using Demo Guard utility for clean demo mode management
// Mock data loaded dynamically only in demo mode

interface ServiceStats {
    totalOptimized: number;
    todayOptimized: number;
    avgImprovement: string;
    status: string;
}

interface Optimization {
    id: number;
    content: string;
    improvement: string;
    timestamp: string;
    status: string;
}

interface TabPanelProps {
    children: React.ReactNode;
    value: number;
    index: number;
}

/**
 * Content Optimizer Service Page
 * Professional AI service dashboard with real-time status and controls
 * 
 * ✨ Features Demo Guard utility for reactive demo/real API switching
 */
const ContentOptimizerService: React.FC = () => {
    // Use Demo Guard hook - automatically re-renders when data source changes
    const isDemo = useDemoMode();
    
    const [currentTab, setCurrentTab] = useState<number>(0);
    const [autoOptimization, setAutoOptimization] = useState<boolean>(true);
    const [isOptimizing, setIsOptimizing] = useState<boolean>(false);
    const [serviceStats, setServiceStats] = useState<ServiceStats>({
        totalOptimized: 0,
        todayOptimized: 0,
        avgImprovement: '0%',
        status: 'loading'
    });
    const [optimizations, setOptimizations] = useState<Optimization[]>([]);
    const [_error, _setError] = useState<string | null>(null);

    // Reactively load data when demo mode changes
    // This ensures switching between demo/real API works instantly
    useEffect(() => {
        loadServiceData();
    }, [isDemo]); // Re-run when demo mode changes

    const loadServiceData = async (): Promise<void> => {
        try {
            // Demo mode: Load mock data dynamically using Demo Guard utility
            if (isDemo) {
                const mockModule = await loadMockData(
                    () => import('../__mocks__/aiServices/contentOptimizer')
                );
                
                if (mockModule) {
                    setServiceStats(mockModule.contentOptimizerStats);
                    setOptimizations(mockModule.recentOptimizations);
                    _setError(null);
                    console.log('✅ Loaded demo data for Content Optimizer');
                }
                return;
            }

            // Real API mode: Fetch live data from backend
            console.log('🔄 Fetching real API data for Content Optimizer...');
            const stats = await AIServicesAPI.getAllStats();
            setServiceStats({
                totalOptimized: stats.content_optimizer.total_optimized,
                todayOptimized: stats.content_optimizer.today_count,
                avgImprovement: stats.content_optimizer.avg_improvement,
                status: stats.content_optimizer.status
            });
            _setError(null);
            console.log('✅ Loaded real API data for Content Optimizer');
        } catch (err) {
            console.error('❌ Failed to load service data:', err);
            _setError('Failed to load real-time data. Please try again.');
            // No fallback to mock - show error to user
        }
    };

    const handleOptimize = async (): Promise<void> => {
        setIsOptimizing(true);
        try {
            // Demo content optimization
            const result = await ContentOptimizerAPI.analyzeContent(
                "Check out our new product! It's amazing and you should buy it now!",
                { channelId: 'demo' }
            );

            // Add to recent optimizations
            const newOptimization: Optimization = {
                id: optimizations.length + 1,
                content: 'Demo Content',
                improvement: `+${Math.round(result.score_improvement)}%`,
                timestamp: 'just now',
                status: 'success'
            };
            setOptimizations(prev => [newOptimization, ...prev.slice(0, 3)]);

        } catch (err) {
            console.error('Optimization failed:', err);
            _setError('Content optimization failed. Please try again.');
        }
        setIsOptimizing(false);
    };

    const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
        <div hidden={value !== index}>
            {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
        </div>
    );

    return (
        <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: '100%' }}>
            {/* Professional Service Header */}
            <Box sx={{ mb: 5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Box
                        sx={{
                            p: 2,
                            borderRadius: 3,
                            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                            color: 'white',
                            mr: 3
                        }}
                    >
                        <OptimizeIcon sx={{ fontSize: 40 }} />
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h3" component="h1" fontWeight={700} sx={{ mb: 0.5 }}>
                            Content Optimizer
                        </Typography>
                        <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 400 }}>
                            AI-powered content enhancement for maximum engagement and performance
                        </Typography>
                    </Box>
                    <Chip
                        label="Active"
                        color="success"
                        variant="filled"
                        sx={{
                            fontWeight: 600,
                            fontSize: '0.9rem',
                            height: 36,
                            boxShadow: '0 4px 12px rgba(76, 175, 80, 0.3)'
                        }}
                    />
                </Box>

                {/* Enhanced Statistics Grid */}
                <Grid container spacing={3}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card
                            elevation={0}
                            sx={{
                                textAlign: 'center',
                                p: 3,
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                color: 'white',
                                position: 'relative',
                                overflow: 'hidden',
                                borderRadius: 3,
                                '&:hover': {
                                    transform: 'translateY(-4px)',
                                    boxShadow: '0 12px 40px rgba(102, 126, 234, 0.3)'
                                },
                                transition: 'all 0.3s ease'
                            }}
                        >
                            <Typography variant="h3" fontWeight={700} sx={{ mb: 1 }}>
                                {serviceStats.totalOptimized}
                            </Typography>
                            <Typography variant="body1" sx={{ opacity: 0.9 }}>
                                Total Optimized
                            </Typography>
                            <OptimizeIcon sx={{
                                position: 'absolute',
                                right: 16,
                                top: 16,
                                fontSize: 32,
                                opacity: 0.2
                            }} />
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card
                            elevation={0}
                            sx={{
                                textAlign: 'center',
                                p: 3,
                                background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                                color: 'white',
                                position: 'relative',
                                overflow: 'hidden',
                                borderRadius: 3,
                                '&:hover': {
                                    transform: 'translateY(-4px)',
                                    boxShadow: '0 12px 40px rgba(240, 147, 251, 0.3)'
                                },
                                transition: 'all 0.3s ease'
                            }}
                        >
                            <Typography variant="h3" fontWeight={700} sx={{ mb: 1 }}>
                                {serviceStats.todayOptimized}
                            </Typography>
                            <Typography variant="body1" sx={{ opacity: 0.9 }}>
                                Today's Count
                            </Typography>
                            <AnalyticsIcon sx={{
                                position: 'absolute',
                                right: 16,
                                top: 16,
                                fontSize: 32,
                                opacity: 0.2
                            }} />
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card
                            elevation={0}
                            sx={{
                                textAlign: 'center',
                                p: 3,
                                background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                                color: 'white',
                                position: 'relative',
                                overflow: 'hidden',
                                borderRadius: 3,
                                '&:hover': {
                                    transform: 'translateY(-4px)',
                                    boxShadow: '0 12px 40px rgba(79, 172, 254, 0.3)'
                                },
                                transition: 'all 0.3s ease'
                            }}
                        >
                            <Typography variant="h3" fontWeight={700} sx={{ mb: 1 }}>
                                {serviceStats.avgImprovement}
                            </Typography>
                            <Typography variant="body1" sx={{ opacity: 0.9 }}>
                                Avg Improvement
                            </Typography>
                            <AnalyticsIcon sx={{
                                position: 'absolute',
                                right: 16,
                                top: 16,
                                fontSize: 32,
                                opacity: 0.2
                            }} />
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card
                            elevation={0}
                            sx={{
                                p: 3,
                                background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                borderRadius: 3,
                                '&:hover': {
                                    transform: 'translateY(-4px)',
                                    boxShadow: '0 12px 40px rgba(250, 112, 154, 0.3)'
                                },
                                transition: 'all 0.3s ease'
                            }}
                        >
                            <Button
                                variant="contained"
                                size="large"
                                startIcon={<OptimizeIcon />}
                                onClick={handleOptimize}
                                disabled={isOptimizing}
                                sx={{
                                    width: '100%',
                                    minHeight: 56,
                                    backgroundColor: 'rgba(255,255,255,0.95)',
                                    color: 'primary.main',
                                    fontWeight: 600,
                                    fontSize: '1.1rem',
                                    borderRadius: 2,
                                    '&:hover': {
                                        backgroundColor: 'white',
                                        transform: 'scale(1.05)',
                                        boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                                    },
                                    '&:disabled': {
                                        backgroundColor: 'rgba(255,255,255,0.7)',
                                        color: 'text.disabled'
                                    },
                                    transition: 'all 0.3s ease'
                                }}
                            >
                                {isOptimizing ? 'Optimizing...' : 'Optimize Content'}
                            </Button>
                        </Card>
                    </Grid>
                </Grid>
            </Box>

            {/* Enhanced Service Tabs */}
            <Card
                elevation={0}
                sx={{
                    borderRadius: 3,
                    overflow: 'hidden',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
                }}
            >
                <Box sx={{
                    background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                    p: 2
                }}>
                    <Tabs
                        value={currentTab}
                        onChange={(_e, newValue: number) => setCurrentTab(newValue)}
                        sx={{
                            '& .MuiTabs-indicator': {
                                backgroundColor: 'primary.main',
                                height: 3,
                                borderRadius: 2
                            },
                            '& .MuiTab-root': {
                                fontWeight: 600,
                                fontSize: '1rem',
                                textTransform: 'none',
                                minHeight: 64,
                                '&.Mui-selected': {
                                    color: 'primary.main'
                                }
                            }
                        }}
                    >
                        <Tab
                            label="Recent Activity"
                            icon={<AnalyticsIcon />}
                            iconPosition="start"
                            sx={{ px: 3 }}
                        />
                        <Tab
                            label="Settings"
                            icon={<SettingsIcon />}
                            iconPosition="start"
                            sx={{ px: 3 }}
                        />
                        <Tab
                            label="Schedule"
                            icon={<ScheduleIcon />}
                            iconPosition="start"
                            sx={{ px: 3 }}
                        />
                    </Tabs>
                </Box>

                {/* Enhanced Recent Activity Tab */}
                <TabPanel value={currentTab} index={0}>
                    <CardContent sx={{ p: 4 }}>
                        {isOptimizing && (
                            <Alert
                                severity="info"
                                sx={{
                                    mb: 4,
                                    borderRadius: 2,
                                    '& .MuiAlert-message': {
                                        width: '100%'
                                    }
                                }}
                            >
                                <Box>
                                    <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>
                                        🤖 AI is optimizing your content...
                                    </Typography>
                                    <LinearProgress
                                        sx={{
                                            borderRadius: 2,
                                            height: 6
                                        }}
                                    />
                                </Box>
                            </Alert>
                        )}

                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                            <Typography variant="h5" fontWeight={700}>
                                Recent Optimizations
                            </Typography>
                            <Chip
                                label={`${optimizations.length} completed`}
                                size="small"
                                color="primary"
                                sx={{ ml: 2, fontWeight: 600 }}
                            />
                        </Box>

                        <Grid container spacing={3}>
                            {optimizations.map((item, index) => (
                                <Grid item xs={12} key={item.id}>
                                    <Card
                                        elevation={0}
                                        sx={{
                                            p: 3,
                                            border: '1px solid',
                                            borderColor: 'divider',
                                            borderRadius: 3,
                                            position: 'relative',
                                            background: index % 2 === 0
                                                ? 'linear-gradient(135deg, #f8f9ff 0%, #f0f4f8 100%)'
                                                : 'linear-gradient(135deg, #fff8f0 0%, #f8f4f0 100%)',
                                            '&:hover': {
                                                boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
                                                transform: 'translateY(-2px)'
                                            },
                                            transition: 'all 0.3s ease'
                                        }}
                                    >
                                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                            <Box
                                                sx={{
                                                    p: 1.5,
                                                    borderRadius: 2,
                                                    backgroundColor: 'success.main',
                                                    color: 'white',
                                                    mr: 2
                                                }}
                                            >
                                                <SuccessIcon />
                                            </Box>
                                            <Box sx={{ flexGrow: 1 }}>
                                                <Typography variant="h6" fontWeight={600} sx={{ mb: 0.5 }}>
                                                    {item.content}
                                                </Typography>
                                                <Typography variant="body2" color="text.secondary">
                                                    {item.timestamp}
                                                </Typography>
                                            </Box>
                                            <Chip
                                                label={item.improvement}
                                                color="success"
                                                sx={{
                                                    fontWeight: 700,
                                                    fontSize: '0.9rem',
                                                    height: 32
                                                }}
                                            />
                                        </Box>
                                        <Typography variant="body2" color="text.secondary">
                                            Content successfully optimized with AI enhancements for better engagement
                                        </Typography>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </CardContent>
                </TabPanel>

                {/* Settings Tab */}
                <TabPanel value={currentTab} index={1}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 3 }}>
                            Optimization Settings
                        </Typography>

                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={autoOptimization}
                                        onChange={(e) => setAutoOptimization(e.target.checked)}
                                    />
                                }
                                label="Automatic Content Optimization"
                            />

                            <Divider />

                            <Typography variant="subtitle1" fontWeight={600}>
                                Optimization Targets
                            </Typography>

                            <FormControlLabel
                                control={<Switch defaultChecked />}
                                label="Engagement Rate"
                            />
                            <FormControlLabel
                                control={<Switch defaultChecked />}
                                label="Readability Score"
                            />
                            <FormControlLabel
                                control={<Switch />}
                                label="SEO Optimization"
                            />
                            <FormControlLabel
                                control={<Switch defaultChecked />}
                                label="Sentiment Analysis"
                            />
                        </Box>
                    </CardContent>
                </TabPanel>

                {/* Schedule Tab */}
                <TabPanel value={currentTab} index={2}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 3 }}>
                            Optimization Schedule
                        </Typography>

                        <Alert severity="info">
                            Scheduled optimization features coming soon. Currently running in real-time mode.
                        </Alert>
                    </CardContent>
                </TabPanel>
            </Card>
        </Box>
    );
};

export default ContentOptimizerService;
