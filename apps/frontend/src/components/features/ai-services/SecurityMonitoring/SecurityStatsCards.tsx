/**
 * Security Stats Cards Component
 * Displays key security metrics in card layout
 */

import React from 'react';
import { Grid, Card, Typography, Badge, Box } from '@mui/material';
import ShieldIcon from '@mui/icons-material/Shield';

interface SecurityStatsCardsProps {
  threatsBlocked: number;
  securityScore: number;
  activeMonitors: number;
  realTimeMonitoring: boolean;
}

export const SecurityStatsCards: React.FC<SecurityStatsCardsProps> = ({
  threatsBlocked,
  securityScore,
  activeMonitors,
  realTimeMonitoring
}) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ textAlign: 'center', p: 2 }}>
          <Typography variant="h4" color="success.main" fontWeight={600}>
            {threatsBlocked}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Threats Blocked
          </Typography>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ textAlign: 'center', p: 2 }}>
          <Typography variant="h4" color="primary.main" fontWeight={600}>
            {securityScore}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Security Score
          </Typography>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ textAlign: 'center', p: 2 }}>
          <Typography variant="h4" color="info.main" fontWeight={600}>
            {activeMonitors}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Active Monitors
          </Typography>
        </Card>
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <Card
          sx={{
            textAlign: 'center',
            p: 2,
            bgcolor: realTimeMonitoring ? 'success.light' : 'grey.100'
          }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Badge
              variant="dot"
              color={realTimeMonitoring ? 'success' : 'default'}
              sx={{
                '& .MuiBadge-badge': {
                  right: '50%',
                  top: 8,
                  animation: realTimeMonitoring ? 'pulse 2s infinite' : 'none'
                },
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.5 },
                  '100%': { opacity: 1 }
                }
              }}
            >
              <ShieldIcon
                sx={{
                  fontSize: 40,
                  color: realTimeMonitoring ? 'success.main' : 'grey.500',
                  mb: 1
                }}
              />
            </Badge>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {realTimeMonitoring ? 'Monitoring Active' : 'Monitoring Paused'}
            </Typography>
          </Box>
        </Card>
      </Grid>
    </Grid>
  );
};

export default SecurityStatsCards;
