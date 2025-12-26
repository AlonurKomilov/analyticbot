/**
 * Available AI Upgrades Card Component
 * Shows AI services available for purchase
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Skeleton,
  alpha,
  useTheme,
  Tooltip,
} from '@mui/material';
import {
  Rocket as UpgradeIcon,
  Lock as LockedIcon,
  AutoAwesome as AIServiceIcon,
  ArrowForward as ArrowIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import type { AvailableAIService } from '../../types';

interface AvailableAIUpgradesCardProps {
  services: AvailableAIService[];
  activeServiceKeys: string[];
  userTier: string;
  isLoading: boolean;
}

const getTierLevel = (tier: string): number => {
  const levels: Record<string, number> = {
    free: 0,
    basic: 1,
    pro: 2,
    enterprise: 3,
  };
  return levels[tier] || 0;
};

const getServiceColor = (service: AvailableAIService): string => {
  if (service.color) return service.color;
  const colorMap: Record<string, string> = {
    content_scheduler: '#9C27B0',
    auto_reply: '#FF9800',
    competitor_analysis: '#2196F3',
    custom_queries: '#4CAF50',
  };
  return colorMap[service.id] || '#9C27B0';
};

export const AvailableAIUpgradesCard: React.FC<AvailableAIUpgradesCardProps> = ({
  services,
  activeServiceKeys,
  userTier,
  isLoading,
}) => {
  const theme = useTheme();
  const navigate = useNavigate();

  // Filter out already active services
  const availableServices = services.filter(
    (s) => !activeServiceKeys.includes(s.id) && !s.enabled
  );

  const handleViewService = (serviceId: string) => {
    navigate(`/marketplace/service/${serviceId}`);
  };

  const handleViewAll = () => {
    navigate('/marketplace?category=ai');
  };

  if (isLoading) {
    return (
      <Card
        sx={{
          background: `linear-gradient(135deg, ${alpha('#FFD700', 0.05)} 0%, ${alpha('#FFA000', 0.05)} 100%)`,
          border: `1px solid ${alpha('#FFD700', 0.2)}`,
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <UpgradeIcon sx={{ color: '#FFD700' }} />
            <Typography variant="h6">Available AI Upgrades</Typography>
          </Box>
          <Box display="flex" gap={2} flexWrap="wrap">
            {[1, 2].map((i) => (
              <Skeleton key={i} variant="rounded" width={200} height={100} />
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (availableServices.length === 0) {
    return null; // Don't show if no upgrades available
  }

  const userTierLevel = getTierLevel(userTier);

  return (
    <Card
      sx={{
        background: `linear-gradient(135deg, ${alpha('#FFD700', 0.08)} 0%, ${alpha('#FFA000', 0.05)} 100%)`,
        border: `1px solid ${alpha('#FFD700', 0.25)}`,
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <UpgradeIcon sx={{ color: '#FFD700' }} />
            <Typography variant="h6" fontWeight={600}>
              Available AI Upgrades
            </Typography>
            <Chip
              label={availableServices.length}
              size="small"
              sx={{
                ml: 1,
                backgroundColor: alpha('#FFD700', 0.2),
                color: '#B8860B',
                fontWeight: 600,
              }}
            />
          </Box>
          <Button
            size="small"
            endIcon={<ArrowIcon />}
            onClick={handleViewAll}
            sx={{ color: '#B8860B' }}
          >
            View All
          </Button>
        </Box>

        <Box display="flex" gap={2} flexWrap="wrap">
          {availableServices.slice(0, 4).map((service) => {
            const requiredTierLevel = getTierLevel(service.tier_required);
            const isLocked = requiredTierLevel > userTierLevel;
            const serviceColor = getServiceColor(service);

            return (
              <Box
                key={service.id}
                sx={{
                  position: 'relative',
                  width: 200,
                  p: 2,
                  borderRadius: 2,
                  backgroundColor: alpha(serviceColor, isLocked ? 0.05 : 0.1),
                  border: `1px ${isLocked ? 'dashed' : 'solid'} ${alpha(serviceColor, 0.3)}`,
                  opacity: isLocked ? 0.7 : 1,
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    transform: isLocked ? 'none' : 'translateY(-2px)',
                    boxShadow: isLocked ? 'none' : `0 4px 20px ${alpha(serviceColor, 0.2)}`,
                  },
                }}
              >
                {/* Lock Badge */}
                {isLocked && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 8,
                      right: 8,
                    }}
                  >
                    <Tooltip title={`Requires ${service.tier_required} tier`}>
                      <LockedIcon sx={{ color: theme.palette.text.secondary, fontSize: 18 }} />
                    </Tooltip>
                  </Box>
                )}

                {/* Header */}
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <Box
                    sx={{
                      width: 32,
                      height: 32,
                      borderRadius: 1,
                      backgroundColor: alpha(serviceColor, 0.2),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <AIServiceIcon sx={{ color: serviceColor, fontSize: 18 }} />
                  </Box>
                  <Typography variant="body2" fontWeight={600} noWrap sx={{ flex: 1 }}>
                    {service.name}
                  </Typography>
                </Box>

                {/* Description */}
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    mb: 1.5,
                    minHeight: 32,
                  }}
                >
                  {service.description}
                </Typography>

                {/* Tier Badge */}
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Chip
                    label={service.tier_required}
                    size="small"
                    sx={{
                      fontSize: '0.65rem',
                      height: 20,
                      textTransform: 'capitalize',
                      backgroundColor: alpha(serviceColor, 0.15),
                      color: serviceColor,
                    }}
                  />
                  {!isLocked && (
                    <Button
                      size="small"
                      variant="text"
                      onClick={() => handleViewService(service.id)}
                      sx={{ 
                        fontSize: '0.7rem', 
                        color: serviceColor,
                        minWidth: 'auto',
                        p: 0.5,
                      }}
                    >
                      Get
                    </Button>
                  )}
                </Box>
              </Box>
            );
          })}
        </Box>
      </CardContent>
    </Card>
  );
};

export default AvailableAIUpgradesCard;
