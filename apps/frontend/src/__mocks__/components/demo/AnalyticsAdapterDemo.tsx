// @ts-nocheck - Demo file with outdated API - not used in production
import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  Grid,
  Chip,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Psychology as MockIcon,
  CloudSync as RealIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

// Import our new services and hooks
import { useDataSource, useAnalytics } from '@hooks/useDataSource';
import { DataSourceManager } from '@utils/dataSourceManager';

interface TestResults {
  mock: {
    success: boolean;
    responseTime: number;
    adapter: string;
  };
  real: {
    success: boolean;
    responseTime: number;
    adapter: string;
    error: string | null;
  };
}

interface TestResultsError {
  error: string;
}

const AnalyticsAdapterDemo: React.FC = () => {
  const [testing, setTesting] = useState<boolean>(false);
  const [testResults, setTestResults] = useState<TestResults | TestResultsError | null>(null);
  const { currentDataSource, isUsingMock, switchDataSource } = useDataSource();

  // Test both adapters with a demo channel
  const demoChannelId = 'demo_test_channel';
  const {
    channelOverview: mockOverview,
    loading: mockLoading,
    error: mockError
  } = useAnalytics(demoChannelId, 7, 'mock');

  const {
    channelOverview: realOverview,
    loading: realLoading,
    error: realError
  } = useAnalytics(demoChannelId, 7, 'real');

  const handleSwitchToMock = async (): Promise<void> => {
    try {
      await switchDataSource('mock');
    } catch (error) {
      console.error('Failed to switch to mock:', error);
    }
  };

  const handleSwitchToReal = async (): Promise<void> => {
    try {
      await switchDataSource('real');
    } catch (error) {
      console.error('Failed to switch to real:', error);
    }
  };

  const runAdapterTests = async (): Promise<void> => {
    setTesting(true);
    setTestResults(null);

    try {
      // Test mock adapter performance
      const mockStart = performance.now();
      const mockManager = new DataSourceManager();
      await mockManager.switchToSource('mock');
      const mockEnd = performance.now();

      // Test real adapter (may fail if not configured)
      let realTime = 0;
      let realSuccess = true;
      let realErrorMsg: string | null = null;

      try {
        const realStart = performance.now();
        await mockManager.switchToSource('real');
        const realEnd = performance.now();
        realTime = realEnd - realStart;
      } catch (error) {
        realSuccess = false;
        realErrorMsg = error instanceof Error ? error.message : 'Unknown error';
      }

      setTestResults({
        mock: {
          success: true,
          responseTime: mockEnd - mockStart,
          adapter: 'MockAnalyticsAdapter'
        },
        real: {
          success: realSuccess,
          responseTime: realTime,
          adapter: 'TelegramAnalyticsAdapter',
          error: realErrorMsg
        }
      });
    } catch (error) {
      setTestResults({
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setTesting(false);
    }
  };

  const isTestResultsError = (results: TestResults | TestResultsError | null): results is TestResultsError => {
    return results !== null && 'error' in results && !('mock' in results);
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Analytics Adapter System Demo
      </Typography>

      <Typography variant="body1" color="text.secondary" paragraph>
        This demo showcases the new analytics adapter pattern that provides clean separation
        between mock and real data sources for development and production environments.
      </Typography>

      {/* Current Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current Configuration
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item>
              <Chip
                icon={isUsingMock ? <MockIcon /> : <RealIcon />}
                label={isUsingMock ? 'Mock Data Source' : 'Real Data Source'}
                color={isUsingMock ? 'warning' : 'success'}
                variant="outlined"
              />
            </Grid>
            <Grid item>
              <Typography variant="body2" color="text.secondary">
                Data Source: {currentDataSource}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Switch Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Data Source Switching
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Button
              variant={isUsingMock ? "contained" : "outlined"}
              startIcon={<MockIcon />}
              onClick={handleSwitchToMock}
              disabled={isUsingMock}
            >
              Use Mock Data
            </Button>
            <Button
              variant={!isUsingMock ? "contained" : "outlined"}
              startIcon={<RealIcon />}
              onClick={handleSwitchToReal}
              disabled={!isUsingMock}
            >
              Use Real Data
            </Button>
          </Box>
          <Typography variant="caption" color="text.secondary">
            Switch between mock and real data sources in real-time
          </Typography>
        </CardContent>
      </Card>

      {/* Adapter Testing */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Adapter Performance Testing
          </Typography>
          <Button
            variant="contained"
            onClick={runAdapterTests}
            disabled={testing}
            startIcon={testing ? <CircularProgress size={16} /> : <SettingsIcon />}
          >
            {testing ? 'Testing Adapters...' : 'Test Both Adapters'}
          </Button>

          {testResults && (
            <Box sx={{ mt: 2 }}>
              {isTestResultsError(testResults) ? (
                <Alert severity="error">
                  Test Error: {testResults.error}
                </Alert>
              ) : (
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <MockIcon sx={{ mr: 1 }} />
                          <Typography variant="subtitle1">Mock Adapter</Typography>
                          {testResults.mock.success && <SuccessIcon color="success" sx={{ ml: 1 }} />}
                        </Box>
                        <Typography variant="body2">
                          Response Time: {testResults.mock.responseTime.toFixed(2)}ms
                        </Typography>
                        <Typography variant="body2">
                          Adapter: {testResults.mock.adapter}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <RealIcon sx={{ mr: 1 }} />
                          <Typography variant="subtitle1">Real Adapter</Typography>
                          {testResults.real.success ?
                            <SuccessIcon color="success" sx={{ ml: 1 }} /> :
                            <ErrorIcon color="error" sx={{ ml: 1 }} />
                          }
                        </Box>
                        {testResults.real.success ? (
                          <>
                            <Typography variant="body2">
                              Response Time: {testResults.real.responseTime.toFixed(2)}ms
                            </Typography>
                            <Typography variant="body2">
                              Adapter: {testResults.real.adapter}
                            </Typography>
                          </>
                        ) : (
                          <Typography variant="body2" color="error">
                            Error: {testResults.real.error}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              )}
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Data Preview */}
      <Grid container spacing={3}>
        {/* Mock Data Preview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Mock Data Preview
              </Typography>
              {mockLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress />
                </Box>
              ) : mockError ? (
                <Alert severity="error">
                  Mock Error: {mockError.message}
                </Alert>
              ) : mockOverview ? (
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Channel ID: {mockOverview.channel_id}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    Subscribers: {mockOverview.raw_analytics?.overview?.total_subscribers || 'N/A'}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    Views: {mockOverview.raw_analytics?.overview?.total_views || 'N/A'}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    Engagement: {mockOverview.raw_analytics?.overview?.avg_engagement_rate || 'N/A'}%
                  </Typography>
                  <Chip
                    label="Mock Data"
                    size="small"
                    color="warning"
                    variant="outlined"
                    sx={{ mt: 1 }}
                  />
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No mock data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Real Data Preview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Real Data Preview
              </Typography>
              {realLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress />
                </Box>
              ) : realError ? (
                <Alert severity="warning">
                  Real data not available: {realError.message}
                </Alert>
              ) : realOverview ? (
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Channel ID: {realOverview.channel_id}
                  </Typography>
                  <Typography variant="body2" gutterBottom>
                    Data available from Telegram API
                  </Typography>
                  <Chip
                    label="Live Data"
                    size="small"
                    color="success"
                    variant="outlined"
                    sx={{ mt: 1 }}
                  />
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Configure Telegram API for real data
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Architecture Info */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Architecture Benefits
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" gutterBottom>
                Clean Separation
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Mock and real data sources are completely separated with no code mixing
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" gutterBottom>
                Easy Development
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Develop and test with realistic mock data without API dependencies
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" gutterBottom>
                Runtime Switching
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Switch between mock and real data sources without code changes
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle2" gutterBottom>
                Centralized Config
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All data source configuration managed in one place
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AnalyticsAdapterDemo;
