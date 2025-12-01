/**
 * Worker Status Card Component
 * Displays automatic collection worker status
 */
import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Alert,
  AlertTitle,
  Divider,
} from '@mui/material';
import { Schedule, CheckCircle, Cancel } from '@mui/icons-material';
import type { WorkerStatus } from '../types';
import { formatTimeAgo } from '../utils';

interface WorkerStatusCardProps {
  workerStatus: WorkerStatus;
}

export const WorkerStatusCard: React.FC<WorkerStatusCardProps> = ({ workerStatus }) => {
  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <Schedule color="primary" />
          <Typography variant="h6">Automatic Worker Status</Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Background collection service information
        </Typography>
        <Divider sx={{ my: 2 }} />

        {/* Active Collection Progress */}
        {workerStatus.currently_collecting && (
          <Alert severity="info" sx={{ mb: 3 }}>
            <AlertTitle>Collection in Progress</AlertTitle>
            <Box>
              {workerStatus.current_channel && (
                <Typography variant="body2" gutterBottom>
                  Currently collecting: <strong>{workerStatus.current_channel}</strong>
                </Typography>
              )}
              {workerStatus.collection_start_time && (
                <Typography variant="body2" gutterBottom>
                  Running for: <strong>{formatTimeAgo(workerStatus.collection_start_time)}</strong>
                </Typography>
              )}
              {workerStatus.channels_total > 0 ? (
                <>
                  <Typography variant="body2" gutterBottom>
                    Progress: <strong>{workerStatus.channels_processed || 0} / {workerStatus.channels_total}</strong> channels
                    {' '}({((workerStatus.channels_processed || 0) / workerStatus.channels_total * 100).toFixed(0)}%)
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={((workerStatus.channels_processed || 0) / workerStatus.channels_total) * 100}
                    sx={{ my: 1, height: 6, borderRadius: 1 }}
                  />
                </>
              ) : (
                <>
                  <Typography variant="body2" gutterBottom color="text.secondary">
                    Progress: <strong>Initializing...</strong>
                  </Typography>
                  <LinearProgress sx={{ my: 1, height: 6, borderRadius: 1 }} />
                </>
              )}
              <Typography variant="body2">
                Messages collected: <strong>{workerStatus.messages_collected_current_run}</strong>
                {workerStatus.errors_current_run > 0 && (
                  <span style={{ color: '#f44336', marginLeft: 8 }}>
                    Errors: {workerStatus.errors_current_run}
                  </span>
                )}
              </Typography>
            </Box>
          </Alert>
        )}

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Worker Status</Typography>
              <Box display="flex" alignItems="center" gap={1} mt={1}>
                {workerStatus.worker_running ? (
                  <>
                    <CheckCircle color="success" />
                    <Typography variant="h6">Running</Typography>
                  </>
                ) : (
                  <>
                    <Cancel color="error" />
                    <Typography variant="h6">Stopped</Typography>
                  </>
                )}
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Collection Interval</Typography>
              <Typography variant="h4" mt={1}>{workerStatus.worker_interval_minutes}min</Typography>
              <Typography variant="caption" color="text.secondary">Between runs</Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Runs Today</Typography>
              <Typography variant="h4" mt={1}>{workerStatus.runs_today}</Typography>
              <Typography variant="caption" color="error.main">
                Errors: {workerStatus.errors_today}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box>
              <Typography variant="body2" color="text.secondary">Next Run</Typography>
              <Typography variant="body1" fontWeight="medium" mt={1}>
                {formatTimeAgo(workerStatus.next_run)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Last: {formatTimeAgo(workerStatus.last_run)}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default WorkerStatusCard;
