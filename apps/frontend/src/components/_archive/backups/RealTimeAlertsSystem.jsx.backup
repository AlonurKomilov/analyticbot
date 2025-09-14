import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Alert,
  Chip,
  IconButton,
  Collapse,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Badge,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Slider,
  Grid,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  NotificationsActive as NotificationsActiveIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  People as PeopleIcon,
  Visibility as VisibilityIcon,
  Settings as SettingsIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { apiClient } from '../../utils/apiClient';

const RealTimeAlertsSystem = ({ channelId = 'demo_channel' }) => {
  const [alerts, setAlerts] = useState([]);
  const [alertRules, setAlertRules] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [newRuleDialog, setNewRuleDialog] = useState(false);
  const [loading, setLoading] = useState(false);

  // Default alert rules
  const defaultRules = [
    {
      id: 'growth-spike',
      name: 'Growth Spike Alert',
      type: 'growth',
      condition: 'greater_than',
      threshold: 15,
      enabled: true,
      description: 'Alert when growth rate exceeds 15%',
      icon: TrendingUpIcon,
      color: 'success',
    },
    {
      id: 'low-engagement',
      name: 'Low Engagement Warning',
      type: 'engagement',
      condition: 'less_than',
      threshold: 3,
      enabled: true,
      description: 'Alert when engagement rate drops below 3%',
      icon: TrendingDownIcon,
      color: 'warning',
    },
    {
      id: 'subscriber-milestone',
      name: 'Subscriber Milestone',
      type: 'subscribers',
      condition: 'milestone',
      threshold: 1000,
      enabled: true,
      description: 'Alert when reaching subscriber milestones',
      icon: PeopleIcon,
      color: 'info',
    },
    {
      id: 'view-surge',
      name: 'View Surge Alert',
      type: 'views',
      condition: 'surge',
      threshold: 50,
      enabled: false,
      description: 'Alert when views increase by 50% above average',
      icon: VisibilityIcon,
      color: 'primary',
    },
  ];

  const [newRule, setNewRule] = useState({
    name: '',
    type: 'growth',
    condition: 'greater_than',
    threshold: 10,
    enabled: true,
  });

  useEffect(() => {
    // Initialize with default rules if none exist
    if (alertRules.length === 0) {
      setAlertRules(defaultRules);
    }

    // Simulate real-time alert checking
    const checkAlerts = async () => {
      try {
        // In a real implementation, this would fetch actual analytics data
        // For now, simulate with random conditions to demonstrate functionality
        const simulatedData = {
          growth_rate: Math.random() * 25, // 0-25%
          engagement_rate: Math.random() * 10, // 0-10%
          subscribers: 850 + Math.floor(Math.random() * 200), // 850-1050
          views: 5000 + Math.floor(Math.random() * 3000), // 5000-8000
        };

        const newAlerts = [];
        const currentTime = new Date();

        alertRules.forEach(rule => {
          if (!rule.enabled) return;

          let shouldAlert = false;
          let alertMessage = '';

          switch (rule.type) {
            case 'growth':
              if (rule.condition === 'greater_than' && simulatedData.growth_rate > rule.threshold) {
                shouldAlert = true;
                alertMessage = `Growth rate reached ${simulatedData.growth_rate.toFixed(1)}% (threshold: ${rule.threshold}%)`;
              }
              break;

            case 'engagement':
              if (rule.condition === 'less_than' && simulatedData.engagement_rate < rule.threshold) {
                shouldAlert = true;
                alertMessage = `Engagement rate dropped to ${simulatedData.engagement_rate.toFixed(1)}% (threshold: ${rule.threshold}%)`;
              }
              break;

            case 'subscribers':
              if (rule.condition === 'milestone' && simulatedData.subscribers >= rule.threshold) {
                shouldAlert = true;
                alertMessage = `Reached ${simulatedData.subscribers} subscribers!`;
              }
              break;

            case 'views':
              if (rule.condition === 'surge' && Math.random() > 0.7) { // 30% chance for demo
                shouldAlert = true;
                alertMessage = `View surge detected: ${simulatedData.views} views in last hour`;
              }
              break;
          }

          if (shouldAlert) {
            // Check if we haven't already shown this alert recently (prevent spam)
            const recentAlert = alerts.find(alert => 
              alert.ruleId === rule.id && 
              (currentTime - new Date(alert.timestamp)) < 300000 // 5 minutes
            );

            if (!recentAlert) {
              newAlerts.push({
                id: `${rule.id}-${Date.now()}`,
                ruleId: rule.id,
                title: rule.name,
                message: alertMessage,
                type: rule.color,
                timestamp: currentTime.toISOString(),
                icon: rule.icon,
                read: false,
              });
            }
          }
        });

        if (newAlerts.length > 0) {
          setAlerts(prev => [...newAlerts, ...prev].slice(0, 50)); // Keep last 50 alerts
        }
      } catch (error) {
        console.error('Error checking alerts:', error);
      }
    };

    // Check for alerts every 30 seconds
    const interval = setInterval(checkAlerts, 30000);
    
    // Initial check
    checkAlerts();

    return () => clearInterval(interval);
  }, [alertRules, alerts]);

  const toggleRule = (ruleId) => {
    setAlertRules(prev => 
      prev.map(rule => 
        rule.id === ruleId 
          ? { ...rule, enabled: !rule.enabled }
          : rule
      )
    );
  };

  const deleteAlert = (alertId) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const markAllAsRead = () => {
    setAlerts(prev => prev.map(alert => ({ ...alert, read: true })));
  };

  const addNewRule = () => {
    const rule = {
      ...newRule,
      id: `custom-${Date.now()}`,
      icon: getIconForType(newRule.type),
      color: getColorForType(newRule.type),
      description: `Custom rule: ${newRule.name}`,
    };

    setAlertRules(prev => [...prev, rule]);
    setNewRule({ name: '', type: 'growth', condition: 'greater_than', threshold: 10, enabled: true });
    setNewRuleDialog(false);
  };

  const getIconForType = (type) => {
    switch (type) {
      case 'growth': return TrendingUpIcon;
      case 'engagement': return TrendingDownIcon;
      case 'subscribers': return PeopleIcon;
      case 'views': return VisibilityIcon;
      default: return NotificationsIcon;
    }
  };

  const getColorForType = (type) => {
    switch (type) {
      case 'growth': return 'success';
      case 'engagement': return 'warning';
      case 'subscribers': return 'info';
      case 'views': return 'primary';
      default: return 'default';
    }
  };

  const unreadCount = alerts.filter(alert => !alert.read).length;

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsActiveIcon />
            </Badge>
            Real-time Alerts System
          </Typography>
          <Box>
            <IconButton onClick={() => setSettingsOpen(true)} size="small">
              <SettingsIcon />
            </IconButton>
            <IconButton 
              onClick={() => setIsExpanded(!isExpanded)} 
              size="small"
            >
              {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        {/* Alert Summary */}
        <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
          <Chip 
            label={`${alerts.length} Total Alerts`} 
            size="small" 
            variant="outlined" 
          />
          <Chip 
            label={`${alertRules.filter(r => r.enabled).length} Active Rules`} 
            size="small" 
            color="primary" 
          />
          {unreadCount > 0 && (
            <Chip 
              label={`${unreadCount} Unread`} 
              size="small" 
              color="error" 
              onClick={markAllAsRead}
              clickable
            />
          )}
        </Box>

        <Collapse in={isExpanded}>
          {/* Recent Alerts */}
          {alerts.length > 0 ? (
            <List sx={{ maxHeight: 300, overflow: 'auto' }}>
              {alerts.slice(0, 10).map((alert) => {
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
                        onClick={() => deleteAlert(alert.id)}
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
                        <Box>
                          <Typography variant="body2">{alert.message}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(alert.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                );
              })}
            </List>
          ) : (
            <Alert severity="info">
              No alerts yet. The system is monitoring your channel and will notify you of important changes.
            </Alert>
          )}
        </Collapse>

        {/* Settings Dialog */}
        <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Alert Rules Configuration</DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Configure when you want to receive alerts for your channel performance.
            </Typography>

            <Box sx={{ mb: 3 }}>
              <Button 
                startIcon={<AddIcon />} 
                variant="outlined" 
                onClick={() => setNewRuleDialog(true)}
                sx={{ mb: 2 }}
              >
                Add New Rule
              </Button>
            </Box>

            <List>
              {alertRules.map((rule, index) => {
                const IconComponent = rule.icon;
                return (
                  <Box key={rule.id}>
                    <ListItem>
                      <ListItemIcon>
                        <IconComponent color={rule.color} />
                      </ListItemIcon>
                      <ListItemText
                        primary={rule.name}
                        secondary={rule.description}
                      />
                      <FormControlLabel
                        control={
                          <Switch
                            checked={rule.enabled}
                            onChange={() => toggleRule(rule.id)}
                            color="primary"
                          />
                        }
                        label="Enabled"
                      />
                    </ListItem>
                    {index < alertRules.length - 1 && <Divider />}
                  </Box>
                );
              })}
            </List>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSettingsOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        {/* New Rule Dialog */}
        <Dialog open={newRuleDialog} onClose={() => setNewRuleDialog(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Create New Alert Rule</DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Rule Name"
                  value={newRule.name}
                  onChange={(e) => setNewRule(prev => ({ ...prev, name: e.target.value }))}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  select
                  label="Metric Type"
                  value={newRule.type}
                  onChange={(e) => setNewRule(prev => ({ ...prev, type: e.target.value }))}
                  SelectProps={{ native: true }}
                >
                  <option value="growth">Growth Rate</option>
                  <option value="engagement">Engagement Rate</option>
                  <option value="subscribers">Subscribers</option>
                  <option value="views">Views</option>
                </TextField>
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  select
                  label="Condition"
                  value={newRule.condition}
                  onChange={(e) => setNewRule(prev => ({ ...prev, condition: e.target.value }))}
                  SelectProps={{ native: true }}
                >
                  <option value="greater_than">Greater Than</option>
                  <option value="less_than">Less Than</option>
                  <option value="milestone">Milestone</option>
                  <option value="surge">Surge Detection</option>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <Typography gutterBottom>Threshold: {newRule.threshold}</Typography>
                <Slider
                  value={newRule.threshold}
                  onChange={(e, value) => setNewRule(prev => ({ ...prev, threshold: value }))}
                  min={1}
                  max={100}
                  step={1}
                  marks={[
                    { value: 1, label: '1' },
                    { value: 50, label: '50' },
                    { value: 100, label: '100' },
                  ]}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setNewRuleDialog(false)}>Cancel</Button>
            <Button 
              onClick={addNewRule} 
              variant="contained"
              disabled={!newRule.name.trim()}
            >
              Create Rule
            </Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

export default RealTimeAlertsSystem;
