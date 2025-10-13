import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Chip
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

const DataSourceStatus = React.memo(({
  isLoading,
  hasError,
  errors,
  actions,
  isUsingRealAPI,
  dataSource,
  switchDataSource,
  onRefresh
}) => {
  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Advanced Analytics Dashboard
        </Typography>
        <LinearProgress sx={{ mt: 2 }} />
        <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
          Loading analytics data from {isUsingRealAPI ? 'real API' : 'mock service'}...
        </Typography>
      </Box>
    );
  }

  if (hasError) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Advanced Analytics Dashboard
        </Typography>
        <Alert severity="error" sx={{ mt: 2 }}>
          <Typography variant="h6">Failed to load analytics data</Typography>
          <Typography variant="body2">
            {Object.values(errors).filter(Boolean).join(', ') || 'Unknown error occurred'}
          </Typography>
          <Box sx={{ mt: 2 }}>
            <button onClick={actions.clearAllErrors} style={{ marginRight: 8 }}>
              Clear Errors
            </button>
            <button onClick={onRefresh}>
              Retry
            </button>
          </Box>
        </Alert>
      </Box>
    );
  }

  // Header with data source controls
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
      <Typography variant="h5" component="h2">
        <TimelineIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
        Advanced Analytics Dashboard
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Chip
          label={isUsingRealAPI ? '🟢 Real API' : '🟡 Mock Data'}
          color={isUsingRealAPI ? 'success' : 'warning'}
          size="small"
          onClick={() => switchDataSource(isUsingRealAPI ? 'mock' : 'api')}
          sx={{ cursor: 'pointer' }}
        />
        <Tooltip title="Refresh dashboard">
          <IconButton onClick={onRefresh} size="small">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
});

DataSourceStatus.displayName = 'DataSourceStatus';

export default DataSourceStatus;
