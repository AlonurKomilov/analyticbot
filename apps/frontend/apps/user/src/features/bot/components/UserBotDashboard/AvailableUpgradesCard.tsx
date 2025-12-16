/**
 * Available Upgrades Card Component
 * Shows bot services user doesn't own yet with "unlock" visual style
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Skeleton,
  alpha,
  Button,
} from '@mui/material';
import {
  Lock as LockIcon,
  ShoppingCart as CartIcon,
  RocketLaunch as RocketIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { getServiceIcon } from '@/features/marketplace';

export interface AvailableService {
  id: number;
  service_key: string;
  name: string;
  short_description: string;
  icon: string | null;
  color: string | null;
  price_credits_monthly: number;
  is_featured: boolean;
  is_popular: boolean;
}

interface AvailableUpgradesCardProps {
  services: AvailableService[];
  activeServiceKeys: string[];
  isLoading: boolean;
}

export const AvailableUpgradesCard: React.FC<AvailableUpgradesCardProps> = ({
  services,
  activeServiceKeys,
  isLoading,
}) => {
  const navigate = useNavigate();
  
  // Filter to only show bot services that user doesn't have
  const availableServices = services.filter(
    s => s.service_key.startsWith('bot_') && !activeServiceKeys.includes(s.service_key)
  );

  if (isLoading) {
    return (
      <Card sx={{ bgcolor: 'rgba(255, 255, 255, 0.02)' }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <RocketIcon sx={{ color: 'text.secondary' }} />
            <Typography variant="h6" color="text.secondary">
              Available Upgrades
            </Typography>
          </Box>
          <Box display="flex" gap={2} flexWrap="wrap">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} variant="rounded" width={160} height={100} />
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (availableServices.length === 0) {
    return (
      <Card
        sx={{
          bgcolor: 'rgba(76, 175, 80, 0.1)',
          border: '1px solid rgba(76, 175, 80, 0.3)',
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" gap={1}>
            <RocketIcon sx={{ color: '#4caf50' }} />
            <Typography variant="h6" color="#4caf50">
              🎉 Fully Powered Up!
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" mt={1}>
            You have all available bot services! Your bot is running at maximum potential.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Show max 4 available services, prioritize featured/popular
  const displayServices = [...availableServices]
    .sort((a, b) => {
      if (a.is_featured !== b.is_featured) return a.is_featured ? -1 : 1;
      if (a.is_popular !== b.is_popular) return a.is_popular ? -1 : 1;
      return a.price_credits_monthly - b.price_credits_monthly;
    })
    .slice(0, 4);

  return (
    <Card
      sx={{
        bgcolor: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <RocketIcon sx={{ color: 'text.secondary' }} />
            <Typography variant="h6" color="text.secondary">
              Available Upgrades
            </Typography>
            <Chip
              label={availableServices.length}
              size="small"
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                color: 'text.secondary',
                fontSize: '0.75rem',
              }}
            />
          </Box>
          {availableServices.length > 4 && (
            <Chip
              label="View All"
              size="small"
              onClick={() => navigate('/marketplace?tab=services')}
              sx={{
                cursor: 'pointer',
                bgcolor: 'rgba(255, 255, 255, 0.1)',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.2)',
                },
              }}
            />
          )}
        </Box>

        <Box display="flex" gap={2} flexWrap="wrap">
          {displayServices.map((service) => {
            const serviceColor = service.color || '#888';

            return (
              <Box
                key={service.id}
                sx={{
                  width: 160,
                  p: 2,
                  borderRadius: 2,
                  bgcolor: 'rgba(255, 255, 255, 0.03)',
                  border: '1px dashed rgba(255, 255, 255, 0.15)',
                  position: 'relative',
                  transition: 'all 0.2s ease',
                  cursor: 'pointer',
                  opacity: 0.7,
                  '&:hover': {
                    opacity: 1,
                    borderColor: alpha(serviceColor, 0.5),
                    bgcolor: alpha(serviceColor, 0.1),
                    transform: 'translateY(-2px)',
                  },
                }}
                onClick={() => navigate(`/marketplace?tab=services&highlight=${service.service_key}`)}
              >
                {/* Lock Badge */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: -8,
                    right: -8,
                    bgcolor: 'rgba(0, 0, 0, 0.6)',
                    borderRadius: '50%',
                    p: 0.5,
                    display: 'flex',
                  }}
                >
                  <LockIcon sx={{ fontSize: 12, color: 'rgba(255, 255, 255, 0.6)' }} />
                </Box>

                {/* Popular/Featured Badge */}
                {(service.is_featured || service.is_popular) && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: -8,
                      left: -8,
                    }}
                  >
                    <Chip
                      label={service.is_featured ? '⭐' : '🔥'}
                      size="small"
                      sx={{
                        height: 20,
                        fontSize: '0.65rem',
                        bgcolor: service.is_featured ? '#FFD700' : '#ff5722',
                        color: service.is_featured ? '#000' : '#fff',
                      }}
                    />
                  </Box>
                )}

                {/* Icon */}
                <Box
                  sx={{
                    width: 36,
                    height: 36,
                    borderRadius: 1.5,
                    bgcolor: alpha(serviceColor, 0.2),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: alpha(serviceColor, 0.6),
                    mb: 1,
                    mx: 'auto',
                    filter: 'grayscale(50%)',
                  }}
                >
                  {getServiceIcon(service.service_key)}
                </Box>

                {/* Name */}
                <Typography
                  variant="caption"
                  fontWeight={500}
                  textAlign="center"
                  display="block"
                  noWrap
                  title={service.name}
                  sx={{ color: 'text.secondary', mb: 0.5 }}
                >
                  {service.name.replace('Bot ', '').replace(' System', '')}
                </Typography>

                {/* Price */}
                <Typography
                  variant="caption"
                  textAlign="center"
                  display="block"
                  sx={{ color: '#FFD700', fontWeight: 600 }}
                >
                  {service.price_credits_monthly} credits/mo
                </Typography>
              </Box>
            );
          })}
        </Box>

        {/* CTA */}
        <Box mt={2} textAlign="center">
          <Button
            variant="outlined"
            size="small"
            startIcon={<CartIcon />}
            onClick={() => navigate('/marketplace?tab=services')}
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.2)',
              color: 'text.secondary',
              '&:hover': {
                borderColor: '#667eea',
                color: '#667eea',
              },
            }}
          >
            Browse All Power-Ups
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AvailableUpgradesCard;
