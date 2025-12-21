/**
 * Active AI Services Card Component
 * Shows user's active AI service subscriptions with "power-up" visual feel
 * Similar to Bot's ActiveServicesCard
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
  useTheme,
  Button,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Bolt as BoltIcon,
  CheckCircle as ActiveIcon,
  Schedule as ExpiringIcon,
  Add as AddIcon,
  AutoAwesome as AIServiceIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import type { ActiveAIService } from '../../types';

interface ActiveAIServicesCardProps {
  services: ActiveAIService[];
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

const getServiceIcon = (serviceKey: string): React.ReactNode => {
  // Map service keys to icons
  const iconMap: Record<string, React.ReactNode> = {
    ai_content_optimizer: <AIServiceIcon />,
    ai_analytics: <AIServiceIcon />,
    ai_auto_reply: <AIServiceIcon />,
  };
  return iconMap[serviceKey] || <AIServiceIcon />;
};

const getServiceColor = (color: string | null, serviceKey: string): string => {
  if (color) return color;
  // Default colors based on service key
  const colorMap: Record<string, string> = {
    ai_content_optimizer: '#9C27B0',
    ai_analytics: '#2196F3',
    ai_auto_reply: '#FF9800',
  };
  return colorMap[serviceKey] || '#9C27B0';
};

export const ActiveAIServicesCard: React.FC<ActiveAIServicesCardProps> = ({
  services,
  isLoading,
}) => {
  const theme = useTheme();
  const navigate = useNavigate();

  // Filter to only AI services
  const aiServices = services.filter(s => s.service_key.startsWith('ai_'));

  const handleConfigureService = (serviceKey: string) => {
    navigate(`/ai/services/${serviceKey}`);
  };

  const handleGetMore = () => {
    navigate('/marketplace?category=ai');
  };

  if (isLoading) {
    return (
      <Card
        sx={{
          background: `linear-gradient(135deg, ${alpha('#9C27B0', 0.1)} 0%, ${alpha('#673AB7', 0.1)} 100%)`,
          border: `1px solid ${alpha('#9C27B0', 0.3)}`,
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <BoltIcon sx={{ color: '#FFD700' }} />
            <Typography variant="h6">Active AI Power-Ups</Typography>
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

  if (aiServices.length === 0) {
    return (
      <Card
        sx={{
          background: `linear-gradient(135deg, ${alpha('#757575', 0.1)} 0%, ${alpha('#616161', 0.1)} 100%)`,
          border: `1px dashed ${alpha(theme.palette.text.secondary, 0.3)}`,
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={1}>
              <BoltIcon sx={{ color: '#FFD700' }} />
              <Typography variant="h6">Active AI Power-Ups</Typography>
              <Chip label="0" size="small" sx={{ ml: 1 }} />
            </Box>
            <Button
              variant="contained"
              size="small"
              startIcon={<AddIcon />}
              onClick={handleGetMore}
              sx={{
                background: 'linear-gradient(90deg, #9C27B0 0%, #673AB7 100%)',
              }}
            >
              Get AI Services
            </Button>
          </Box>
          <Box
            sx={{
              mt: 3,
              p: 3,
              textAlign: 'center',
              borderRadius: 2,
              backgroundColor: alpha(theme.palette.background.paper, 0.5),
            }}
          >
            <AIServiceIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
            <Typography variant="body1" color="text.secondary">
              No AI services active
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Purchase AI services from the marketplace to unlock powerful features
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      sx={{
        background: `linear-gradient(135deg, ${alpha('#9C27B0', 0.1)} 0%, ${alpha('#673AB7', 0.1)} 100%)`,
        border: `1px solid ${alpha('#9C27B0', 0.3)}`,
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <BoltIcon sx={{ color: '#FFD700' }} />
            <Typography variant="h6" fontWeight={600}>
              Active AI Power-Ups
            </Typography>
            <Chip
              label={aiServices.length}
              size="small"
              sx={{
                ml: 1,
                backgroundColor: alpha('#9C27B0', 0.2),
                color: '#9C27B0',
                fontWeight: 600,
              }}
            />
          </Box>
          <Button
            variant="outlined"
            size="small"
            startIcon={<AddIcon />}
            onClick={handleGetMore}
            sx={{ borderColor: '#9C27B0', color: '#9C27B0' }}
          >
            Get More
          </Button>
        </Box>

        <Box display="flex" gap={2} flexWrap="wrap">
          {aiServices.map((service) => {
            const daysRemaining = getDaysRemaining(service.expires_at);
            const isExpiring = daysRemaining <= 7;
            const serviceColor = getServiceColor(service.color, service.service_key);
            const dailyUsage = getUsagePercentage(service.usage_count_daily, service.usage_quota_daily);

            return (
              <Box
                key={service.id}
                sx={{
                  position: 'relative',
                  width: 140,
                  p: 2,
                  borderRadius: 2,
                  backgroundColor: alpha(serviceColor, 0.15),
                  border: `1px solid ${alpha(serviceColor, 0.3)}`,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: `0 4px 20px ${alpha(serviceColor, 0.3)}`,
                  },
                }}
              >
                {/* Status Badge */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: 8,
                    right: 8,
                  }}
                >
                  {isExpiring ? (
                    <Tooltip title={`Expires in ${daysRemaining} days`}>
                      <ExpiringIcon sx={{ color: '#FF9800', fontSize: 18 }} />
                    </Tooltip>
                  ) : (
                    <Tooltip title="Active">
                      <ActiveIcon sx={{ color: '#4CAF50', fontSize: 18 }} />
                    </Tooltip>
                  )}
                </Box>

                {/* Icon */}
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: 1.5,
                    backgroundColor: alpha(serviceColor, 0.2),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mb: 1.5,
                    mx: 'auto',
                    color: serviceColor,
                    '& svg': { fontSize: 24 },
                  }}
                >
                  {getServiceIcon(service.service_key)}
                </Box>

                {/* Name */}
                <Typography
                  variant="body2"
                  fontWeight={600}
                  textAlign="center"
                  noWrap
                  sx={{ mb: 1 }}
                >
                  {service.service_name}
                </Typography>

                {/* Usage */}
                {service.usage_quota_daily && (
                  <Box sx={{ mb: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={dailyUsage}
                      sx={{
                        height: 4,
                        borderRadius: 1,
                        backgroundColor: alpha(serviceColor, 0.2),
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: serviceColor,
                          borderRadius: 1,
                        },
                      }}
                    />
                    <Typography variant="caption" color="text.secondary" textAlign="center" display="block">
                      {service.usage_count_daily}/{service.usage_quota_daily} Today
                    </Typography>
                  </Box>
                )}

                {/* Settings Button */}
                <Box textAlign="center">
                  <Tooltip title="Configure">
                    <IconButton
                      size="small"
                      onClick={() => handleConfigureService(service.service_key)}
                      sx={{
                        color: serviceColor,
                        '&:hover': {
                          backgroundColor: alpha(serviceColor, 0.1),
                        },
                      }}
                    >
                      <SettingsIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
            );
          })}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ActiveAIServicesCard;
