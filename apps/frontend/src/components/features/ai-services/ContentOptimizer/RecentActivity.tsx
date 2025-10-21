/**
 * Recent Activity Component
 * Displays recent content optimizations
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  Alert,
  LinearProgress
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useDemoMode, loadMockData } from '@/__mocks__/utils/demoGuard';

interface RecentActivityProps {
  isOptimizing: boolean;
}

interface Optimization {
  id: number;
  content: string;
  improvement: string;
  timestamp: string;
  status?: 'completed' | 'pending' | 'failed';
}

export const RecentActivity: React.FC<RecentActivityProps> = ({ isOptimizing }) => {
  const isDemo = useDemoMode();
  const [optimizations, setOptimizations] = useState<Optimization[]>([]);

  // Load optimizations on mount and when demo mode changes
  useEffect(() => {
    const loadOptimizations = async () => {
      if (isDemo) {
        // Load mock data dynamically in demo mode
        const mock = await loadMockData(() => import('@/__mocks__/data/recentOptimizations'));
        if (mock?.mockOptimizations) {
          setOptimizations(mock.mockOptimizations.slice(0, 3)); // Show top 3
        }
      } else {
        // Real API implementation
        // const response = await fetch('/api/optimizations/recent');
        // const data = await response.json();
        // setOptimizations(data);
        setOptimizations([]); // Empty until real API implemented
      }
    };

    loadOptimizations();
  }, [isDemo]);

  return (
    <CardContent sx={{ p: 4 }}>
      {isOptimizing && (
        <Alert
          severity="info"
          sx={{
            mb: 4,
            borderRadius: 2,
            '& .MuiAlert-message': {
              width: '100%'
            }
          }}
        >
          <Box>
            <Typography variant="body1" sx={{ mb: 2, fontWeight: 500 }}>
              🤖 AI is optimizing your content...
            </Typography>
            <LinearProgress
              sx={{
                borderRadius: 2,
                height: 6
              }}
            />
          </Box>
        </Alert>
      )}

      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" fontWeight={700}>
          Recent Optimizations
        </Typography>
        <Chip
          label={`${optimizations.length} completed`}
          size="small"
          color="primary"
          sx={{ ml: 2, fontWeight: 600 }}
        />
      </Box>

      <Grid container spacing={3}>
        {optimizations.map((item, index) => (
          <Grid item xs={12} key={item.id}>
            <Card
              elevation={0}
              sx={{
                p: 3,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 3,
                position: 'relative',
                background: index % 2 === 0
                  ? 'linear-gradient(135deg, #f8f9ff 0%, #f0f4f8 100%)'
                  : 'linear-gradient(135deg, #fff8f0 0%, #f8f4f0 100%)',
                '&:hover': {
                  boxShadow: '0 8px 30px rgba(0,0,0,0.12)',
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.3s ease'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: 2,
                    backgroundColor: 'success.main',
                    color: 'white',
                    mr: 2
                  }}
                >
                  <CheckCircleIcon />
                </Box>
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" fontWeight={600} sx={{ mb: 0.5 }}>
                    {item.content}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {item.timestamp}
                  </Typography>
                </Box>
                <Chip
                  label={item.improvement}
                  color="success"
                  sx={{
                    fontWeight: 700,
                    fontSize: '0.9rem',
                    height: 32
                  }}
                />
              </Box>
              <Typography variant="body2" color="text.secondary">
                Content successfully optimized with AI enhancements for better engagement
              </Typography>
            </Card>
          </Grid>
        ))}
      </Grid>
    </CardContent>
  );
};

export default RecentActivity;
