import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Box, Grid } from '@mui/material';
import { useDataSource, useAllAnalytics } from '../../../hooks/useDataSource';

// Import extracted components
import DataSourceStatus from './DataSourceStatus';
import OverviewMetrics from './OverviewMetrics';
import SmartAlertsPanel from './SmartAlertsPanel';
import DashboardCharts from './DashboardCharts';
import PerformanceScoreWidget from './PerformanceScoreWidget';

const AdvancedAnalyticsDashboard = ({ channelId = 'demo_channel' }) => {
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
    if (overview && topPosts?.length) {
      // Convert top posts to trends format for charts
      setTrends(topPosts.slice(0, 10));
    }
  }, [overview, topPosts]);

  // Refresh handler
  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await Promise.all([
        actions.refreshOverview?.(),
        actions.refreshPostDynamics?.(),
        actions.refreshTopPosts?.()
      ]);
    } catch (error) {
      console.error('Failed to refresh dashboard:', error);
    } finally {
      setRefreshing(false);
    }
  };

  // Handle loading and error states
  if (isLoading || hasError) {
    return (
      <DataSourceStatus
        isLoading={isLoading}
        hasError={hasError}
        errors={errors}
        actions={actions}
        isUsingRealAPI={isUsingRealAPI}
        dataSource={dataSource}
        switchDataSource={switchDataSource}
        onRefresh={handleRefresh}
      />
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header with Data Source Status */}
      <DataSourceStatus
        isLoading={refreshing}
        hasError={false}
        errors={{}}
        actions={actions}
        isUsingRealAPI={isUsingRealAPI}
        dataSource={dataSource}
        switchDataSource={switchDataSource}
        onRefresh={handleRefresh}
      />

      {/* Smart Alerts Panel */}
      <SmartAlertsPanel
        overview={overview}
        postDynamics={postDynamics}
        topPosts={topPosts}
      />

      {/* Overview Metrics Grid */}
      <OverviewMetrics metrics={metrics} />

      {/* Advanced Charts */}
      <Grid container spacing={3}>
        {/* Trends Chart */}
        <Grid item xs={12} lg={8}>
          <DashboardCharts trends={trends} />
        </Grid>

        {/* Performance Score Widget */}
        <PerformanceScoreWidget metrics={metrics} />
      </Grid>
    </Box>
  );
};

AdvancedAnalyticsDashboard.propTypes = {
  channelId: PropTypes.string
};

export default AdvancedAnalyticsDashboard;
