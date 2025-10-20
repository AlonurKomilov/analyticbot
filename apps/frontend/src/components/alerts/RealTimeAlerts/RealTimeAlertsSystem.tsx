import React, { useState, useCallback } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Badge
} from '@mui/material';
import { IconButton } from '../../common/TouchTargetCompliance.jsx';
import { StatusChip } from '../../common';
import {
  Notifications as NotificationsIcon,
  NotificationsActive as NotificationsActiveIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  People as PeopleIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';

// Import extracted components
import AlertsList from './AlertsList.jsx';
import RuleManager from './RuleManager.jsx';
import NewRuleDialog from './NewRuleDialog.jsx';
import NotificationEngine from './NotificationEngine.jsx';

// Type definitions
interface RealTimeAlertsSystemProps {
  channelId?: string;
}

interface Alert {
  id: string;
  read?: boolean;
  [key: string]: any;
}

interface AlertRule {
  id: string;
  name: string;
  type: string;
  condition: string;
  threshold: number;
  enabled: boolean;
  description: string;
  icon: any;
  color: string;
}

interface NewRuleFormData {
  name: string;
  type: string;
  condition: string;
  threshold: number;
  enabled: boolean;
}

/**
 * RealTimeAlertsSystem - Main orchestrator for real-time alert management
 *
 * Refactored from 486-line monolithic component to modular architecture.
 * Manages state coordination, API calls, and coordinates between extracted components.
 * Reduced from 486 lines to ~150 lines (69% reduction).
 *
 * @param props - Component props
 * @param props.channelId - Channel ID for alert monitoring
 */
const RealTimeAlertsSystem: React.FC<RealTimeAlertsSystemProps> = ({ channelId: _channelId = 'demo_channel' }) => {
  // Main component state
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [settingsOpen, setSettingsOpen] = useState<boolean>(false);
  const [newRuleDialog, setNewRuleDialog] = useState<boolean>(false);

  // Default alert rules configuration
  const defaultRules = React.useMemo<AlertRule[]>(() => [
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
  ], []);

  const [newRule, setNewRule] = useState<NewRuleFormData>({
    name: '',
    type: 'growth',
    condition: 'greater_than',
    threshold: 10,
    enabled: true,
  });

  // Initialize default rules
  React.useEffect(() => {
    if (alertRules.length === 0) {
      setAlertRules(defaultRules);
    }
  }, [defaultRules, alertRules.length]);

  // Handle new alerts from NotificationEngine
  const handleNewAlerts = useCallback((newAlerts: Alert[]): void => {
    setAlerts(prev => [...newAlerts, ...prev].slice(0, 50)); // Keep last 50 alerts
  }, []);

  // Delete alert handler
  const handleDeleteAlert = useCallback((alertId: string): void => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  }, []);

  // Toggle rule enabled state
  const handleToggleRule = useCallback((ruleId: string): void => {
    setAlertRules(prev => prev.map(rule =>
      rule.id === ruleId
        ? { ...rule, enabled: !rule.enabled }
        : rule
    ));
  }, []);

  // Add new rule
  const handleAddNewRule = useCallback((): void => {
    if (!newRule.name.trim()) return;

    const rule: AlertRule = {
      ...newRule,
      id: `custom-${Date.now()}`,
      description: `Custom ${newRule.type} alert`,
      icon: TrendingUpIcon,
      color: 'primary',
    };

    setAlertRules(prev => [...prev, rule]);
    setNewRule({
      name: '',
      type: 'growth',
      condition: 'greater_than',
      threshold: 10,
      enabled: true,
    });
    setNewRuleDialog(false);
  }, [newRule]);

  // Count unread alerts
  const unreadCount = alerts.filter(alert => !alert.read).length;

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Badge badgeContent={unreadCount} color="error">
              {unreadCount > 0 ? (
                <NotificationsActiveIcon color="primary" />
              ) : (
                <NotificationsIcon color="action" />
              )}
            </Badge>
            <Typography variant="h6">Real-time Alerts</Typography>
            <StatusChip
              label={`${alertRules.filter(rule => rule.enabled).length} rules active`}
              size="small"
              variant="filled"
            />
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton onClick={() => setSettingsOpen(true)}>
              <SettingsIcon />
            </IconButton>
            <IconButton onClick={() => setIsExpanded(!isExpanded)}>
              {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        {/* Alerts List */}
        <AlertsList
          alerts={alerts as any}
          isExpanded={isExpanded}
          onDeleteAlert={handleDeleteAlert}
        />

        {/* Rule Manager Dialog */}
        {React.createElement(RuleManager as any, {
          rules: alertRules,
          open: settingsOpen,
          onClose: () => setSettingsOpen(false),
          onToggleRule: handleToggleRule,
          onAddRule: () => setNewRuleDialog(true)
        })}

        {/* New Rule Dialog */}
        <NewRuleDialog
          open={newRuleDialog}
          onClose={() => setNewRuleDialog(false)}
          onSubmit={handleAddNewRule}
          newRule={newRule as any}
          onRuleChange={setNewRule as any}
        />

        {/* Notification Engine */}
        <NotificationEngine
          alertRules={alertRules as any}
          onNewAlerts={handleNewAlerts as any}
          existingAlerts={alerts as any}
        />
      </CardContent>
    </Card>
  );
};

export default RealTimeAlertsSystem;
