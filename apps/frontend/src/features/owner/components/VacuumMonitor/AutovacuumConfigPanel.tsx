/**
 * AutovacuumConfigPanel Component
 * Displays autovacuum configuration settings in a collapsible panel
 */

import React from 'react';
import {
  Card,
  CardContent,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Alert,
  Tooltip,
  Collapse
} from '@mui/material';
import type { AutovacuumConfig } from './types';

interface AutovacuumConfigPanelProps {
  config: AutovacuumConfig | null;
  show: boolean;
}

export const AutovacuumConfigPanel: React.FC<AutovacuumConfigPanelProps> = ({
  config,
  show
}) => {
  if (!config) return null;

  return (
    <Collapse in={show}>
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
    </Collapse>
  );
};
