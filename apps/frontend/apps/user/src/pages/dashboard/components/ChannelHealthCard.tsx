/**
 * ChannelHealthCard Component
 *
 * Shows health status for a single channel with actionable quick buttons.
 * Displays: subscribers, growth, avg views, last post, engagement, sync status
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Avatar,
  Chip,
  Button,
  Tooltip,
  Divider,
  alpha,
  useTheme,
} from '@mui/material';
import {
  Visibility as ViewsIcon,
  Schedule as ScheduleIcon,
  CheckCircle as HealthyIcon,
  Warning as StaleIcon,
  Error as ErrorIcon,
  HelpOutline as UnknownIcon,
  Analytics as AnalyticsIcon,
  Edit as EditIcon,
  Refresh as CollectIcon,
} from '@mui/icons-material';

export interface ChannelHealthData {
  id: number;
  name: string;
  username?: string;
  subscribers: number;
  subscriber_growth_week: number;
  avg_views: number;
  last_post_time?: string;
  last_post_ago?: string;
  engagement_rate: number;
  engagement_change: number;
  last_sync?: string;
  last_sync_ago?: string;
  sync_status: 'healthy' | 'stale' | 'error' | 'never' | 'unknown';
  bot_is_admin: boolean;
  mtproto_enabled: boolean;
}

interface ChannelHealthCardProps {
  channel: ChannelHealthData;
  onCollect?: (channelId: number) => void;
}

const ChannelHealthCard: React.FC<ChannelHealthCardProps> = ({ channel, onCollect }) => {
  const theme = useTheme();
  const navigate = useNavigate();

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  const getSyncStatusConfig = (status: string) => {
    switch (status) {
      case 'healthy':
        return {
          icon: <HealthyIcon fontSize="small" />,
          color: theme.palette.success.main,
          label: 'Healthy',
        };
      case 'stale':
        return {
          icon: <StaleIcon fontSize="small" />,
          color: theme.palette.warning.main,
          label: 'Stale',
        };
      case 'error':
        return {
          icon: <ErrorIcon fontSize="small" />,
          color: theme.palette.error.main,
          label: 'Error',
        };
      case 'never':
        return {
          icon: <UnknownIcon fontSize="small" />,
          color: theme.palette.grey[500],
          label: 'Never synced',
        };
      default:
        return {
          icon: <UnknownIcon fontSize="small" />,
          color: theme.palette.grey[500],
          label: 'Unknown',
        };
    }
  };

  const syncConfig = getSyncStatusConfig(channel.sync_status);

  return (
    <Paper
      sx={{
        p: 2.5,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'all 0.2s ease',
        '&:hover': {
          boxShadow: theme.shadows[6],
        },
      }}
    >
      {/* Header: Avatar + Name + Sync Status */}
      <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
        <Avatar
          sx={{
            width: 48,
            height: 48,
            bgcolor: theme.palette.primary.main,
            fontSize: 20,
            fontWeight: 'bold',
          }}
        >
          {channel.name?.[0]?.toUpperCase() || 'C'}
        </Avatar>

        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="subtitle1" fontWeight="bold" noWrap>
            {channel.name}
          </Typography>
          {channel.username && (
            <Typography variant="caption" color="text.secondary">
              @{channel.username}
            </Typography>
          )}
        </Box>

        <Tooltip title={`Sync: ${syncConfig.label}`}>
          <Chip
            size="small"
            icon={syncConfig.icon}
            label={channel.last_sync_ago || syncConfig.label}
            sx={{
              height: 24,
              fontSize: 11,
              backgroundColor: alpha(syncConfig.color, 0.1),
              color: syncConfig.color,
              '& .MuiChip-icon': { color: syncConfig.color },
            }}
          />
        </Tooltip>
      </Box>

      {/* Stats Grid */}
      <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 2 }}>
        {/* Subscribers */}
        <Box>
          <Typography variant="caption" color="text.secondary">
            Subscribers
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Typography variant="h6" fontWeight="bold">
              {formatNumber(channel.subscribers)}
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            total
          </Typography>
        </Box>

        {/* Avg Views */}
        <Box>
          <Typography variant="caption" color="text.secondary">
            Avg Views
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <ViewsIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="h6" fontWeight="bold">
              {formatNumber(channel.avg_views)}
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            per post
          </Typography>
        </Box>

        {/* Last Post */}
        <Box>
          <Typography variant="caption" color="text.secondary">
            Last Post
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <ScheduleIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
            <Typography variant="body2" fontWeight="600">
              {channel.last_post_ago || 'No posts'}
            </Typography>
          </Box>
        </Box>

        {/* Engagement */}
        <Box>
          <Typography variant="caption" color="text.secondary">
            Engagement
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Typography variant="h6" fontWeight="bold">
              {channel.engagement_rate.toFixed(1)}%
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            avg rate
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ my: 1.5 }} />

      {/* Quick Actions */}
      <Box sx={{ display: 'flex', gap: 1, mt: 'auto' }}>
        <Button
          size="small"
          variant="outlined"
          startIcon={<AnalyticsIcon />}
          onClick={() => navigate(`/analytics?channel=${channel.id}`)}
          sx={{ flex: 1, fontSize: 12 }}
        >
          Analytics
        </Button>
        <Button
          size="small"
          variant="outlined"
          startIcon={<EditIcon />}
          onClick={() => navigate(`/posts/create?channel=${channel.id}`)}
          sx={{ flex: 1, fontSize: 12 }}
        >
          Post
        </Button>
        {channel.mtproto_enabled && (
          <Tooltip title="Collect latest data">
            <Button
              size="small"
              variant="outlined"
              onClick={() => onCollect?.(channel.id)}
              sx={{ minWidth: 40, px: 1 }}
            >
              <CollectIcon fontSize="small" />
            </Button>
          </Tooltip>
        )}
      </Box>
    </Paper>
  );
};

export default ChannelHealthCard;
