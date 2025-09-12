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
    FormControlLabel
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

/**
 * Churn Predictor Service Page
 * Advanced customer retention analysis and risk assessment
 */
const ChurnPredictorService = () => {
    const [currentTab, setCurrentTab] = useState(0);
    const [riskThreshold, setRiskThreshold] = useState('medium');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [autoMonitoring, setAutoMonitoring] = useState(true);

    const serviceStats = {
        churnRate: '12.3%',
        atRiskUsers: 47,
        savedCustomers: 23,
        status: 'beta'
    };

    const riskUsers = [
        {
            id: 1,
            username: '@marketingpro',
            riskScore: 85,
            riskLevel: 'high',
            lastActive: '3 days ago',
            engagementDrop: '-45%',
            factors: ['Decreased activity', 'No recent purchases', 'Support complaints']
        },
        {
            id: 2,
            username: '@socialmedia_exp',
            riskScore: 72,
            riskLevel: 'high',
            lastActive: '1 day ago',
            engagementDrop: '-32%',
            factors: ['Reduced engagement', 'Payment issues', 'Feature complaints']
        },
        {
            id: 3,
            username: '@content_creator',
            riskScore: 58,
            riskLevel: 'medium',
            lastActive: '2 hours ago',
            engagementDrop: '-18%',
            factors: ['Irregular usage pattern', 'Competitor mentions']
        },
        {
            id: 4,
            username: '@business_growth',
            riskScore: 34,
            riskLevel: 'low',
            lastActive: '30 minutes ago',
            engagementDrop: '-8%',
            factors: ['Slight activity decrease']
        }
    ];

    const retentionStrategies = [
        {
            strategy: 'Personalized Re-engagement Campaign',
            effectiveness: '78%',
            targetGroup: 'High Risk Users',
            description: 'Customized content and offers based on user behavior'
        },
        {
            strategy: 'Feature Education Program',
            effectiveness: '65%',
            targetGroup: 'Medium Risk Users',
            description: 'Guided tutorials for underutilized features'
        },
        {
            strategy: 'Premium Support Access',
            effectiveness: '82%',
            targetGroup: 'All Risk Levels',
            description: 'Priority customer support and dedicated assistance'
        }
    ];

    const getRiskColor = (level) => {
        switch (level) {
            case 'high': return 'error';
            case 'medium': return 'warning';
            case 'low': return 'success';
            default: return 'default';
        }
    };

    const getRiskIcon = (level) => {
        switch (level) {
            case 'high': return <HighRiskIcon color="error" />;
            case 'medium': return <WarningIcon color="warning" />;
            case 'low': return <SafeIcon color="success" />;
            default: return <SafeIcon />;
        }
    };

    const handleAnalyze = () => {
        setIsAnalyzing(true);
        setTimeout(() => setIsAnalyzing(false), 5000);
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
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="error.main" fontWeight={600}>
                                {serviceStats.churnRate}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Current Churn Rate
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="warning.main" fontWeight={600}>
                                {serviceStats.atRiskUsers}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Users at Risk
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Card sx={{ textAlign: 'center', p: 2 }}>
                            <Typography variant="h4" color="success.main" fontWeight={600}>
                                {serviceStats.savedCustomers}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                                Customers Saved
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
                                {isAnalyzing ? 'Analyzing...' : 'Analyze Risk'}
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
                                    onChange={(e) => setRiskThreshold(e.target.value)}
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
                            {riskUsers.map((user) => (
                                <ListItem 
                                    key={user.id}
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
                                            {user.factors.map((factor, index) => (
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
                            ))}
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
                            {retentionStrategies.map((strategy, index) => (
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
                            ))}
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
            </Card>
        </Box>
    );
};

export default ChurnPredictorService;