/**
 * Owner Dashboard - Main Page
 *
 * Main dashboard for owner-only features including database management,
 * system monitoring, and backup operations.
 *
 * Access: OWNER ROLE ONLY (Level 4)
 */

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Alert,
  AlertTitle,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  Storage as StorageIcon,
  Backup as BackupIcon,
  Speed as SpeedIcon,
  CleaningServices as CleaningServicesIcon,
} from '@mui/icons-material';
import DatabaseStatsComponent from './components/DatabaseStats';
import DatabaseBackupComponent from './components/DatabaseBackup';
import { QueryPerformanceMonitor } from './components/QueryPerformanceMonitor';
import { VacuumMonitor } from './components/VacuumMonitor';

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

export const OwnerDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Page Header */}
      <Box mb={4}>
        <Box display="flex" alignItems="center" mb={2}>
          <SecurityIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
          <Box>
            <Typography variant="h4" component="h1" fontWeight="bold">
              Owner Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              System administration, database management, and performance monitoring
            </Typography>
          </Box>
        </Box>

        {/* Owner-Only Warning */}
        <Alert severity="warning" icon={<WarningIcon />} sx={{ mt: 2 }}>
          <AlertTitle>Owner Access Only</AlertTitle>
          This dashboard contains sensitive system data and administrative functions.
          Only users with owner role (Level 4) can access these features.
        </Alert>
      </Box>

      {/* Tabs Navigation */}
      <Paper elevation={2}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab
            icon={<StorageIcon />}
            label="Database Stats"
            iconPosition="start"
          />
          <Tab
            icon={<BackupIcon />}
            label="Backup Management"
            iconPosition="start"
          />
          <Tab
            icon={<SpeedIcon />}
            label="Query Performance"
            iconPosition="start"
          />
          <Tab
            icon={<CleaningServicesIcon />}
            label="VACUUM Operations"
            iconPosition="start"
          />
        </Tabs>

        {/* Tab 0: Database Statistics */}
        <TabPanel value={tabValue} index={0}>
          <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50' }}>
            <DatabaseStatsComponent />
          </Paper>
        </TabPanel>

        {/* Tab 1: Database Backup */}
        <TabPanel value={tabValue} index={1}>
          <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50' }}>
            <DatabaseBackupComponent />
          </Paper>
          <Box mt={3} px={3} pb={3}>
            <Alert severity="info">
              <AlertTitle>About Database Backups</AlertTitle>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                <li>Backups are created manually from this dashboard (no auto-scheduling)</li>
                <li>Backups are compressed and stored locally for 7 days</li>
                <li>Always verify backup integrity before relying on it for restore</li>
                <li>The most recent backup cannot be deleted for safety</li>
                <li>All backup operations are logged for audit purposes</li>
              </ul>
            </Alert>
          </Box>
        </TabPanel>

        {/* Tab 2: Query Performance Monitor */}
        <TabPanel value={tabValue} index={2}>
          <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50' }}>
            <QueryPerformanceMonitor />
          </Paper>
          <Box mt={3} px={3} pb={3}>
            <Alert severity="info">
              <AlertTitle>About Query Performance Monitoring</AlertTitle>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                <li>Powered by PostgreSQL pg_stat_statements extension</li>
                <li>Tracks execution time, call frequency, and performance metrics</li>
                <li>Queries &gt;1 second are automatically logged</li>
                <li>Use this to identify optimization opportunities</li>
                <li>Reset statistics after optimizations to measure improvements</li>
                <li>Auto-refresh updates data every 30 seconds when enabled</li>
              </ul>
            </Alert>
          </Box>
        </TabPanel>

        {/* Tab 3: VACUUM Operations Monitor */}
        <TabPanel value={tabValue} index={3}>
          <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50' }}>
            <VacuumMonitor />
          </Paper>
          <Box mt={3} px={3} pb={3}>
            <Alert severity="info">
              <AlertTitle>About VACUUM Operations</AlertTitle>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                <li>Autovacuum runs automatically every 30 seconds on all tables</li>
                <li>Aggressive settings applied to high-write tables (post_metrics, posts, channels)</li>
                <li>Manual VACUUM recommended for tables with &gt;5% dead tuples</li>
                <li>VACUUM FULL reclaims maximum space but requires exclusive lock</li>
                <li>Table-specific thresholds optimize performance for your workload</li>
                <li>Regular vacuum prevents bloat and maintains query performance</li>
              </ul>
            </Alert>
          </Box>
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default OwnerDashboard;
