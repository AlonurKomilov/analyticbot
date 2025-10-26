/**
 * Content Optimizer Statistics Component
 * Displays key metrics in gradient cards
 */

import React from 'react';
import { Grid, Card, Typography, Button } from '@mui/material';
import OptimizeIcon from '@mui/icons-material/AutoFixHigh';
import AnalyticsIcon from '@mui/icons-material/Analytics';

interface ContentOptimizerStatsProps {
  totalOptimized: number;
  todayOptimized: number;
  avgImprovement: number;
  onOptimize: () => void;
  isOptimizing: boolean;
}

export const ContentOptimizerStats: React.FC<ContentOptimizerStatsProps> = ({
  totalOptimized,
  todayOptimized,
  avgImprovement,
  onOptimize,
  isOptimizing
}) => {
  return (
    <Grid container spacing={3}>
      {/* Total Optimized Card */}
      <Grid item xs={12} sm={6} md={3}>
        <Card
          elevation={0}
          sx={{
            textAlign: 'center',
            p: 3,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
            borderRadius: 3,
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 12px 40px rgba(102, 126, 234, 0.3)'
            },
            transition: 'all 0.3s ease'
          }}
        >
          <Typography variant="h3" fontWeight={700} sx={{ mb: 1 }}>
            {totalOptimized}
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.9 }}>
            Total Optimized
          </Typography>
          <OptimizeIcon sx={{
            position: 'absolute',
            right: 16,
            top: 16,
            fontSize: 32,
            opacity: 0.2
          }} />
        </Card>
      </Grid>

      {/* Today's Count Card */}
      <Grid item xs={12} sm={6} md={3}>
        <Card
          elevation={0}
          sx={{
            textAlign: 'center',
            p: 3,
            background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
            borderRadius: 3,
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 12px 40px rgba(240, 147, 251, 0.3)'
            },
            transition: 'all 0.3s ease'
          }}
        >
          <Typography variant="h3" fontWeight={700} sx={{ mb: 1 }}>
            {todayOptimized}
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.9 }}>
            Today's Count
          </Typography>
          <AnalyticsIcon sx={{
            position: 'absolute',
            right: 16,
            top: 16,
            fontSize: 32,
            opacity: 0.2
          }} />
        </Card>
      </Grid>

      {/* Average Improvement Card */}
      <Grid item xs={12} sm={6} md={3}>
        <Card
          elevation={0}
          sx={{
            textAlign: 'center',
            p: 3,
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
            borderRadius: 3,
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 12px 40px rgba(79, 172, 254, 0.3)'
            },
            transition: 'all 0.3s ease'
          }}
        >
          <Typography variant="h3" fontWeight={700} sx={{ mb: 1 }}>
            {avgImprovement}
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.9 }}>
            Avg Improvement
          </Typography>
          <AnalyticsIcon sx={{
            position: 'absolute',
            right: 16,
            top: 16,
            fontSize: 32,
            opacity: 0.2
          }} />
        </Card>
      </Grid>

      {/* Optimize Button Card */}
      <Grid item xs={12} sm={6} md={3}>
        <Card
          elevation={0}
          sx={{
            p: 3,
            background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: 3,
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: '0 12px 40px rgba(250, 112, 154, 0.3)'
            },
            transition: 'all 0.3s ease'
          }}
        >
          <Button
            variant="contained"
            size="large"
            startIcon={<OptimizeIcon />}
            onClick={onOptimize}
            disabled={isOptimizing}
            sx={{
              width: '100%',
              minHeight: 56,
              backgroundColor: 'rgba(255,255,255,0.95)',
              color: 'primary.main',
              fontWeight: 600,
              fontSize: '1.1rem',
              borderRadius: 2,
              '&:hover': {
                backgroundColor: 'white',
                transform: 'scale(1.05)',
                boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
              },
              '&:disabled': {
                backgroundColor: 'rgba(255,255,255,0.7)',
                color: 'text.disabled'
              },
              transition: 'all 0.3s ease'
            }}
          >
            {isOptimizing ? 'Optimizing...' : 'Optimize Content'}
          </Button>
        </Card>
      </Grid>
    </Grid>
  );
};

export default ContentOptimizerStats;
