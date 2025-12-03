/**
 * Bot Information Card Component
 */
import React from 'react';
import { Box, Card, CardContent, Chip, Typography, Alert } from '@mui/material';
import { SmartToy } from '@mui/icons-material';
import { BotStatusResponse } from '@/types';
import { getStatusIcon, getStatusColor } from './utils';

interface BotInfoCardProps {
  bot: BotStatusResponse;
}

export const BotInfoCard: React.FC<BotInfoCardProps> = ({ bot }) => {
  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <SmartToy sx={{ mr: 1, fontSize: 32 }} />
          <Typography variant="h6">Bot Information</Typography>
        </Box>

        <Box mb={2}>
          <Typography variant="body2" color="text.secondary">
            Username
          </Typography>
          <Typography variant="body1" fontWeight="bold">
            @{bot?.bot_username || 'Unknown'}
          </Typography>
        </Box>

        <Box mb={2}>
          <Typography variant="body2" color="text.secondary">
            Bot ID
          </Typography>
          <Typography variant="body1">{bot?.bot_id || 'N/A'}</Typography>
        </Box>

        <Box mb={2}>
          <Typography variant="body2" color="text.secondary">
            Status
          </Typography>
          <Box display="flex" alignItems="center" mt={1}>
            {getStatusIcon(bot.status)}
            <Chip
              label={bot.status.toUpperCase()}
              color={getStatusColor(bot.status)}
              size="small"
              sx={{ ml: 1 }}
            />
            {bot.is_verified && (
              <Chip label="VERIFIED" color="success" size="small" sx={{ ml: 1 }} />
            )}
          </Box>
        </Box>

        {bot.suspension_reason && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            <Typography variant="body2" fontWeight="bold">
              Suspension Reason:
            </Typography>
            <Typography variant="body2">{bot.suspension_reason}</Typography>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};
