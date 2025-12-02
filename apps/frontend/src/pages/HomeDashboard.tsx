/**
 * HomeDashboard - Main landing page after login
 * 
 * Shows a quick overview with:
 * - Welcome message and quick stats
 * - Quick access cards to main features
 * - Recent activity summary
 * - System status
 * 
 * This is different from AnalyticsPage which shows detailed analytics.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActionArea,
  Skeleton,
  Chip,
  Avatar,
  Divider,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Analytics as AnalyticsIcon,
  Forum as ChannelsIcon,
  Article as PostsIcon,
  Schedule as ScheduleIcon,
  SmartToy as BotIcon,
  TrendingUp as TrendingIcon,
  Visibility as ViewsIcon,
  People as SubscribersIcon,
  Speed as EngagementIcon,
  ArrowForward as ArrowIcon,
} from '@mui/icons-material';
import { useChannelStore, useAuthStore } from '@store';
import { TouchTargetProvider } from '@shared/components/ui';

interface QuickStatProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: number;
  color: string;
  isLoading?: boolean;
}

const QuickStat: React.FC<QuickStatProps> = ({ title, value, icon, trend, color, isLoading }) => {
  const theme = useTheme();
  
  if (isLoading) {
    return (
      <Paper sx={{ p: 2, height: '100%' }}>
        <Skeleton variant="circular" width={40} height={40} />
        <Skeleton variant="text" width="60%" sx={{ mt: 1 }} />
        <Skeleton variant="text" width="40%" />
      </Paper>
    );
  }
  
  return (
    <Paper
      sx={{
        p: 2,
        height: '100%',
        background: `linear-gradient(135deg, ${alpha(color, 0.1)} 0%, ${alpha(color, 0.05)} 100%)`,
        borderLeft: `4px solid ${color}`,
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[4],
        },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {title}
          </Typography>
          <Typography variant="h4" fontWeight="bold">
            {value}
          </Typography>
          {trend !== undefined && (
            <Chip
              size="small"
              icon={<TrendingIcon sx={{ fontSize: 14 }} />}
              label={`${trend > 0 ? '+' : ''}${trend}%`}
              color={trend >= 0 ? 'success' : 'error'}
              sx={{ mt: 1, height: 20, fontSize: 11 }}
            />
          )}
        </Box>
        <Avatar sx={{ bgcolor: alpha(color, 0.2), color: color }}>
          {icon}
        </Avatar>
      </Box>
    </Paper>
  );
};

interface QuickAccessCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  path: string;
  color: string;
}

const QuickAccessCard: React.FC<QuickAccessCardProps> = ({ title, description, icon, path, color }) => {
  const navigate = useNavigate();
  const theme = useTheme();
  
  return (
    <Card
      sx={{
        height: '100%',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: theme.shadows[8],
        },
      }}
    >
      <CardActionArea onClick={() => navigate(path)} sx={{ height: '100%', p: 2 }}>
        <CardContent sx={{ p: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ bgcolor: alpha(color, 0.15), color: color, mr: 2 }}>
              {icon}
            </Avatar>
            <Typography variant="h6" fontWeight="600">
              {title}
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {description}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', color: color }}>
            <Typography variant="body2" fontWeight="500">
              Open
            </Typography>
            <ArrowIcon sx={{ fontSize: 16, ml: 0.5 }} />
          </Box>
        </CardContent>
      </CardActionArea>
    </Card>
  );
};

const HomeDashboard: React.FC = () => {
  const theme = useTheme();
  const { user } = useAuthStore();
  const { channels, selectedChannel, isLoading } = useChannelStore();
  const [stats, setStats] = useState({
    subscribers: 0,
    totalViews: 0,
    totalPosts: 0,
    engagement: 0,
  });

  useEffect(() => {
    // Calculate stats from selected channel or aggregate
    if (selectedChannel) {
      const metrics = selectedChannel.metrics;
      setStats({
        subscribers: selectedChannel.subscriberCount || 0,
        totalViews: metrics?.totalViews || 0,
        totalPosts: metrics?.totalPosts || 0,
        engagement: metrics?.engagementRate || 0,
      });
    } else if (channels.length > 0) {
      // Aggregate stats from all channels
      const aggregated = channels.reduce((acc, ch) => {
        const metrics = ch.metrics;
        return {
          subscribers: acc.subscribers + (ch.subscriberCount || 0),
          totalViews: acc.totalViews + (metrics?.totalViews || 0),
          totalPosts: acc.totalPosts + (metrics?.totalPosts || 0),
          engagement: acc.engagement + (metrics?.engagementRate || 0),
        };
      }, { subscribers: 0, totalViews: 0, totalPosts: 0, engagement: 0 });
      
      aggregated.engagement = channels.length > 0 ? aggregated.engagement / channels.length : 0;
      setStats(aggregated);
    }
  }, [channels, selectedChannel]);

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const quickAccessItems: QuickAccessCardProps[] = [
    {
      title: 'Analytics',
      description: 'View detailed channel analytics, post performance, and insights',
      icon: <AnalyticsIcon />,
      path: '/analytics',
      color: theme.palette.primary.main,
    },
    {
      title: 'Channels',
      description: 'Manage your Telegram channels and settings',
      icon: <ChannelsIcon />,
      path: '/channels',
      color: theme.palette.info.main,
    },
    {
      title: 'Posts',
      description: 'Create, edit, and schedule posts for your channels',
      icon: <PostsIcon />,
      path: '/posts',
      color: theme.palette.success.main,
    },
    {
      title: 'Scheduled Posts',
      description: 'View and manage your scheduled content',
      icon: <ScheduleIcon />,
      path: '/scheduled',
      color: theme.palette.warning.main,
    },
    {
      title: 'My Bot',
      description: 'Configure and monitor your Telegram bot',
      icon: <BotIcon />,
      path: '/bot/dashboard',
      color: theme.palette.secondary.main,
    },
    {
      title: 'AI Services',
      description: 'Access AI-powered tools for content optimization',
      icon: <TrendingIcon />,
      path: '/services',
      color: '#9c27b0',
    },
  ];

  const greeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <TouchTargetProvider>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        {/* Welcome Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            {greeting()}, {user?.username || 'User'}! 👋
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Here's an overview of your channels and quick access to key features.
          </Typography>
        </Box>

        {/* Quick Stats */}
        <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
          Quick Overview
        </Typography>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <QuickStat
              title="Total Subscribers"
              value={formatNumber(stats.subscribers)}
              icon={<SubscribersIcon />}
              color={theme.palette.primary.main}
              isLoading={isLoading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <QuickStat
              title="Total Views"
              value={formatNumber(stats.totalViews)}
              icon={<ViewsIcon />}
              color={theme.palette.info.main}
              isLoading={isLoading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <QuickStat
              title="Total Posts"
              value={formatNumber(stats.totalPosts)}
              icon={<PostsIcon />}
              color={theme.palette.success.main}
              isLoading={isLoading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <QuickStat
              title="Avg Engagement"
              value={`${stats.engagement.toFixed(1)}%`}
              icon={<EngagementIcon />}
              color={theme.palette.warning.main}
              isLoading={isLoading}
            />
          </Grid>
        </Grid>

        <Divider sx={{ my: 4 }} />

        {/* Quick Access */}
        <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
          Quick Access
        </Typography>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {quickAccessItems.map((item) => (
            <Grid item xs={12} sm={6} md={4} key={item.title}>
              <QuickAccessCard {...item} />
            </Grid>
          ))}
        </Grid>

        {/* Channels Summary */}
        {channels.length > 0 && (
          <>
            <Divider sx={{ my: 4 }} />
            <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
              Your Channels ({channels.length})
            </Typography>
            <Grid container spacing={2}>
              {channels.slice(0, 4).map((channel) => (
                <Grid item xs={12} sm={6} md={3} key={channel.id}>
                  <Paper sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Avatar sx={{ bgcolor: theme.palette.primary.main, mr: 1.5, width: 32, height: 32 }}>
                        {(channel.name || 'C')[0].toUpperCase()}
                      </Avatar>
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography variant="body2" fontWeight="600" noWrap>
                          {channel.name || 'Channel'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatNumber(channel.subscriberCount || 0)} subscribers
                        </Typography>
                      </Box>
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </>
        )}
      </Container>
    </TouchTargetProvider>
  );
};

export default HomeDashboard;
