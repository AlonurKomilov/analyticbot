/**
 * VACUUM & Table Health Monitor Component
 *
 * Provides comprehensive monitoring and control of PostgreSQL VACUUM operations
 * for the owner dashboard. Displays table health, dead tuple statistics, bloat
 * analysis, and allows manual VACUUM triggering.
 *
 * Refactored: Nov 2025 - Split into sub-components
 *
 * Features:
 * - Real-time table health monitoring
 * - Dead tuple percentage visualization
 * - Manual VACUUM control (standard and FULL)
 * - Autovacuum configuration display
 * - Tables needing attention alerts
 * - Auto-refresh capability
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  FormControlLabel,
  Switch,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  IconButton
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  CleaningServices as CleaningServicesIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { ownerApi } from '../../services/ownerApi';

// Sub-components
import { VacuumSummaryCards } from './VacuumSummaryCards';
import { AutovacuumConfigPanel } from './AutovacuumConfigPanel';
import { VacuumTableList } from './VacuumTableList';
import { VacuumDialog } from './VacuumDialog';

// Types
import type { TableHealth, VacuumSummary, AutovacuumConfig, VacuumDialogState } from './types';

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
  const [vacuumDialog, setVacuumDialog] = useState<VacuumDialogState>({
    open: false,
    tableName: '',
    full: false
  });
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

  const closeVacuumDialog = () => {
    setVacuumDialog({ open: false, tableName: '', full: false });
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
        <VacuumSummaryCards
          summary={summary}
          tablesNeedingAttention={tablesNeedingAttention}
        />
      )}

      {/* Autovacuum Configuration */}
      <AutovacuumConfigPanel config={config} show={showConfig} />

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
        <VacuumTableList
          tables={tables}
          vacuuming={vacuuming}
          onVacuumClick={openVacuumDialog}
        />
      )}

      {/* Manual VACUUM Dialog */}
      <VacuumDialog
        dialogState={vacuumDialog}
        vacuuming={vacuuming}
        onClose={closeVacuumDialog}
        onConfirm={handleManualVacuum}
      />

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

export default VacuumMonitor;
