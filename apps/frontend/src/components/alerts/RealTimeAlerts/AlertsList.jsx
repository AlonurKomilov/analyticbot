import React from 'react';
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  Box,
  Alert,
  Collapse
} from '@mui/material';
import {
  Delete as DeleteIcon
} from '@mui/icons-material';

/**
 * AlertsList - Memoized component for displaying real-time alerts
 * 
 * Handles alert display with filtering, severity indicators, and real-time updates.
 * Optimized for high-frequency alert updates in multi-user dashboard scenarios.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.alerts - Array of alert objects
 * @param {boolean} props.isExpanded - Whether the alerts list is expanded
 * @param {Function} props.onDeleteAlert - Callback for deleting alerts
 * @param {number} props.maxAlerts - Maximum number of alerts to display (default: 10)
 */
const AlertsList = React.memo(({ 
  alerts = [], 
  isExpanded = false, 
  onDeleteAlert,
  maxAlerts = 10 
}) => {
  return (
    <Collapse in={isExpanded}>
      {/* Recent Alerts */}
      {alerts.length > 0 ? (
        <List sx={{ maxHeight: 300, overflow: 'auto' }}>
          {alerts.slice(0, maxAlerts).map((alert) => {
            const IconComponent = alert.icon;
            return (
              <ListItem 
                key={alert.id}
                sx={{ 
                  border: '1px solid',
                  borderColor: `${alert.type}.light`,
                  borderRadius: 1,
                  mb: 1,
                  backgroundColor: alert.read ? 'inherit' : `${alert.type}.light`,
                  opacity: alert.read ? 0.7 : 1,
                }}
                secondaryAction={
                  <IconButton 
                    edge="end" 
                    aria-label="delete" 
                    onClick={() => onDeleteAlert?.(alert.id)}
                    size="small"
                  >
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  <IconComponent color={alert.type} />
                </ListItemIcon>
                <ListItemText
                  primary={alert.title}
                  secondary={
                    <React.Fragment>
                      <span style={{ display: 'block' }}>{alert.message}</span>
                      <span style={{ fontSize: '0.75rem', color: 'text.secondary', display: 'block' }}>
                        {new Date(alert.timestamp).toLocaleTimeString()}
                      </span>
                    </React.Fragment>
                  }
                />
              </ListItem>
            );
          })}
        </List>
      ) : (
        <Alert severity="info">
          No alerts yet. The system is actively monitoring for real-time events.
        </Alert>
      )}
    </Collapse>
  );
});

AlertsList.displayName = 'AlertsList';

export default AlertsList;