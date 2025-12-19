/**
 * Session Health Card Component
 * Displays MTProto session health metrics with modern design
 */
import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Paper,
  Avatar,
  alpha,
} from '@mui/material';
import {
  CheckCircle,
  Wifi,
  WifiOff,
  SyncAlt,
  Speed as SpeedIcon,
  Error as ErrorIcon,
  Schedule,
} from '@mui/icons-material';
import type { SessionHealth } from '../types';
import { formatTimeAgo } from '../utils';

interface SessionHealthCardProps {
  sessionHealth: SessionHealth;
}

interface StatItemProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext?: string;
  color?: string;
  badge?: React.ReactNode;
}

const StatItem: React.FC<StatItemProps> = ({ icon, label, value, subtext, color = '#10b981', badge }) => (
  <Box display="flex" alignItems="center" gap={1.5}>
    <Box
      sx={{
        width: 40,
        height: 40,
        borderRadius: 1.5,
        bgcolor: alpha(color, 0.15),
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: color,
      }}
    >
      {icon}
    </Box>
    <Box>
      <Typography variant="caption" color="text.secondary" textTransform="uppercase" letterSpacing={0.5} fontSize="0.65rem">
        {label}
      </Typography>
      <Box display="flex" alignItems="center" gap={0.5}>
        <Typography variant="subtitle1" fontWeight={600} lineHeight={1.2}>
          {value}
        </Typography>
        {badge}
      </Box>
      {subtext && (
        <Typography variant="caption" color="text.secondary" fontSize="0.65rem">
          {subtext}
        </Typography>
      )}
    </Box>
  </Box>
);

const getHealthChip = (score: number, t: any) => {
  if (score >= 90) return <Chip label={t('mtproto:sessionHealth.excellent')} size="small" sx={{ height: 20, fontSize: '0.65rem', bgcolor: 'rgba(16, 185, 129, 0.2)', color: '#10b981' }} />;
  if (score >= 70) return <Chip label={t('mtproto:sessionHealth.good')} size="small" sx={{ height: 20, fontSize: '0.65rem', bgcolor: 'rgba(59, 130, 246, 0.2)', color: '#3b82f6' }} />;
  if (score >= 50) return <Chip label={t('mtproto:sessionHealth.fair')} size="small" sx={{ height: 20, fontSize: '0.65rem', bgcolor: 'rgba(245, 158, 11, 0.2)', color: '#f59e0b' }} />;
  return <Chip label={t('mtproto:sessionHealth.poor')} size="small" sx={{ height: 20, fontSize: '0.65rem', bgcolor: 'rgba(239, 68, 68, 0.2)', color: '#ef4444' }} />;
};

export const SessionHealthCard: React.FC<SessionHealthCardProps> = ({ sessionHealth }) => {
  const { t } = useTranslation(['mtproto', 'common']);
  const sessionReady = sessionHealth.session_valid && sessionHealth.health_score >= 70;
  const healthColor = sessionHealth.health_score >= 90 ? '#10b981' : sessionHealth.health_score >= 70 ? '#3b82f6' : sessionHealth.health_score >= 50 ? '#f59e0b' : '#ef4444';

  return (
    <Card 
      sx={{ 
        mb: 3,
        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(6, 182, 212, 0.08) 100%)',
        border: '1px solid rgba(16, 185, 129, 0.2)',
      }}
    >
      <CardContent>
        {/* Header */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar
              sx={{
                width: 48,
                height: 48,
                bgcolor: alpha(healthColor, 0.2),
                color: healthColor,
              }}
            >
              {sessionReady ? (
                <Wifi sx={{ fontSize: 28 }} />
              ) : sessionHealth.session_valid ? (
                <Wifi sx={{ fontSize: 28 }} />
              ) : (
                <WifiOff sx={{ fontSize: 28 }} />
              )}
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight={600}>
                {t('mtproto:sessionHealth.title')}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {t('mtproto:sessionHealth.description')}
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Stats Grid */}
        <Paper
          sx={{
            p: 2,
            background: 'rgba(0, 0, 0, 0.2)',
            borderRadius: 2,
          }}
        >
          <Grid container spacing={2}>
            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<SpeedIcon sx={{ fontSize: 20 }} />}
                label={t('mtproto:sessionHealth.overallHealth')}
                value={`${sessionHealth.health_score.toFixed(0)}%`}
                color={healthColor}
                badge={getHealthChip(sessionHealth.health_score, t)}
              />
              <LinearProgress
                variant="determinate"
                value={sessionHealth.health_score}
                sx={{ 
                  mt: 1, 
                  height: 4, 
                  borderRadius: 1,
                  bgcolor: alpha(healthColor, 0.2),
                  '& .MuiLinearProgress-bar': {
                    bgcolor: healthColor,
                  }
                }}
              />
            </Grid>

            <Grid item xs={6} sm={3}>
              <StatItem
                icon={sessionHealth.session_connected ? <SyncAlt sx={{ fontSize: 20 }} /> : <CheckCircle sx={{ fontSize: 20 }} />}
                label={t('mtproto:sessionHealth.connectionStatus')}
                value={sessionHealth.session_connected ? t('mtproto:sessionHealth.collecting') : t('common:ready')}
                subtext={`${t('mtproto:sessionHealth.lastUsed')}: ${formatTimeAgo(sessionHealth.session_last_used)}`}
                color={sessionHealth.session_connected ? '#3b82f6' : '#10b981'}
              />
            </Grid>

            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<Schedule sx={{ fontSize: 20 }} />}
                label={t('mtproto:sessionHealth.apiCallsToday')}
                value={sessionHealth.api_calls_today || 0}
                subtext={`${t('mtproto:sessionHealth.rateLimits')}: ${sessionHealth.rate_limit_hits_today || 0}`}
                color="#8b5cf6"
              />
            </Grid>

            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<ErrorIcon sx={{ fontSize: 20 }} />}
                label={t('mtproto:sessionHealth.connectionErrors')}
                value={sessionHealth.connection_errors_today || 0}
                subtext={t('common:today')}
                color={sessionHealth.connection_errors_today > 0 ? '#ef4444' : '#10b981'}
              />
            </Grid>
          </Grid>
        </Paper>
      </CardContent>
    </Card>
  );
};

export default SessionHealthCard;
