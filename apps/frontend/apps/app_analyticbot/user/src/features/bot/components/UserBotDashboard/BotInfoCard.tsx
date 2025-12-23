/**
 * Bot Information Card Component
 */
import React from 'react';
import { Box, Card, CardContent, Chip, Typography, Alert, Avatar, alpha, Button } from '@mui/material';
import { SmartToy, CheckCircle, Error as ErrorIcon, VerifiedUser as VerifyIcon } from '@mui/icons-material';
import { BotStatusResponse } from '@/types';
import { getStatusColor } from './utils';

interface BotInfoCardProps {
  bot: BotStatusResponse;
  onVerify?: () => void;
  isVerifying?: boolean;
}

export const BotInfoCard: React.FC<BotInfoCardProps> = ({ bot, onVerify, isVerifying }) => {
  const isActive = bot.status === 'active';
  const needsVerification = !bot.is_verified || bot.status === 'pending' || !bot.bot_id;
  
  return (
    <Card
      sx={{
        height: '100%',
        background: isActive 
          ? 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(46, 125, 50, 0.1) 100%)'
          : 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(245, 124, 0, 0.1) 100%)',
        border: isActive 
          ? '1px solid rgba(76, 175, 80, 0.3)'
          : '1px solid rgba(255, 152, 0, 0.3)',
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <Avatar
            sx={{
              width: 56,
              height: 56,
              bgcolor: isActive ? alpha('#4caf50', 0.2) : alpha('#ff9800', 0.2),
              color: isActive ? '#4caf50' : '#ff9800',
            }}
          >
            <SmartToy sx={{ fontSize: 32 }} />
          </Avatar>
          <Box>
            <Typography variant="h6" fontWeight={600}>
              Bot Information
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Your Telegram bot details
            </Typography>
          </Box>
        </Box>

        <Box 
          sx={{ 
            display: 'grid', 
            gridTemplateColumns: '1fr',
            gap: 2,
          }}
        >
          <Box>
            <Typography variant="caption" color="text.secondary" textTransform="uppercase" letterSpacing={0.5}>
              Username
            </Typography>
            <Typography variant="body1" fontWeight={600} sx={{ fontFamily: 'monospace' }}>
              @{bot?.bot_username || 'Unknown'}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary" textTransform="uppercase" letterSpacing={0.5}>
              Bot ID
            </Typography>
            <Typography variant="body1" sx={{ fontFamily: 'monospace' }}>
              {bot?.bot_id || 'N/A'}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary" textTransform="uppercase" letterSpacing={0.5}>
              Status
            </Typography>
            <Box display="flex" alignItems="center" gap={1} mt={0.5}>
              {isActive ? (
                <CheckCircle sx={{ color: '#4caf50', fontSize: 20 }} />
              ) : (
                <ErrorIcon sx={{ color: '#ff9800', fontSize: 20 }} />
              )}
              <Chip
                label={bot.status.toUpperCase()}
                color={getStatusColor(bot.status)}
                size="small"
                sx={{ fontWeight: 600 }}
              />
              {bot.is_verified && (
                <Chip 
                  label="VERIFIED" 
                  color="info" 
                  size="small" 
                  sx={{ fontWeight: 600 }}
                />
              )}
            </Box>
          </Box>
        </Box>

        {needsVerification && onVerify && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="body2" fontWeight="bold">
                  Bot Not Verified
                </Typography>
                <Typography variant="body2">
                  Click verify to test the bot token and activate your bot.
                </Typography>
              </Box>
              <Button
                variant="contained"
                color="primary"
                startIcon={<VerifyIcon />}
                onClick={() => {
                  console.log('[BotInfoCard] Verify button clicked');
                  console.log('[BotInfoCard] onVerify function:', onVerify);
                  console.log('[BotInfoCard] isVerifying:', isVerifying);
                  if (onVerify) {
                    onVerify();
                  }
                }}
                disabled={isVerifying}
                size="small"
              >
                {isVerifying ? 'Verifying...' : 'Verify Bot'}
              </Button>
            </Box>
          </Alert>
        )}

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
