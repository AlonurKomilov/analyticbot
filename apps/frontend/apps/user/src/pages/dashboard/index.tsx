/**
 * HomeDashboard - New Design (December 2025)
 *
 * Main landing page after login with actionable, real-time information:
 * - Action Required Banner (alerts needing attention)
 * - Today's Snapshot (real-time stats)
 * - Channel Health Cards (per-channel status with quick actions)
 * - Recent Activity Feed (live updates)
 * - Contextual Quick Actions
 */

import React, { useEffect, useState, useCallback } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Skeleton,
  Alert,
} from '@mui/material';
import { apiClient } from '@/api/client';
import { TouchTargetProvider } from '@shared/components/ui';
import {
  ActionRequiredBanner,
  TodaySnapshot,
  ChannelHealthCard,
  RecentActivityFeed,
  QuickActionsPanel,
  PerformanceSparkline,
  type ActionAlert,
  type TodayStatsData,
  type ChannelHealthData,
  type ActivityItem,
  type QuickAction,
} from './components';

interface WelcomeMessage {
  greeting: string;
  message: string;
  emoji: string;
}

interface DashboardData {
  user_id: number;
  username?: string;
  welcome: WelcomeMessage;
  alerts: ActionAlert[];
  today: TodayStatsData;
  channels: ChannelHealthData[];
  activity: ActivityItem[];
  quick_actions: QuickAction[];
  sparkline_views: number[];
  sparkline_labels: string[];
  last_updated: string;
  has_channels: boolean;
  has_bot: boolean;
  has_mtproto: boolean;
}

const HomeDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = useCallback(async () => {
    try {
      setError(null);
      const data = await apiClient.get<DashboardData>('/dashboard');
      setDashboardData(data);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();

    // Refresh every 2 minutes
    const interval = setInterval(fetchDashboardData, 120000);
    return () => clearInterval(interval);
  }, [fetchDashboardData]);

  const handleCollectData = async (channelId: number) => {
    try {
      await apiClient.post(`/user-mtproto/collection/${channelId}/trigger`);
      // Refresh dashboard after triggering collection
      setTimeout(fetchDashboardData, 2000);
    } catch (err) {
      console.error('Failed to trigger collection:', err);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <TouchTargetProvider>
        <Container maxWidth="xl" sx={{ py: 3 }}>
          {/* Header skeleton */}
          <Box sx={{ mb: 4 }}>
            <Skeleton variant="text" width={300} height={40} />
            <Skeleton variant="text" width={400} height={24} />
          </Box>

          {/* Stats skeleton */}
          <Grid container spacing={2.5} sx={{ mb: 4 }}>
            {[1, 2, 3, 4].map((i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <Skeleton variant="rounded" height={140} />
              </Grid>
            ))}
          </Grid>

          {/* Content skeleton */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Skeleton variant="rounded" height={300} />
            </Grid>
            <Grid item xs={12} md={4}>
              <Skeleton variant="rounded" height={300} />
            </Grid>
          </Grid>
        </Container>
      </TouchTargetProvider>
    );
  }

  // Error state
  if (error) {
    return (
      <TouchTargetProvider>
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
          <Typography variant="body2" color="text.secondary">
            Please try refreshing the page or contact support if the issue persists.
          </Typography>
        </Container>
      </TouchTargetProvider>
    );
  }

  const data = dashboardData!;

  return (
    <TouchTargetProvider>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        {/* Smart Welcome Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            {data.welcome.greeting} {data.welcome.emoji}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {data.welcome.message}
          </Typography>
        </Box>

        {/* Action Required Banner */}
        {data.alerts.length > 0 && (
          <ActionRequiredBanner alerts={data.alerts} />
        )}

        {/* Today's Snapshot */}
        <TodaySnapshot data={data.today} isLoading={false} />

        {/* Main Content Grid */}
        <Grid container spacing={3}>
          {/* Left Column: Channel Health Cards */}
          <Grid item xs={12} lg={8}>
            {data.has_channels ? (
              <>
                <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
                  📊 Your Channels ({data.channels.length})
                </Typography>
                <Grid container spacing={2.5}>
                  {data.channels.map((channel) => (
                    <Grid item xs={12} sm={6} key={channel.id}>
                      <ChannelHealthCard
                        channel={channel}
                        onCollect={handleCollectData}
                      />
                    </Grid>
                  ))}
                </Grid>
              </>
            ) : (
              <QuickActionsPanel
                actions={data.quick_actions}
                hasChannels={data.has_channels}
              />
            )}
          </Grid>

          {/* Right Column: Activity Feed + Quick Actions + Sparkline */}
          <Grid item xs={12} lg={4}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* 7-Day Performance Sparkline */}
              {data.has_channels && (
                <PerformanceSparkline
                  data={data.sparkline_views}
                  labels={data.sparkline_labels}
                  isLoading={false}
                />
              )}

              {/* Recent Activity */}
              <RecentActivityFeed
                activities={data.activity}
                isLoading={false}
                maxItems={6}
              />

              {/* Quick Actions (only if user has channels) */}
              {data.has_channels && data.quick_actions.length > 0 && (
                <QuickActionsPanel
                  actions={data.quick_actions}
                  hasChannels={data.has_channels}
                />
              )}
            </Box>
          </Grid>
        </Grid>

        {/* Last updated indicator */}
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="caption" color="text.disabled">
            Last updated: {new Date(data.last_updated).toLocaleTimeString()}
            {' · '}Auto-refreshes every 2 minutes
          </Typography>
        </Box>
      </Container>
    </TouchTargetProvider>
  );
};

export default HomeDashboard;
