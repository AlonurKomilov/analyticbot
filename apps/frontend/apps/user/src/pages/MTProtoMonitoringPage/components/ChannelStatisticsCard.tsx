/**
 * Channel Statistics Card Component
 * Displays per-channel collection statistics
 */
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Paper,
  Chip,
  Divider,
} from '@mui/material';
import { TrendingUp } from '@mui/icons-material';
import type { ChannelStats } from '../types';
import { formatTimeAgo } from '../utils';

interface ChannelStatisticsCardProps {
  channels: ChannelStats[];
}

export const ChannelStatisticsCard: React.FC<ChannelStatisticsCardProps> = ({ channels }) => {
  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <TrendingUp color="primary" />
          <Typography variant="h6">Channel Collection Statistics</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Per-channel collection progress
        </Typography>
        <Divider sx={{ my: 2 }} />

        {channels.length === 0 ? (
          <Box textAlign="center" py={4}>
            <Typography color="text.secondary">No channels configured yet</Typography>
          </Box>
        ) : (
          <Box>
            {channels.map((channel) => (
              <Paper
                key={channel.channel_id}
                variant="outlined"
                sx={{ p: 2, mb: 2, '&:hover': { bgcolor: 'action.hover' } }}
              >
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={4}>
                    <Box>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="subtitle1" fontWeight="medium">
                          {channel.channel_name}
                        </Typography>
                        {channel.collection_enabled ? (
                          <Chip label="Active" color="success" size="small" />
                        ) : (
                          <Chip label="Disabled" size="small" />
                        )}
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        ID: {channel.channel_id}
                      </Typography>
                    </Box>
                  </Grid>

                  <Grid item xs={4} md={2}>
                    <Box textAlign="center">
                      <Typography variant="h5">{channel.total_posts}</Typography>
                      <Typography variant="caption" color="text.secondary">Posts</Typography>
                    </Box>
                  </Grid>

                  <Grid item xs={4} md={3}>
                    <Box textAlign="center">
                      <Typography variant="body2" fontWeight="medium">
                        {formatTimeAgo(channel.latest_post_date)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">Newest Post</Typography>
                    </Box>
                  </Grid>

                  <Grid item xs={4} md={3}>
                    <Box textAlign="center">
                      <Typography variant="body2" fontWeight="medium">
                        {formatTimeAgo(channel.last_collected)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">Last Synced</Typography>
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
