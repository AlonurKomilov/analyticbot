/**
 * Active Monitors Component
 * Displays status of active security monitors
 */

import React from 'react';
import {
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';

import { SecurityMonitor } from '@features/ai-services/services';

interface ActiveMonitorsProps {
  monitors: SecurityMonitor[];
}

const getMonitorIcon = (status: string) => {
  switch (status) {
    case 'active': return <CheckCircleIcon color="success" />;
    case 'maintenance': return <WarningIcon color="warning" />;
    case 'offline': return <ErrorIcon color="error" />;
    default: return <CheckCircleIcon />;
  }
};

export const ActiveMonitors: React.FC<ActiveMonitorsProps> = ({ monitors }) => {
  return (
    <CardContent>
      <Typography variant="h6" sx={{ mb: 3 }}>
        Security Monitor Status
      </Typography>

      <List>
        {monitors.map((monitor, index) => (
          <ListItem
            key={index}
            sx={{
              border: 1,
              borderColor: 'divider',
              borderRadius: 1,
              mb: 1
            }}
          >
            <ListItemIcon>
              {getMonitorIcon(monitor.status)}
            </ListItemIcon>
            <ListItemText
              primary={monitor.name}
              secondary={`Last update: ${monitor.lastUpdate}`}
            />
            <Chip
              label={monitor.status}
              color={
                monitor.status === 'active' ? 'success' :
                monitor.status === 'maintenance' ? 'warning' : 'error'
              }
              size="small"
              variant="outlined"
            />
          </ListItem>
        ))}
      </List>
    </CardContent>
  );
};

export default ActiveMonitors;
