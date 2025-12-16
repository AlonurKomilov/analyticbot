/**
 * Bot Configuration & Stats Card Component
 */
import React from 'react';
import { Box, Card, CardContent, Typography, Avatar, alpha, Divider } from '@mui/material';
import { 
  Settings, 
  Speed as SpeedIcon, 
  Memory as ConcurrentIcon, 
  QueryStats as RequestsIcon,
  AccessTime as TimeIcon 
} from '@mui/icons-material';
import { BotStatusResponse } from '@/types';
import { format } from 'date-fns';

interface BotStatsCardProps {
  bot: BotStatusResponse;
}

interface StatItemProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color?: string;
}

const StatItem: React.FC<StatItemProps> = ({ icon, label, value, color = '#667eea' }) => (
  <Box display="flex" alignItems="center" gap={2}>
    <Box
      sx={{
        width: 40,
        height: 40,
        borderRadius: 1.5,
        bgcolor: alpha(color, 0.15),
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: color,
      }}
    >
      {icon}
    </Box>
    <Box>
      <Typography variant="caption" color="text.secondary" textTransform="uppercase" letterSpacing={0.5}>
        {label}
      </Typography>
      <Typography variant="h6" fontWeight={600}>
        {value}
      </Typography>
    </Box>
  </Box>
);

export const BotStatsCard: React.FC<BotStatsCardProps> = ({ bot }) => {
  return (
    <Card
      sx={{
        height: '100%',
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
        border: '1px solid rgba(102, 126, 234, 0.2)',
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <Avatar
            sx={{
              width: 56,
              height: 56,
              bgcolor: alpha('#667eea', 0.2),
              color: '#667eea',
            }}
          >
            <Settings sx={{ fontSize: 32 }} />
          </Avatar>
          <Box>
            <Typography variant="h6" fontWeight={600}>
              Configuration & Stats
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Performance metrics
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <StatItem
            icon={<SpeedIcon fontSize="small" />}
            label="Rate Limit (RPS)"
            value={bot.max_requests_per_second}
            color="#4caf50"
          />

          <StatItem
            icon={<ConcurrentIcon fontSize="small" />}
            label="Max Concurrent Requests"
            value={bot.max_concurrent_requests}
            color="#2196f3"
          />

          <Divider sx={{ my: 1, opacity: 0.2 }} />

          <StatItem
            icon={<RequestsIcon fontSize="small" />}
            label="Total Requests"
            value={bot.total_requests.toLocaleString()}
            color="#9c27b0"
          />

          <StatItem
            icon={<TimeIcon fontSize="small" />}
            label="Last Used"
            value={bot.last_used_at ? format(new Date(bot.last_used_at), 'MMM d, yyyy') : 'Never'}
            color="#ff9800"
          />
        </Box>
      </CardContent>
    </Card>
  );
};
