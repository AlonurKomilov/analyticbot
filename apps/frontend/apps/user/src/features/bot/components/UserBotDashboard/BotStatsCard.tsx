/**
 * Bot Configuration & Stats Card Component
 */
import React from 'react';
import { Box, Card, CardContent, Typography } from '@mui/material';
import { Settings } from '@mui/icons-material';
import { BotStatusResponse } from '@/types';
import { format } from 'date-fns';

interface BotStatsCardProps {
  bot: BotStatusResponse;
}

export const BotStatsCard: React.FC<BotStatsCardProps> = ({ bot }) => {
  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Settings sx={{ mr: 1, fontSize: 32 }} />
          <Typography variant="h6">Configuration & Stats</Typography>
        </Box>

        <Box mb={2}>
          <Typography variant="body2" color="text.secondary">
            Rate Limit (RPS)
          </Typography>
          <Typography variant="h5">{bot.max_requests_per_second}</Typography>
        </Box>

        <Box mb={2}>
          <Typography variant="body2" color="text.secondary">
            Max Concurrent Requests
          </Typography>
          <Typography variant="h5">{bot.max_concurrent_requests}</Typography>
        </Box>

        <Box mb={2}>
          <Typography variant="body2" color="text.secondary">
            Total Requests
          </Typography>
          <Typography variant="h5">{bot.total_requests.toLocaleString()}</Typography>
        </Box>

        <Box>
          <Typography variant="body2" color="text.secondary">
            Last Used
          </Typography>
          <Typography variant="body1">
            {bot.last_used_at
              ? format(new Date(bot.last_used_at), 'PPpp')
              : 'Never'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};
