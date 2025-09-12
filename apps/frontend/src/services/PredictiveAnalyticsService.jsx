import React, { useState } from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    Button,
    Grid,
    Chip,
    Alert,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Tabs,
    Tab,
    FormControl,
    InputLabel,
    Select,
    MenuItem
} from '@mui/material';
import {
    TrendingUp as PredictiveIcon,
    Timeline as TimelineIcon,
    Analytics as AnalyticsIcon,
    Settings as SettingsIcon,
    TrendingDown as DownIcon,
    TrendingFlat as FlatIcon
} from '@mui/icons-material';

/**
 * Predictive Analytics Service Page
 * Enterprise-grade predictive modeling and trend analysis
 */
const PredictiveAnalyticsService = () => {
    const [currentTab, setCurrentTab] = useState(0);
    const [timeRange, setTimeRange] = useState('30d');
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    const serviceStats = {
        accuracy: '94.2%',
        predictions: 156,
        trends: 8,
        status: 'active'
    };

    const predictions = [
        { 
            metric: 'Engagement Rate', 
            current: '3.2%', 
            predicted: '4.1%', 
            trend: 'up', 
            confidence: '92%',
            timeframe: '7 days'
        },
        { 
            metric: 'Follower Growth', 
            current: '2.1K', 
            predicted: '2.8K', 
            trend: 'up', 
            confidence: '88%',
            timeframe: '30 days'
        },
        { 
            metric: 'Content Performance', 
            current: '67%', 
            predicted: '71%', 
            trend: 'up', 
            confidence: '95%',
            timeframe: '14 days'
        },
        { 
            metric: 'User Activity', 
            current: '89%', 
            predicted: '85%', 
            trend: 'down', 
            confidence: '79%',
            timeframe: '7 days'
        },
        { 
            metric: 'Revenue Impact', 
            current: '$12.4K', 
            predicted: '$13.8K', 
            trend: 'up', 
            confidence: '91%',
            timeframe: '30 days'
        }
    ];

    const trendInsights = [
        {
            title: 'Peak Engagement Hours',
            insight: '2-4 PM shows highest engagement potential',
            impact: 'High',
            action: 'Schedule content during peak hours'
        },
        {
            title: 'Content Type Preference',
            insight: 'Video content outperforming text by 340%',
            impact: 'Very High',
            action: 'Increase video content production'
        },
        {
            title: 'Seasonal Trend',
            insight: 'Holiday season traffic expected +45%',
            impact: 'Medium',
            action: 'Prepare seasonal content strategy'
        }
    ];

    const getTrendIcon = (trend) => {
        switch (trend) {
            case 'up': return <PredictiveIcon color="success" />;
            case 'down': return <DownIcon color="error" />;
            default: return <FlatIcon color="warning" />;
        }
    };

    const getTrendColor = (trend) => {
        switch (trend) {
            case 'up': return 'success.main';
            case 'down': return 'error.main';
            default: return 'warning.main';
        }
    };

    const getImpactColor = (impact) => {
        switch (impact) {
            case 'Very High': return 'error';
            case 'High': return 'warning';
            case 'Medium': return 'info';
            default: return 'default';
        }
    };

    const handleAnalyze = () => {
        setIsAnalyzing(true);
        setTimeout(() => setIsAnalyzing(false), 4000);
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
                    <PredictiveIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                    <Typography variant="h4" component="h1" fontWeight={600}>
                        Predictive Analytics
                    </Typography>
                    <Chip 
                        label="Active" 
                        color="success" 
                        variant="filled"
                        sx={{ ml: 'auto' }}
                    />
                </Box>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                    Advanced AI predictions for future performance trends and optimization opportunities
                </Typography>

                {/* Quick Stats */}
                <Grid container spacing={3}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="primary.main" fontWeight={600}>
                                {serviceStats.accuracy}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Model Accuracy
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="success.main" fontWeight={600}>
                                {serviceStats.predictions}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Active Predictions
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="warning.main" fontWeight={600}>
                                {serviceStats.trends}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Trend Alerts
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Button
                                variant="contained"
                                size="large"
                                startIcon={<AnalyticsIcon />}
                                onClick={handleAnalyze}
                                disabled={isAnalyzing}
                                sx={{ width: '100%', minHeight: 44 }}
                            >
                                {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
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
                    <Tab label="Predictions" icon={<TimelineIcon />} />
                    <Tab label="Trend Insights" icon={<AnalyticsIcon />} />
                    <Tab label="Settings" icon={<SettingsIcon />} />
                </Tabs>

                {/* Predictions Tab */}
                <TabPanel value={currentTab} index={0}>
                    <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                            <Typography variant="h6">
                                Performance Predictions
                            </Typography>
                            <FormControl size="small">
                                <InputLabel>Time Range</InputLabel>
                                <Select
                                    value={timeRange}
                                    label="Time Range"
                                    onChange={(e) => setTimeRange(e.target.value)}
                                >
                                    <MenuItem value="7d">7 Days</MenuItem>
                                    <MenuItem value="14d">14 Days</MenuItem>
                                    <MenuItem value="30d">30 Days</MenuItem>
                                    <MenuItem value="90d">90 Days</MenuItem>
                                </Select>
                            </FormControl>
                        </Box>

                        {isAnalyzing && (
                            <Alert severity="info" sx={{ mb: 3 }}>
                                Running predictive analysis models...
                            </Alert>
                        )}
                        
                        <TableContainer component={Paper} variant="outlined">
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell><strong>Metric</strong></TableCell>
                                        <TableCell><strong>Current</strong></TableCell>
                                        <TableCell><strong>Predicted</strong></TableCell>
                                        <TableCell><strong>Trend</strong></TableCell>
                                        <TableCell><strong>Confidence</strong></TableCell>
                                        <TableCell><strong>Timeframe</strong></TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {predictions.map((prediction, index) => (
                                        <TableRow key={index}>
                                            <TableCell>{prediction.metric}</TableCell>
                                            <TableCell>{prediction.current}</TableCell>
                                            <TableCell sx={{ color: getTrendColor(prediction.trend), fontWeight: 600 }}>
                                                {prediction.predicted}
                                            </TableCell>
                                            <TableCell>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    {getTrendIcon(prediction.trend)}
                                                </Box>
                                            </TableCell>
                                            <TableCell>{prediction.confidence}</TableCell>
                                            <TableCell>{prediction.timeframe}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </CardContent>
                </TabPanel>

                {/* Trend Insights Tab */}
                <TabPanel value={currentTab} index={1}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 3 }}>
                            AI-Generated Insights
                        </Typography>
                        
                        <Grid container spacing={3}>
                            {trendInsights.map((insight, index) => (
                                <Grid item xs={12} md={6} key={index}>
                                    <Card sx={{ p: 2, height: '100%' }}>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                            <Typography variant="h6" sx={{ fontWeight: 600 }}>
                                                {insight.title}
                                            </Typography>
                                            <Chip 
                                                label={insight.impact} 
                                                color={getImpactColor(insight.impact)}
                                                size="small"
                                            />
                                        </Box>
                                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                            {insight.insight}
                                        </Typography>
                                        <Typography variant="body2" sx={{ fontWeight: 500, color: 'primary.main' }}>
                                            Recommended Action: {insight.action}
                                        </Typography>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </CardContent>
                </TabPanel>

                {/* Settings Tab */}
                <TabPanel value={currentTab} index={2}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 3 }}>
                            Prediction Model Settings
                        </Typography>
                        
                        <Alert severity="info">
                            Advanced model configuration settings available for enterprise users.
                        </Alert>
                    </CardContent>
                </TabPanel>
            </Card>
        </Box>
    );
};

export default PredictiveAnalyticsService;