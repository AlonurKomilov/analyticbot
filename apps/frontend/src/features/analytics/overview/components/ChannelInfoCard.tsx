/**
 * ChannelInfoCard Component
 * Displays channel information header with user-friendly metrics
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Tooltip,
  useTheme,
} from '@mui/material';
import { NewReleases, Verified, Schedule, TrackChanges } from '@mui/icons-material';
import type { ChannelOverviewData } from '../types';

export interface ChannelInfoCardProps {
  info: ChannelOverviewData['channel_info'];
}

export const ChannelInfoCard: React.FC<ChannelInfoCardProps> = ({ info }) => {
  const theme = useTheme();
  
  // Helper to format the date nicely
  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return 'Unknown';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return 'Unknown';
    }
  };

  // Get channel maturity based on actual Telegram age (if available)
  const getChannelMaturity = (ageDays: number | null): { label: string; color: 'warning' | 'info' | 'success' | 'default'; icon: React.ReactElement; description: string } | null => {
    if (ageDays === null) return null;
    
    if (ageDays < 30) {
      return { 
        label: 'New Channel', 
        color: 'warning', 
        icon: <NewReleases fontSize="small" />,
        description: 'Channel created less than a month ago'
      };
    } else if (ageDays < 180) {
      return { 
        label: 'Growing', 
        color: 'info', 
        icon: <Schedule fontSize="small" />,
        description: 'Channel is in growth phase'
      };
    } else if (ageDays < 365) {
      return { 
        label: 'Established', 
        color: 'success', 
        icon: <Verified fontSize="small" />,
        description: 'Well-established channel'
      };
    } else {
      return { 
        label: 'Veteran', 
        color: 'success', 
        icon: <Verified fontSize="small" />,
        description: `Channel has been active for ${Math.floor(ageDays / 365)}+ years`
      };
    }
  };

  // Get tracking status based on how long we've been tracking
  const getTrackingStatus = (ageDays: number): { label: string; description: string } => {
    if (ageDays < 7) {
      return { label: 'New', description: 'Recently added - building analytics history' };
    } else if (ageDays < 30) {
      return { label: 'Building', description: 'Collecting analytics data' };
    } else if (ageDays < 90) {
      return { label: 'Good', description: 'Solid analytics history available' };
    } else {
      return { label: 'Rich', description: 'Comprehensive analytics history' };
    }
  };

  const channelMaturity = getChannelMaturity(info.channel_age_days);
  const trackingStatus = getTrackingStatus(info.age_days);
  const trackingSinceFormatted = formatDate(info.created_at);
  const channelCreatedFormatted = formatDate(info.telegram_created_at);

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: 2,
              bgcolor: theme.palette.primary.main,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: 24,
              fontWeight: 'bold',
            }}
          >
            {info.title?.charAt(0) || 'C'}
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" fontWeight="bold">
              {info.title}
            </Typography>
            {info.username && (
              <Typography variant="body2" color="text.secondary">
                @{info.username}
              </Typography>
            )}
            <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap', alignItems: 'center' }}>
              {/* Channel Age Badge (from Telegram) - only show if available */}
              {channelMaturity && info.channel_age_formatted && (
                <Tooltip 
                  title={
                    <Box>
                      <Typography variant="body2">{channelMaturity.description}</Typography>
                      <Typography variant="caption" sx={{ opacity: 0.8 }}>
                        Created on {channelCreatedFormatted}
                      </Typography>
                    </Box>
                  }
                  arrow
                  placement="top"
                >
                  <Chip
                    size="small"
                    icon={channelMaturity.icon}
                    label={`${info.channel_age_formatted} old`}
                    color={channelMaturity.color}
                    variant="filled"
                    sx={{ cursor: 'help' }}
                  />
                </Tooltip>
              )}
              
              {/* Tracking Duration */}
              <Tooltip 
                title={
                  <Box>
                    <Typography variant="body2">{trackingStatus.description}</Typography>
                    <Typography variant="caption" sx={{ opacity: 0.8 }}>
                      Tracking since {trackingSinceFormatted}
                    </Typography>
                  </Box>
                }
                arrow
                placement="top"
              >
                <Chip
                  size="small"
                  icon={<TrackChanges fontSize="small" />}
                  label={`${info.age_formatted} tracked`}
                  variant="outlined"
                  sx={{ cursor: 'help' }}
                />
              </Tooltip>
              
              {/* Active/Inactive Status */}
              <Chip
                size="small"
                label={info.is_active ? '● Active' : '○ Inactive'}
                color={info.is_active ? 'success' : 'default'}
                variant="outlined"
              />
            </Box>
          </Box>
        </Box>
        {info.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            {info.description}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default ChannelInfoCard;
