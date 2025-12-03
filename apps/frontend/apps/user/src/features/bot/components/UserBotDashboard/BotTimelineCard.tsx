/**
 * Bot Timeline Card Component
 */
import React from 'react';
import { Box, Card, CardContent, Typography } from '@mui/material';
import { BotStatusResponse } from '@/types';
import { format } from 'date-fns';

interface BotTimelineCardProps {
  bot: BotStatusResponse;
}

export const BotTimelineCard: React.FC<BotTimelineCardProps> = ({ bot }) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>
          Timeline
        </Typography>

        <Box display="flex" justifyContent="space-between" mb={2}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Created
            </Typography>
            <Typography variant="body1">
              {bot.created_at && format(new Date(bot.created_at), 'PPpp')}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              Last Updated
            </Typography>
            <Typography variant="body1">
              {bot.updated_at && format(new Date(bot.updated_at), 'PPpp')}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};
