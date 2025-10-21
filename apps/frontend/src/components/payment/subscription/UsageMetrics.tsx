/**
 * UsageMetrics Component
 *
 * Extracted from SubscriptionDashboard - displays subscription usage statistics,
 * limits, and progress indicators
 */

import React from 'react';

interface SubscriptionLimits {
    users?: number;
    storage?: number;
    api_calls?: number;
    reports?: number;
}

interface Subscription {
    limits?: SubscriptionLimits;
}

interface Usage {
    active_users?: number;
    storage_used?: number;
    api_calls?: number;
    reports_generated?: number;
}

interface UsageMetricsProps {
    subscription: Subscription;
    usage: Usage | null;
}
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  LinearProgress,
  Grid,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  Storage,
  People,
  BarChart
} from '@mui/icons-material';

const UsageMetrics: React.FC<UsageMetricsProps> = ({ subscription, usage }) => {
  if (!usage) return null;

  const metrics = [
    {
      icon: <People sx={{ fontSize: 20 }} />,
      label: 'Active Users',
      current: usage.active_users || 0,
      limit: subscription.limits?.users || 100,
      color: 'primary'
    },
    {
      icon: <Storage sx={{ fontSize: 20 }} />,
      label: 'Storage Used',
      current: usage.storage_used || 0,
      limit: subscription.limits?.storage || 1000,
      unit: 'MB',
      color: 'secondary'
    },
    {
      icon: <BarChart sx={{ fontSize: 20 }} />,
      label: 'API Calls',
      current: usage.api_calls || 0,
      limit: subscription.limits?.api_calls || 10000,
      color: 'success'
    },
    {
      icon: <TrendingUp sx={{ fontSize: 20 }} />,
      label: 'Analytics Reports',
      current: usage.reports_generated || 0,
      limit: subscription.limits?.reports || 50,
      color: 'info'
    }
  ];

  const getUsagePercentage = (current: number, limit: number): number => {
    return limit > 0 ? Math.min((current / limit) * 100, 100) : 0;
  };

  const getProgressColor = (percentage: number): 'error' | 'warning' | 'primary' => {
    if (percentage >= 90) return 'error';
    if (percentage >= 75) return 'warning';
    return 'primary';
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardHeader
        title={
          <Typography variant="h6">Usage & Limits</Typography>
        }
        subheader="Current billing period usage"
      />
      <CardContent>
        <Grid container spacing={3}>
          {metrics.map((metric, index) => {
            const percentage = getUsagePercentage(metric.current, metric.limit);
            const progressColor = getProgressColor(percentage);

            return (
              <Grid item xs={12} sm={6} key={index}>
                <Box>
                  <Box display="flex" alignItems="center" gap={1} mb={1}>
                    {metric.icon}
                    <Typography variant="subtitle2">
                      {metric.label}
                    </Typography>
                  </Box>

                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2" color="text.secondary">
                      {metric.current.toLocaleString()}{metric.unit && ` ${metric.unit}`} / {metric.limit.toLocaleString()}{metric.unit && ` ${metric.unit}`}
                    </Typography>
                    <Typography variant="body2" color={`${progressColor}.main`}>
                      {percentage.toFixed(0)}%
                    </Typography>
                  </Box>

                  <LinearProgress
                    variant="determinate"
                    value={percentage}
                    color={progressColor}
                    sx={{ height: 6, borderRadius: 3 }}
                  />

                  {percentage >= 90 && (
                    <Typography variant="caption" color="error" sx={{ mt: 0.5, display: 'block' }}>
                      Approaching limit - consider upgrading
                    </Typography>
                  )}
                </Box>

                {index < metrics.length - 1 && index % 2 === 1 && (
                  <Divider sx={{ mt: 2 }} />
                )}
              </Grid>
            );
          })}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default UsageMetrics;
