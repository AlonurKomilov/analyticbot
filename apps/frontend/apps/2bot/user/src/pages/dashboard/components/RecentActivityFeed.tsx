/**
 * RecentActivityFeed Component
 *
 * Shows a live feed of recent activities across all channels.
 * Types: syncs, new posts, subscriber changes, scheduled posts
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Chip,
  Skeleton,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Sync as SyncIcon,
  Article as PostIcon,
  People as SubscriberIcon,
  Schedule as ScheduleIcon,
  Visibility as ViewIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

export interface ActivityItem {
  id: string;
  type: 'sync' | 'post' | 'subscriber' | 'scheduled' | 'view' | 'error';
  icon: string;
  message: string;
  channel_name?: string;
  channel_id?: number;
  timestamp: string;
  time_ago: string;
}

interface RecentActivityFeedProps {
  activities: ActivityItem[];
  isLoading?: boolean;
  maxItems?: number;
}

const RecentActivityFeed: React.FC<RecentActivityFeedProps> = ({
  activities,
  isLoading,
  maxItems = 8
}) => {
  const theme = useTheme();

  const getActivityIcon = (type: string, emoji: string) => {
    // If emoji is provided, use it
    if (emoji && emoji !== type) {
      return (
        <Typography sx={{ fontSize: 20 }}>
          {emoji}
        </Typography>
      );
    }

    // Otherwise use Material icons
    switch (type) {
      case 'sync':
        return <SyncIcon fontSize="small" />;
      case 'post':
        return <PostIcon fontSize="small" />;
      case 'subscriber':
        return <SubscriberIcon fontSize="small" />;
      case 'scheduled':
        return <ScheduleIcon fontSize="small" />;
      case 'view':
        return <ViewIcon fontSize="small" />;
      case 'error':
        return <ErrorIcon fontSize="small" />;
      default:
        return <SyncIcon fontSize="small" />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'sync':
        return theme.palette.info.main;
      case 'post':
        return theme.palette.success.main;
      case 'subscriber':
        return theme.palette.primary.main;
      case 'scheduled':
        return theme.palette.warning.main;
      case 'view':
        return theme.palette.secondary.main;
      case 'error':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[500];
    }
  };

  if (isLoading) {
    return (
      <Paper sx={{ p: 2.5 }}>
        <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
          🔄 Recent Activity
        </Typography>
        <List disablePadding>
          {[1, 2, 3, 4].map((i) => (
            <ListItem key={i} disablePadding sx={{ py: 1 }}>
              <ListItemAvatar sx={{ minWidth: 44 }}>
                <Skeleton variant="circular" width={32} height={32} />
              </ListItemAvatar>
              <ListItemText
                primary={<Skeleton variant="text" width="80%" />}
                secondary={<Skeleton variant="text" width="40%" />}
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    );
  }

  if (activities.length === 0) {
    return (
      <Paper sx={{ p: 2.5 }}>
        <Typography variant="h6" fontWeight="600" sx={{ mb: 2 }}>
          🔄 Recent Activity
        </Typography>
        <Box
          sx={{
            py: 4,
            textAlign: 'center',
            color: 'text.secondary',
          }}
        >
          <SyncIcon sx={{ fontSize: 40, opacity: 0.3, mb: 1 }} />
          <Typography variant="body2">
            No recent activity
          </Typography>
          <Typography variant="caption" color="text.disabled">
            Activity will appear here once you start collecting data
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2.5 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6" fontWeight="600">
          🔄 Recent Activity
        </Typography>
        <Chip
          label={`${activities.length} events`}
          size="small"
          sx={{ height: 22, fontSize: 11 }}
        />
      </Box>

      <List disablePadding>
        {activities.slice(0, maxItems).map((activity, index) => {
          const color = getActivityColor(activity.type);

          return (
            <ListItem
              key={activity.id}
              disablePadding
              sx={{
                py: 1.5,
                borderBottom: index < Math.min(activities.length, maxItems) - 1
                  ? `1px solid ${theme.palette.divider}`
                  : 'none',
              }}
            >
              <ListItemAvatar sx={{ minWidth: 44 }}>
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    backgroundColor: alpha(color, 0.1),
                    color: color,
                  }}
                >
                  {getActivityIcon(activity.type, activity.icon)}
                </Avatar>
              </ListItemAvatar>

              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                    {activity.channel_name && (
                      <Chip
                        label={activity.channel_name}
                        size="small"
                        sx={{
                          height: 20,
                          fontSize: 10,
                          backgroundColor: alpha(theme.palette.primary.main, 0.1),
                        }}
                      />
                    )}
                    <Typography
                      variant="body2"
                      component="span"
                      sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 1,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {activity.message}
                    </Typography>
                  </Box>
                }
                secondary={
                  <Typography variant="caption" color="text.secondary">
                    {activity.time_ago}
                  </Typography>
                }
              />
            </ListItem>
          );
        })}
      </List>
    </Paper>
  );
};

export default RecentActivityFeed;
