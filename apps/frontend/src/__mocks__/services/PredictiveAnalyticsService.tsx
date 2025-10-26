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
    CardContent,
    SelectChangeEvent
} from '@mui/material';
import {
    TrendingUp as PredictiveIcon,
    Timeline as TimelineIcon,
    Analytics as AnalyticsIcon,
    Settings as SettingsIcon,
    TrendingDown as DownIcon,
    TrendingFlat as FlatIcon,
    TrendingUp
} from '@mui/icons-material';
import { ModernCard, ModernCardHeader } from '@shared/components/ui';
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
 *
 * NOTE: This is a MOCK/DEMO component for demonstration purposes only.
 * The real production implementation is located at:
 * /apps/frontend/src/services/PredictiveAnalyticsService.tsx
 */

interface TabPanelProps {
    children: React.ReactNode;
    value: number;
    index: number;
}

interface PredictiveStats {
    accuracy: number;
    activeModels: number;
    predictionsMade: number;
    confidenceScore: number;
}

interface Forecast {
    metric: string;
    currentValue: string | number;
    predictedValue: string | number;
    trend: 'up' | 'down' | 'flat';
    change: string;
    confidence: number;
}

interface TrendInsight {
    title: string;
    description: string;
    impact: 'High' | 'Medium' | 'Low';
    timeframe: string;
}

interface ForecastModel {
    name: string;
    description: string;
    accuracy: number;
    status: 'Active' | 'Inactive';
}

type TimeRange = '7d' | '30d' | '90d' | '1y';

const PredictiveAnalyticsService: React.FC = () => {
    const [currentTab, setCurrentTab] = useState<number>(0);
    const [timeRange, setTimeRange] = useState<TimeRange>('30d');
    const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);

    // Use mock data (type assertions for demo compatibility)
    const stats: PredictiveStats = predictiveStats as any;
    const predictions: Forecast[] = mockForecasts as any;
    const insights: TrendInsight[] = trendInsights as any;
    const models: ForecastModel[] = forecastModels as any;

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number): void => {
        setCurrentTab(newValue);
    };

    const handleTimeRangeChange = (event: SelectChangeEvent<TimeRange>): void => {
        setTimeRange(event.target.value as TimeRange);
    };

    const handleAnalyze = (): void => {
        setIsAnalyzing(true);
        setTimeout(() => setIsAnalyzing(false), 3000);
    };

    const getTrendIcon = (trend: string): React.ReactNode => {
        switch(trend) {
            case 'up': return <TrendingUp color="success" />;
            case 'down': return <DownIcon color="error" />;
            case 'flat': return <FlatIcon color="warning" />;
            default: return <TimelineIcon />;
        }
    };

    const getTrendColor = (trend: string): string => {
        switch(trend) {
            case 'up': return '#4caf50';
            case 'down': return '#f44336';
            case 'flat': return '#ff9800';
            default: return '#2196f3';
        }
    };

    const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
        <div hidden={value !== index} style={{ paddingTop: (SEMANTIC_SPACING as any).sections?.small || 16 }}>
            {value === index && children}
        </div>
    );

    return (
        <Box sx={{ p: (SEMANTIC_SPACING as any).sections?.medium || 3 }}>
            {/* Header */}
            <Box sx={{ mb: (SEMANTIC_SPACING as any).sections?.medium || 3 }}>
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
            <Grid container spacing={(SEMANTIC_SPACING as any).components?.medium || 2} sx={{ mb: (SEMANTIC_SPACING as any).sections?.medium || 3 }}>
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
                                    {(predictions || []).map((prediction: Forecast, index: number) => (
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
                            {(insights || []).map((insight: TrendInsight, index: number) => (
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
                            {(models || []).map((model: ForecastModel, index: number) => (
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
