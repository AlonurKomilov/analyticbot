/**
 * Active MTProto Services Card Component
 * Shows user's active MTProto service subscriptions with "power-up" visual feel
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
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
  History as HistoryIcon,
  Schedule as ScheduleIcon,
  Download as DownloadIcon,
  ImportExport as ExportIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export interface ActiveMTProtoService {
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

interface ActiveMTProtoServicesCardProps {
  services: ActiveMTProtoService[];
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
      return <BoltIcon />;
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

export const ActiveMTProtoServicesCard: React.FC<ActiveMTProtoServicesCardProps> = ({
  services,
  isLoading,
}) => {
  const { t } = useTranslation(['mtproto', 'common']);
  const navigate = useNavigate();
  
  // Filter only MTProto services
  const mtprotoServices = services.filter(s => s.service_key.startsWith('mtproto_'));

  const handleConfigureService = (serviceKey: string) => {
    navigate(`/workers/mtproto/service/${serviceKey}`);
  };

  if (isLoading) {
    return (
      <Card
        sx={{
          mb: 3,
          background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(76, 175, 80, 0.1) 100%)',
          border: '1px solid rgba(33, 150, 243, 0.3)',
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <BoltIcon sx={{ color: '#2196F3' }} />
            <Typography variant="h6">{t('mtproto:services.activePowerUps', 'Active MTProto Power-Ups')}</Typography>
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

  if (mtprotoServices.length === 0) {
    return (
      <Card
        sx={{
          mb: 3,
          background: 'linear-gradient(135deg, rgba(100, 100, 100, 0.1) 0%, rgba(80, 80, 80, 0.1) 100%)',
          border: '1px dashed rgba(255, 255, 255, 0.2)',
        }}
      >
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <BoltIcon sx={{ color: 'text.secondary' }} />
            <Typography variant="h6" color="text.secondary">
              {t('mtproto:services.noPowerUps', 'No Active MTProto Power-Ups')}
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" mb={2}>
            {t('mtproto:services.noPowerUpsDesc', 'Supercharge your MTProto with premium features! Get history access, auto-collection, media downloads, and bulk export capabilities.')}
          </Typography>
          <Chip
            label={t('mtproto:services.browsePowerUps', 'Browse MTProto Power-Ups')}
            onClick={() => navigate('/marketplace?tab=services&category=mtproto_services')}
            sx={{
              cursor: 'pointer',
              background: 'linear-gradient(135deg, #2196F3 0%, #4CAF50 100%)',
              color: 'white',
              '&:hover': {
                background: 'linear-gradient(135deg, #4CAF50 0%, #2196F3 100%)',
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
        mb: 3,
        background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(76, 175, 80, 0.15) 100%)',
        border: '1px solid rgba(33, 150, 243, 0.4)',
        position: 'relative',
        overflow: 'visible',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: -1,
          left: -1,
          right: -1,
          bottom: -1,
          background: 'linear-gradient(135deg, #2196F3, #4CAF50, #2196F3)',
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
            <BoltIcon sx={{ color: '#2196F3', filter: 'drop-shadow(0 0 4px #2196F3)' }} />
            <Typography variant="h6" fontWeight={600}>
              {t('mtproto:services.activePowerUps', 'Active MTProto Power-Ups')}
            </Typography>
            <Chip
              label={mtprotoServices.length}
              size="small"
              sx={{
                bgcolor: 'rgba(33, 150, 243, 0.3)',
                color: '#90CAF9',
                fontWeight: 600,
              }}
            />
          </Box>
          <Chip
            label={t('mtproto:services.getMore', '+ Get More')}
            size="small"
            onClick={() => navigate('/marketplace?tab=services&category=mtproto_services')}
            sx={{
              cursor: 'pointer',
              bgcolor: 'rgba(76, 175, 80, 0.2)',
              color: '#81C784',
              '&:hover': {
                bgcolor: 'rgba(76, 175, 80, 0.3)',
              },
            }}
          />
        </Box>

        <Box display="flex" gap={2} flexWrap="wrap">
          {mtprotoServices.map((service) => {
            const daysRemaining = getDaysRemaining(service.expires_at);
            const isExpiringSoon = daysRemaining <= 7 && daysRemaining > 0;
            const dailyUsage = getUsagePercentage(service.usage_count_daily, service.usage_quota_daily);
            const serviceColor = service.color || getMTProtoServiceColor(service.service_key);

            return (
              <Box
                key={service.id}
                sx={{
                  width: 160,
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
                    <Tooltip title={t('mtproto:services.expiresIn', { days: daysRemaining })}>
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
                    <Tooltip title={t('common:active', 'Active')}>
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

                {/* Service Icon */}
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    bgcolor: alpha(serviceColor, 0.2),
                    color: serviceColor,
                    mb: 1.5,
                    mx: 'auto',
                  }}
                >
                  {getMTProtoServiceIcon(service.service_key)}
                </Box>

                {/* Service Name */}
                <Typography
                  variant="body2"
                  fontWeight={600}
                  textAlign="center"
                  noWrap
                  title={service.service_name}
                  sx={{ mb: 1 }}
                >
                  {service.service_name}
                </Typography>

                {/* Daily Quota Progress (if applicable) */}
                {service.usage_quota_daily && (
                  <Box sx={{ mt: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={dailyUsage}
                      sx={{
                        height: 4,
                        borderRadius: 2,
                        bgcolor: alpha(serviceColor, 0.2),
                        '& .MuiLinearProgress-bar': {
                          bgcolor: dailyUsage > 80 ? '#f44336' : serviceColor,
                        },
                      }}
                    />
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center', mt: 0.5 }}>
                      {service.usage_count_daily}/{service.usage_quota_daily} {t('common:today', 'today')}
                    </Typography>
                  </Box>
                )}

                {/* Settings Icon */}
                <Box
                  sx={{
                    position: 'absolute',
                    bottom: 8,
                    right: 8,
                  }}
                >
                  <Tooltip title={t('common:configure', 'Configure')}>
                    <IconButton size="small" sx={{ color: alpha(serviceColor, 0.7) }}>
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

export default ActiveMTProtoServicesCard;
