import React, { useEffect, useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Paper,
  Typography,
  Button,
  Stack,
  LinearProgress,
  CircularProgress,
  Collapse,
  Alert
} from '@mui/material';
import {
  Replay as ReplayIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

import { initializeApp, showDataSourceNotification } from '../utils/initializeApp.js';

/**
 * Silent health check wrapper
 *
 * Runs health checks in background without blocking user experience.
 * Only shows UI if critical failures are detected.
 *
 * Modes:
 * - silent (default): Checks run in background, app renders immediately
 * - blocking: Shows splash until checks complete (for admin/debug)
 */
const HealthStartupSplash = ({ children, options = {} }) => {
  const [initializing, setInitializing] = useState(true);
  const [progress, setProgress] = useState(null);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [overrideReady, setOverrideReady] = useState(false);

  // Silent mode: run checks but don't block app render
  const silentMode = options.silent ?? (import.meta.env.VITE_HEALTH_CHECK_SILENT !== 'false');

  const runInit = useCallback(async () => {
    setInitializing(true);
    setProgress(null);
    setReport(null);
    setError(null);

    try {
      const result = await initializeApp({
        fullHealthCheck: options.fullHealthCheck ?? (import.meta.env.VITE_FULL_HEALTH_CHECK === 'true'),
        skipOptional: options.skipOptional ?? (import.meta.env.VITE_SKIP_OPTIONAL_CHECKS !== 'false'),
        onProgress: silentMode ? null : ((p) => setProgress(p)) // No progress updates in silent mode
      });

      setReport(result.healthReport || null);

      // Store health report globally for SystemHealthDashboard
      if (result.healthReport) {
        window.__APP_HEALTH_REPORT__ = result.healthReport;
        window.dispatchEvent(new CustomEvent('healthReportAvailable', {
          detail: result.healthReport
        }));
      }

      // Show data source notification if applicable
      if (result.dataSource === 'mock') {
        showDataSourceNotification('mock', result.error ? 'api_unavailable' : null);
      }

      // If initialization returned an error, mark it
      if (!result.success) {
        setError(result.error || 'Initialization failed');
      }

      // In silent mode, log warnings but don't block
      if (silentMode && result.healthReport && !result.isProductionReady) {
        console.warn('⚠️ Background health check detected issues (not blocking user)');
        console.warn('Open System Health Dashboard for details');
      }
    } catch (e) {
      setError(e?.message || String(e));
      if (silentMode) {
        console.error('Health check error (silent mode):', e);
      }
    } finally {
      setInitializing(false);
    }
  }, [options.fullHealthCheck, options.skipOptional, silentMode]);

  useEffect(() => {
    runInit();
  }, [runInit]);

  const criticalFailed = !!(report && report.criticalFailures && report.criticalFailures.length > 0);
  const productionReady = !!(report && report.isProductionReady && report.isProductionReady());

  // In silent mode: render app immediately, show inline warning if critical failures
  if (silentMode) {
    return (
      <>
        {children}

        {/* Inline warning banner for critical failures (non-blocking) */}
        <Collapse in={!initializing && criticalFailed && !overrideReady}>
          <Box sx={{ position: 'fixed', bottom: 16, right: 16, zIndex: 9999, maxWidth: 400 }}>
            <Alert
              severity="warning"
              action={
                <Button size="small" onClick={() => setOverrideReady(true)}>
                  Dismiss
                </Button>
              }
            >
              <Typography variant="body2" fontWeight="bold">
                System Health Warning
              </Typography>
              <Typography variant="caption">
                Some backend services may be unavailable. Check System Health Dashboard for details.
              </Typography>
            </Alert>
          </Box>
        </Collapse>
      </>
    );
  }

  // Blocking mode: show splash until ready
  if (!initializing && (productionReady || overrideReady) && !error) {
    // Render children (the real app) when ready or user overrides
    return <>{children}</>;
  }

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
      <Paper sx={{ width: '100%', maxWidth: 920, p: 4 }} elevation={3}>
        <Stack spacing={2} alignItems="stretch">
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="h5">Starting application</Typography>
            {initializing ? (
              <CircularProgress size={20} />
            ) : productionReady ? (
              <CheckCircleIcon color="success" />
            ) : (
              <WarningIcon color="warning" />
            )}
          </Stack>

          <Typography variant="body2" color="text.secondary">
            The app is running comprehensive startup checks to ensure the backend API and critical
            services are available. This helps avoid surprising runtime errors in production.
          </Typography>

          {/* Progress bar */}
          <Box>
            <LinearProgress variant={initializing ? 'indeterminate' : 'determinate'} value={progress && progress.total ? (progress.current / progress.total) * 100 : 0} />
            {progress && (
              <Typography variant="caption" color="text.secondary">
                {`Checking ${progress.current}/${progress.total} — ${progress.check?.name || ''}`}
              </Typography>
            )}
          </Box>

          {/* Error or report summary */}
          {!initializing && error && (
            <Box>
              <Typography color="error">Initialization error: {String(error)}</Typography>
            </Box>
          )}

          {!initializing && report && (
            <Box>
              <Typography variant="subtitle1">Startup Check Summary</Typography>
              <Typography variant="body2" color="text.secondary">
                Status: {report.getStatusEmoji()} {report.overallStatus}
                {' — '}
                Duration: {report.getDuration()}ms
              </Typography>

              {report.criticalFailures && report.criticalFailures.length > 0 && (
                <Box mt={1}>
                  <Typography color="error" variant="body2">Critical failures:</Typography>
                  {report.criticalFailures.map((f, idx) => (
                    <Typography key={idx} variant="caption">• {f.name}: {f.error}</Typography>
                  ))}
                </Box>
              )}
            </Box>
          )}

          {/* Actions */}
          <Stack direction="row" spacing={2} justifyContent="flex-end">
            <Button
              variant="outlined"
              startIcon={<ReplayIcon />}
              onClick={() => runInit()}
              disabled={initializing}
            >
              Retry
            </Button>

            <Button
              variant="contained"
              color={criticalFailed ? 'warning' : 'primary'}
              startIcon={criticalFailed ? <WarningIcon /> : <CheckCircleIcon />}
              onClick={() => setOverrideReady(true)}
              disabled={initializing}
            >
              {criticalFailed ? 'Continue Anyway (unsafe)' : 'Continue'}
            </Button>
          </Stack>
        </Stack>
      </Paper>
    </Box>
  );
};

HealthStartupSplash.propTypes = {
  children: PropTypes.node,
  options: PropTypes.object
};

export default HealthStartupSplash;
