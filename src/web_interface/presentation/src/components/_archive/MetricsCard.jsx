import React, { useState } from 'react';
import {
    Card,
    CardContent,
    Typography,
    Box,
    Grid,
    Chip,
    IconButton,
    Tooltip,
    Avatar,
    LinearProgress,
    Divider,
    Button,
    Collapse
} from '@mui/material';
import {
    TrendingUp as TrendingUpIcon,
    TrendingDown as TrendingDownIcon,
    TrendingFlat as TrendingFlatIcon,
    Visibility as ViewsIcon,
    ThumbUp as EngagementIcon,
    Speed as SpeedIcon,
    Star as StarIcon,
    ExpandMore as ExpandMoreIcon,
    ExpandLess as ExpandLessIcon,
    Refresh as RefreshIcon,
    Analytics as AnalyticsIcon
} from '@mui/icons-material';

const MetricsCard = ({ metrics, loading = false, onRefresh, showDetails = true }) => {
    const [expanded, setExpanded] = useState(false);

    if (loading) {
        return (
            <Card sx={{ minHeight: 200 }}>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Loading Metrics...
                    </Typography>
                    <LinearProgress sx={{ mt: 2 }} />
                </CardContent>
            </Card>
        );
    }

    if (!metrics) {
        return (
            <Card sx={{ minHeight: 200 }}>
                <CardContent>
                    <Typography variant="h6" color="text.secondary">
                        No metrics data available
                    </Typography>
                </CardContent>
            </Card>
        );
    }

    const {
        totalViews = 0,
        growthRate = 0,
        engagementRate = 0,
        reachScore = 0,
        activeUsers = 0,
        performanceScore = 0
    } = metrics;

    const getTrendIcon = (value) => {
        if (value > 5) return <TrendingUpIcon color="success" />;
        if (value < -5) return <TrendingDownIcon color="error" />;
        return <TrendingFlatIcon color="warning" />;
    };

    const getScoreColor = (score) => {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'error';
    };

    const getPerformanceLevel = (score) => {
        if (score >= 90) return 'Excellent';
        if (score >= 75) return 'Good';
        if (score >= 60) return 'Average';
        if (score >= 40) return 'Below Average';
        return 'Needs Attention';
    };

    return (
        <Card sx={{ 
            height: '100%',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'visible'
        }}>
            <CardContent>
                {/* Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <AnalyticsIcon />
                        Performance Metrics
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                        {onRefresh && (
                            <Tooltip title="Refresh metrics">
                                <IconButton size="small" onClick={onRefresh} sx={{ color: 'white' }}>
                                    <RefreshIcon />
                                </IconButton>
                            </Tooltip>
                        )}
                        {showDetails && (
                            <Tooltip title={expanded ? "Show less" : "Show more"}>
                                <IconButton 
                                    size="small" 
                                    onClick={() => setExpanded(!expanded)}
                                    sx={{ color: 'white' }}
                                >
                                    {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                                </IconButton>
                            </Tooltip>
                        )}
                    </Box>
                </Box>

                {/* Main Metrics Grid */}
                <Grid container spacing={2}>
                    {/* Total Views */}
                    <Grid item xs={6} md={3}>
                        <Box sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1 }}>
                                <ViewsIcon />
                            </Avatar>
                            <Typography variant="h5" fontWeight="bold">
                                {totalViews.toLocaleString()}
                            </Typography>
                            <Typography variant="caption" sx={{ opacity: 0.9 }}>
                                Total Views
                            </Typography>
                        </Box>
                    </Grid>

                    {/* Growth Rate */}
                    <Grid item xs={6} md={3}>
                        <Box sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1 }}>
                                {getTrendIcon(growthRate)}
                            </Avatar>
                            <Typography variant="h5" fontWeight="bold">
                                {growthRate > 0 ? '+' : ''}{growthRate.toFixed(1)}%
                            </Typography>
                            <Typography variant="caption" sx={{ opacity: 0.9 }}>
                                Growth Rate
                            </Typography>
                        </Box>
                    </Grid>

                    {/* Engagement Rate */}
                    <Grid item xs={6} md={3}>
                        <Box sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1 }}>
                                <EngagementIcon />
                            </Avatar>
                            <Typography variant="h5" fontWeight="bold">
                                {engagementRate.toFixed(1)}%
                            </Typography>
                            <Typography variant="caption" sx={{ opacity: 0.9 }}>
                                Engagement
                            </Typography>
                        </Box>
                    </Grid>

                    {/* Performance Score */}
                    <Grid item xs={6} md={3}>
                        <Box sx={{ textAlign: 'center' }}>
                            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1 }}>
                                <StarIcon />
                            </Avatar>
                            <Typography variant="h5" fontWeight="bold">
                                {performanceScore}
                            </Typography>
                            <Typography variant="caption" sx={{ opacity: 0.9 }}>
                                Score
                            </Typography>
                        </Box>
                    </Grid>
                </Grid>

                {/* Performance Level Indicator */}
                <Box sx={{ mt: 3, mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" sx={{ opacity: 0.9 }}>
                            Performance Level
                        </Typography>
                        <Chip 
                            label={getPerformanceLevel(performanceScore)}
                            color={getScoreColor(performanceScore)}
                            size="small"
                            sx={{ color: 'white', fontWeight: 'bold' }}
                        />
                    </Box>
                    <LinearProgress 
                        variant="determinate" 
                        value={performanceScore} 
                        sx={{ 
                            height: 8, 
                            borderRadius: 4,
                            bgcolor: 'rgba(255,255,255,0.2)',
                            '& .MuiLinearProgress-bar': {
                                borderRadius: 4,
                                bgcolor: performanceScore >= 70 ? '#4caf50' : performanceScore >= 40 ? '#ff9800' : '#f44336'
                            }
                        }} 
                    />
                </Box>

                {/* Expanded Details */}
                <Collapse in={expanded}>
                    <Divider sx={{ my: 2, bgcolor: 'rgba(255,255,255,0.2)' }} />
                    
                    <Grid container spacing={2}>
                        <Grid item xs={6}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1, width: 32, height: 32 }}>
                                    <SpeedIcon fontSize="small" />
                                </Avatar>
                                <Typography variant="h6" fontWeight="bold">
                                    {reachScore}
                                </Typography>
                                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                                    Reach Score
                                </Typography>
                            </Box>
                        </Grid>
                        
                        <Grid item xs={6}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', mx: 'auto', mb: 1, width: 32, height: 32 }}>
                                    <Typography variant="body2" fontWeight="bold">
                                        {Math.floor(activeUsers / 1000)}K
                                    </Typography>
                                </Avatar>
                                <Typography variant="h6" fontWeight="bold">
                                    {activeUsers.toLocaleString()}
                                </Typography>
                                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                                    Active Users
                                </Typography>
                            </Box>
                        </Grid>
                    </Grid>

                    {/* Performance Insights */}
                    <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                            Quick Insights:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                            {growthRate > 10 && (
                                <Chip 
                                    label="🚀 High Growth" 
                                    size="small" 
                                    sx={{ bgcolor: 'rgba(76, 175, 80, 0.8)', color: 'white' }} 
                                />
                            )}
                            {engagementRate > 5 && (
                                <Chip 
                                    label="💡 Great Engagement" 
                                    size="small" 
                                    sx={{ bgcolor: 'rgba(33, 150, 243, 0.8)', color: 'white' }} 
                                />
                            )}
                            {performanceScore > 80 && (
                                <Chip 
                                    label="⭐ Excellent Performance" 
                                    size="small" 
                                    sx={{ bgcolor: 'rgba(255, 193, 7, 0.8)', color: 'white' }} 
                                />
                            )}
                            {totalViews > 10000 && (
                                <Chip 
                                    label="👥 Popular Content" 
                                    size="small" 
                                    sx={{ bgcolor: 'rgba(156, 39, 176, 0.8)', color: 'white' }} 
                                />
                            )}
                        </Box>
                    </Box>
                </Collapse>
            </CardContent>
        </Card>
    );
};

export default MetricsCard;
