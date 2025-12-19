/**
 * Available MTProto Upgrades Card Component
 * Shows MTProto services available for purchase
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Skeleton,
  alpha,
} from '@mui/material';
import {
  RocketLaunch as UpgradeIcon,
  Lock as LockIcon,
  ShoppingCart as CartIcon,
  History as HistoryIcon,
  Schedule as ScheduleIcon,
  Download as DownloadIcon,
  ImportExport as ExportIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export interface AvailableMTProtoService {
  id: number;
  service_key: string;
  name: string;
  description: string;
  credits_per_month: number;
  icon: string | null;
  color: string | null;
  category: string;
  features: string[];
}

interface AvailableMTProtoUpgradesCardProps {
  services: AvailableMTProtoService[];
  activeServiceKeys: string[];
  isLoading: boolean;
}

// Get icon for MTProto service
const getMTProtoServiceIcon = (serviceKey: string) => {
  switch (serviceKey) {
    case 'mtproto_history_access':
      return <HistoryIcon />;
    case 'mtproto_auto_collect':
      return <ScheduleIcon />;
    case 'mtproto_media_download':
      return <DownloadIcon />;
    case 'mtproto_bulk_export':
      return <ExportIcon />;
    default:
      return <UpgradeIcon />;
  }
};

// Get color for MTProto service
const getMTProtoServiceColor = (serviceKey: string): string => {
  switch (serviceKey) {
    case 'mtproto_history_access':
      return '#2196F3'; // Blue
    case 'mtproto_auto_collect':
      return '#4CAF50'; // Green
    case 'mtproto_media_download':
      return '#FF9800'; // Orange
    case 'mtproto_bulk_export':
      return '#9C27B0'; // Purple
    default:
      return '#667eea';
  }
};

export const AvailableMTProtoUpgradesCard: React.FC<AvailableMTProtoUpgradesCardProps> = ({
  services,
  activeServiceKeys,
  isLoading,
}) => {
  const { t } = useTranslation(['mtproto', 'common']);
  const navigate = useNavigate();

  // Filter MTProto services that are not already active
  const availableMTProtoServices = services.filter(
    s => s.service_key.startsWith('mtproto_') && !activeServiceKeys.includes(s.service_key)
  );

  const handleSubscribe = (serviceKey: string) => {
    navigate(`/marketplace/service/${serviceKey}`);
  };

  if (isLoading) {
    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <UpgradeIcon sx={{ color: 'text.secondary' }} />
            <Typography variant="h6">{t('mtproto:services.availableUpgrades', 'Available MTProto Upgrades')}</Typography>
          </Box>
          <Box display="flex" gap={2} flexWrap="wrap">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} variant="rounded" width={140} height={100} />
            ))}
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (availableMTProtoServices.length === 0) {
    return null; // Don't show if all services are already active
  }

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <UpgradeIcon sx={{ color: 'text.secondary' }} />
            <Typography variant="h6">
              {t('mtproto:services.availableUpgrades', 'Available MTProto Upgrades')}
            </Typography>
            <Chip
              label={availableMTProtoServices.length}
              size="small"
              sx={{
                bgcolor: 'rgba(156, 39, 176, 0.2)',
                color: '#CE93D8',
                fontWeight: 600,
              }}
            />
          </Box>
          <Chip
            label={t('common:browseAll', 'Browse All Power-Ups')}
            size="small"
            onClick={() => navigate('/marketplace?tab=services')}
            icon={<CartIcon sx={{ fontSize: 16 }} />}
            sx={{
              cursor: 'pointer',
              bgcolor: 'rgba(156, 39, 176, 0.1)',
              color: '#CE93D8',
              '&:hover': {
                bgcolor: 'rgba(156, 39, 176, 0.2)',
              },
            }}
          />
        </Box>

        <Box display="flex" gap={2} flexWrap="wrap">
          {availableMTProtoServices.map((service) => {
            const serviceColor = service.color || getMTProtoServiceColor(service.service_key);

            return (
              <Box
                key={service.id}
                sx={{
                  width: 140,
                  p: 2,
                  borderRadius: 2,
                  bgcolor: 'background.paper',
                  border: '1px solid',
                  borderColor: 'divider',
                  position: 'relative',
                  transition: 'all 0.2s ease',
                  cursor: 'pointer',
                  opacity: 0.85,
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: `0 4px 20px ${alpha(serviceColor, 0.2)}`,
                    borderColor: serviceColor,
                    opacity: 1,
                  },
                }}
                onClick={() => handleSubscribe(service.service_key)}
              >
                {/* Lock Badge */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: -8,
                    right: -8,
                    bgcolor: 'grey.700',
                    borderRadius: '50%',
                    p: 0.5,
                    display: 'flex',
                  }}
                >
                  <LockIcon sx={{ fontSize: 14, color: 'grey.400' }} />
                </Box>

                {/* Service Icon */}
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    bgcolor: alpha(serviceColor, 0.1),
                    color: 'grey.500',
                    mb: 1,
                    mx: 'auto',
                  }}
                >
                  {getMTProtoServiceIcon(service.service_key)}
                </Box>

                {/* Service Name */}
                <Typography
                  variant="body2"
                  fontWeight={500}
                  textAlign="center"
                  noWrap
                  color="text.secondary"
                  title={service.name}
                  sx={{ mb: 0.5 }}
                >
                  {service.name}
                </Typography>

                {/* Price */}
                <Typography
                  variant="caption"
                  textAlign="center"
                  sx={{
                    display: 'block',
                    color: serviceColor,
                    fontWeight: 600,
                  }}
                >
                  {service.credits_per_month} {t('common:creditsPerMonth', 'credits/mo')}
                </Typography>
              </Box>
            );
          })}
        </Box>
      </CardContent>
    </Card>
  );
};

export default AvailableMTProtoUpgradesCard;
