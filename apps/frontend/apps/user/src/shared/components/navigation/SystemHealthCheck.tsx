/**
 * System Health Check UI Component
 *
 * Displays real-time health check progress during app initialization
 * Shows production readiness status with detailed component checks
 */

import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Alert,
  Collapse,
  IconButton,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  HourglassEmpty as HourglassEmptyIcon,
  ExpandMore as ExpandMoreIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  Security as SecurityIcon,
  Dashboard as DashboardIcon
} from '@mui/icons-material';

/**
 * Type definitions
 */
export type CheckStatus = 'passed' | 'failed' | 'degraded' | 'timeout' | 'pending';
export type CheckCategory = 'critical' | 'important' | 'optional';
export type OverallStatus = 'passed' | 'degraded' | 'failed';

export interface HealthCheck {
  name: string;
  category: CheckCategory;
  description: string;
  status: CheckStatus;
  duration: number;
  details?: Record<string, any>;
  error?: string;
}

export interface HealthCheckReport {
  overallStatus: OverallStatus;
  checks: HealthCheck[];
  criticalFailures: HealthCheck[];
  warnings: HealthCheck[];
  recommendations: string[];
  getDuration: () => number;
  getStatusEmoji: () => string;
  isProductionReady: () => boolean;
}

export interface HealthCheckProgress {
  current: number;
  total: number;
  check?: HealthCheck;
}

export interface SystemHealthCheckProps {
  report?: HealthCheckReport;
  loading?: boolean;
  progress?: HealthCheckProgress | null;
}

interface HealthCheckItemProps {
  check: HealthCheck;
  expanded: boolean;
  onToggle: () => void;
}

interface CheckStatusIconResult {
  icon: React.ReactElement;
  color: 'success' | 'error' | 'warning' | 'default';
}

/**
 * Get icon and color for check status
 */
const getCheckStatusIcon = (status: CheckStatus): CheckStatusIconResult => {
  switch (status) {
    case 'passed':
      return { icon: <CheckCircleIcon />, color: 'success' };
    case 'failed':
      return { icon: <ErrorIcon />, color: 'error' };
    case 'degraded':
      return { icon: <WarningIcon />, color: 'warning' };
    case 'timeout':
      return { icon: <HourglassEmptyIcon />, color: 'warning' };
    default:
      return { icon: <HourglassEmptyIcon />, color: 'default' };
  }
};

/**
 * Get icon for check category
 */
const getCategoryIcon = (category: CheckCategory): React.ReactElement => {
  switch (category) {
    case 'critical':
      return <SecurityIcon />;
    case 'important':
      return <DashboardIcon />;
    case 'optional':
      return <SpeedIcon />;
    default:
      return <StorageIcon />;
  }
};

/**
 * Individual health check item
 */
