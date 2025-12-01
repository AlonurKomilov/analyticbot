/**
 * VacuumTableList Component
 * Displays the table health list with vacuum actions
 */

import React from 'react';
import {
  Box,
  Button,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Tooltip
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import type { TableHealth } from './types';

interface VacuumTableListProps {
  tables: TableHealth[];
  vacuuming: boolean;
  onVacuumClick: (tableName: string, full: boolean) => void;
}

/**
 * Format date relative to now
 */
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

/**
 * Get health status chip for a table
 */
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

export const VacuumTableList: React.FC<VacuumTableListProps> = ({
  tables,
  vacuuming,
  onVacuumClick
}) => {
  return (
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
                    onClick={() => onVacuumClick(table.table_name, false)}
                    disabled={vacuuming}
                  >
                    VACUUM
                  </Button>
                  <Tooltip title="VACUUM FULL (locks table, use with caution)">
                    <Button
                      size="small"
                      variant="outlined"
                      color="warning"
                      onClick={() => onVacuumClick(table.table_name, true)}
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
  );
};
