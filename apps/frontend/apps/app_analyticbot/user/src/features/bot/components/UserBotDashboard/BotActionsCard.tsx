/**
 * Bot Actions Card Component
 */
import React from 'react';
import { Box, Button, Card, CardContent, Typography, Divider } from '@mui/material';
import { Delete, Settings, Send, Store } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

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
  const navigate = useNavigate();

  return (
    <Card sx={{ bgcolor: 'rgba(255, 255, 255, 0.02)' }}>
      <CardContent>
        <Typography variant="h6" mb={2} color="text.secondary">
          Quick Actions
        </Typography>
        <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
          {/* Primary Actions */}
          <Button
            variant="contained"
            startIcon={<Send />}
            onClick={onSendTestMessage}
            sx={{
              background: 'linear-gradient(135deg, #4caf50 0%, #2e7d32 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #2e7d32 0%, #4caf50 100%)',
              },
            }}
          >
            Send Test Message
          </Button>
          
          <Button
            variant="contained"
            startIcon={<Store />}
            onClick={() => navigate('/marketplace?tab=services')}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
              },
            }}
          >
            Browse Power-Ups
          </Button>

          <Divider orientation="vertical" flexItem sx={{ mx: 1, opacity: 0.3 }} />

          {/* Secondary Actions */}
          <Button
            variant="outlined"
            startIcon={<Settings />}
            onClick={onUpdateRateLimits}
            disabled={isUpdating}
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.2)',
              color: 'text.secondary',
              '&:hover': {
                borderColor: 'rgba(255, 255, 255, 0.4)',
                bgcolor: 'rgba(255, 255, 255, 0.05)',
              },
            }}
          >
            Rate Limits
          </Button>
          
          <Button
            variant="outlined"
            color="error"
            startIcon={<Delete />}
            onClick={onRemoveBot}
            disabled={isRemoving}
            sx={{
              borderColor: 'rgba(244, 67, 54, 0.3)',
              '&:hover': {
                borderColor: 'rgba(244, 67, 54, 0.5)',
                bgcolor: 'rgba(244, 67, 54, 0.1)',
              },
            }}
          >
            Remove Bot
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};
