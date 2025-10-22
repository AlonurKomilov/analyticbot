import React, { useState, useCallback, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Badge,
  CircularProgress,
  Alert as MuiAlert
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
  Visibility as VisibilityIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

// Import extracted components
import AlertsList from './AlertsList.jsx';
import RuleManager from './RuleManager.jsx';
import NewRuleDialog from './NewRuleDialog.jsx';
import NotificationEngine from './NotificationEngine.jsx';

// Import new hooks
import { useAlerts } from '@hooks/useAlerts';

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
 * ✅ UPDATED (Oct 22, 2025): Now uses useAlerts hook for real API integration
 * Connects to AlertsOrchestratorService backend for live monitoring and alerts
 *
 * Features:
 * - Real-time alert fetching from backend
 * - Live monitoring metrics
 * - Auto-refresh support
 * - Alert rules management
 * - Comprehensive workflow execution
 *
 * @param props - Component props
 * @param props.channelId - Channel ID for alert monitoring
 */
const RealTimeAlertsSystem: React.FC<RealTimeAlertsSystemProps> = ({ channelId = 'demo_channel' }) => {
  // Use the new alerts hook for API integration
  const {
    alerts: apiAlerts,
    alertRules: apiAlertRules,
    liveMetrics,
    loading,
    error,
    refresh
  } = useAlerts({
    channelId,
    autoFetch: true,
    refreshInterval: 30000 // Refresh every 30 seconds
  });

  // Local UI state
  const [localAlerts, setLocalAlerts] = useState<Alert[]>([]);
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

  // Merge API alerts with locally added alerts
  useEffect(() => {
    if (apiAlerts.length > 0) {
      setLocalAlerts(prevAlerts => {
        const apiAlertIds = new Set(apiAlerts.map(a => a.id));
        const localOnlyAlerts = prevAlerts.filter(a => !apiAlertIds.has(a.id));
        return [...apiAlerts, ...localOnlyAlerts];
      });
    }
  }, [apiAlerts]);

  // Combined alerts and rules for display
  const alerts = localAlerts.length > 0 ? localAlerts : apiAlerts;
  const alertRules = apiAlertRules.length > 0 ? apiAlertRules : defaultRules;

  const [newRule, setNewRule] = useState<NewRuleFormData>({
    name: '',
    type: 'growth',
    condition: 'greater_than',
    threshold: 10,
    enabled: true,
  });

  // Initialize default rules
  React.useEffect(() => {
    // Default rules are now used as fallback in the const declaration above
    // No need to set state here
  }, [defaultRules]);

  // Handle new alerts from NotificationEngine or manual triggers
  const handleNewAlerts = useCallback((newAlerts: Alert[]): void => {
    setLocalAlerts(prev => [...newAlerts, ...prev].slice(0, 50)); // Keep last 50 alerts
  }, []);

  // Delete alert handler (works for both API and local alerts)
  const handleDeleteAlert = useCallback((alertId: string): void => {
    setLocalAlerts(prev => prev.filter(alert => alert.id !== alertId));
  }, []);

  // Toggle rule enabled state (local only - in production, would sync with backend)
  const handleToggleRule = useCallback((_ruleId: string): void => {
    // Note: This only affects the local defaultRules fallback
    // When using API rules, you'd need to call an update endpoint
    console.warn('Rule toggle - backend sync not yet implemented for API rules');
  }, []);

  // Add new rule (local only - in production, would sync with backend)
  const handleAddNewRule = useCallback((): void => {
    if (!newRule.name.trim()) return;

    // Note: This only affects the local defaultRules fallback
    // When using API rules, you'd need to call a create endpoint
    console.warn('Add new rule - backend sync not yet implemented for API rules');

    setNewRule({
      name: '',
      type: 'growth',
      condition: 'greater_than',
      threshold: 10,
      enabled: true,
    });
    setNewRuleDialog(false);
  }, [newRule]);

  // Count unread alerts (handle both Alert types)
  const unreadCount = alerts.filter(alert => 'read' in alert ? !alert.read : false).length;

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
              label={loading ? 'Loading...' : `${alertRules.filter(rule => rule.enabled).length} rules active`}
              size="small"
              variant="filled"
            />
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton
              onClick={() => refresh()}
              disabled={loading}
              title="Refresh alerts"
            >
              {loading ? <CircularProgress size={20} /> : <RefreshIcon />}
            </IconButton>
            <IconButton onClick={() => setSettingsOpen(true)}>
              <SettingsIcon />
            </IconButton>
            <IconButton onClick={() => setIsExpanded(!isExpanded)}>
              {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        {/* Error Display */}
        {error && (
          <MuiAlert severity="error" sx={{ mb: 2 }} onClose={() => {}}>
            Failed to load alerts: {error}
          </MuiAlert>
        )}

        {/* Live Metrics Display */}
        {liveMetrics && (
          <Box sx={{ mb: 2, p: 1.5, bgcolor: 'background.paper', borderRadius: 1, border: '1px solid', borderColor: 'divider' }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 'bold' }}>
              Live Metrics: {liveMetrics.alerts.length} alerts •
              Status: {liveMetrics.status} •
              Last updated: {new Date(liveMetrics.timestamp).toLocaleTimeString()}
            </Typography>
          </Box>
        )}

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
          channelId={channelId}
          alertRules={alertRules as any}
          onNewAlerts={handleNewAlerts as any}
          existingAlerts={alerts as any}
        />
      </CardContent>
    </Card>
  );
};

export default RealTimeAlertsSystem;
