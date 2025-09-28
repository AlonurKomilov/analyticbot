import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Timeline as TimelineIcon,
  Notifications as NotificationsIcon,
  NotificationsActive as NotificationsActiveIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { useDataSource, useAllAnalytics, useAnalytics } from '../../hooks/useDataSource';

const AdvancedAnalyticsDashboard = ({ channelId = 'demo_channel' }) => {
  const theme = useTheme();
  const { dataSource, isUsingRealAPI, switchDataSource } = useDataSource();
  const { 
    overview, 
    postDynamics, 
    topPosts, 
    bestTime,
    isLoading,
    hasError,
    errors,
    actions 
  } = useAllAnalytics(channelId);
  
  const [trends, setTrends] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  // Create computed metrics from the new data structure
  const metrics = overview ? {
    totalViews: overview.totalViews || 0,
    growthRate: overview.growthRate || 0,
    engagementRate: overview.avgEngagement || 0,
    reachScore: overview.reachScore || 76, // Default value for demo
    activeUsers: overview.activeUsers || 0,
  } : null;

  // Process analytics data when it loads
  useEffect(() => {
    if (overview) {
      // Generate smart alerts based on data
      generateSmartAlerts(overview, postDynamics, topPosts);

      // Convert top posts to trends format for charts
      if (topPosts?.length) {
        setTrends(topPosts.slice(0, 10));
      }
    }
  }, [overview, postDynamics, topPosts]);

  const generateSmartAlerts = (overviewData, dynamicsData, topPostsData) => {
    const newAlerts = [];

    if (!overviewData) return;

    // Growth spike alert
    if (overviewData.growthRate && overviewData.growthRate > 15) {
      newAlerts.push({
        id: 'growth-spike',
        type: 'success',
        title: '🚀 Growth Spike Detected!',
        message: `${overviewData.growthRate.toFixed(1)}% growth detected`,
        timestamp: new Date().toISOString(),
      });
    }

    // Low engagement alert
    if (overviewData.avgEngagement && overviewData.avgEngagement < 3) {
      newAlerts.push({
        id: 'low-engagement',
        type: 'warning',
        title: '⚠️ Low Engagement Alert',
        message: `Engagement rate dropped to ${overviewData.avgEngagement?.toFixed(1)}%`,
        timestamp: new Date().toISOString(),
      });
    }

    // High view count achievement
    if (overviewData.totalViews && overviewData.totalViews > 50000) {
      newAlerts.push({
        id: 'high-views',
        type: 'info',
        title: '🎯 Excellent Views!',
        message: `Total views reached ${overviewData.totalViews.toLocaleString()}`,
        timestamp: new Date().toISOString(),
      });
    }

    // Active post performance
    if (topPostsData?.length && topPostsData[0].views > 10000) {
      newAlerts.push({
        id: 'viral-post',
        type: 'success',
        title: '🔥 Viral Post Alert!',
        message: `Top post reached ${topPostsData[0].views.toLocaleString()} views`,
        timestamp: new Date().toISOString(),
      });
    }

    setAlerts(newAlerts);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    // Use the refetchAll action from useAllAnalytics
    await actions.refetchAll();
    setTimeout(() => {
      setRefreshing(false);
    }, 500);
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  const getMetricColor = (value, thresholds = { good: 10, warning: 5 }) => {
    if (value >= thresholds.good) return theme.palette.success.main;
    if (value >= thresholds.warning) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Advanced Analytics Dashboard
        </Typography>
        <LinearProgress sx={{ mt: 2 }} />
        <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
          Loading analytics data from {isUsingRealAPI ? 'real API' : 'mock service'}...
        </Typography>
      </Box>
    );
  }

  if (hasError) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Advanced Analytics Dashboard
        </Typography>
        <Alert severity="error" sx={{ mt: 2 }}>
          <Typography variant="h6">Failed to load analytics data</Typography>
          <Typography variant="body2">
            {Object.values(errors).filter(Boolean).join(', ') || 'Unknown error occurred'}
          </Typography>
          <Box sx={{ mt: 2 }}>
            <button onClick={actions.clearAllErrors} style={{ marginRight: 8 }}>
              Clear Errors
            </button>
            <button onClick={handleRefresh}>
              Retry
            </button>
          </Box>
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Advanced Analytics Dashboard
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip 
            icon={<NotificationsActiveIcon />} 
            label={`${alerts.length} Active Alerts`}
            color={alerts.length > 0 ? 'warning' : 'default'}
            size="small"
          />
          <Tooltip title="Refresh Data">
            <IconButton 
              onClick={handleRefresh} 
              disabled={refreshing}
              size="small"
            >
              <RefreshIcon sx={{ 
                animation: refreshing ? 'spin 1s linear infinite' : 'none',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' },
                }
              }} />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Error Alert */}
      {hasError && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {Object.values(errors).filter(Boolean).join(', ') || 'Analytics data loading failed'}
        </Alert>
      )}

      {/* Smart Alerts */}
      {alerts.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {alerts.map((alert) => (
            <Alert 
              key={alert.id} 
              severity={alert.type} 
              sx={{ mb: 1 }}
              icon={<NotificationsIcon />}
            >
              <Typography variant="subtitle2">{alert.title}</Typography>
              <Typography variant="body2">{alert.message}</Typography>
            </Alert>
          ))}
        </Box>
      )}

      {/* Key Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Total Views
                  </Typography>
                  <Typography variant="h5" component="div">
                    {formatNumber(metrics?.totalViews)}
                  </Typography>
                </Box>
                <TrendingUpIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Growth Rate
                  </Typography>
                  <Typography 
                    variant="h5" 
                    component="div"
                    sx={{ color: getMetricColor(metrics?.growthRate) }}
                  >
                    {metrics?.growthRate?.toFixed(1)}%
                  </Typography>
                </Box>
                {metrics?.growthRate > 0 ? 
                  <TrendingUpIcon sx={{ color: getMetricColor(metrics?.growthRate), fontSize: 40 }} /> :
                  <TrendingDownIcon color="error" sx={{ fontSize: 40 }} />
                }
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Engagement Rate
                  </Typography>
                  <Typography 
                    variant="h5" 
                    component="div"
                    sx={{ color: getMetricColor(metrics?.engagementRate) }}
                  >
                    {metrics?.engagementRate?.toFixed(1)}%
                  </Typography>
                </Box>
                <Box 
                  sx={{ 
                    width: 40, 
                    height: 40, 
                    borderRadius: '50%', 
                    backgroundColor: theme.palette.primary.main,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '0.8rem',
                    fontWeight: 'bold'
                  }}
                >
                  {metrics?.engagementRate?.toFixed(0)}%
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Reach Score
                  </Typography>
                  <Typography variant="h5" component="div">
                    {metrics?.reachScore}%
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={metrics?.reachScore || 0} 
                  sx={{ 
                    width: 40, 
                    height: 8, 
                    borderRadius: 4,
                    transform: 'rotate(-90deg)',
                    transformOrigin: 'center'
                  }} 
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom variant="body2">
                    Active Users
                  </Typography>
                  <Typography variant="h5" component="div">
                    {formatNumber(metrics?.activeUsers)}
                  </Typography>
                </Box>
                <Box 
                  sx={{ 
                    width: 40, 
                    height: 40, 
                    borderRadius: '50%', 
                    backgroundColor: theme.palette.success.main,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '1.2rem'
                  }}
                >
                  👥
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Advanced Charts */}
      <Grid container spacing={3}>
        {/* Trends Chart */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📈 Weekly Performance Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Line 
                    type="monotone" 
                    dataKey="views" 
                    stroke={theme.palette.primary.main} 
                    strokeWidth={3}
                    name="Views"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="engagement" 
                    stroke={theme.palette.secondary.main} 
                    strokeWidth={3}
                    name="Engagement"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Distribution */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🎯 Performance Score
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', pt: 2 }}>
                <Box 
                  sx={{ 
                    width: 120, 
                    height: 120, 
                    borderRadius: '50%', 
                    background: `conic-gradient(${theme.palette.success.main} ${(metrics?.engagementRate || 0) * 3.6}deg, ${theme.palette.grey[300]} 0deg)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    mb: 2
                  }}
                >
                  <Box 
                    sx={{ 
                      width: 90, 
                      height: 90, 
                      borderRadius: '50%', 
                      backgroundColor: theme.palette.background.paper,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexDirection: 'column'
                    }}
                  >
                    <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                      {Math.round((metrics?.engagementRate || 0) * 10)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Score
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary" align="center">
                  Based on engagement rate, growth, and reach metrics
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AdvancedAnalyticsDashboard;
