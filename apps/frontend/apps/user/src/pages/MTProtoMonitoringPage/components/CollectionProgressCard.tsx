/**
 * Collection Progress Card Component
 * Displays data collection progress across channels with modern design
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
  Paper,
  Avatar,
  alpha,
  Chip,
} from '@mui/material';
import { 
  Storage, 
  SignalCellular4Bar, 
  DataUsage,
  Schedule,
  Folder,
} from '@mui/icons-material';
import type { CollectionProgress } from '../types';
import { formatTimeAgo } from '../utils';

interface CollectionProgressCardProps {
  collectionProgress: CollectionProgress;
}

interface StatItemProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  subtext?: string;
  color?: string;
  badge?: React.ReactNode;
  progress?: number;
}

const StatItem: React.FC<StatItemProps> = ({ icon, label, value, subtext, color = '#3b82f6', badge, progress }) => (
  <Box>
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
    {progress !== undefined && (
      <LinearProgress
        variant="determinate"
        value={progress}
        sx={{ 
          mt: 1, 
          height: 4, 
          borderRadius: 1,
          bgcolor: alpha(color, 0.2),
          '& .MuiLinearProgress-bar': {
            bgcolor: color,
          }
        }}
      />
    )}
  </Box>
);

export const CollectionProgressCard: React.FC<CollectionProgressCardProps> = ({
  collectionProgress,
}) => {
  const { t } = useTranslation(['mtproto', 'common']);
  const progressColor = collectionProgress.estimated_completion_percent >= 80 ? '#10b981' : collectionProgress.estimated_completion_percent >= 50 ? '#3b82f6' : '#f59e0b';
  
  return (
    <Card 
      sx={{ 
        mb: 3,
        background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(6, 182, 212, 0.08) 100%)',
        border: '1px solid rgba(59, 130, 246, 0.2)',
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
                bgcolor: alpha('#3b82f6', 0.2),
                color: '#3b82f6',
              }}
            >
              <Storage sx={{ fontSize: 28 }} />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight={600}>
                {t('mtproto:monitoring.progress')}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {t('mtproto:monitoring.progressDescription')}
              </Typography>
            </Box>
          </Box>
          {collectionProgress.collection_active && (
            <Chip
              icon={<SignalCellular4Bar sx={{ fontSize: 14 }} />}
              label={t('mtproto:monitoring.collectingNow')}
              size="small"
              sx={{
                height: 24,
                bgcolor: 'rgba(16, 185, 129, 0.2)',
                color: '#10b981',
                '& .MuiChip-icon': { color: '#10b981' },
              }}
            />
          )}
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
                icon={<DataUsage sx={{ fontSize: 20 }} />}
                label={t('mtproto:monitoring.completion')}
                value={`${collectionProgress.estimated_completion_percent.toFixed(0)}%`}
                color={progressColor}
                progress={collectionProgress.estimated_completion_percent}
              />
            </Grid>

            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<Folder sx={{ fontSize: 20 }} />}
                label={t('mtproto:monitoring.activeChannels')}
                value={`${collectionProgress.active_channels} / ${collectionProgress.total_channels}`}
                subtext={collectionProgress.collection_active ? t('mtproto:monitoring.collectingNow') : t('mtproto:monitoring.idle')}
                color={collectionProgress.collection_active ? '#10b981' : '#6b7280'}
              />
            </Grid>

            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<Storage sx={{ fontSize: 20 }} />}
                label={t('mtproto:monitoring.totalPosts')}
                value={collectionProgress.total_posts_collected.toLocaleString()}
                subtext={t('mtproto:monitoring.collected')}
                color="#8b5cf6"
              />
            </Grid>

            <Grid item xs={6} sm={3}>
              <StatItem
                icon={<Schedule sx={{ fontSize: 20 }} />}
                label={t('mtproto:monitoring.lastCollection')}
                value={formatTimeAgo(collectionProgress.last_collection_time)}
                subtext={`${t('mtproto:monitoring.next')}: ${formatTimeAgo(collectionProgress.next_collection_eta)}`}
                color="#06b6d4"
              />
            </Grid>
          </Grid>
        </Paper>
      </CardContent>
    </Card>
  );
};

export default CollectionProgressCard;
