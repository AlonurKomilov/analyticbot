/**
 * Analytics Overview Page
 * ========================
 * 
 * TGStat-style comprehensive channel overview dashboard.
 * Displays key metrics, charts, and channel information.
 * 
 * ✨ Refactored: 833 lines → 9 files
 * - components/utils.ts: Utility functions
 * - components/MetricCard.tsx: Metric display card
 * - components/ChannelInfoCard.tsx: Channel info header
 * - components/SimpleChart.tsx: Simple bar chart
 * - components/DemographicsCard.tsx: Demographics display
 * - components/TrafficSourcesCard.tsx: Traffic sources
 * - components/StatsCards.tsx: Posts/Engagement/Reach stats
 * - components/LoadingSkeleton.tsx: Loading state
 * - components/TelegramStatsSection.tsx: Telegram Stats API section
 */

import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Alert,
  IconButton,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  TrendingUp,
  Visibility,
  ThumbUp,
  Share,
  Comment,
  CalendarToday,
  Refresh,
} from '@mui/icons-material';
import { useOverview, useTelegramStats } from './useOverview';
import {
  MetricCard,
  ChannelInfoCard,
  SimpleChart,
  PostsStatsCard,
  EngagementStatsCard,
  ReachStatsCard,
  LoadingSkeleton,
  TelegramStatsSection,
  formatNumber,
  formatPercentage,
  getEngagementRatePerformance,
  getGrowthPerformance,
  getPostingFrequencyPerformance,
  getCitationIndexPerformance,
  getViewsPerformance,
  METRIC_TOOLTIPS,
} from './components';

interface OverviewPageProps {
  channelId?: string | number | null;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({ channelId }) => {
  const theme = useTheme();

  // Always use all_time for channel overview
  const { data, isLoading, isError, error, refetch } = useOverview(channelId, {
    period: 'all_time',
    refreshInterval: 60000,
  });

  // Fetch Telegram Stats API data (demographics, traffic sources, growth)
  const { 
    data: telegramStats, 
    isLoading: telegramStatsLoading,
  } = useTelegramStats(channelId, {
    refreshInterval: 300000, // 5 min refresh
    enabled: !!channelId,
  });

  if (!channelId) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">
          Please select a channel to view the analytics overview.
        </Alert>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LoadingSkeleton />
      </Box>
    );
  }

  if (isError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" action={
          <IconButton size="small" onClick={() => refetch()}>
            <Refresh />
          </IconButton>
        }>
          Failed to load analytics: {error?.message || 'Unknown error'}
        </Alert>
      </Box>
    );
  }

  if (!data) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">
          No analytics data available for this channel.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight="bold">
          Channel Overview
        </Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={() => refetch()} size="small">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Channel Info */}
      <ChannelInfoCard info={data.channel_info} />

      {/* Key Metrics Grid */}
      <Typography variant="h6" sx={{ mb: 2 }}>
        Key Metrics
      </Typography>
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <MetricCard
            title="Subscribers"
            value={data.subscribers.total}
            change={data.subscribers.week_change}
            subtitle={data.subscribers.week_change !== 0 
              ? `${data.subscribers.week_change > 0 ? '+' : ''}${data.subscribers.week_change} this week`
              : 'No change this week'
            }
            icon={<TrendingUp />}
            performance={getGrowthPerformance(data.subscribers.growth_rate)}
            tooltipDetails={{
              description: METRIC_TOOLTIPS.subscribers.description,
              calculation: METRIC_TOOLTIPS.subscribers.calculation,
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <MetricCard
            title="Total Posts"
            value={data.posts.total}
            subtitle={`${data.posts.avg_per_day.toFixed(1)} posts per day`}
            icon={<CalendarToday />}
            performance={getPostingFrequencyPerformance(data.posts.avg_per_day)}
            tooltipDetails={{
              description: METRIC_TOOLTIPS.totalPosts.description,
              calculation: METRIC_TOOLTIPS.totalPosts.calculation,
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <MetricCard
            title="Total Views"
            value={data.engagement.total_views}
            subtitle={`${formatNumber(data.engagement.avg_views_per_post)} avg per post`}
            icon={<Visibility />}
            performance={getViewsPerformance(data.engagement.avg_views_per_post, data.subscribers.total)}
            tooltipDetails={{
              description: METRIC_TOOLTIPS.totalViews.description,
              calculation: METRIC_TOOLTIPS.avgViewsPerPost.calculation,
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <MetricCard
            title="Engagement Rate"
            value={formatPercentage(data.engagement.engagement_rate)}
            subtitle={`${formatNumber(data.engagement.total_reactions + data.engagement.total_forwards)} interactions`}
            icon={<ThumbUp />}
            performance={getEngagementRatePerformance(data.engagement.engagement_rate)}
            tooltipDetails={{
              description: METRIC_TOOLTIPS.engagementRate.description,
              calculation: METRIC_TOOLTIPS.engagementRate.calculation,
              benchmark: METRIC_TOOLTIPS.engagementRate.benchmark,
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <MetricCard
            title="Avg Post Reach"
            value={data.reach.avg_post_reach}
            subtitle={`Ad Reach: ${formatNumber(data.reach.avg_ad_reach)}`}
            icon={<Share />}
            tooltipDetails={{
              description: METRIC_TOOLTIPS.avgPostReach.description,
              calculation: METRIC_TOOLTIPS.avgPostReach.calculation,
            }}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2}>
          <MetricCard
            title="Citation Index"
            value={data.reach.citation_index.toFixed(1)}
            subtitle="Virality score"
            icon={<Comment />}
            performance={getCitationIndexPerformance(data.reach.citation_index)}
            tooltipDetails={{
              description: METRIC_TOOLTIPS.citationIndex.description,
              calculation: METRIC_TOOLTIPS.citationIndex.calculation,
              benchmark: METRIC_TOOLTIPS.citationIndex.benchmark,
            }}
          />
        </Grid>
      </Grid>

      {/* Detailed Stats Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <PostsStatsCard posts={data.posts} />
        </Grid>
        <Grid item xs={12} md={4}>
          <EngagementStatsCard engagement={data.engagement} />
        </Grid>
        <Grid item xs={12} md={4}>
          <ReachStatsCard reach={data.reach} />
        </Grid>
      </Grid>

      {/* Telegram Statistics Section */}
      <TelegramStatsSection
        telegramStats={telegramStats}
        isLoading={telegramStatsLoading}
      />

      {/* Charts Section */}
      <Typography variant="h6" sx={{ mb: 2 }}>
        Historical Trends
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <SimpleChart
              data={data.views_history}
              title="Views Over Time"
              color={theme.palette.primary.main}
            />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <SimpleChart
              data={data.posts_history}
              title="Posts Over Time"
              color={theme.palette.secondary.main}
            />
          </Paper>
        </Grid>
      </Grid>

      {/* Footer */}
      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Last updated: {new Date(data.generated_at).toLocaleString()}
        </Typography>
      </Box>
    </Box>
  );
};

export default OverviewPage;
