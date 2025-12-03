/**
 * PerformanceSparkline Component
 *
 * Shows a 7-day mini trend chart for posts activity.
 * Simple sparkline visualization without external charting library.
 */

import React from 'react';
import {
  Box,
  Paper,
  Typography,
  useTheme,
  alpha,
} from '@mui/material';
import { ShowChart as ChartIcon } from '@mui/icons-material';

interface PerformanceSparklineProps {
  data: number[];
  labels: string[];
  isLoading?: boolean;
}

const PerformanceSparkline: React.FC<PerformanceSparklineProps> = ({
  data,
  labels,
  isLoading,
}) => {
  const theme = useTheme();

  if (isLoading || !data || data.length === 0) {
    return null;
  }

  const maxValue = Math.max(...data, 1);
  const totalPosts = data.reduce((a, b) => a + b, 0);
  const hasActivity = totalPosts > 0;

  // Calculate bar heights as percentages
  const getBarHeight = (value: number) => {
    if (maxValue === 0) return 10;
    return Math.max((value / maxValue) * 100, 10);
  };

  return (
    <Paper
      sx={{
        p: 2.5,
        background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.04)} 0%, ${alpha(theme.palette.primary.main, 0.01)} 100%)`,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <ChartIcon sx={{ color: theme.palette.primary.main, fontSize: 20 }} />
        <Typography variant="subtitle2" fontWeight="600">
          7-Day Post Activity
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
          {totalPosts} posts this week
        </Typography>
      </Box>

      {hasActivity ? (
        <Box
          sx={{
            display: 'flex',
            alignItems: 'flex-end',
            justifyContent: 'space-between',
            height: 80,
            gap: 1,
          }}
        >
          {data.map((value, index) => (
            <Box
              key={index}
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                flex: 1,
              }}
            >
              <Box
                sx={{
                  width: '100%',
                  maxWidth: 32,
                  height: `${getBarHeight(value)}%`,
                  minHeight: 8,
                  backgroundColor: value > 0 
                    ? theme.palette.primary.main 
                    : alpha(theme.palette.grey[500], 0.3),
                  borderRadius: '4px 4px 0 0',
                  transition: 'height 0.3s ease',
                  position: 'relative',
                  '&:hover': {
                    backgroundColor: value > 0 
                      ? theme.palette.primary.dark 
                      : alpha(theme.palette.grey[500], 0.4),
                  },
                  '&::after': value > 0 ? {
                    content: `"${value}"`,
                    position: 'absolute',
                    top: -18,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    fontSize: 10,
                    fontWeight: 'bold',
                    color: theme.palette.text.primary,
                  } : {},
                }}
              />
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ mt: 0.5, fontSize: 10 }}
              >
                {labels[index]}
              </Typography>
            </Box>
          ))}
        </Box>
      ) : (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: 80,
            color: 'text.secondary',
          }}
        >
          <Typography variant="body2">No posts in the last 7 days</Typography>
          <Typography variant="caption">
            Start posting to see activity trends
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default PerformanceSparkline;
