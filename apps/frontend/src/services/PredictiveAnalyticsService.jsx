import React, { useState } from 'react';
import {
    Box,
    Typography,
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
    MenuItem,
    Card,
    CardContent
} from '@mui/material';
import {
    TrendingUp as PredictiveIcon,
    Timeline as TimelineIcon,
    Analytics as AnalyticsIcon,
    Settings as SettingsIcon,
    TrendingDown as DownIcon,
    TrendingFlat as FlatIcon
} from '@mui/icons-material';
import ModernCard, { ModernCardHeader } from '../components/common/ModernCard.jsx';
import { SEMANTIC_SPACING } from '../theme/spacingSystem.js';

// Import centralized mock data
import { 
    predictiveStats, 
    mockForecasts, 
    trendInsights, 
    forecastModels 
} from '../__mocks__/aiServices/predictiveAnalytics.js';

/**
 * Predictive Analytics Service Page
 * Enterprise-grade predictive modeling and trend analysis
 */
const PredictiveAnalyticsService = () => {
    const [currentTab, setCurrentTab] = useState(0);
    const [timeRange, setTimeRange] = useState('30d');
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    // Use centralized mock data
    const serviceStats = predictiveStats;
    const predictions = mockForecasts;
    const trendData = trendInsights;

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
                        <PredictiveIcon sx={{ fontSize: 40 }} />
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h3" component="h1" fontWeight={700} sx={{ mb: 0.5 }}>
                            Predictive Analytics
                        </Typography>
                        <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 400 }}>
                            Advanced AI predictions for future performance trends and optimization opportunities
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
                        <ModernCard 
                            variant="elevated"
                            sx={{ 
                                textAlign: 'center',
                                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                color: 'white',
                                '&:hover': {
                                    transform: 'translateY(-4px)',
                                    boxShadow: '0 12px 40px rgba(102, 126, 234, 0.3)'
                                }
                            }}
                        >
                            <Typography 
                                variant="h3" 
                                fontWeight={700} 
                                sx={{ mb: SEMANTIC_SPACING.ELEMENT_SPACING }}
                            >
                                {serviceStats.accuracy}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Model Accuracy
                            </Typography>
                        </ModernCard>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <ModernCard variant="standard" sx={{ textAlign: 'center' }}>
                            <Typography 
                                variant="h4" 
                                color="success.main" 
                                fontWeight={600}
                                sx={{ mb: SEMANTIC_SPACING.ELEMENT_SPACING }}
                            >
                                {serviceStats.predictions}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Active Predictions
                            </Typography>
                        </ModernCard>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <ModernCard variant="standard" sx={{ textAlign: 'center' }}>
                            <Typography 
                                variant="h4" 
                                color="warning.main" 
                                fontWeight={600}
                                sx={{ mb: SEMANTIC_SPACING.ELEMENT_SPACING }}
                            >
                                {serviceStats.trends}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Trend Alerts
                            </Typography>
                        </ModernCard>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <ModernCard variant="standard" sx={{ textAlign: 'center', display: 'flex', alignItems: 'center' }}>
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
                        </ModernCard>
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
                            {trendData.map((insight, index) => (
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