const HealthCheckItem: React.FC<HealthCheckItemProps> = ({ check, expanded, onToggle }) => {
  const { icon, color } = getCheckStatusIcon(check.status);
  const hasDetails = check.details && Object.keys(check.details).length > 0;
  const hasError = Boolean(check.error);

  return (
    <>
      <ListItem
        sx={{
          borderLeft: 4,
          borderColor: `${color}.main`,
          mb: 1,
          borderRadius: 1,
          bgcolor: 'background.paper',
          '&:hover': {
            bgcolor: 'action.hover'
          }
        }}
      >
        <ListItemIcon>
          {icon}
        </ListItemIcon>
        <ListItemText
          primary={
            <Box display="flex" alignItems="center" gap={1}>
              <Typography variant="body1" fontWeight="medium">
                {check.name}
              </Typography>
              <Chip
                label={check.category}
                size="small"
                color={
                  check.category === 'critical' ? 'error' :
                  check.category === 'important' ? 'warning' : 'default'
                }
                variant="outlined"
              />
            </Box>
          }
          secondary={
            <Box>
              <Typography variant="caption" color="text.secondary">
                {check.description}
              </Typography>
              {check.duration > 0 && (
                <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>
                  • {check.duration}ms
                </Typography>
              )}
            </Box>
          }
        />
        {(hasDetails || hasError) && (
          <IconButton
            onClick={onToggle}
            size="small"
            sx={{
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.3s'
            }}
          >
            <ExpandMoreIcon />
          </IconButton>
        )}
      </ListItem>

      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <Box sx={{ ml: 4, mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          {hasError && (
            <Alert severity={color === 'default' ? 'info' : color} sx={{ mb: 1 }}>
              {check.error}
            </Alert>
          )}
          {hasDetails && (
            <Box>
              <Typography variant="caption" fontWeight="bold" color="text.secondary">
                Details:
              </Typography>
              <pre style={{ fontSize: '0.75rem', marginTop: 4, overflow: 'auto' }}>
                {JSON.stringify(check.details, null, 2)}
              </pre>
            </Box>
          )}
        </Box>
      </Collapse>
    </>
  );
};

/**
 * Main system health check display
 */
export const SystemHealthCheck: React.FC<SystemHealthCheckProps> = ({
  report,
  loading = false,
  progress = null
}) => {
  const [expandedChecks, setExpandedChecks] = useState<Set<string>>(new Set());

  const toggleCheck = (checkName: string) => {
    setExpandedChecks(prev => {
      const next = new Set(prev);
      if (next.has(checkName)) {
        next.delete(checkName);
      } else {
        next.add(checkName);
      }
      return next;
    });
  };

  if (loading) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="400px"
        p={3}
      >
        <Paper elevation={3} sx={{ p: 4, maxWidth: 600, width: '100%' }}>
          <Typography variant="h5" gutterBottom align="center">
            🏥 Running System Health Checks
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
            Verifying API endpoints, services, and system components...
          </Typography>

          <LinearProgress sx={{ mb: 2 }} />

          {progress && (
            <Box>
              <Typography variant="body2" align="center">
                {progress.current} / {progress.total} checks completed
              </Typography>
              {progress.check && (
                <Typography variant="caption" color="text.secondary" align="center" display="block">
                  {progress.check.name}
                </Typography>
              )}
            </Box>
          )}
        </Paper>
      </Box>
    );
  }

  if (!report) {
    return null;
  }

  // Group checks by category
  const checksByCategory: Record<CheckCategory, HealthCheck[]> = {
    critical: [],
    important: [],
    optional: []
  };

  report.checks.forEach(check => {
    if (checksByCategory[check.category]) {
      checksByCategory[check.category].push(check);
    }
  });

  const overallColor: 'success' | 'warning' | 'error' =
    report.overallStatus === 'passed' ? 'success' :
    report.overallStatus === 'degraded' ? 'warning' : 'error';

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 900, mx: 'auto' }}>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h5">
          {report.getStatusEmoji()} System Health Report
        </Typography>
        <Box display="flex" gap={1}>
          <Chip
            label={report.overallStatus.toUpperCase()}
            color={overallColor}
            variant="filled"
          />
          <Chip
            label={`${report.getDuration()}ms`}
            variant="outlined"
            size="small"
            icon={<SpeedIcon />}
          />
        </Box>
      </Box>

      {/* Production Readiness Status */}
      <Alert
        severity={report.isProductionReady() ? 'success' : 'error'}
        sx={{ mb: 3 }}
      >
        <Typography variant="body1" fontWeight="bold">
          {report.isProductionReady() ?
            '✅ System is Production Ready' :
            '❌ System NOT Production Ready'
          }
        </Typography>
        <Typography variant="body2">
          {report.isProductionReady() ?
            'All critical checks passed. System is ready for deployment.' :
            `${report.criticalFailures.length} critical failure(s) detected. Review issues below.`
          }
        </Typography>
      </Alert>

      {/* Critical Failures */}
      {report.criticalFailures.length > 0 && (
        <Box mb={3}>
          <Alert severity="error">
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Critical Failures
            </Typography>
            <List dense>
              {report.criticalFailures.map((failure, idx) => (
                <ListItem key={idx}>
                  <ListItemText
                    primary={failure.name}
                    secondary={failure.error}
                  />
                </ListItem>
              ))}
            </List>
          </Alert>
        </Box>
      )}

      {/* Warnings */}
      {report.warnings.length > 0 && (
        <Box mb={3}>
          <Alert severity="warning">
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Warnings
            </Typography>
            <List dense>
              {report.warnings.map((warning, idx) => (
                <ListItem key={idx}>
                  <ListItemText
                    primary={warning.name}
                    secondary={warning.error}
                  />
                </ListItem>
              ))}
            </List>
          </Alert>
        </Box>
      )}

      {/* Checks by Category */}
      {(Object.entries(checksByCategory) as [CheckCategory, HealthCheck[]][]).map(([category, checks]) => {
        if (checks.length === 0) return null;

        return (
          <Box key={category} mb={3}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              {getCategoryIcon(category)}
              <Typography variant="h6" textTransform="capitalize">
                {category} Checks
              </Typography>
              <Chip
                label={`${checks.filter(c => c.status === 'passed').length}/${checks.length} passed`}
                size="small"
                variant="outlined"
              />
            </Box>
            <List>
              {checks.map((check, idx) => (
                <HealthCheckItem
                  key={idx}
                  check={check}
                  expanded={expandedChecks.has(check.name)}
                  onToggle={() => toggleCheck(check.name)}
                />
              ))}
            </List>
          </Box>
        );
      })}

      <Divider sx={{ my: 3 }} />

      {/* Recommendations */}
      {report.recommendations.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            💡 Recommendations
          </Typography>
          <List>
            {report.recommendations.map((rec, idx) => (
              <ListItem key={idx}>
                <ListItemText primary={rec} />
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Paper>
  );
};

export default SystemHealthCheck;
