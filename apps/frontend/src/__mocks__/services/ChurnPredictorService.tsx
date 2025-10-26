import React, { useState, ChangeEvent } from 'react';
import {
    Box,
    Typography,
    Button,
    Grid,
    Chip,
    Alert,
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
import { ModernCard, ModernCardHeader } from '@shared/components/ui';
import { SEMANTIC_SPACING } from '../../theme/spacingSystem.js';

// Import mock data
import {
    churnPredictorStats,
    mockChurnPredictions,
    retentionStrategies
} from '../aiServices/churnPredictor.js';

/**
 * Mock Churn Predictor Service Page
 * Demo implementation with mock data for demo users
 *
 * NOTE: This is a MOCK/DEMO component for demonstration purposes only.
 * The real production implementation is located at:
 * /apps/frontend/src/services/ChurnPredictorService.tsx
 */

interface TabPanelProps {
    children: React.ReactNode;
    value: number;
    index: number;
}

interface ChurnUser {
    id: string;
    name: string;
    risk: 'high' | 'medium' | 'low';
    score: number;
    factors: string[];
}

interface RetentionStrategy {
    title: string;
    description: string;
    targetAudience: string;
    expectedImpact: string;
}

interface ChurnStats {
    totalCustomers: number;
    atRisk: number;
    retentionRate: number;
    avgRiskScore: number;
}

type RiskThreshold = 'all' | 'high' | 'medium';

const ChurnPredictorService: React.FC = () => {
    const [currentTab, setCurrentTab] = useState<number>(0);
    const [riskThreshold, setRiskThreshold] = useState<RiskThreshold>('medium');
    const [autoRefresh, setAutoRefresh] = useState<boolean>(true);

    // Use mock data with safety checks (type assertions for demo compatibility)
    const stats: ChurnStats = churnPredictorStats as any;
    const riskUsers: ChurnUser[] = (mockChurnPredictions as any) || [];
    const strategies: RetentionStrategy[] = (retentionStrategies as any) || [];

    const handleTabChange = (_event: React.SyntheticEvent, newValue: number): void => {
        setCurrentTab(newValue);
    };

    const handleThresholdChange = (event: SelectChangeEvent<RiskThreshold>): void => {
        setRiskThreshold(event.target.value as RiskThreshold);
    };

    const getRiskColor = (risk: string): string => {
        switch(risk) {
            case 'high': return '#f44336';
            case 'medium': return '#ff9800';
            case 'low': return '#4caf50';
            default: return '#757575';
        }
    };

    const getRiskIcon = (risk: string): React.ReactNode => {
        switch(risk) {
            case 'high': return <HighRiskIcon sx={{ color: '#f44336' }} />;
            case 'medium': return <WarningIcon sx={{ color: '#ff9800' }} />;
            case 'low': return <SafeIcon sx={{ color: '#4caf50' }} />;
            default: return <ChurnIcon />;
        }
    };

    const filteredUsers = riskUsers.filter((user: ChurnUser) => {
        if (riskThreshold === 'all') return true;
        if (riskThreshold === 'high') return user.risk === 'high';
        if (riskThreshold === 'medium') return user.risk === 'high' || user.risk === 'medium';
        return true;
    });

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
                    <ChurnIcon color="primary" />
                    Churn Predictor
                </Typography>
                <Typography variant="body1" color="text.secondary">
                    Predict customer churn and implement retention strategies using AI-powered analysis.
                </Typography>

                <Alert severity="info" sx={{ mt: 2 }}>
                    🎭 Demo Mode: Showing sample churn prediction data. In production, this would analyze real customer behavior patterns.
                </Alert>
            </Box>

            {/* Statistics Overview */}
            <Grid container spacing={(SEMANTIC_SPACING as any).components?.medium || 2} sx={{ mb: (SEMANTIC_SPACING as any).sections?.medium || 3 }}>
                <Grid item xs={12} sm={6} md={3}>
                    <ModernCard>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>
                                Total Customers
                            </Typography>
                            <Typography variant="h4">
                                {stats?.totalCustomers || 0}
                            </Typography>
                        </CardContent>
                    </ModernCard>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <ModernCard>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>
                                At Risk
                            </Typography>
                            <Typography variant="h4" sx={{ color: '#f44336' }}>
                                {stats?.atRisk || 0}
                            </Typography>
                        </CardContent>
                    </ModernCard>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <ModernCard>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>
                                Retention Rate
                            </Typography>
                            <Typography variant="h4" sx={{ color: '#4caf50' }}>
                                {stats?.retentionRate || 0}%
                            </Typography>
                        </CardContent>
                    </ModernCard>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <ModernCard>
                        <CardContent>
                            <Typography color="text.secondary" gutterBottom>
                                Avg. Risk Score
                            </Typography>
                            <Typography variant="h4">
                                {stats?.avgRiskScore || 0}%
                            </Typography>
                        </CardContent>
                    </ModernCard>
                </Grid>
            </Grid>

            {/* Main Content */}
            <ModernCard>
                <ModernCardHeader
                    title="Churn Analysis"
                    action={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={autoRefresh}
                                        onChange={(e: ChangeEvent<HTMLInputElement>) => setAutoRefresh(e.target.checked)}
                                    />
                                }
                                label="Auto Refresh"
                            />
                            <FormControl size="small" sx={{ minWidth: 120 }}>
                                <InputLabel>Risk Filter</InputLabel>
                                <Select
                                    value={riskThreshold}
                                    label="Risk Filter"
                                    onChange={handleThresholdChange}
                                >
                                    <MenuItem value="all">All</MenuItem>
                                    <MenuItem value="high">High Risk Only</MenuItem>
                                    <MenuItem value="medium">Medium+ Risk</MenuItem>
                                </Select>
                            </FormControl>
                        </Box>
                    }
                />

                <Tabs
                    value={currentTab}
                    onChange={handleTabChange}
                    sx={{ px: 3, borderBottom: 1, borderColor: 'divider' }}
                >
                    <Tab label="Risk Assessment" icon={<AnalyticsIcon />} />
                    <Tab label="Retention Strategies" icon={<ProtectionIcon />} />
                    <Tab label="Settings" icon={<SettingsIcon />} />
                </Tabs>

                {/* Risk Assessment Tab */}
                <TabPanel value={currentTab} index={0}>
                    <Box sx={{ p: 3 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Customer Risk Analysis ({filteredUsers.length} customers)
                        </Typography>

                        <Grid container spacing={2}>
                            {(filteredUsers || []).map((user: ChurnUser, index: number) => (
                                <Grid item xs={12} md={6} key={index}>
                                    <Card variant="outlined">
                                        <CardContent>
                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                                <Box>
                                                    <Typography variant="h6">
                                                        {user.name}
                                                    </Typography>
                                                    <Typography variant="body2" color="text.secondary">
                                                        Customer ID: {user.id}
                                                    </Typography>
                                                </Box>
                                                {getRiskIcon(user.risk)}
                                            </Box>

                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" sx={{ mb: 1 }}>
                                                    Risk Score: {user.score}%
                                                </Typography>
                                                <LinearProgress
                                                    variant="determinate"
                                                    value={user.score}
                                                    sx={{
                                                        height: 8,
                                                        borderRadius: 4,
                                                        '& .MuiLinearProgress-bar': {
                                                            backgroundColor: getRiskColor(user.risk)
                                                        }
                                                    }}
                                                />
                                            </Box>

                                            <Typography variant="body2" sx={{ mb: 1 }}>
                                                <strong>Risk Factors:</strong>
                                            </Typography>
                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                                {(user.factors || []).map((factor: string, index: number) => (
                                                    <Chip
                                                        key={index}
                                                        label={factor}
                                                        size="small"
                                                        variant="outlined"
                                                    />
                                                ))}
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                </TabPanel>

                {/* Retention Strategies Tab */}
                <TabPanel value={currentTab} index={1}>
                    <Box sx={{ p: 3 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Recommended Retention Strategies
                        </Typography>

                        <Grid container spacing={2}>
                            {(strategies || []).map((strategy: RetentionStrategy, index: number) => (
                                <Grid item xs={12} md={6} key={index}>
                                    <Card variant="outlined">
                                        <CardContent>
                                            <Typography variant="h6" sx={{ mb: 1 }}>
                                                {strategy.title}
                                            </Typography>
                                            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                                {strategy.description}
                                            </Typography>

                                            <Box sx={{ mb: 2 }}>
                                                <Typography variant="body2" sx={{ mb: 1 }}>
                                                    Target Audience:
                                                </Typography>
                                                <Chip
                                                    label={strategy.targetAudience}
                                                    color="primary"
                                                    variant="outlined"
                                                />
                                            </Box>

                                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <Typography variant="body2">
                                                    Expected Impact: <strong>{strategy.expectedImpact}</strong>
                                                </Typography>
                                                <Button size="small" variant="outlined">
                                                    Implement
                                                </Button>
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                    </Box>
                </TabPanel>

                {/* Settings Tab */}
                <TabPanel value={currentTab} index={2}>
                    <Box sx={{ p: 3 }}>
                        <Typography variant="h6" sx={{ mb: 2 }}>
                            Prediction Settings
                        </Typography>

                        <Alert severity="info">
                            🎭 Demo Mode: Settings are simulated for demonstration purposes.
                        </Alert>

                        <Box sx={{ mt: 2 }}>
                            <Typography variant="body1">
                                Configure churn prediction parameters, model thresholds, and notification settings.
                            </Typography>
                        </Box>
                    </Box>
                </TabPanel>
            </ModernCard>
        </Box>
    );
};

export default ChurnPredictorService;
