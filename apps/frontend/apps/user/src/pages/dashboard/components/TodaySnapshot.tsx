/**
 * TodaySnapshot Component
 *
 * Shows real-time today's statistics with trend indicators.
 * Includes: new subscribers, views today, posts today, best performing post
 */

import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Chip,
  Skeleton,
  alpha,
  useTheme,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  People as SubscribersIcon,
  Visibility as ViewsIcon,
  Article as PostsIcon,
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material';

export interface TodayStatsData {
  new_subscribers: number;
  subscriber_change_percent: number;
  total_views: number;
  views_change_percent: number;
  posts_today: number;
  best_post_title?: string;
  best_post_views: number;
  best_post_id?: number;
}

interface TodaySnapshotProps {
  data?: TodayStatsData;
  isLoading?: boolean;
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: number;
  color: string;
  subtitle?: string;
  isLoading?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  trend,
  color,
  subtitle,
  isLoading
}) => {
  const theme = useTheme();

  if (isLoading) {
    return (
      <Paper sx={{ p: 2.5, height: '100%' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Skeleton variant="circular" width={32} height={32} />
          <Skeleton variant="text" width="60%" />
        </Box>
        <Skeleton variant="text" width="40%" height={40} />
        <Skeleton variant="text" width="50%" />
      </Paper>
    );
  }

  const getTrendIcon = () => {
    if (trend === undefined || trend === 0) return null;
    return trend > 0 ? <TrendingUpIcon sx={{ fontSize: 14 }} /> : <TrendingDownIcon sx={{ fontSize: 14 }} />;
  };

  return (
    <Paper
      sx={{
        p: 2.5,
        height: '100%',
        background: `linear-gradient(135deg, ${alpha(color, 0.08)} 0%, ${alpha(color, 0.02)} 100%)`,
        borderTop: `3px solid ${color}`,
        transition: 'all 0.2s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[4],
        },
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: 1.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: alpha(color, 0.15),
            color: color,
          }}
        >
          {icon}
        </Box>
        <Typography variant="body2" color="text.secondary" fontWeight={500}>
          {title}
        </Typography>
      </Box>

      <Typography variant="h4" fontWeight="bold" sx={{ mb: 0.5 }}>
        {value}
      </Typography>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {trend !== undefined && trend !== 0 && (
          <Chip
            size="small"
            icon={getTrendIcon() || undefined}
            label={`${trend > 0 ? '+' : ''}${trend.toFixed(1)}%`}
            color={trend > 0 ? 'success' : 'error'}
            sx={{
              height: 22,
              fontSize: 11,
              '& .MuiChip-icon': { fontSize: 14 },
            }}
          />
        )}
        {subtitle && (
          <Typography variant="caption" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

const TodaySnapshot: React.FC<TodaySnapshotProps> = ({ data, isLoading }) => {
  const theme = useTheme();

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  const truncateText = (text: string, maxLen: number) => {
    if (text.length <= maxLen) return text;
    return text.slice(0, maxLen) + '...';
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Typography variant="h6" fontWeight="600">
          📅 Today's Activity
        </Typography>
        <Typography variant="caption" color="text.secondary">
          ({new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })})
        </Typography>
      </Box>

      <Grid container spacing={2.5}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="New Subscribers"
            value={data ? (data.new_subscribers >= 0 ? `+${formatNumber(data.new_subscribers)}` : formatNumber(data.new_subscribers)) : '0'}
            icon={<SubscribersIcon fontSize="small" />}
            trend={data?.subscriber_change_percent}
            color={theme.palette.primary.main}
            subtitle="vs yesterday"
            isLoading={isLoading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Views Today"
            value={data ? formatNumber(data.total_views) : '0'}
            icon={<ViewsIcon fontSize="small" />}
            trend={data?.views_change_percent}
            color={theme.palette.info.main}
            subtitle="across all posts"
            isLoading={isLoading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Posts Today"
            value={data?.posts_today ?? 0}
            icon={<PostsIcon fontSize="small" />}
            color={theme.palette.success.main}
            subtitle="published today"
            isLoading={isLoading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          {isLoading ? (
            <Paper sx={{ p: 2.5, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Skeleton variant="circular" width={32} height={32} />
                <Skeleton variant="text" width="60%" />
              </Box>
              <Skeleton variant="text" width="80%" />
              <Skeleton variant="text" width="40%" />
            </Paper>
          ) : data?.best_post_title ? (
            <Paper
              sx={{
                p: 2.5,
                height: '100%',
                background: `linear-gradient(135deg, ${alpha(theme.palette.warning.main, 0.08)} 0%, ${alpha(theme.palette.warning.main, 0.02)} 100%)`,
                borderTop: `3px solid ${theme.palette.warning.main}`,
                transition: 'all 0.2s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: theme.shadows[4],
                },
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: 1.5,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: alpha(theme.palette.warning.main, 0.15),
                    color: theme.palette.warning.main,
                  }}
                >
                  <TrophyIcon fontSize="small" />
                </Box>
                <Typography variant="body2" color="text.secondary" fontWeight={500}>
                  Best Post Today
                </Typography>
              </Box>

              <Typography
                variant="body2"
                fontWeight="600"
                sx={{
                  mb: 0.5,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical',
                }}
              >
                "{truncateText(data.best_post_title, 60)}"
              </Typography>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: 'text.secondary' }}>
                <ViewsIcon sx={{ fontSize: 14 }} />
                <Typography variant="caption">
                  {formatNumber(data.best_post_views)} views
                </Typography>
              </Box>
            </Paper>
          ) : (
            <Paper
              sx={{
                p: 2.5,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: alpha(theme.palette.grey[500], 0.05),
                borderTop: `3px solid ${theme.palette.grey[400]}`,
              }}
            >
              <TrophyIcon sx={{ fontSize: 32, color: 'text.disabled', mb: 1 }} />
              <Typography variant="body2" color="text.secondary" textAlign="center">
                No posts today yet
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default TodaySnapshot;
