/**
 * System Health Dashboard
 *
 * Admin page to view comprehensive system health checks
 * Shows production readiness status and detailed component checks
 */

import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Stack,
  FormControlLabel,
  Switch,
  CircularProgress
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  PlayArrow as PlayArrowIcon,
  Dashboard as DashboardIcon
} from '@mui/icons-material';

import { SystemHealthCheck } from '@shared/components/navigation';
import { runProductionReadinessCheck, formatReadinessReport } from '@/utils/systemHealthCheck';

interface ProgressData {
  current?: number;
  total?: number;
  status?: string;
  [key: string]: any;
}

interface HealthReport {
  passed?: boolean;
  critical?: number;
  important?: number;
  optional?: number;
  [key: string]: any;
}

/**
 * System Health Dashboard Page
 */
const SystemHealthDashboard: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [report, setReport] = useState<HealthReport | null>(null);
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [skipOptional, setSkipOptional] = useState<boolean>(true);

  const runHealthCheck = async () => {
    setLoading(true);
    setReport(null);
    setProgress(null);

    try {
      const result = await runProductionReadinessCheck({
        skipOptional,
        timeout: 10000,
        onProgress: (progressData: ProgressData) => {
          setProgress(progressData);
        }
      });

      setReport(result);

      // Also log to console
      console.log(formatReadinessReport(result));
    } catch (error) {
      console.error('Health check failed:', error);
    } finally {
      setLoading(false);
      setProgress(null);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Paper elevation={0} sx={{ p: 3, mb: 3, bgcolor: 'primary.main', color: 'white' }}>
        <Stack direction="row" alignItems="center" spacing={2}>
          <DashboardIcon sx={{ fontSize: 40 }} />
          <Box>
            <Typography variant="h4" gutterBottom>
              System Health Dashboard
            </Typography>
            <Typography variant="body1">
              Comprehensive production readiness checks for all API endpoints and system components
            </Typography>
          </Box>
        </Stack>
      </Paper>

      {/* Controls */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stack direction="row" spacing={2} alignItems="center">
          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <PlayArrowIcon />}
            onClick={runHealthCheck}
            disabled={loading}
            size="large"
          >
            {loading ? 'Running Checks...' : 'Run Health Check'}
          </Button>

          {report && (
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={runHealthCheck}
              disabled={loading}
            >
              Re-run
            </Button>
          )}

          <Box flexGrow={1} />

          <FormControlLabel
            control={
              <Switch
                checked={skipOptional}
                onChange={(e) => setSkipOptional(e.target.checked)}
                disabled={loading}
              />
            }
            label="Skip Optional Checks"
          />
        </Stack>

        <Box mt={2}>
          <Typography variant="body2" color="text.secondary">
            <strong>Critical Checks:</strong> API health, database, authentication, dashboard endpoints
            <br />
            <strong>Important Checks:</strong> Analytics endpoints, performance benchmarks
            <br />
            <strong>Optional Checks:</strong> Environment configuration, browser storage
          </Typography>
        </Box>
      </Paper>

      {/* Results */}
      {loading || report ? (
        <SystemHealthCheck
          report={report as any}
          loading={loading}
          progress={progress as any}
        />
      ) : (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No health check results yet
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Click "Run Health Check" to verify system readiness
          </Typography>
          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={runHealthCheck}
            size="large"
          >
            Start Health Check
          </Button>
        </Paper>
      )}

      {/* Info Box */}
      <Paper sx={{ p: 3, mt: 3, bgcolor: 'info.light', color: 'info.contrastText' }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          💡 About Production Readiness Checks
        </Typography>
        <Typography variant="body2">
          These comprehensive checks validate that all critical API endpoints and system components
          are functioning correctly before deployment to production. The system performs:
        </Typography>
        <ul style={{ marginTop: 8, marginBottom: 0 }}>
          <li>API availability and response time checks</li>
          <li>Database and cache connectivity validation</li>
          <li>Authentication service verification</li>
          <li>Critical endpoint availability (dashboard, analytics, insights)</li>
          <li>Performance benchmarking (response times)</li>
          <li>Environment and security configuration checks</li>
        </ul>
      </Paper>

      {/* Auto-run info */}
      {!report && (
        <Paper sx={{ p: 2, mt: 2, bgcolor: 'grey.100' }}>
          <Typography variant="caption" color="text.secondary">
            <strong>💡 Tip:</strong> Set <code>VITE_FULL_HEALTH_CHECK=true</code> in your <code>.env</code> file
            to automatically run health checks on every app startup (useful for CI/CD pipelines).
          </Typography>
        </Paper>
      )}
    </Container>
  );
};

export default SystemHealthDashboard;
