/**
 * SimpleChart Component
 * Displays a simple bar chart for historical data
 */

import React from 'react';
import { Box, Typography, Tooltip } from '@mui/material';
import { formatNumber } from './utils';

export interface SimpleChartProps {
  data: Array<{ date: string; value: number }>;
  title: string;
  color?: string;
}

export const SimpleChart: React.FC<SimpleChartProps> = ({ 
  data, 
  title, 
  color = '#1976d2' 
}) => {
  const maxValue = Math.max(...data.map((d) => d.value), 1);
  
  if (data.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body2" color="text.secondary">
          No data available for chart
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 0.5, height: 100, mt: 2 }}>
        {data.slice(-14).map((point, index) => (
          <Tooltip key={index} title={`${point.date}: ${formatNumber(point.value)}`}>
            <Box
              sx={{
                flex: 1,
                minWidth: 8,
                height: `${(point.value / maxValue) * 100}%`,
                bgcolor: color,
                borderRadius: '2px 2px 0 0',
                transition: 'all 0.2s',
                '&:hover': {
                  opacity: 0.8,
                },
              }}
            />
          </Tooltip>
        ))}
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
        <Typography variant="caption" color="text.secondary">
          {data[data.length - 14]?.date || data[0]?.date}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {data[data.length - 1]?.date}
        </Typography>
      </Box>
    </Box>
  );
};

export default SimpleChart;
