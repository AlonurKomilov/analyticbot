/**
 * Bot Timeline Card Component
 */
import React from 'react';
import { Box, Card, CardContent, Typography, alpha } from '@mui/material';
import { 
  EventNote as CalendarIcon, 
  Update as UpdateIcon 
} from '@mui/icons-material';
import { BotStatusResponse } from '@/types';
import { format } from 'date-fns';

interface BotTimelineCardProps {
  bot: BotStatusResponse;
}

export const BotTimelineCard: React.FC<BotTimelineCardProps> = ({ bot }) => {
  return (
    <Card sx={{ bgcolor: 'rgba(255, 255, 255, 0.02)' }}>
      <CardContent sx={{ py: 2 }}>
        <Typography variant="subtitle2" color="text.secondary" mb={2}>
          Timeline
        </Typography>

        <Box display="flex" justifyContent="space-between" flexWrap="wrap" gap={3}>
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
              <CalendarIcon fontSize="small" />
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Created
              </Typography>
              <Typography variant="body2" fontWeight={500}>
                {bot.created_at && format(new Date(bot.created_at), 'MMM d, yyyy, h:mm a')}
              </Typography>
            </Box>
          </Box>

          <Box display="flex" alignItems="center" gap={1.5}>
            <Box
              sx={{
                width: 36,
                height: 36,
                borderRadius: 1,
                bgcolor: alpha('#2196f3', 0.15),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#2196f3',
              }}
            >
              <UpdateIcon fontSize="small" />
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Last Updated
              </Typography>
              <Typography variant="body2" fontWeight={500}>
                {bot.updated_at && format(new Date(bot.updated_at), 'MMM d, yyyy, h:mm a')}
              </Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};
