/**
 * Active Services Card Component
 * Shows user's active bot service subscriptions with "power-up" visual feel
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Skeleton,
  alpha,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Bolt as BoltIcon,
  CheckCircle as ActiveIcon,
  Schedule as ExpiringIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { getServiceIcon } from '@/features/marketplace';

export interface ActiveService {
  id: number;
  service_key: string;
  service_name: string;
  icon: string | null;
  color: string | null;
  status: 'active' | 'expired' | 'cancelled';
  expires_at: string;
  usage_quota_daily: number | null;
  usage_quota_monthly: number | null;
  usage_count_daily: number;
  usage_count_monthly: number;
}

interface ActiveServicesCardProps {
  services: ActiveService[];
  isLoading: boolean;
}

const getDaysRemaining = (expiresAt: string): number => {
  const now = new Date();
  const expires = new Date(expiresAt);
  const diff = expires.getTime() - now.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
};

const getUsagePercentage = (used: number, quota: number | null): number => {
  if (!quota) return 0;
  return Math.min((used / quota) * 100, 100);
};

export const ActiveServicesCard: React.FC<ActiveServicesCardProps> = ({
  services,
  isLoading,
}) => {
  const navigate = useNavigate();
  const botServices = services.filter(s => s.service_key.startsWith('bot_'));

  const handleConfigureService = (serviceKey: string) => {
    navigate(`/workers/bot/service/${serviceKey}`);
  };

  if (isLoading) {
    return (
      <Card
        sx={{
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
          border: '1px solid rgba(102, 126, 234, 0.3)',
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <BoltIcon sx={{ color: '#FFD700' }} />
            <Typography variant="h6">Active Power-Ups</Typography>
          </Box>
          <Box display="flex" gap={2} flexWrap="wrap">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} variant="rounded" width={140} height={120} />
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (botServices.length === 0) {
    return (
      <Card
        sx={{
          background: 'linear-gradient(135deg, rgba(100, 100, 100, 0.1) 0%, rgba(80, 80, 80, 0.1) 100%)',
          border: '1px dashed rgba(255, 255, 255, 0.2)',
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <BoltIcon sx={{ color: 'text.secondary' }} />
            <Typography variant="h6" color="text.secondary">
              No Active Power-Ups
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" mb={2}>
            Supercharge your bot with premium features! Get spam protection, auto-moderation, welcome messages, and more.
          </Typography>
          <Chip
            label="Browse Power-Ups"
            onClick={() => navigate('/marketplace?tab=services')}
            sx={{
              cursor: 'pointer',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              '&:hover': {
                background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
              },
            }}
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      sx={{
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%)',
        border: '1px solid rgba(102, 126, 234, 0.4)',
        position: 'relative',
        overflow: 'visible',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: -1,
          left: -1,
          right: -1,
          bottom: -1,
          background: 'linear-gradient(135deg, #667eea, #764ba2, #667eea)',
          backgroundSize: '200% 200%',
          animation: 'gradientShift 3s ease infinite',
          borderRadius: 'inherit',
          zIndex: -1,
          opacity: 0.5,
        },
        '@keyframes gradientShift': {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        },
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <BoltIcon sx={{ color: '#FFD700', filter: 'drop-shadow(0 0 4px #FFD700)' }} />
            <Typography variant="h6" fontWeight={600}>
              Active Power-Ups
            </Typography>
            <Chip
              label={botServices.length}
              size="small"
              sx={{
                bgcolor: 'rgba(102, 126, 234, 0.3)',
                color: '#a5b4fc',
                fontWeight: 600,
              }}
            />
          </Box>
          <Chip
            label="+ Get More"
            size="small"
            onClick={() => navigate('/marketplace?tab=services')}
            sx={{
              cursor: 'pointer',
              bgcolor: 'rgba(255, 215, 0, 0.2)',
              color: '#FFD700',
              '&:hover': {
                bgcolor: 'rgba(255, 215, 0, 0.3)',
              },
            }}
          />
        </Box>

        <Box display="flex" gap={2} flexWrap="wrap">
          {botServices.map((service) => {
            const daysRemaining = getDaysRemaining(service.expires_at);
            const isExpiringSoon = daysRemaining <= 7 && daysRemaining > 0;
            const dailyUsage = getUsagePercentage(service.usage_count_daily, service.usage_quota_daily);
            const serviceColor = service.color || '#667eea';

            return (
              <Box
                key={service.id}
                sx={{
                  width: 140,
                  p: 2,
                  borderRadius: 2,
                  bgcolor: alpha(serviceColor, 0.15),
                  border: `1px solid ${alpha(serviceColor, 0.4)}`,
                  position: 'relative',
                  transition: 'all 0.2s ease',
                  cursor: 'pointer',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: `0 4px 20px ${alpha(serviceColor, 0.3)}`,
                    bgcolor: alpha(serviceColor, 0.2),
                  },
                }}
                onClick={() => handleConfigureService(service.service_key)}
              >
                {/* Status Badge */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: -8,
                    right: -8,
                  }}
                >
                  {isExpiringSoon ? (
                    <Tooltip title={`Expires in ${daysRemaining} days`}>
                      <Box
                        sx={{
                          bgcolor: '#ff9800',
                          borderRadius: '50%',
                          p: 0.5,
                          display: 'flex',
                          animation: 'pulse 2s infinite',
                          '@keyframes pulse': {
                            '0%': { boxShadow: '0 0 0 0 rgba(255, 152, 0, 0.4)' },
                            '70%': { boxShadow: '0 0 0 6px rgba(255, 152, 0, 0)' },
                            '100%': { boxShadow: '0 0 0 0 rgba(255, 152, 0, 0)' },
                          },
                        }}
                      >
                        <ExpiringIcon sx={{ fontSize: 14, color: 'white' }} />
                      </Box>
                    </Tooltip>
                  ) : (
                    <Tooltip title="Active">
                      <Box
                        sx={{
                          bgcolor: '#4caf50',
                          borderRadius: '50%',
                          p: 0.5,
                          display: 'flex',
                        }}
                      >
                        <ActiveIcon sx={{ fontSize: 14, color: 'white' }} />
                      </Box>
                    </Tooltip>
                  )}
                </Box>

                {/* Icon */}
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: 1.5,
                    bgcolor: alpha(serviceColor, 0.3),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: serviceColor,
                    mb: 1,
                    mx: 'auto',
                  }}
                >
                  {getServiceIcon(service.service_key)}
                </Box>

                {/* Name */}
                <Typography
                  variant="caption"
                  fontWeight={600}
                  textAlign="center"
                  display="block"
                  noWrap
                  title={service.service_name}
                  sx={{ color: 'text.primary', mb: 1 }}
                >
                  {service.service_name.replace('Bot ', '').replace(' System', '')}
                </Typography>

                {/* Usage Bar (if applicable) */}
                {service.usage_quota_daily && (
                  <Box>
                    <LinearProgress
                      variant="determinate"
                      value={dailyUsage}
                      sx={{
                        height: 4,
                        borderRadius: 2,
                        bgcolor: alpha(serviceColor, 0.2),
                        '& .MuiLinearProgress-bar': {
                          bgcolor: dailyUsage > 80 ? '#ff5722' : serviceColor,
                        },
                      }}
                    />
                    <Typography variant="caption" color="text.secondary" fontSize={10}>
                      {service.usage_count_daily}/{service.usage_quota_daily} today
                    </Typography>
                  </Box>
                )}

                {/* Configure Button */}
                <Tooltip title="Configure">
                  <IconButton
                    size="small"
                    sx={{
                      position: 'absolute',
                      bottom: 4,
                      right: 4,
                      opacity: 0.6,
                      '&:hover': { opacity: 1 },
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleConfigureService(service.service_key);
                    }}
                  >
                    <SettingsIcon sx={{ fontSize: 16 }} />
                  </IconButton>
                </Tooltip>
              </Box>
            );
          })}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ActiveServicesCard;
