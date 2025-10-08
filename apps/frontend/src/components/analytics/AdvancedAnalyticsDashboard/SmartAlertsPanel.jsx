import React, { useState, useEffect } from 'react';
import {
  Box,
  Alert,
  IconButton,
  Tooltip,
  Collapse,
  List,
  ListItem,
  ListItemText,
  Typography
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  NotificationsActive as NotificationsActiveIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import { generateSmartAlerts } from './dashboardUtils';

const SmartAlertsPanel = React.memo(({ overview, postDynamics, topPosts }) => {
  const [alerts, setAlerts] = useState([]);
  const [showAlerts, setShowAlerts] = useState(false);

  // Generate alerts when data changes
  useEffect(() => {
    if (overview) {
      const newAlerts = generateSmartAlerts(overview, postDynamics, topPosts);
      setAlerts(newAlerts);
    }
  }, [overview, postDynamics, topPosts]);

  const dismissAlert = (alertId) => {
    setAlerts(prevAlerts => prevAlerts.filter(alert => alert.id !== alertId));
  };

  if (alerts.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      {/* Alerts Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Tooltip title="Smart alerts">
          <IconButton
            size="small"
            onClick={() => setShowAlerts(!showAlerts)}
            color={alerts.length > 0 ? "warning" : "default"}
          >
            {alerts.length > 0 ? <NotificationsActiveIcon /> : <NotificationsIcon />}
          </IconButton>
        </Tooltip>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Smart Alerts ({alerts.length})
        </Typography>
        <IconButton size="small" onClick={() => setShowAlerts(!showAlerts)}>
          {showAlerts ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </IconButton>
      </Box>

      {/* Alerts List */}
      <Collapse in={showAlerts}>
        <List sx={{ bgcolor: 'background.paper', borderRadius: 1 }}>
          {alerts.map((alert) => (
            <ListItem key={alert.id} sx={{ mb: 1 }}>
              <Alert
                severity={alert.type}
                sx={{ width: '100%' }}
                action={
                  <IconButton
                    size="small"
                    onClick={() => dismissAlert(alert.id)}
                  >
                    <CloseIcon fontSize="inherit" />
                  </IconButton>
                }
              >
                <Typography variant="subtitle2" gutterBottom>
                  {alert.title}
                </Typography>
                <Typography variant="body2">
                  {alert.message}
                </Typography>
                <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </Typography>
              </Alert>
            </ListItem>
          ))}
        </List>
      </Collapse>
    </Box>
  );
});

SmartAlertsPanel.displayName = 'SmartAlertsPanel';

export default SmartAlertsPanel;
