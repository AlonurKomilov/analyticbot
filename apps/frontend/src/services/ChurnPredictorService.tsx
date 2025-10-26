import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Button,
    Grid,
    Chip,
    Alert,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Tabs,
    Tab,
    LinearProgress,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Switch,
    FormControlLabel,
    Card,
    CardContent,
    CircularProgress,
    SelectChangeEvent
} from '@mui/material';
import {
    PersonRemove as ChurnIcon,
    Warning as WarningIcon,
    CheckCircle as SafeIcon,
    Error as HighRiskIcon,
    Analytics as AnalyticsIcon,
    Settings as SettingsIcon,
    Shield as ProtectionIcon
} from '@mui/icons-material';
import { ModernCard } from '@shared/components/ui';
import { SEMANTIC_SPACING } from '../theme/spacingSystem';
import { apiClient } from '../api/client';

interface ChurnStats {
    churnRate?: string;
    highRiskUsers?: number;
    savedCustomers?: number;
}

interface RiskUser {
    userId?: string;
    id?: string;
    username: string;
    lastActive: string;
    engagementDrop: string;
    riskLevel: 'high' | 'medium' | 'low';
    riskScore: number;
    factors?: string[];
}

interface RetentionStrategy {
    strategy: string;
    effectiveness: string;
    targetGroup: string;
    description: string;
}

interface TabPanelProps {
    children: React.ReactNode;
    value: number;
    index: number;
}

type RiskLevel = 'high' | 'medium' | 'low';
type RiskThreshold = 'low' | 'medium' | 'high';

/**
 * Churn Predictor Service Page
 * Advanced customer retention analysis and risk assessment
 */
