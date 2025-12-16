/**
 * Session Health Card Component
 * Displays MTProto session health metrics
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
  Divider,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Wifi,
  WifiOff,
  SyncAlt,
} from '@mui/icons-material';
import type { SessionHealth } from '../types';
import { formatTimeAgo, getHealthColor } from '../utils';

interface SessionHealthCardProps {
  sessionHealth: SessionHealth;
}

const getHealthChip = (score: number, t: any) => {
  if (score >= 90) return <Chip label={t('mtproto:sessionHealth.excellent')} color="success" size="small" />;
  if (score >= 70) return <Chip label={t('mtproto:sessionHealth.good')} color="success" size="small" />;
  if (score >= 50) return <Chip label={t('mtproto:sessionHealth.fair')} color="warning" size="small" />;
  return <Chip label={t('mtproto:sessionHealth.poor')} color="error" size="small" />;
};

export const SessionHealthCard: React.FC<SessionHealthCardProps> = ({ sessionHealth }) => {
  const { t } = useTranslation(['mtproto', 'common']);
  // Session is valid and ready to work
  const sessionReady = sessionHealth.session_valid && sessionHealth.health_score >= 70;

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          {sessionReady ? (
            <Wifi color="success" />
          ) : sessionHealth.session_valid ? (
            <Wifi color="warning" />
          ) : (
            <WifiOff color="error" />
          )}
          <Typography variant="h6">{t('mtproto:sessionHealth.title')}</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {t('mtproto:sessionHealth.description')}
        </Typography>
        <Divider sx={{ my: 2 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:sessionHealth.overallHealth')}</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                <Typography variant="h3" color={getHealthColor(sessionHealth.health_score)}>
                  {sessionHealth.health_score.toFixed(0)}%
                </Typography>
                {getHealthChip(sessionHealth.health_score, t)}
              </Box>
              <LinearProgress
                variant="determinate"
                value={sessionHealth.health_score}
                color={getHealthColor(sessionHealth.health_score)}
                sx={{ mt: 1, height: 8, borderRadius: 1 }}
              />
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:sessionHealth.connectionStatus')}</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                {sessionHealth.session_connected ? (
                  <>
                    <SyncAlt color="primary" />
                    <Tooltip title={t('mtproto:sessionHealth.collectingTooltip')}>
                      <Typography variant="h6">{t('mtproto:sessionHealth.collecting')}</Typography>
                    </Tooltip>
                  </>
                ) : sessionReady ? (
                  <>
                    <CheckCircle color="success" />
                    <Tooltip title={t('mtproto:sessionHealth.readyTooltip')}>
                      <Typography variant="h6">{t('common:ready')}</Typography>
                    </Tooltip>
                  </>
                ) : sessionHealth.session_valid ? (
                  <>
                    <CheckCircle color="warning" />
                    <Typography variant="h6">{t('mtproto:sessionHealth.sessionValid')}</Typography>
                  </>
                ) : (
                  <>
                    <Cancel color="error" />
                    <Typography variant="h6">{t('mtproto:status.notConfigured')}</Typography>
                  </>
                )}
              </Box>
              <Typography variant="caption" color="text.secondary">
                {t('mtproto:sessionHealth.lastUsed')}: {formatTimeAgo(sessionHealth.session_last_used)}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:sessionHealth.apiCallsToday')}</Typography>
              <Typography variant="h4" mt={1}>{sessionHealth.api_calls_today}</Typography>
              <Typography variant="caption" color="text.secondary">
                {t('mtproto:sessionHealth.rateLimits')}: {sessionHealth.rate_limit_hits_today}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:sessionHealth.connectionErrors')}</Typography>
              <Typography variant="h4" color={sessionHealth.connection_errors_today > 0 ? "error" : "text.primary"} mt={1}>
                {sessionHealth.connection_errors_today}
              </Typography>
              <Typography variant="caption" color="text.secondary">{t('common:today')}</Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SessionHealthCard;
