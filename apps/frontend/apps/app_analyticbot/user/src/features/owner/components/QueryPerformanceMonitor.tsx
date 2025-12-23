import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Chip,
  TextField,
  Grid,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';
import SpeedIcon from '@mui/icons-material/Speed';
import WarningIcon from '@mui/icons-material/Warning';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { ownerApi } from '../services/ownerApi';

interface QueryPerformance {
  query: string;
  calls: number;
  total_time_ms: number;
  mean_time_ms: number;
  min_time_ms: number;
  max_time_ms: number;
  stddev_time_ms: number;
  percent_total: number;
}

interface SlowQuery {
  query: string;
  calls: number;
  mean_time_ms: number;
  max_time_ms: number;
  total_time_ms: number;
}

interface QueryStatsSummary {
  total_queries_tracked: number;
  slow_queries_count: number;
  total_exec_time_ms: number;
  avg_query_time_ms: number;
  total_calls: number;
  top_called_queries: Array<{ query: string; calls: number }>;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export const QueryPerformanceMonitor: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<QueryStatsSummary | null>(null);
  const [queries, setQueries] = useState<QueryPerformance[]>([]);
  const [slowQueries, setSlowQueries] = useState<SlowQuery[]>([]);
  const [tabValue, setTabValue] = useState(0);
  const [queryLimit, setQueryLimit] = useState(20);
  const [slowQueryThreshold, setSlowQueryThreshold] = useState(100);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [summaryData, queriesData, slowQueriesData] = await Promise.all([
        ownerApi.getQueryStatsSummary(),
        ownerApi.getQueryPerformance(queryLimit),
        ownerApi.getSlowQueries(slowQueryThreshold, 20),
      ]);

      setSummary(summaryData);
      setQueries(queriesData.queries);
      setSlowQueries(slowQueriesData.queries);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch query performance data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [queryLimit, slowQueryThreshold]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [autoRefresh, queryLimit, slowQueryThreshold]);

  const handleResetStats = async () => {
    if (!window.confirm('Are you sure you want to reset all query statistics? This action cannot be undone.')) {
      return;
    }

    setLoading(true);
    try {
      await ownerApi.resetQueryStats();
      alert('Query statistics have been reset successfully');
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset statistics');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (ms: number): string => {
    if (ms < 1) return `${(ms * 1000).toFixed(0)}μs`;
    if (ms < 1000) return `${ms.toFixed(2)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const getTimeColor = (ms: number): string => {
    if (ms < 10) return 'success';
    if (ms < 50) return 'info';
    if (ms < 100) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SpeedIcon /> Query Performance Monitor
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant={autoRefresh ? 'contained' : 'outlined'}
            size="small"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
          </Button>
          <Tooltip title="Refresh data">
            <IconButton onClick={fetchData} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Reset all statistics (WARNING: Cannot be undone)">
            <IconButton onClick={handleResetStats} color="error" disabled={loading}>
              <DeleteSweepIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      {summary && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Queries Tracked
                </Typography>
                <Typography variant="h4">{summary.total_queries_tracked}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Slow Queries (&gt;100ms)
                </Typography>
                <Typography variant="h4" color={summary.slow_queries_count > 0 ? 'error' : 'success'}>
                  {summary.slow_queries_count}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Avg Query Time
                </Typography>
                <Typography variant="h4">{formatTime(summary.avg_query_time_ms)}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Calls
                </Typography>
                <Typography variant="h4">{summary.total_calls.toLocaleString()}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Card>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label="Top Queries by Time" />
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                Slow Queries
                {slowQueries.length > 0 && (
                  <Chip
                    size="small"
                    label={slowQueries.length}
                    color="error"
                    icon={<WarningIcon />}
                  />
                )}
              </Box>
            }
          />
          <Tab label="Most Called Queries" />
        </Tabs>

        <CardContent>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              {/* Tab 0: Top Queries by Total Time */}
              <TabPanel value={tabValue} index={0}>
                <Box sx={{ mb: 2 }}>
                  <TextField
                    label="Number of queries to show"
                    type="number"
                    size="small"
                    value={queryLimit}
                    onChange={(e) => setQueryLimit(Number(e.target.value))}
                    InputProps={{ inputProps: { min: 1, max: 100 } }}
                  />
                </Box>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Query</TableCell>
                        <TableCell align="right">Calls</TableCell>
                        <TableCell align="right">Mean Time</TableCell>
                        <TableCell align="right">Max Time</TableCell>
                        <TableCell align="right">Total Time</TableCell>
                        <TableCell align="right">% of Total</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {queries.map((q, idx) => (
                        <TableRow key={idx} hover>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                              {q.query}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">{q.calls.toLocaleString()}</TableCell>
                          <TableCell align="right">
                            <Chip
                              size="small"
                              label={formatTime(q.mean_time_ms)}
                              color={getTimeColor(q.mean_time_ms) as any}
                            />
                          </TableCell>
                          <TableCell align="right">{formatTime(q.max_time_ms)}</TableCell>
                          <TableCell align="right">{formatTime(q.total_time_ms)}</TableCell>
                          <TableCell align="right">{q.percent_total}%</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </TabPanel>

              {/* Tab 1: Slow Queries */}
              <TabPanel value={tabValue} index={1}>
                <Box sx={{ mb: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
                  <TextField
                    label="Threshold (ms)"
                    type="number"
                    size="small"
                    value={slowQueryThreshold}
                    onChange={(e) => setSlowQueryThreshold(Number(e.target.value))}
                    InputProps={{ inputProps: { min: 0 } }}
                  />
                  <Alert severity={slowQueries.length > 0 ? 'warning' : 'success'} sx={{ flex: 1 }}>
                    {slowQueries.length > 0
                      ? `Found ${slowQueries.length} queries exceeding ${slowQueryThreshold}ms`
                      : `No queries exceeding ${slowQueryThreshold}ms - Great performance!`}
                  </Alert>
                </Box>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Query</TableCell>
                        <TableCell align="right">Calls</TableCell>
                        <TableCell align="right">Mean Time</TableCell>
                        <TableCell align="right">Max Time</TableCell>
                        <TableCell align="right">Total Time</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {slowQueries.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={5} align="center">
                            <Typography variant="body2" color="textSecondary">
                              No slow queries found
                            </Typography>
                          </TableCell>
                        </TableRow>
                      ) : (
                        slowQueries.map((q, idx) => (
                          <TableRow key={idx} hover>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                                {q.query}
                              </Typography>
                            </TableCell>
                            <TableCell align="right">{q.calls.toLocaleString()}</TableCell>
                            <TableCell align="right">
                              <Chip
                                size="small"
                                label={formatTime(q.mean_time_ms)}
                                color="error"
                                icon={<WarningIcon />}
                              />
                            </TableCell>
                            <TableCell align="right">{formatTime(q.max_time_ms)}</TableCell>
                            <TableCell align="right">{formatTime(q.total_time_ms)}</TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </TabPanel>

              {/* Tab 2: Most Called Queries */}
              <TabPanel value={tabValue} index={2}>
                {summary && (
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Query</TableCell>
                          <TableCell align="right">Calls</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {summary.top_called_queries.map((q, idx) => (
                          <TableRow key={idx} hover>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                                {q.query}
                              </Typography>
                            </TableCell>
                            <TableCell align="right">
                              <Chip
                                size="small"
                                label={q.calls.toLocaleString()}
                                color="primary"
                                icon={<TrendingUpIcon />}
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </TabPanel>
            </>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};
