/**
 * Owner Dashboard - Main Page
 *
 * Main dashboard for owner-only features including database management,
 * system monitoring, and backup operations.
 *
 * Access: OWNER ROLE ONLY (Level 4)
 */

import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Divider,
  Alert,
  AlertTitle,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import DatabaseStatsComponent from '../components/DatabaseStats';
import DatabaseBackupComponent from '../components/DatabaseBackup';

export const OwnerDashboard: React.FC = () => {
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
              System administration and database management
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

      {/* Database Statistics Section */}
      <Paper elevation={0} sx={{ mb: 4, p: 3, bgcolor: 'grey.50' }}>
        <DatabaseStatsComponent />
      </Paper>

      <Divider sx={{ my: 4 }} />

      {/* Database Backup Section */}
      <Paper elevation={0} sx={{ p: 3, bgcolor: 'grey.50' }}>
        <DatabaseBackupComponent />
      </Paper>

      {/* Additional Info */}
      <Box mt={4}>
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
    </Container>
  );
};

export default OwnerDashboard;
