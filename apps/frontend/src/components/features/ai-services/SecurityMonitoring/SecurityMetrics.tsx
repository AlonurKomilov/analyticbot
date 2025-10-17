/**
 * Security Metrics Component
 * Displays security score breakdown in table format
 */

import React from 'react';
import {
  CardContent,
  Typography,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
  Chip
} from '@mui/material';

interface SecurityMetric {
  metric: string;
  score: number;
  status: 'excellent' | 'good' | 'needs-attention' | 'poor';
}

interface SecurityMetricsProps {
  metrics: SecurityMetric[];
}

const getScoreColor = (status: string): string => {
  switch (status) {
    case 'excellent': return 'success.main';
    case 'good': return 'info.main';
    case 'needs-attention': return 'warning.main';
    case 'poor': return 'error.main';
    default: return 'text.secondary';
  }
};

export const SecurityMetrics: React.FC<SecurityMetricsProps> = ({ metrics }) => {
  return (
    <CardContent>
      <Typography variant="h6" sx={{ mb: 3 }}>
        Security Score Breakdown
      </Typography>

      <TableContainer component={Paper} variant="outlined">
        <Table>
          <TableHead>
            <TableRow>
              <TableCell><strong>Security Area</strong></TableCell>
              <TableCell><strong>Score</strong></TableCell>
              <TableCell><strong>Status</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {metrics.map((metric, index) => (
              <TableRow key={index}>
                <TableCell>{metric.metric}</TableCell>
                <TableCell>
                  <Typography
                    variant="h6"
                    sx={{ color: getScoreColor(metric.status) }}
                  >
                    {metric.score}%
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={metric.status.replace('-', ' ')}
                    color={
                      metric.status === 'excellent' ? 'success' :
                      metric.status === 'good' ? 'info' :
                      metric.status === 'needs-attention' ? 'warning' : 'error'
                    }
                    size="small"
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </CardContent>
  );
};

export default SecurityMetrics;
