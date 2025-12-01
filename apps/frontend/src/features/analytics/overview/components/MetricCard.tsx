/**
 * MetricCard Component
 * Displays a single metric with optional change indicator
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tooltip,
  useTheme,
} from '@mui/material';
import { Info } from '@mui/icons-material';
import { formatNumber, formatChange } from './utils';

export interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: number;
  icon?: React.ReactNode;
  tooltip?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  change,
  icon,
  tooltip,
}) => {
  const theme = useTheme();
  const changeInfo = change !== undefined ? formatChange(change) : null;

  return (
    <Card sx={{ height: '100%', position: 'relative' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
              {tooltip && (
                <Tooltip title={tooltip}>
                  <Info sx={{ fontSize: 14, ml: 0.5, verticalAlign: 'middle', opacity: 0.6 }} />
                </Tooltip>
              )}
            </Typography>
            <Typography variant="h5" fontWeight="bold">
              {typeof value === 'number' ? formatNumber(value) : value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
            {changeInfo && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                <Typography variant="body2" sx={{ color: changeInfo.color, display: 'flex', alignItems: 'center' }}>
                  {changeInfo.icon}
                  {changeInfo.text}
                </Typography>
              </Box>
            )}
          </Box>
          {icon && (
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                bgcolor: theme.palette.primary.light + '20',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: theme.palette.primary.main,
              }}
            >
              {icon}
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default MetricCard;
