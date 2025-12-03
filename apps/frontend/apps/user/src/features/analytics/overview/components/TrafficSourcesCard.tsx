/**
 * TrafficSourcesCard Component
 * Displays traffic source breakdown with progress bars
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  LinearProgress,
  useTheme,
} from '@mui/material';
import { Link as LinkIcon } from '@mui/icons-material';
import { formatPercentage } from './utils';
import type { TrafficSource } from '../types';

export interface TrafficSourcesCardProps {
  data: TrafficSource[];
}

const getSourceIcon = (sourceType: string): string => {
  switch (sourceType.toLowerCase()) {
    case 'search':
      return '🔍';
    case 'mentions':
      return '📢';
    case 'links':
      return '🔗';
    case 'other_channels':
      return '📺';
    case 'direct':
      return '💬';
    case 'other':
    default:
      return '📊';
  }
};

export const TrafficSourcesCard: React.FC<TrafficSourcesCardProps> = ({ data }) => {
  const theme = useTheme();

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Box
          sx={{
            width: 32,
            height: 32,
            borderRadius: 1,
            bgcolor: theme.palette.secondary.light + '20',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: theme.palette.secondary.main,
          }}
        >
          <LinkIcon fontSize="small" />
        </Box>
        <Typography variant="subtitle1" fontWeight="bold">
          Traffic Sources
        </Typography>
      </Box>
      <Divider sx={{ mb: 2 }} />

      {data.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
          No traffic source data available
        </Typography>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {data.map((source, index) => (
            <Box key={index}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <span>{getSourceIcon(source.source_type)}</span>
                  <Typography variant="body2">{source.source_name}</Typography>
                </Box>
                <Typography variant="body2" fontWeight="medium">
                  {formatPercentage(source.percentage, 1)}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={source.percentage}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  bgcolor: theme.palette.grey[200],
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 3,
                    bgcolor: theme.palette.secondary.main,
                  },
                }}
              />
            </Box>
          ))}
        </Box>
      )}
    </Paper>
  );
};

export default TrafficSourcesCard;
