import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  useTheme
} from '@mui/material';

interface Metrics {
  engagementRate?: number;
}

interface PerformanceScoreWidgetProps {
  metrics: Metrics;
}

/**
 * PerformanceScoreWidget - Displays circular performance score gauge
 * 
 * Shows performance score based on engagement rate with visual circular indicator
 */
const PerformanceScoreWidget: React.FC<PerformanceScoreWidgetProps> = React.memo(({ metrics }) => {
  const theme = useTheme();

  const performanceScore = Math.round((metrics?.engagementRate || 0) * 10);

  return (
    <Grid item xs={12} lg={4}>
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🎯 Performance Score
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', pt: 2 }}>
            <Box
              sx={{
                width: 120,
                height: 120,
                borderRadius: '50%',
                background: `conic-gradient(${theme.palette.success.main} ${(metrics?.engagementRate || 0) * 3.6}deg, ${theme.palette.grey[300]} 0deg)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                position: 'relative',
                mb: 2
              }}
            >
              <Box
                sx={{
                  width: 90,
                  height: 90,
                  borderRadius: '50%',
                  backgroundColor: theme.palette.background.paper,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexDirection: 'column'
                }}
              >
                <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                  {performanceScore}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Score
                </Typography>
              </Box>
            </Box>
            <Typography variant="body2" color="text.secondary" align="center">
              Based on engagement rate, growth, and reach metrics
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Grid>
  );
});

PerformanceScoreWidget.displayName = 'PerformanceScoreWidget';

export default PerformanceScoreWidget;
