/**
 * Threat Alerts Component
 * Displays list of security threats and alerts
 */

import React from 'react';
import {
  Box,
  CardContent,
  Typography,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import NotificationsIcon from '@mui/icons-material/Notifications';

import { SecurityAlert } from '@features/ai-services/services';

interface ThreatAlertsProps {
  alerts: SecurityAlert[];
}

const getSeverityColor = (severity: string): 'error' | 'warning' | 'info' | 'success' | 'default' => {
  switch (severity) {
    case 'critical': return 'error';
    case 'high': return 'warning';
    case 'medium': return 'info';
    case 'low': return 'success';
    default: return 'default';
  }
};

const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case 'critical': return <ErrorIcon color="error" />;
    case 'high': return <WarningIcon color="warning" />;
    case 'medium': return <NotificationsIcon color="info" />;
    case 'low': return <CheckCircleIcon color="success" />;
    default: return <CheckCircleIcon />;
  }
};

export const ThreatAlerts: React.FC<ThreatAlertsProps> = ({ alerts }) => {
  return (
    <CardContent>
      <Typography variant="h6" sx={{ mb: 3 }}>
        Recent Security Alerts
      </Typography>

      {alerts.length === 0 ? (
        <Alert severity="success">
          No security threats detected. Your system is secure.
        </Alert>
      ) : (
        <List>
          {alerts.map((alert) => (
            <ListItem
              key={alert.id}
              sx={{
                border: 1,
                borderColor: 'divider',
                borderRadius: 2,
                mb: 2,
                borderLeftColor: getSeverityColor(alert.severity) + '.main',
                borderLeftWidth: 4
              }}
            >
              <ListItemIcon>
                {getSeverityIcon(alert.severity)}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1" fontWeight={600}>
                      {alert.type}
                    </Typography>
                    <Chip
                      label={alert.severity.toUpperCase()}
                      color={getSeverityColor(alert.severity)}
                      size="small"
                    />
                    <Chip
                      label={alert.action}
                      variant="outlined"
                      size="small"
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      {alert.description}
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block', mt: 0.5 }}>
                      Source: {alert.source} • {alert.timestamp}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      )}
    </CardContent>
  );
};

export default ThreatAlerts;