const ChurnPredictorService: React.FC = () => {
    const [currentTab, setCurrentTab] = useState<number>(0);
    const [riskThreshold, setRiskThreshold] = useState<RiskThreshold>('medium');
    const [autoMonitoring, setAutoMonitoring] = useState<boolean>(true);
    const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);

    // Real data state
    const [stats, setStats] = useState<ChurnStats | null>(null);
    const [riskUsers, setRiskUsers] = useState<RiskUser[]>([]);
    const [strategies, setStrategies] = useState<RetentionStrategy[]>([]);

    // Load real churn prediction data
    useEffect(() => {
        const loadChurnData = async (): Promise<void> => {
            setLoading(true);
            setError(null);

            try {
                // Real API calls would go here
                const [statsResponse, usersResponse, strategiesResponse] = await Promise.all([
                    apiClient.get('/ai/churn/stats'),
                    apiClient.get('/ai/churn/predictions'),
                    apiClient.get('/ai/churn/strategies')
                ]);

                setStats((statsResponse as any).data);
                setRiskUsers((usersResponse as any).data);
                setStrategies((strategiesResponse as any).data);
            } catch (err) {
                setError('Failed to load churn prediction data');
                console.error('Churn data loading error:', err);
            } finally {
                setLoading(false);
            }
        };

        loadChurnData();
    }, []);

    const getRiskColor = (level: RiskLevel): 'error' | 'warning' | 'success' | 'default' => {
        switch (level) {
            case 'high': return 'error';
            case 'medium': return 'warning';
            case 'low': return 'success';
            default: return 'default';
        }
    };

    const getRiskIcon = (level: RiskLevel): React.ReactNode => {
        switch (level) {
            case 'high': return <HighRiskIcon color="error" />;
            case 'medium': return <WarningIcon color="warning" />;
            case 'low': return <SafeIcon color="success" />;
            default: return <SafeIcon />;
        }
    };

    const handleAnalyze = (): void => {
        setIsAnalyzing(true);
        setTimeout(() => setIsAnalyzing(false), 5000);
    };

    const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
        <div hidden={value !== index}>
            {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
        </div>
    );

    // Show loading state
    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                <CircularProgress />
                <Typography sx={{ ml: 2 }}>Loading churn prediction data...</Typography>
            </Box>
        );
    }

    // Show error state
    if (error) {
        return (
            <Box sx={{ p: 3 }}>
                <Alert severity="error" sx={{ mb: 2 }}>
                    {error}
                </Alert>
                <Button variant="contained" onClick={() => window.location.reload()}>
                    Retry
                </Button>
            </Box>
        );
    }

    return (
        <Box>
            {/* Service Header */}
            <Box sx={{ mb: 4 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <ChurnIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                    <Typography variant="h4" component="h1" fontWeight={600}>
                        Churn Predictor
                    </Typography>
                    <Chip
                        label="Beta"
                        color="warning"
                        variant="filled"
                        sx={{ ml: 'auto' }}
                    />
                </Box>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                    Advanced customer retention analysis with predictive risk assessment and intervention strategies
                </Typography>

                {/* Quick Stats */}
                <Grid container spacing={3}>
                    <Grid item xs={12} sm={6} md={3}>
                        <ModernCard variant="standard" sx={{ textAlign: 'center' }}>
                            <Typography
                                variant="h4"
                                color="error.main"
                                fontWeight={600}
                                sx={{ mb: SEMANTIC_SPACING.ELEMENT_SPACING }}
                            >
                                {stats?.churnRate || 'N/A'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Current Churn Rate
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
                                {stats?.highRiskUsers || 'N/A'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Users at Risk
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
                                {stats?.savedCustomers || 'N/A'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Customers Saved
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
                                {isAnalyzing ? 'Analyzing...' : 'Analyze Risk'}
                            </Button>
                        </ModernCard>
                    </Grid>
                </Grid>
            </Box>

            {/* Service Tabs */}
            <ModernCard variant="elevated">
                <Tabs
                    value={currentTab}
                    onChange={(_e, newValue: number) => setCurrentTab(newValue)}
                    sx={{ borderBottom: 1, borderColor: 'divider' }}
                >
                    <Tab label="Risk Dashboard" icon={<WarningIcon />} />
                    <Tab label="Retention Strategies" icon={<ProtectionIcon />} />
                    <Tab label="Settings" icon={<SettingsIcon />} />
                </Tabs>

                {/* Risk Dashboard Tab */}
                <TabPanel value={currentTab} index={0}>
                    <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                            <Typography variant="h6">
                                High-Risk Users
                            </Typography>
                            <FormControl size="small">
                                <InputLabel>Risk Threshold</InputLabel>
                                <Select
                                    value={riskThreshold}
                                    label="Risk Threshold"
                                    onChange={(e: SelectChangeEvent) => setRiskThreshold(e.target.value as RiskThreshold)}
                                >
                                    <MenuItem value="low">Low Risk (30+)</MenuItem>
                                    <MenuItem value="medium">Medium Risk (50+)</MenuItem>
                                    <MenuItem value="high">High Risk (70+)</MenuItem>
                                </Select>
                            </FormControl>
                        </Box>

                        {isAnalyzing && (
                            <Alert severity="info" sx={{ mb: 3 }}>
                                <Typography variant="body2" sx={{ mb: 1 }}>
                                    Analyzing customer behavior patterns...
                                </Typography>
                                <LinearProgress />
                            </Alert>
                        )}

                        <List>
                            {riskUsers && riskUsers.length > 0 ? riskUsers.map((user) => (
                                <ListItem
                                    key={user.userId || user.id}
                                    sx={{
                                        border: 1,
                                        borderColor: 'divider',
                                        borderRadius: 2,
                                        mb: 2,
                                        flexDirection: 'column',
                                        alignItems: 'stretch'
                                    }}
                                >
                                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', mb: 1 }}>
                                        <ListItemIcon>
                                            {getRiskIcon(user.riskLevel)}
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={user.username}
                                            secondary={`Last active: ${user.lastActive} • Engagement: ${user.engagementDrop}`}
                                        />
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Typography variant="h6" sx={{ minWidth: 60, textAlign: 'center' }}>
                                                {user.riskScore}%
                                            </Typography>
                                            <Chip
                                                label={user.riskLevel.toUpperCase()}
                                                color={getRiskColor(user.riskLevel)}
                                                size="small"
                                            />
                                        </Box>
                                    </Box>

                                    <Box sx={{ pl: 7 }}>
                                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                            <strong>Risk Factors:</strong>
                                        </Typography>
                                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                            {(user.factors || []).map((factor, index) => (
                                                <Chip
                                                    key={index}
                                                    label={factor}
                                                    size="small"
                                                    variant="outlined"
                                                />
                                            ))}
                                        </Box>
                                    </Box>
                                </ListItem>
                            )) : (
                                <ListItem>
                                    <Typography variant="body2" color="text.secondary">
                                        No risk users data available. Please check your connection or try again later.
                                    </Typography>
                                </ListItem>
                            )}
                        </List>
                    </CardContent>
                </TabPanel>

                {/* Retention Strategies Tab */}
                <TabPanel value={currentTab} index={1}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 3 }}>
                            Recommended Retention Strategies
                        </Typography>

                        <Grid container spacing={3}>
                            {strategies && strategies.length > 0 ? strategies.map((strategy, index) => (
                                <Grid item xs={12} md={6} key={index}>
                                    <Card sx={{ p: 3, height: '100%' }}>
                                        <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
                                            {strategy.strategy}
                                        </Typography>

                                        <Box sx={{ mb: 2 }}>
                                            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                                                Effectiveness Rate
                                            </Typography>
                                            <Typography variant="h5" color="success.main" fontWeight={600}>
                                                {strategy.effectiveness}
                                            </Typography>
                                        </Box>

                                        <Chip
                                            label={strategy.targetGroup}
                                            color="primary"
                                            size="small"
                                            sx={{ mb: 2 }}
                                        />

                                        <Typography variant="body2" color="text.secondary">
                                            {strategy.description}
                                        </Typography>

                                        <Button
                                            variant="outlined"
                                            fullWidth
                                            sx={{ mt: 2, minHeight: 44 }}
                                        >
                                            Deploy Strategy
                                        </Button>
                                    </Card>
                                </Grid>
                            )) : (
                                <Grid item xs={12}>
                                    <Typography variant="body2" color="text.secondary" textAlign="center">
                                        No retention strategies available. Please check your connection or try again later.
                                    </Typography>
                                </Grid>
                            )}
                        </Grid>
                    </CardContent>
                </TabPanel>

                {/* Settings Tab */}
                <TabPanel value={currentTab} index={2}>
                    <CardContent>
                        <Typography variant="h6" sx={{ mb: 3 }}>
                            Churn Prediction Settings
                        </Typography>

                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={autoMonitoring}
                                        onChange={(e) => setAutoMonitoring(e.target.checked)}
                                    />
                                }
                                label="Automatic Risk Monitoring"
                            />

                            <FormControlLabel
                                control={<Switch defaultChecked />}
                                label="Real-time Alerts"
                            />

                            <FormControlLabel
                                control={<Switch />}
                                label="Weekly Risk Reports"
                            />

                            <Alert severity="warning" sx={{ mt: 2 }}>
                                This service is in Beta. Prediction accuracy may vary and should be used in conjunction with other retention strategies.
                            </Alert>
                        </Box>
                    </CardContent>
                </TabPanel>
            </ModernCard>
        </Box>
    );
};

export default ChurnPredictorService;
