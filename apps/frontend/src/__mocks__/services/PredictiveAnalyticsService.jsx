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
import ModernCard, { ModernCardHeader } from '../../components/common/ModernCard.jsx';
import { SEMANTIC_SPACING } from '../../theme/spacingSystem.js';

// Import mock data
import {
    predictiveStats,
    mockForecasts,
    trendInsights,
    forecastModels
} from '../aiServices/predictiveAnalytics.js';

/**
 * Mock Predictive Analytics Service Page
 * Demo implementation with mock data for demo users
 */
const PredictiveAnalyticsService = () => {
    const [currentTab, setCurrentTab] = useState(0);
    const [timeRange, setTimeRange] = useState('30d');
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    // Use mock data
    const stats = predictiveStats;
    const predictions = mockForecasts;
    const insights = trendInsights;
    const models = forecastModels;

    const handleTabChange = (event, newValue) => {
        setCurrentTab(newValue);
    };

    const handleTimeRangeChange = (event) => {
        setTimeRange(event.target.value);
    };

    const handleAnalyze = () => {
        setIsAnalyzing(true);
        setTimeout(() => setIsAnalyzing(false), 3000);
    };

    const getTrendIcon = (trend) => {
        switch(trend) {
            case 'up': return <TrendingUp color="success" />;
            case 'down': return <DownIcon color="error" />;
            case 'flat': return <FlatIcon color="warning" />;
            default: return <TimelineIcon />;
        }
    };

    const getTrendColor = (trend) => {
        switch(trend) {
            case 'up': return '#4caf50';
            case 'down': return '#f44336';
            case 'flat': return '#ff9800';
            default: return '#2196f3';
        }
    };

    const TabPanel = ({ children, value, index }) => (
        <div hidden={value !== index} style={{ paddingTop: SEMANTIC_SPACING.sections.small }}>
            {value === index && children}
        </div>
    );

    return (
        <Box sx={{ p: SEMANTIC_SPACING.sections.medium }}>
            {/* Header */}
            <Box sx={{ mb: SEMANTIC_SPACING.sections.medium }}>
                <Typography variant="h4" sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <PredictiveIcon color="primary" />
                    Predictive Analytics
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Advanced forecasting and predictive modeling using machine learning algorithms.
                </Typography>

                <Alert severity="info" sx={{ mt: 2 }}>
                    🎭 Demo Mode: Showing sample predictive analytics data. In production, this would analyze real historical data to make predictions.
                </Alert>
            </Box>

            {/* Statistics Overview */}
            <Grid container spacing={SEMANTIC_SPACING.components.medium} sx={{ mb: SEMANTIC_SPACING.sections.medium }}>
                <Grid item xs={12} sm={6} md={3}>
                    <ModernCard>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>
                                Forecast Accuracy
                            </Typography>
                            <Typography variant="h4" sx={{ color: '#4caf50' }}>
                                {stats?.accuracy || 'N/A'}%
                            </Typography>
                        </CardContent>
                    </ModernCard>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <ModernCard>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>
                                Active Models
                            </Typography>
                            <Typography variant="h4">
                                {stats?.activeModels || 0}
                            </Typography>
                        </CardContent>
                    </ModernCard>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <ModernCard>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>
                                Predictions Made
                            </Typography>
                            <Typography variant="h4">
                                {stats?.predictionsMade || 0}
                            </Typography>
                        </CardContent>
                    </ModernCard>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <ModernCard>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>
                                Confidence Score
                            </Typography>
                            <Typography variant="h4" sx={{ color: '#2196f3' }}>
                                {stats?.confidenceScore || 0}%
                            </Typography>
                        </CardContent>
                    </ModernCard>
                </Grid>
            </Grid>

            {/* Main Content */}
            <ModernCard>
                <ModernCardHeader
                    title="Predictive Analysis"
                    action={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <FormControl size="small" sx={{ minWidth: 120 }}>
                                <InputLabel>Time Range</InputLabel>
                                <Select
                                    value={timeRange}
                                    label="Time Range"
                                    onChange={handleTimeRangeChange}
                                >
                                    <MenuItem value="7d">7 Days</MenuItem>
                                    <MenuItem value="30d">30 Days</MenuItem>
                                    <MenuItem value="90d">90 Days</MenuItem>
                                    <MenuItem value="1y">1 Year</MenuItem>
                                </Select>
                            </FormControl>
                            <Button
                                variant="contained"
                                onClick={handleAnalyze}
                                disabled={isAnalyzing}
                            >
                                {isAnalyzing ? 'Analyzing...' : 'Run Analysis'}
                            </Button>
                        </Box>
                    }
                />

                <Tabs
                    value={currentTab}
                    onChange={handleTabChange}
                    sx={{ px: 3, borderBottom: 1, borderColor: 'divider' }}
                >
                    <Tab label="Forecasts" icon={<TimelineIcon />} />
                    <Tab label="Trends" icon={<AnalyticsIcon />} />
                    <Tab label="Models" icon={<SettingsIcon />} />
                </Tabs>

                {/* Forecasts Tab */}
                <TabPanel value={currentTab} index={0}>
                    <Box sx={{ p: 3 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Prediction Results
                        </Typography>

                        <TableContainer component={Paper} variant="outlined">
                            <Table>
                                <TableHead>
                                    <TableRow>
                                        <TableCell>Metric</TableCell>
                                        <TableCell>Current Value</TableCell>
                                        <TableCell>Predicted Value</TableCell>
                                        <TableCell>Trend</TableCell>
                                        <TableCell>Confidence</TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {(predictions || []).map((prediction, index) => (
                                        <TableRow key={index}>
                                            <TableCell>{prediction.metric}</TableCell>
                                            <TableCell>{prediction.currentValue}</TableCell>
                                            <TableCell>{prediction.predictedValue}</TableCell>
                                            <TableCell>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                    {getTrendIcon(prediction.trend)}
                                                    <Typography
                                                        variant="body2"
                                                        sx={{ color: getTrendColor(prediction.trend) }}
                                                    >
                                                        {prediction.change}
                                                    </Typography>
                                                </Box>
                                            </TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={`${prediction.confidence}%`}
                                                    color={prediction.confidence > 80 ? 'success' : prediction.confidence > 60 ? 'warning' : 'error'}
                                                    size="small"
                                                />
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer>
                    </Box>
                </TabPanel>

                {/* Trends Tab */}
                <TabPanel value={currentTab} index={1}>
                    <Box sx={{ p: 3 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Trend Insights
                        </Typography>

                        <Grid container spacing={2}>
                            {(insights || []).map((insight, index) => (
                                <Grid item xs={12} md={6} key={index}>
                                    <Card variant="outlined">
                                        <CardContent>
                                            <Typography variant="h6" sx={{ mb: 1 }}>
                                                {insight.title}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                                {insight.description}
                                            </Typography>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <Chip
                                                    label={insight.impact}
                                                    color={insight.impact === 'High' ? 'error' : insight.impact === 'Medium' ? 'warning' : 'success'}
                                                    size="small"
                                                />
                                                <Typography variant="body2">
                                                    {insight.timeframe}
                                                </Typography>
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                </TabPanel>

                {/* Models Tab */}
                <TabPanel value={currentTab} index={2}>
                    <Box sx={{ p: 3 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Prediction Models
                        </Typography>

                        <Alert severity="info" sx={{ mb: 2 }}>
                            🎭 Demo Mode: Model configurations are simulated for demonstration purposes.
                        </Alert>

                        <Grid container spacing={2}>
                            {(models || []).map((model, index) => (
                                <Grid item xs={12} md={4} key={index}>
                                    <Card variant="outlined">
                                        <CardContent>
                                            <Typography variant="h6" sx={{ mb: 1 }}>
                                                {model.name}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                                {model.description}
                                            </Typography>
                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" sx={{ mb: 1 }}>
                                                    Accuracy: <strong>{model.accuracy}%</strong>
                                                </Typography>
                                                <Typography variant="body2">
                                                    Status: <Chip
                                                        label={model.status}
                                                        color={model.status === 'Active' ? 'success' : 'default'}
                                                        size="small"
                                                    />
                                                </Typography>
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                </TabPanel>
            </ModernCard>
        </Box>
    );
};

export default PredictiveAnalyticsService;
