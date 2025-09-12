import React, { useState } from 'react';
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
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
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
    CheckCircle as SuccessIcon,
    Error as ErrorIcon
} from '@mui/icons-material';

/**
 * Content Optimizer Service Page
 * Professional AI service dashboard with real-time status and controls
 */
const ContentOptimizerService = () => {
    const [currentTab, setCurrentTab] = useState(0);
    const [autoOptimization, setAutoOptimization] = useState(true);
    const [isOptimizing, setIsOptimizing] = useState(false);

    const serviceStats = {
        totalOptimized: 1247,
        todayOptimized: 23,
        avgImprovement: '+34%',
        status: 'active'
    };

    const recentOptimizations = [
        { id: 1, content: 'Product Launch Post', improvement: '+42%', timestamp: '2 minutes ago', status: 'success' },
        { id: 2, content: 'Weekly Newsletter', improvement: '+28%', timestamp: '15 minutes ago', status: 'success' },
        { id: 3, content: 'Blog Article Draft', improvement: '+51%', timestamp: '1 hour ago', status: 'success' },
        { id: 4, content: 'Social Media Campaign', improvement: '+38%', timestamp: '2 hours ago', status: 'success' }
    ];

    const handleOptimize = () => {
        setIsOptimizing(true);
        setTimeout(() => setIsOptimizing(false), 3000);
    };

    const TabPanel = ({ children, value, index }) => (
        <div hidden={value !== index}>
            {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
        </div>
    );

    return (
        <Box>
            {/* Service Header */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <OptimizeIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                    <Typography variant="h4" component="h1" fontWeight={600}>
                        Content Optimizer
                    </Typography>
                    <Chip 
                        label="Active" 
                        color="success" 
                        variant="filled"
                        sx={{ ml: 'auto' }}
                    />
                </Box>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                    AI-powered content enhancement for maximum engagement and performance
                </Typography>

                {/* Quick Stats */}
                <Grid container spacing={3}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="primary.main" fontWeight={600}>
                                {serviceStats.totalOptimized}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Total Optimized
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="success.main" fontWeight={600}>
                                {serviceStats.todayOptimized}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Today's Count
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="warning.main" fontWeight={600}>
                                {serviceStats.avgImprovement}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Avg Improvement
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Button
                                variant="contained"
                                size="large"
                                startIcon={<OptimizeIcon />}
                                onClick={handleOptimize}
                                disabled={isOptimizing}
                                sx={{ width: '100%', minHeight: 44 }}
                            >
                                {isOptimizing ? 'Optimizing...' : 'Optimize Content'}
                            </Button>
                        </Card>
                    </Grid>
                </Grid>
            </Box>

            {/* Service Tabs */}
            <Card>
                <Tabs 
                    value={currentTab} 
                    onChange={(e, newValue) => setCurrentTab(newValue)}
                    sx={{ borderBottom: 1, borderColor: 'divider' }}
                >
                    <Tab label="Recent Activity" icon={<AnalyticsIcon />} />
                    <Tab label="Settings" icon={<SettingsIcon />} />
                    <Tab label="Schedule" icon={<ScheduleIcon />} />
                </Tabs>

                {/* Recent Activity Tab */}
                <TabPanel value={currentTab} index={0}>
                    <CardContent>
                        {isOptimizing && (
                            <Alert severity="info" sx={{ mb: 3 }}>
                                <Box>
                                    <Typography variant="body2" sx={{ mb: 1 }}>
                                        Optimizing content...
                                    </Typography>
                                    <LinearProgress />
                                </Box>
                            </Alert>
                        )}

                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Recent Optimizations
                        </Typography>
                        
                        <List>
                            {recentOptimizations.map((item) => (
                                <ListItem 
                                    key={item.id}
                                    sx={{ 
                                        border: 1, 
                                        borderColor: 'divider', 
                                        borderRadius: 1, 
                                        mb: 1
                                    }}
                                >
                                    <ListItemIcon>
                                        <SuccessIcon color="success" />
                                    </ListItemIcon>
                                    <ListItemText
                                        primary={item.content}
                                        secondary={`Improvement: ${item.improvement} • ${item.timestamp}`}
                                    />
                                    <Chip 
                                        label={item.improvement} 
                                        color="success" 
                                        size="small"
                                        variant="outlined"
                                    />
                                </ListItem>
                            ))}
                        </List>
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