/**
 * Recent Activity Component
 * Displays recent content optimizations
 */

import React from 'react';
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

interface RecentActivityProps {
  isOptimizing: boolean;
}

// Mock data - in real app this would come from the service
const mockOptimizations = [
  {
    id: 1,
    content: 'Product Launch Announcement',
    improvement: '+25%',
    timestamp: '2 minutes ago'
  },
  {
    id: 2,
    content: 'Weekly Newsletter Content',
    improvement: '+18%',
    timestamp: '15 minutes ago'
  },
  {
    id: 3,
    content: 'Blog Post Introduction',
    improvement: '+32%',
    timestamp: '1 hour ago'
  }
];

export const RecentActivity: React.FC<RecentActivityProps> = ({ isOptimizing }) => {
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
          label={`${mockOptimizations.length} completed`}
          size="small"
          color="primary"
          sx={{ ml: 2, fontWeight: 600 }}
        />
      </Box>

      <Grid container spacing={3}>
        {mockOptimizations.map((item, index) => (
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
