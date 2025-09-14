import React, { useState, useEffect, useCallback } from 'react';
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
  Button,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Timeline as TimelineIcon,
  Notifications as NotificationsIcon,
  NotificationsActive as NotificationsActiveIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
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

// Use new hooks and services
import { useDataSource, useAnalytics } from '../../hooks/useDataSource';
import DataSourceSettings from '../settings/DataSourceSettings';

const ModernAdvancedAnalyticsDashboard = ({ channelId = 'demo_channel' }) => {
  const theme = useTheme();
  const [showSettings, setShowSettings] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState(30);

  // Use new data source hooks
  const { currentDataSource, isUsingMock } = useDataSource();
  
  // Use new analytics hooks with selected period
  const {
    channelOverview,
    engagement,
    growth,
    loading,
    error,
    refreshData: refreshAnalytics
  } = useAnalytics(channelId, selectedPeriod);

  // Handle manual refresh
  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await refreshAnalytics();
    } finally {
      setRefreshing(false);
    }
  }, [refreshAnalytics]);

  // Process analytics data for display
  const processedData = React.useMemo(() => {
    if (!channelOverview || error) return null;

    const rawAnalytics = channelOverview.raw_analytics;
    const timeSeries = rawAnalytics?.time_series || {};
    
    return {
      overview: rawAnalytics?.overview || {},
      subscribers: timeSeries.subscribers || [],
      views: timeSeries.views || [],
      posts: timeSeries.posts || [],
      engagement: timeSeries.engagement || [],
      growth: growth?.raw_growth || {},
      engagementMetrics: engagement?.raw_engagement || {}
    };
  }, [channelOverview, engagement, growth, error]);

  // Format chart data
  const chartData = React.useMemo(() => {
    if (!processedData) return [];
    
    const { subscribers, views, engagement } = processedData;
    
    // Combine all time series data
    return subscribers.map((item, index) => ({
      date: item.date,
      subscribers: item.value,
      views: views[index]?.value || 0,
      engagement: engagement[index]?.value || 0,
    }));
  }, [processedData]);

  // Calculate trend indicators
  const trends = React.useMemo(() => {
    if (!processedData?.overview) return {};
    
    const overview = processedData.overview;
    
    return {
      subscriberTrend: overview.subscriber_change > 0 ? 'up' : 'down',
      subscriberChange: overview.subscriber_change || 0,
      engagementRate: overview.avg_engagement_rate || 0,
      totalViews: overview.total_views || 0,
      totalPosts: overview.total_posts || 0
    };
  }, [processedData]);

  // Mock alerts for demonstration (in real app, these would come from the backend)
  const alerts = React.useMemo(() => {
    if (isUsingMock) {
      return [
        { type: 'info', message: 'Using mock data for demonstration', severity: 'info' },
        { type: 'success', message: 'Engagement rate increased by 15%', severity: 'success' },
        { type: 'warning', message: 'Post frequency below optimal level', severity: 'warning' }
      ];
    }
    return [
      { type: 'info', message: 'Connected to real analytics data', severity: 'info' }
    ];
  }, [isUsingMock]);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Advanced Analytics Dashboard
        </Typography>
        <LinearProgress sx={{ mb: 2 }} />
        <Typography variant="body2" color="text.secondary">
          Loading analytics data from {isUsingMock ? 'mock' : 'real'} data source...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Advanced Analytics Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip 
            label={isUsingMock ? 'Mock Data' : 'Live Data'} 
            color={isUsingMock ? 'warning' : 'success'}
            size="small"
          />
          <Tooltip title="Data Source Settings">
            <IconButton onClick={() => setShowSettings(true)}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefresh} disabled={refreshing}>
              <RefreshIcon className={refreshing ? 'spinning' : ''} />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Period Selection */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Analysis Period
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          {[7, 30, 90].map(period => (
            <Button
              key={period}
              variant={selectedPeriod === period ? 'contained' : 'outlined'}
              size="small"
              onClick={() => setSelectedPeriod(period)}
            >
              {period} days
            </Button>
          ))}
        </Box>
      </Box>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {alerts.map((alert, index) => (
            <Alert key={index} severity={alert.severity} sx={{ mb: 1 }}>
              {alert.message}
            </Alert>
          ))}
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Error loading analytics: {error.message || 'Unknown error'}
        </Alert>
      )}

      {/* Main Content */}
      {processedData && (
        <Grid container spacing={3}>
          {/* Key Metrics */}
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TimelineIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Subscribers</Typography>
                </Box>
                <Typography variant="h4">
                  {processedData.overview.total_subscribers?.toLocaleString() || 'N/A'}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  {trends.subscriberTrend === 'up' ? (
                    <TrendingUpIcon color="success" />
                  ) : (
                    <TrendingDownIcon color="error" />
                  )}
                  <Typography 
                    variant="body2" 
                    color={trends.subscriberTrend === 'up' ? 'success.main' : 'error.main'}
                    sx={{ ml: 0.5 }}
                  >
                    {trends.subscriberChange > 0 ? '+' : ''}{trends.subscriberChange}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Total Views</Typography>
                </Box>
                <Typography variant="h4">
                  {trends.totalViews?.toLocaleString() || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedPeriod} days period
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <NotificationsIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Engagement Rate</Typography>
                </Box>
                <Typography variant="h4">
                  {trends.engagementRate ? `${trends.engagementRate}%` : 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Average engagement
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TimelineIcon color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6">Total Posts</Typography>
                </Box>
                <Typography variant="h4">
                  {trends.totalPosts || 'N/A'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Content published
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Main Charts */}
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Growth Trends Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) => {
                        const date = new Date(value);
                        return `${date.getMonth() + 1}/${date.getDate()}`;
                      }}
                    />
                    <YAxis tick={{ fontSize: 12 }} />
                    <RechartsTooltip 
                      labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="subscribers" 
                      stroke={theme.palette.primary.main}
                      strokeWidth={2}
                      name="Subscribers"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="views" 
                      stroke={theme.palette.secondary.main}
                      strokeWidth={2}
                      name="Views"
                    />
                    <Line 
                      type="monotone" 
                      dataKey="engagement" 
                      stroke={theme.palette.success.main}
                      strokeWidth={2}
                      name="Engagement"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Engagement Breakdown */}
          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Engagement Breakdown
                </Typography>
                {processedData.engagementMetrics?.breakdown ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={[
                          { name: 'Likes', value: processedData.engagementMetrics.breakdown.likes?.total || 0 },
                          { name: 'Shares', value: processedData.engagementMetrics.breakdown.shares?.total || 0 },
                          { name: 'Comments', value: processedData.engagementMetrics.breakdown.comments?.total || 0 },
                          { name: 'Saves', value: processedData.engagementMetrics.breakdown.saves?.total || 0 },
                        ]}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {COLORS.map((color, index) => (
                          <Cell key={`cell-${index}`} fill={color} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                      Engagement breakdown not available
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {isUsingMock ? 'Enable in mock configuration' : 'Check analytics provider capabilities'}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Data Source Info */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Data Source Information
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="subtitle2">Current Source</Typography>
                    <Typography variant="body2">
                      {currentDataSource === 'mock' ? 'Mock Analytics' : 'Real Analytics'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="subtitle2">Data Type</Typography>
                    <Typography variant="body2">
                      {isUsingMock ? 'Simulated Data' : 'Live API Data'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="subtitle2">Last Updated</Typography>
                    <Typography variant="body2">
                      {channelOverview?.service_metadata?.generated_at ? 
                        new Date(channelOverview.service_metadata.generated_at).toLocaleString() :
                        'Unknown'
                      }
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Typography variant="subtitle2">Adapter</Typography>
                    <Typography variant="body2">
                      {channelOverview?.service_metadata?.adapter || 'Unknown'}
                    </Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Data Source Settings Modal */}
      <DataSourceSettings 
        open={showSettings} 
        onClose={() => setShowSettings(false)} 
      />

      <style jsx>{`
        .spinning {
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </Box>
  );
};

export default ModernAdvancedAnalyticsDashboard;