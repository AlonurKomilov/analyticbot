/**
 * ChannelInfoCard Component
 * Displays channel information header
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  useTheme,
} from '@mui/material';
import { CalendarToday } from '@mui/icons-material';
import type { ChannelOverviewData } from '../types';

export interface ChannelInfoCardProps {
  info: ChannelOverviewData['channel_info'];
}

export const ChannelInfoCard: React.FC<ChannelInfoCardProps> = ({ info }) => {
  const theme = useTheme();

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box
            sx={{
              width: 64,
              height: 64,
              borderRadius: 2,
              bgcolor: theme.palette.primary.main,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: 24,
              fontWeight: 'bold',
            }}
          >
            {info.title?.charAt(0) || 'C'}
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h6" fontWeight="bold">
              {info.title}
            </Typography>
            {info.username && (
              <Typography variant="body2" color="text.secondary">
                @{info.username}
              </Typography>
            )}
            <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
              <Chip
                size="small"
                icon={<CalendarToday fontSize="small" />}
                label={info.age_formatted}
                variant="outlined"
              />
              <Chip
                size="small"
                label={info.is_active ? 'Active' : 'Inactive'}
                color={info.is_active ? 'success' : 'default'}
                variant="outlined"
              />
            </Box>
          </Box>
        </Box>
        {info.description && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            {info.description}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

export default ChannelInfoCard;
