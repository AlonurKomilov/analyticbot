/**
 * MetricCard Component
 * Displays a single metric with optional change indicator and performance badge
 */

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tooltip,
  Chip,
  useTheme,
} from '@mui/material';
import { HelpOutline } from '@mui/icons-material';
import { formatNumber, formatChange, PerformanceInfo } from './utils';

export interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  change?: number;
  icon?: React.ReactNode;
  tooltip?: string;
  tooltipDetails?: {
    description: string;
    calculation?: string;
    benchmark?: string;
  };
  performance?: PerformanceInfo;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  change,
  icon,
  tooltip,
  tooltipDetails,
  performance,
}) => {
  const theme = useTheme();
  const changeInfo = change !== undefined ? formatChange(change) : null;

  // Build rich tooltip content
  const renderTooltipContent = () => {
    if (tooltipDetails) {
      return (
        <Box sx={{ p: 0.5, maxWidth: 280 }}>
          <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
            {tooltipDetails.description}
          </Typography>
          {tooltipDetails.calculation && (
            <Typography variant="caption" display="block" sx={{ mt: 0.5, opacity: 0.9 }}>
              📐 <strong>Formula:</strong> {tooltipDetails.calculation}
            </Typography>
          )}
          {tooltipDetails.benchmark && (
            <Typography variant="caption" display="block" sx={{ mt: 0.5, opacity: 0.9 }}>
              📊 <strong>Benchmark:</strong> {tooltipDetails.benchmark}
            </Typography>
          )}
        </Box>
      );
    }
    return tooltip || '';
  };

  return (
    <Card sx={{ height: '100%', position: 'relative' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
              <Typography variant="body2" color="text.secondary">
                {title}
              </Typography>
              {(tooltip || tooltipDetails) && (
                <Tooltip title={renderTooltipContent()} arrow placement="top">
                  <HelpOutline
                    sx={{
                      fontSize: 14,
                      ml: 0.5,
                      opacity: 0.5,
                      cursor: 'help',
                      '&:hover': { opacity: 1 }
                    }}
                  />
                </Tooltip>
              )}
            </Box>

            <Typography variant="h5" fontWeight="bold">
              {typeof value === 'number' ? formatNumber(value) : value}
            </Typography>

            {/* Performance Badge */}
            {performance && (
              <Chip
                size="small"
                label={`${performance.emoji} ${performance.label}`}
                sx={{
                  mt: 0.5,
                  height: 20,
                  fontSize: '0.7rem',
                  bgcolor: `${performance.color}20`,
                  color: performance.color,
                  border: `1px solid ${performance.color}40`,
                  '& .MuiChip-label': { px: 1 },
                }}
              />
            )}

            {subtitle && (
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                {subtitle}
              </Typography>
            )}

            {changeInfo && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                <Typography variant="body2" sx={{ color: changeInfo.color, display: 'flex', alignItems: 'center', gap: 0.25 }}>
                  {changeInfo.icon}
                  {changeInfo.text}
                </Typography>
              </Box>
            )}
          </Box>
          {icon && (
            <Box
              sx={{
                width: 44,
                height: 44,
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
