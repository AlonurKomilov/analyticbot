import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  useTheme,
  Theme
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
} from '@mui/icons-material';
import { formatNumber, getMetricColor } from './dashboardUtils';

interface Metrics {
  totalViews?: number;
  growthRate?: number;
  engagementRate?: number;
  reachScore?: number;
  activeUsers?: number;
}

interface OverviewMetricsProps {
  metrics?: Metrics;
}

const OverviewMetrics: React.FC<OverviewMetricsProps> = React.memo(({ metrics }) => {
  const theme = useTheme<Theme>();

  if (!metrics) {
    return null;
  }

  return (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      {/* Total Views */}
      <Grid item xs={12} sm={6} md={2.4}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="text.secondary" gutterBottom variant="body2">
                  Total Views
                </Typography>
                <Typography variant="h5" component="div">
                  {formatNumber(metrics?.totalViews)}
                </Typography>
              </Box>
              <TrendingUpIcon color="primary" sx={{ fontSize: 40 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Growth Rate */}
      <Grid item xs={12} sm={6} md={2.4}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="text.secondary" gutterBottom variant="body2">
                  Growth Rate
                </Typography>
                <Typography
                  variant="h5"
                  component="div"
                  sx={{ color: getMetricColor(metrics?.growthRate, { good: 10, warning: 5 }, theme) }}
                >
                  {metrics?.growthRate?.toFixed(1)}%
                </Typography>
              </Box>
              {(metrics?.growthRate ?? 0) > 0 ?
                <TrendingUpIcon sx={{ color: getMetricColor(metrics?.growthRate, { good: 10, warning: 5 }, theme), fontSize: 40 }} /> :
                <TrendingDownIcon color="error" sx={{ fontSize: 40 }} />
              }
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Engagement Rate */}
      <Grid item xs={12} sm={6} md={2.4}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="text.secondary" gutterBottom variant="body2">
                  Engagement Rate
                </Typography>
                <Typography variant="h5" component="div">
                  {metrics?.engagementRate?.toFixed(1)}%
                </Typography>
              </Box>
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: '50%',
                  backgroundColor: theme.palette.primary.main,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '0.8rem',
                  fontWeight: 'bold'
                }}
              >
                {metrics?.engagementRate?.toFixed(0)}%
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Reach Score */}
      <Grid item xs={12} sm={6} md={2.4}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="text.secondary" gutterBottom variant="body2">
                  Reach Score
                </Typography>
                <Typography variant="h5" component="div">
                  {metrics?.reachScore}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={metrics?.reachScore || 0}
                sx={{
                  width: 40,
                  height: 8,
                  borderRadius: 4,
                  transform: 'rotate(-90deg)',
                  transformOrigin: 'center'
                }}
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Active Users */}
      <Grid item xs={12} sm={6} md={2.4}>
        <Card sx={{ height: '100%' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography color="text.secondary" gutterBottom variant="body2">
                  Active Users
                </Typography>
                <Typography variant="h5" component="div">
                  {formatNumber(metrics?.activeUsers)}
                </Typography>
              </Box>
              <Box
                sx={{
                  width: 40,
                  height: 40,
                  borderRadius: '8px',
                  backgroundColor: theme.palette.success.light,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: theme.palette.success.contrastText,
                  fontSize: '1.2rem'
                }}
              >
                👥
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
});

OverviewMetrics.displayName = 'OverviewMetrics';

export default OverviewMetrics;
