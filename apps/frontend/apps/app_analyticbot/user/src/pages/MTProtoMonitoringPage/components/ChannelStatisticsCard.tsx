/**
 * Channel Statistics Card Component
 * Displays per-channel collection statistics with enhanced styling
 */
import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Paper,
  Chip,
  Avatar,
  alpha,
} from '@mui/material';
import { TrendingUp, Article, AccessTime, Sync } from '@mui/icons-material';
import type { ChannelStats } from '../types';
import { formatTimeAgo } from '../utils';

interface ChannelStatisticsCardProps {
  channels: ChannelStats[];
}

export const ChannelStatisticsCard: React.FC<ChannelStatisticsCardProps> = ({ channels }) => {
  const { t } = useTranslation(['mtproto', 'common']);
  
  return (
    <Card 
      sx={{ 
        mb: 3,
        background: 'linear-gradient(135deg, rgba(0, 188, 212, 0.06) 0%, rgba(33, 150, 243, 0.06) 100%)',
        border: '1px solid rgba(0, 188, 212, 0.15)',
      }}
    >
      <CardContent>
        {/* Header */}
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <Avatar
            sx={{
              width: 56,
              height: 56,
              bgcolor: alpha('#00BCD4', 0.15),
              color: '#00BCD4',
            }}
          >
            <TrendingUp sx={{ fontSize: 32 }} />
          </Avatar>
          <Box flex={1}>
            <Typography variant="h6" fontWeight={600}>
              {t('mtproto:channelStats.title', 'Channel Collection Statistics')}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('mtproto:channelStats.description', 'Per-channel collection progress')}
            </Typography>
          </Box>
          <Chip 
            label={`${channels.length} ${t('common:channels', 'channels')}`}
            size="small"
            sx={{ fontWeight: 600, bgcolor: alpha('#00BCD4', 0.15), color: '#00BCD4' }}
          />
        </Box>

        {channels.length === 0 ? (
          <Box 
            textAlign="center" 
            py={4}
            sx={{
              borderRadius: 2,
              bgcolor: alpha('#9e9e9e', 0.05),
              border: '1px dashed',
              borderColor: 'divider',
            }}
          >
            <Typography color="text.secondary">
              {t('mtproto:channelStats.noChannels', 'No channels configured yet')}
            </Typography>
          </Box>
        ) : (
          <Box>
            {channels.map((channel, index) => (
              <Paper
                key={channel.channel_id}
                elevation={0}
                sx={{ 
                  p: 2.5, 
                  mb: index < channels.length - 1 ? 2 : 0, 
                  background: channel.collection_enabled 
                    ? 'linear-gradient(135deg, rgba(76, 175, 80, 0.04) 0%, rgba(33, 150, 243, 0.04) 100%)'
                    : 'linear-gradient(135deg, rgba(158, 158, 158, 0.04) 0%, rgba(158, 158, 158, 0.02) 100%)',
                  border: channel.collection_enabled 
                    ? '1px solid rgba(76, 175, 80, 0.15)'
                    : '1px solid rgba(158, 158, 158, 0.15)',
                  borderRadius: 2,
                  transition: 'all 0.2s ease',
                  '&:hover': { 
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  } 
                }}
              >
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={4}>
                    <Box>
                      <Box display="flex" alignItems="center" gap={1.5}>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {channel.channel_name}
                        </Typography>
                        <Chip 
                          label={channel.collection_enabled ? t('common:active', 'Active') : t('common:disabled', 'Disabled')} 
                          color={channel.collection_enabled ? 'success' : 'default'} 
                          size="small"
                          sx={{ fontWeight: 600, height: 22 }}
                        />
                      </Box>
                      <Typography variant="caption" color="text.secondary" fontFamily="monospace">
                        ID: {channel.channel_id}
                      </Typography>
                    </Box>
                  </Grid>

                  <Grid item xs={4} md={2}>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      <Box
                        sx={{
                          width: 36,
                          height: 36,
                          borderRadius: 1,
                          bgcolor: alpha('#2196F3', 0.15),
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#2196F3',
                        }}
                      >
                        <Article fontSize="small" />
                      </Box>
                      <Box>
                        <Typography variant="h6" fontWeight={700}>{channel.total_posts.toLocaleString()}</Typography>
                        <Typography variant="caption" color="text.secondary">{t('common:posts', 'Posts')}</Typography>
                      </Box>
                    </Box>
                  </Grid>

                  <Grid item xs={4} md={3}>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      <Box
                        sx={{
                          width: 36,
                          height: 36,
                          borderRadius: 1,
                          bgcolor: alpha('#ff9800', 0.15),
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#ff9800',
                        }}
                      >
                        <AccessTime fontSize="small" />
                      </Box>
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {formatTimeAgo(channel.latest_post_date)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">{t('mtproto:channelStats.newestPost', 'Newest Post')}</Typography>
                      </Box>
                    </Box>
                  </Grid>

                  <Grid item xs={4} md={3}>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      <Box
                        sx={{
                          width: 36,
                          height: 36,
                          borderRadius: 1,
                          bgcolor: alpha('#4caf50', 0.15),
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#4caf50',
                        }}
                      >
                        <Sync fontSize="small" />
                      </Box>
                      <Box>
                        <Typography variant="body2" fontWeight={600}>
                          {formatTimeAgo(channel.last_collected)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">{t('mtproto:channelStats.lastSynced', 'Last Synced')}</Typography>
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
              </Paper>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ChannelStatisticsCard;
