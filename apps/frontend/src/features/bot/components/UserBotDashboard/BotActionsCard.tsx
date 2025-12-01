/**
 * Bot Actions Card Component
 */
import React from 'react';
import { Box, Button, Card, CardContent, Typography } from '@mui/material';
import { Delete, Settings, Send } from '@mui/icons-material';

interface BotActionsCardProps {
  onSendTestMessage: () => void;
  onUpdateRateLimits: () => void;
  onRemoveBot: () => void;
  isUpdating: boolean;
  isRemoving: boolean;
}

export const BotActionsCard: React.FC<BotActionsCardProps> = ({
  onSendTestMessage,
  onUpdateRateLimits,
  onRemoveBot,
  isUpdating,
  isRemoving,
}) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>
          Actions
        </Typography>
        <Box display="flex" gap={2} flexWrap="wrap">
          <Button
            variant="contained"
            startIcon={<Send />}
            onClick={onSendTestMessage}
            color="primary"
          >
            Send Test Message
          </Button>
          <Button
            variant="outlined"
            startIcon={<Settings />}
            onClick={onUpdateRateLimits}
            disabled={isUpdating}
          >
            Update Rate Limits
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<Delete />}
            onClick={onRemoveBot}
            disabled={isRemoving}
          >
            Remove Bot
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};
