/**
 * DemographicsCard Component
 * Displays demographic data (languages, countries) with progress bars
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
import { formatPercentage } from './utils';

export interface DemographicItem {
  name: string;
  percentage: number;
}

export interface DemographicsCardProps {
  title: string;
  icon: React.ReactNode;
  data: DemographicItem[];
  emptyMessage?: string;
}

export const DemographicsCard: React.FC<DemographicsCardProps> = ({ 
  title, 
  icon, 
  data, 
  emptyMessage = 'No data available' 
}) => {
  const theme = useTheme();

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Box
          sx={{
            width: 32,
            height: 32,
            borderRadius: 1,
            bgcolor: theme.palette.primary.light + '20',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: theme.palette.primary.main,
          }}
        >
          {icon}
        </Box>
        <Typography variant="subtitle1" fontWeight="bold">
          {title}
        </Typography>
      </Box>
      <Divider sx={{ mb: 2 }} />
      
      {data.length === 0 ? (
        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 2 }}>
          {emptyMessage}
        </Typography>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {data.slice(0, 8).map((item, index) => (
            <Box key={index}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">{item.name}</Typography>
                <Typography variant="body2" fontWeight="medium">
                  {formatPercentage(item.percentage, 1)}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={item.percentage}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  bgcolor: theme.palette.grey[200],
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 3,
                    bgcolor: theme.palette.primary.main,
                    opacity: 1 - (index * 0.08),
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

export default DemographicsCard;
