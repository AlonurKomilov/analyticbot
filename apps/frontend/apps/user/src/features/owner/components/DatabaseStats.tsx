/**
 * Database Statistics Component
 *
 * Displays current database statistics including size, table count, and backup status.
 * Owner-only component for system monitoring.
 *
 * Access: OWNER ROLE ONLY (Level 4)
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  Chip,
} from '@mui/material';
import {
  Storage as StorageIcon,
  TableChart as TableIcon,
  Description as RecordsIcon,
  Backup as BackupIcon,
  Schedule as ClockIcon,
} from '@mui/icons-material';
import { ownerApi } from '../services/ownerApi';
import type { DatabaseStats } from '../types';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  subtitle,
  color = 'primary',
}) => (
  <Card elevation={2}>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 48,
            height: 48,
            borderRadius: 2,
            bgcolor: `${color}.light`,
            color: `${color}.main`,
            mr: 2,
          }}
        >
          {icon}
        </Box>
        <Box>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
          <Typography variant="h5" component="div" fontWeight="bold">
            {value}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

export const DatabaseStatsComponent: React.FC = () => {
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await ownerApi.getDatabaseStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load database stats');
      console.error('Error loading database stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
    // Refresh every 30 seconds
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" onClose={() => setError(null)}>
        {error}
      </Alert>
    );
  }

  if (!stats) {
    return null;
  }

  const getBackupStatusColor = () => {
    if (!stats.last_backup) return 'error';
    if (stats.last_backup.age_days === 0) return 'success';
    if (stats.last_backup.age_days <= 1) return 'success';
    if (stats.last_backup.age_days <= 3) return 'warning';
    return 'error';
  };

  const getBackupStatusLabel = () => {
    if (!stats.last_backup) return 'No backups';
    if (stats.last_backup.age_days === 0) return 'Today';
    if (stats.last_backup.age_days === 1) return 'Yesterday';
    return `${stats.last_backup.age_days} days ago`;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" component="h2" fontWeight="bold">
          Database Statistics
        </Typography>
        <Chip
          label={`${stats.database_name}`}
          color="primary"
          variant="outlined"
          size="small"
        />
      </Box>

      <Grid container spacing={3}>
        {/* Database Size */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Database Size"
            value={stats.size_human}
            icon={<StorageIcon />}
            subtitle={`${stats.size_bytes.toLocaleString()} bytes`}
            color="primary"
          />
        </Grid>

        {/* Table Count */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Tables"
            value={stats.table_count}
            icon={<TableIcon />}
            subtitle="Database tables"
            color="secondary"
          />
        </Grid>

        {/* Total Records */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Records"
            value={stats.total_records.toLocaleString()}
            icon={<RecordsIcon />}
            subtitle="Across major tables"
            color="success"
          />
        </Grid>

        {/* Backup Status */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Backup Status"
            value={stats.backup_count}
            icon={<BackupIcon />}
            subtitle={getBackupStatusLabel()}
            color={getBackupStatusColor()}
          />
        </Grid>
      </Grid>

      {/* Last Backup Details */}
      {stats.last_backup && (
        <Card elevation={1} sx={{ mt: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <ClockIcon sx={{ mr: 1, color: 'text.secondary' }} />
              <Typography variant="subtitle1" fontWeight="bold">
                Last Backup
              </Typography>
            </Box>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Filename
                </Typography>
                <Typography variant="body1" fontFamily="monospace" fontSize="0.875rem">
                  {stats.last_backup.filename}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Size
                </Typography>
                <Typography variant="body1">{stats.last_backup.size}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Created
                </Typography>
                <Typography variant="body1">
                  {new Date(stats.last_backup.created_at).toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Age
                </Typography>
                <Chip
                  label={getBackupStatusLabel()}
                  size="small"
                  color={getBackupStatusColor()}
                />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default DatabaseStatsComponent;
