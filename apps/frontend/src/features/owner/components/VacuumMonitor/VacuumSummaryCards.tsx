/**
 * VacuumSummaryCards Component
 * Displays summary statistics for database vacuum status
 */

import React from 'react';
import { Grid, Card, CardContent, Typography } from '@mui/material';
import type { VacuumSummary, TableHealth } from './types';

interface VacuumSummaryCardsProps {
  summary: VacuumSummary;
  tablesNeedingAttention: TableHealth[];
}

export const VacuumSummaryCards: React.FC<VacuumSummaryCardsProps> = ({
  summary,
  tablesNeedingAttention
}) => {
  return (
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
            <Typography 
              variant="h5" 
              color={tablesNeedingAttention.length > 0 ? 'warning.main' : 'success.main'}
            >
              {tablesNeedingAttention.length}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};
