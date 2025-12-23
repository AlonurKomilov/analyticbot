/**
 * UserBotDashboard Utility Functions
 */
import React from 'react';
import { CheckCircle, Error, Warning, HourglassEmpty } from '@mui/icons-material';
import { BotStatus } from '@/types';
import { StatusColor } from './types';

export const getStatusIcon = (status: BotStatus): React.ReactElement => {
  switch (status) {
    case BotStatus.ACTIVE:
      return <CheckCircle color="success" />;
    case BotStatus.SUSPENDED:
      return <Error color="error" />;
    case BotStatus.RATE_LIMITED:
      return <Warning color="warning" />;
    case BotStatus.PENDING:
      return <HourglassEmpty color="info" />;
    default:
      return <Error color="error" />;
  }
};

export const getStatusColor = (status: BotStatus): StatusColor => {
  switch (status) {
    case BotStatus.ACTIVE:
      return 'success';
    case BotStatus.SUSPENDED:
      return 'error';
    case BotStatus.RATE_LIMITED:
      return 'warning';
    case BotStatus.PENDING:
      return 'info';
    default:
      return 'default';
  }
};

/**
 * Convert channel ID to Telegram chat ID format
 * Modern Telegram channels: -channelId (e.g., 1002678877654 → -1002678877654)
 */
export const convertChannelToChatId = (telegramId: string): number | null => {
  const channelId = parseInt(telegramId, 10);
  if (isNaN(channelId)) {
    return null;
  }
  return -channelId;
};
