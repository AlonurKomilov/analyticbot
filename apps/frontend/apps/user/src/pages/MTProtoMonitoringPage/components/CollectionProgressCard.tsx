/**
 * Collection Progress Card Component
 * Displays data collection progress across channels
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
  Divider,
} from '@mui/material';
import { Storage, SignalCellular4Bar } from '@mui/icons-material';
import type { CollectionProgress } from '../types';
import { formatTimeAgo } from '../utils';

interface CollectionProgressCardProps {
  collectionProgress: CollectionProgress;
}

export const CollectionProgressCard: React.FC<CollectionProgressCardProps> = ({
  collectionProgress,
}) => {
  const { t } = useTranslation(['mtproto', 'common']);
  
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Storage color="primary" />
          <Typography variant="h6">{t('mtproto:monitoring.progress')}</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {t('mtproto:monitoring.progressDescription')}
        </Typography>
        <Divider sx={{ my: 2 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:monitoring.completion')}</Typography>
              <Typography variant="h3" color="primary" mt={1}>
                {collectionProgress.estimated_completion_percent.toFixed(0)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={collectionProgress.estimated_completion_percent}
                sx={{ mt: 1, height: 8, borderRadius: 1 }}
              />
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:monitoring.activeChannels')}</Typography>
              <Typography variant="h4" mt={1}>
                {collectionProgress.active_channels} / {collectionProgress.total_channels}
              </Typography>
              {collectionProgress.collection_active ? (
                <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
                  <SignalCellular4Bar color="success" fontSize="small" />
                  <Typography variant="caption" color="success.main">{t('mtproto:monitoring.collectingNow')}</Typography>
                </Box>
              ) : (
                <Typography variant="caption" color="text.secondary">{t('mtproto:monitoring.idle')}</Typography>
              )}
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:monitoring.totalPosts')}</Typography>
              <Typography variant="h4" mt={1}>
                {collectionProgress.total_posts_collected.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">{t('mtproto:monitoring.collected')}</Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">{t('mtproto:monitoring.lastCollection')}</Typography>
              <Typography variant="body1" fontWeight="medium" mt={1}>
                {formatTimeAgo(collectionProgress.last_collection_time)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {t('mtproto:monitoring.next')}: {formatTimeAgo(collectionProgress.next_collection_eta)}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default CollectionProgressCard;
