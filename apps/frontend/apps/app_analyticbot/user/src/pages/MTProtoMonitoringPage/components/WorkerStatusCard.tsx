/**
 * Worker Status Card Component
 * Displays automatic collection worker status
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
  Alert,
  AlertTitle,
  Divider,
  Chip,
} from '@mui/material';
import { Schedule, CheckCircle, Cancel } from '@mui/icons-material';
import type { WorkerStatus } from '../types';
import { formatTimeAgo } from '../utils';

interface WorkerStatusCardProps {
  workerStatus: WorkerStatus;
}

export const WorkerStatusCard: React.FC<WorkerStatusCardProps> = ({ workerStatus }) => {
  const { t } = useTranslation(['mtproto', 'common']);
  
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Schedule color="primary" />
          <Typography variant="h6">{t('mtproto:worker.automatic')}</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {t('mtproto:worker.description')}
        </Typography>
        <Divider sx={{ my: 2 }} />

        {/* Active Collection Progress */}
        {workerStatus.currently_collecting && (
          <Alert severity="info" sx={{ mb: 3 }}>
            <AlertTitle>{t('mtproto:worker.collectionInProgress')}</AlertTitle>
            <Box>
              {workerStatus.current_channel && (
                <Typography variant="body2" gutterBottom>
                  {t('mtproto:worker.currentlyCollecting')}: <strong>{workerStatus.current_channel}</strong>
                </Typography>
              )}
              {workerStatus.collection_start_time && (
                <Typography variant="body2" gutterBottom>
                  {t('mtproto:worker.runningFor')}: <strong>{formatTimeAgo(workerStatus.collection_start_time)}</strong>
                </Typography>
              )}
              {workerStatus.channels_total > 0 ? (
                <>
                  <Typography variant="body2" gutterBottom>
                    {t('mtproto:monitoring.progress')}: <strong>{workerStatus.channels_processed || 0} / {workerStatus.channels_total}</strong> {t('common:channels')}
                    {' '}({((workerStatus.channels_processed || 0) / workerStatus.channels_total * 100).toFixed(0)}%)
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={((workerStatus.channels_processed || 0) / workerStatus.channels_total) * 100}
                    sx={{ my: 1, height: 6, borderRadius: 1 }}
                  />
                </>
              ) : (
                <>
                  <Typography variant="body2" gutterBottom color="text.secondary">
                    {t('mtproto:monitoring.progress')}: <strong>{t('mtproto:worker.initializing')}</strong>
                  </Typography>
                  <LinearProgress sx={{ my: 1, height: 6, borderRadius: 1 }} />
                </>
              )}
              <Typography variant="body2">
                {t('mtproto:worker.messagesCollected')}: <strong>{workerStatus.messages_collected_current_run}</strong>
                {workerStatus.errors_current_run > 0 && (
                  <span style={{ color: '#f44336', marginLeft: 8 }}>
                    {t('common:errors')}: {workerStatus.errors_current_run}
                  </span>
                )}
              </Typography>
            </Box>
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:worker.title')}</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                {workerStatus.worker_running ? (
                  <>
                    <CheckCircle color="success" />
                    <Typography variant="h6">{t('mtproto:worker.running')}</Typography>
                  </>
                ) : (
                  <>
                    <Cancel color="error" />
                    <Typography variant="h6">{t('mtproto:worker.stopped')}</Typography>
                  </>
                )}
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:monitoring.interval')}</Typography>
              <Box display="flex" alignItems="baseline" gap={1} mt={1}>
                <Typography variant="h4">{workerStatus.worker_interval_minutes}min</Typography>
                <Chip
                  label={workerStatus.plan_name || 'free'}
                  size="small"
                  color={
                    workerStatus.plan_name === 'enterprise' ? 'secondary' :
                    workerStatus.plan_name === 'business' ? 'primary' :
                    workerStatus.plan_name === 'pro' ? 'info' : 'default'
                  }
                  sx={{ textTransform: 'capitalize' }}
                />
              </Box>
              <Typography variant="caption" color="text.secondary">{t('mtproto:worker.betweenRuns')}</Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:worker.runsToday')}</Typography>
              <Typography variant="h4" mt={1}>{workerStatus.runs_today}</Typography>
              <Typography variant="caption" color="error.main">
                {t('common:errors')}: {workerStatus.errors_today}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:worker.nextRun')}</Typography>
              <Typography variant="body1" fontWeight="medium" mt={1}>
                {formatTimeAgo(workerStatus.next_run)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {t('mtproto:worker.last')}: {formatTimeAgo(workerStatus.last_run)}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default WorkerStatusCard;
