/**
 * VACUUM & Table Health Monitor Component
 *
 * Provides comprehensive monitoring and control of PostgreSQL VACUUM operations
 * for the owner dashboard. Displays table health, dead tuple statistics, bloat
 * analysis, and allows manual VACUUM triggering.
 *
 * Features:
 * - Real-time table health monitoring
 * - Dead tuple percentage visualization
 * - Manual VACUUM control (standard and FULL)
 * - Autovacuum configuration display
 * - Tables needing attention alerts
 * - Auto-refresh capability
 *
 * Created: 2025-11-27 (Issue #9)
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControlLabel,
  Grid,
  Paper,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  Tooltip,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  CleaningServices as CleaningServicesIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { ownerApi } from '../services/ownerApi';

interface TableHealth {
  schema: string;
  table_name: string;
  live_tuples: number;
  dead_tuples: number;
  dead_percent: number;
  modifications_since_analyze: number;
  total_size: string;
  total_size_bytes: number;
  last_vacuum: string | null;
  last_autovacuum: string | null;
  last_analyze: string | null;
  last_autoanalyze: string | null;
  vacuum_count: number;
  autovacuum_count: number;
  priority?: string;
}

interface VacuumSummary {
  database_size: string;
  total_tables: number;
  total_live_tuples: number;
  total_dead_tuples: number;
  overall_dead_percent: number;
}

interface AutovacuumConfig {
  global_settings: Record<string, { value: string; unit: string; description: string }>;
  table_specific_settings: Array<{
    schema: string;
    table_name: string;
    vacuum_threshold: string;
    vacuum_scale_factor: string;
    analyze_threshold: string;
    analyze_scale_factor: string;
    vacuum_cost_delay: string;
  }>;
}

export const VacuumMonitor: React.FC = () => {
  const [tables, setTables] = useState<TableHealth[]>([]);
  const [summary, setSummary] = useState<VacuumSummary | null>(null);
  const [tablesNeedingAttention, setTablesNeedingAttention] = useState<TableHealth[]>([]);
  const [config, setConfig] = useState<AutovacuumConfig | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [showConfig, setShowConfig] = useState(false);

  // Vacuum dialog state
  const [vacuumDialog, setVacuumDialog] = useState<{
    open: boolean;
    tableName: string;
    full: boolean;
  }>({ open: false, tableName: '', full: false });
  const [vacuuming, setVacuuming] = useState(false);

  // Filters
  const [deadPercentThreshold, setDeadPercentThreshold] = useState(5);
  const [minDeadTuples, setMinDeadTuples] = useState(100);

  const fetchVacuumStatus = async () => {
    try {
      setLoading(true);
      setError(null);

      const [statusData, attentionData] = await Promise.all([
        ownerApi.getVacuumStatus(),
        ownerApi.getTablesNeedingVacuum(deadPercentThreshold, minDeadTuples),
      ]);

      setTables(statusData.tables);
      setSummary(statusData.summary);
      setTablesNeedingAttention(attentionData.tables);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch vacuum status');
      console.error('Error fetching vacuum status:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAutovacuumConfig = async () => {
    try {
      const configData = await ownerApi.getAutovacuumConfig();
      setConfig(configData);
    } catch (err: any) {
      console.error('Error fetching autovacuum config:', err);
    }
  };

  const handleManualVacuum = async () => {
    try {
      setVacuuming(true);
      await ownerApi.manualVacuumTable(vacuumDialog.tableName, true, vacuumDialog.full);
      setVacuumDialog({ open: false, tableName: '', full: false });

      // Refresh data after vacuum
      setTimeout(() => fetchVacuumStatus(), 2000);
    } catch (err: any) {
      setError(err.message || 'Failed to vacuum table');
      console.error('Error vacuuming table:', err);
    } finally {
      setVacuuming(false);
    }
  };

  const openVacuumDialog = (tableName: string, full: boolean = false) => {
    setVacuumDialog({ open: true, tableName, full });
  };

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return 'Never';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getHealthChip = (deadPercent: number, deadTuples: number) => {
    if (deadPercent >= 10 || deadTuples > 10000) {
      return <Chip label="Critical" color="error" size="small" icon={<ErrorIcon />} />;
    }
    if (deadPercent >= 5 || deadTuples > 1000) {
      return <Chip label="High" color="warning" size="small" icon={<WarningIcon />} />;
    }
    if (deadPercent >= 2 || deadTuples > 500) {
      return <Chip label="Moderate" color="info" size="small" icon={<InfoIcon />} />;
    }
    return <Chip label="Healthy" color="success" size="small" icon={<CheckCircleIcon />} />;
  };

  useEffect(() => {
    fetchVacuumStatus();
    fetchAutovacuumConfig();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchVacuumStatus();
    }, 30000); // 30 seconds

    return () => clearInterval(interval);
  }, [autoRefresh, deadPercentThreshold, minDeadTuples]);

  return (
    <Box>
      {/* Header Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CleaningServicesIcon />
          VACUUM & Table Health Monitor
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                color="primary"
              />
            }
            label="Auto-refresh (30s)"
          />

          <IconButton
            onClick={() => setShowConfig(!showConfig)}
            color={showConfig ? 'primary' : 'default'}
            title="Show autovacuum configuration"
          >
            <SettingsIcon />
          </IconButton>

          <Button
            startIcon={<RefreshIcon />}
            onClick={fetchVacuumStatus}
            disabled={loading}
            variant="outlined"
          >
            Refresh
          </Button>
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
                  Database Size
                </Typography>
                <Typography variant="h5">{summary.database_size}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Total Tables
                </Typography>
                <Typography variant="h5">{summary.total_tables}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Dead Tuples
                </Typography>
                <Typography variant="h5">
                  {summary.total_dead_tuples.toLocaleString()}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {summary.overall_dead_percent.toFixed(2)}% of total
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom variant="body2">
                  Tables Needing Attention
                </Typography>
                <Typography variant="h5" color={tablesNeedingAttention.length > 0 ? 'warning.main' : 'success.main'}>
                  {tablesNeedingAttention.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Autovacuum Configuration */}
      <Collapse in={showConfig}>
        {config && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Autovacuum Configuration
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>Global Settings</Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Setting</TableCell>
                          <TableCell>Value</TableCell>
                          <TableCell>Unit</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {Object.entries(config.global_settings).map(([key, setting]) => (
                          <TableRow key={key}>
                            <TableCell>
                              <Tooltip title={setting.description}>
                                <span style={{ cursor: 'help' }}>{key}</span>
                              </Tooltip>
                            </TableCell>
                            <TableCell>{setting.value}</TableCell>
                            <TableCell>{setting.unit || '-'}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>Table-Specific Overrides</Typography>
                  {config.table_specific_settings.length > 0 ? (
                    <TableContainer component={Paper} variant="outlined">
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Table</TableCell>
                            <TableCell>Vacuum Threshold</TableCell>
                            <TableCell>Scale Factor</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {config.table_specific_settings.map((setting) => (
                            <TableRow key={setting.table_name}>
                              <TableCell><code>{setting.table_name}</code></TableCell>
                              <TableCell>{setting.vacuum_threshold}</TableCell>
                              <TableCell>{setting.vacuum_scale_factor}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  ) : (
                    <Alert severity="info">No table-specific overrides configured</Alert>
                  )}
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        )}
      </Collapse>

      {/* Tables Needing Attention */}
      {tablesNeedingAttention.length > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            ⚠️ {tablesNeedingAttention.length} table(s) need attention
          </Typography>
          <Typography variant="body2">
            The following tables have high dead tuple ratios or have never been vacuumed.
            Consider running manual VACUUM to improve performance.
          </Typography>
        </Alert>
      )}

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2, alignItems: 'center' }}>
        <TextField
          label="Dead % Threshold"
          type="number"
          value={deadPercentThreshold}
          onChange={(e) => setDeadPercentThreshold(Number(e.target.value))}
          size="small"
          sx={{ width: 150 }}
          InputProps={{ inputProps: { min: 0, max: 100 } }}
        />
        <TextField
          label="Min Dead Tuples"
          type="number"
          value={minDeadTuples}
          onChange={(e) => setMinDeadTuples(Number(e.target.value))}
          size="small"
          sx={{ width: 150 }}
          InputProps={{ inputProps: { min: 0 } }}
        />
        <Button
          variant="outlined"
          size="small"
          onClick={fetchVacuumStatus}
        >
          Apply Filters
        </Button>
      </Box>

      {/* Tables List */}
      {loading && tables.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Table Name</TableCell>
                <TableCell align="right">Live Tuples</TableCell>
                <TableCell align="right">Dead Tuples</TableCell>
                <TableCell align="right">Dead %</TableCell>
                <TableCell>Health</TableCell>
                <TableCell>Size</TableCell>
                <TableCell>Last Autovacuum</TableCell>
                <TableCell>Last Vacuum</TableCell>
                <TableCell>Vacuum Count</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {tables.map((table) => (
                <TableRow
                  key={table.table_name}
                  sx={{
                    backgroundColor: table.dead_percent > 10 ? 'rgba(211, 47, 47, 0.05)' :
                                   table.dead_percent > 5 ? 'rgba(237, 108, 2, 0.05)' : 'inherit'
                  }}
                >
                  <TableCell>
                    <code style={{ fontWeight: 'bold' }}>{table.table_name}</code>
                  </TableCell>
                  <TableCell align="right">{table.live_tuples.toLocaleString()}</TableCell>
                  <TableCell align="right">
                    <Typography
                      component="span"
                      sx={{
                        color: table.dead_tuples > 10000 ? 'error.main' :
                               table.dead_tuples > 1000 ? 'warning.main' : 'inherit'
                      }}
                    >
                      {table.dead_tuples.toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography
                      component="span"
                      sx={{
                        fontWeight: 'bold',
                        color: table.dead_percent > 10 ? 'error.main' :
                               table.dead_percent > 5 ? 'warning.main' : 'inherit'
                      }}
                    >
                      {table.dead_percent.toFixed(2)}%
                    </Typography>
                  </TableCell>
                  <TableCell>{getHealthChip(table.dead_percent, table.dead_tuples)}</TableCell>
                  <TableCell>{table.total_size}</TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(table.last_autovacuum)}
                    </Typography>
                    {table.autovacuum_count > 0 && (
                      <Typography variant="caption" color="textSecondary">
                        ({table.autovacuum_count} times)
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(table.last_vacuum)}
                    </Typography>
                    {table.vacuum_count > 0 && (
                      <Typography variant="caption" color="textSecondary">
                        ({table.vacuum_count} times)
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {table.vacuum_count + table.autovacuum_count}
                  </TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                      <Button
                        size="small"
                        variant="outlined"
                        onClick={() => openVacuumDialog(table.table_name, false)}
                        disabled={vacuuming}
                      >
                        VACUUM
                      </Button>
                      <Tooltip title="VACUUM FULL (locks table, use with caution)">
                        <Button
                          size="small"
                          variant="outlined"
                          color="warning"
                          onClick={() => openVacuumDialog(table.table_name, true)}
                          disabled={vacuuming}
                        >
                          FULL
                        </Button>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Manual VACUUM Dialog */}
      <Dialog open={vacuumDialog.open} onClose={() => !vacuuming && setVacuumDialog({ open: false, tableName: '', full: false })}>
        <DialogTitle>
          Confirm Manual {vacuumDialog.full ? 'VACUUM FULL' : 'VACUUM'}
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            {vacuumDialog.full ? (
              <>
                <strong>⚠️ WARNING: VACUUM FULL</strong>
                <br /><br />
                This will perform a full vacuum on table <code><strong>{vacuumDialog.tableName}</strong></code>.
                <br /><br />
                <strong>VACUUM FULL:</strong>
                <ul>
                  <li>Requires an <strong>exclusive lock</strong> on the table</li>
                  <li>Blocks all reads and writes during operation</li>
                  <li>Can take significant time on large tables</li>
                  <li>Reclaims maximum disk space</li>
                  <li>Should be used during maintenance windows</li>
                </ul>
                <br />
                Are you sure you want to proceed?
              </>
            ) : (
              <>
                This will perform a standard vacuum on table <code><strong>{vacuumDialog.tableName}</strong></code>.
                <br /><br />
                <strong>Standard VACUUM:</strong>
                <ul>
                  <li>Runs concurrently with normal operations</li>
                  <li>Does not block reads or writes</li>
                  <li>Removes dead tuples</li>
                  <li>Updates table statistics (ANALYZE)</li>
                  <li>Safe to run during business hours</li>
                </ul>
              </>
            )}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setVacuumDialog({ open: false, tableName: '', full: false })} disabled={vacuuming}>
            Cancel
          </Button>
          <Button
            onClick={handleManualVacuum}
            color={vacuumDialog.full ? 'warning' : 'primary'}
            variant="contained"
            disabled={vacuuming}
            startIcon={vacuuming ? <CircularProgress size={20} /> : <CleaningServicesIcon />}
          >
            {vacuuming ? 'Running...' : `Run ${vacuumDialog.full ? 'VACUUM FULL' : 'VACUUM'}`}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Info Alert */}
      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>About VACUUM:</strong> PostgreSQL VACUUM reclaims storage by removing dead tuples (deleted/updated rows).
          Autovacuum runs automatically, but manual VACUUM can be useful for large updates or high-write tables.
          <br /><br />
          <strong>Health Status:</strong>
          <ul style={{ marginTop: '8px', marginBottom: 0 }}>
            <li><strong>Healthy:</strong> &lt;2% dead tuples</li>
            <li><strong>Moderate:</strong> 2-5% dead tuples</li>
            <li><strong>High:</strong> 5-10% dead tuples or &gt;1000 dead rows</li>
            <li><strong>Critical:</strong> &gt;10% dead tuples or &gt;10000 dead rows</li>
          </ul>
        </Typography>
      </Alert>
    </Box>
  );
};
