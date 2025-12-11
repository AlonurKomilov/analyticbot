/**
 * Session Health Card Component
 * Displays MTProto session health metrics
 */
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  Divider,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle,
  Cancel,
  Wifi,
  WifiOff,
  SyncAlt,
} from '@mui/icons-material';
import type { SessionHealth } from '../types';
import { formatTimeAgo, getHealthColor } from '../utils';

interface SessionHealthCardProps {
  sessionHealth: SessionHealth;
}

const getHealthChip = (score: number) => {
  if (score >= 90) return <Chip label="Excellent" color="success" size="small" />;
  if (score >= 70) return <Chip label="Good" color="success" size="small" />;
  if (score >= 50) return <Chip label="Fair" color="warning" size="small" />;
  return <Chip label="Poor" color="error" size="small" />;
};

export const SessionHealthCard: React.FC<SessionHealthCardProps> = ({ sessionHealth }) => {
  // Session is valid and ready to work
  const sessionReady = sessionHealth.session_valid && sessionHealth.health_score >= 70;
  
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          {sessionReady ? (
            <Wifi color="success" />
          ) : sessionHealth.session_valid ? (
            <Wifi color="warning" />
          ) : (
            <WifiOff color="error" />
          )}
          <Typography variant="h6">Session Health</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          MTProto connection and performance metrics
        </Typography>
        <Divider sx={{ my: 2 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Overall Health</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                <Typography variant="h3" color={getHealthColor(sessionHealth.health_score)}>
                  {sessionHealth.health_score.toFixed(0)}%
                </Typography>
                {getHealthChip(sessionHealth.health_score)}
              </Box>
              <LinearProgress
                variant="determinate"
                value={sessionHealth.health_score}
                color={getHealthColor(sessionHealth.health_score)}
                sx={{ mt: 1, height: 8, borderRadius: 1 }}
              />
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Connection Status</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                {sessionHealth.session_connected ? (
                  <>
                    <SyncAlt color="primary" />
                    <Tooltip title="Actively collecting data right now">
                      <Typography variant="h6">Collecting</Typography>
                    </Tooltip>
                  </>
                ) : sessionReady ? (
                  <>
                    <CheckCircle color="success" />
                    <Tooltip title="Session is valid and ready. Connects automatically when collection starts.">
                      <Typography variant="h6">Ready</Typography>
                    </Tooltip>
                  </>
                ) : sessionHealth.session_valid ? (
                  <>
                    <CheckCircle color="warning" />
                    <Typography variant="h6">Session Valid</Typography>
                  </>
                ) : (
                  <>
                    <Cancel color="error" />
                    <Typography variant="h6">Not Configured</Typography>
                  </>
                )}
              </Box>
              <Typography variant="caption" color="text.secondary">
                Last used: {formatTimeAgo(sessionHealth.session_last_used)}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">API Calls Today</Typography>
              <Typography variant="h4" mt={1}>{sessionHealth.api_calls_today}</Typography>
              <Typography variant="caption" color="text.secondary">
                Rate limits: {sessionHealth.rate_limit_hits_today}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Connection Errors</Typography>
              <Typography variant="h4" color={sessionHealth.connection_errors_today > 0 ? "error" : "text.primary"} mt={1}>
                {sessionHealth.connection_errors_today}
              </Typography>
              <Typography variant="caption" color="text.secondary">Today</Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default SessionHealthCard;
