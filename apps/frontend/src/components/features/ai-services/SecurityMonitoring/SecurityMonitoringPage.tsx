/**
 * Security Monitoring Page Component
 * Main page for real-time security analysis and threat detection
 * UI ONLY - all business logic in service layer
 */

import React, { useState, useEffect } from 'react';
import { Box, Card, Tabs, Tab, Badge } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import ShieldIcon from '@mui/icons-material/Shield';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SettingsIcon from '@mui/icons-material/Settings';

import { useSecurityMonitoring } from '@hooks/useSecurityMonitoring';
import { SecurityHeader } from './SecurityHeader';
import { SecurityStatsCards } from './SecurityStatsCards';
import { ThreatAlerts } from './ThreatAlerts';
import { SecurityMetrics } from './SecurityMetrics';
import { ActiveMonitors } from './ActiveMonitors';
import { SecuritySettings } from './SecuritySettings';
import { SecurityAlert } from '@services/ai/securityMonitoring';

// Import mock data for alerts and metrics
import {
  mockSecurityAlerts as rawMockAlerts,
  securityMetrics as rawSecurityMetrics
} from '@/__mocks__/aiServices/securityMonitor.js';

// Transform mock data to match our types
const mockSecurityAlerts: SecurityAlert[] = rawMockAlerts.map((alert: any) => ({
  id: alert.id,
  type: alert.type,
  severity: alert.severity.toLowerCase() as 'critical' | 'high' | 'medium' | 'low',
  timestamp: alert.timestamp,
  source: alert.source,
  action: alert.status || 'Monitored',
  description: alert.description,
  status: alert.status === 'Investigating' ? 'new' : alert.status === 'Resolved' ? 'resolved' : 'acknowledged'
}));

const securityMetrics = rawSecurityMetrics.map((metric: any) => ({
  metric: metric.metric,
  score: parseInt(metric.value) || 0,
  status: metric.status
}));

interface TabPanelProps {
  children: React.ReactNode;
  value: number;
  index: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
  </div>
);

export const SecurityMonitoringPage: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);

  const {
    stats,
    monitors,
    threats,
    realTimeMonitoring,
    loadStats,
    loadMonitors,
    sortAlerts,
    setRealTimeMonitoring
  } = useSecurityMonitoring();

  // Load data on mount
  useEffect(() => {
    loadStats();
    loadMonitors();
  }, [loadStats, loadMonitors]);

  // Combine and sort alerts
  const allAlerts = sortAlerts([...mockSecurityAlerts, ...threats]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Box>
      {/* Service Header */}
      <SecurityHeader status={stats.status} />

      {/* Quick Stats */}
      <SecurityStatsCards
        threatsBlocked={stats.threatsBlocked}
        securityScore={stats.securityScore}
        activeMonitors={stats.activeMonitors}
        realTimeMonitoring={realTimeMonitoring}
      />

      {/* Service Tabs */}
      <Card sx={{ mt: 4 }}>
        <Tabs
          value={currentTab}
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab
            label={
              <Badge badgeContent={allAlerts.length} color="error">
                Threat Alerts
              </Badge>
            }
            icon={<WarningIcon />}
            iconPosition="start"
          />
          <Tab
            label="Security Metrics"
            icon={<ShieldIcon />}
            iconPosition="start"
          />
          <Tab
            label="Active Monitors"
            icon={<NotificationsIcon />}
            iconPosition="start"
          />
          <Tab
            label="Settings"
            icon={<SettingsIcon />}
            iconPosition="start"
          />
        </Tabs>

        <TabPanel value={currentTab} index={0}>
          <ThreatAlerts alerts={allAlerts} />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          <SecurityMetrics metrics={securityMetrics} />
        </TabPanel>

        <TabPanel value={currentTab} index={2}>
          <ActiveMonitors monitors={monitors} />
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <SecuritySettings
            realTimeMonitoring={realTimeMonitoring}
            onRealTimeMonitoringChange={setRealTimeMonitoring}
          />
        </TabPanel>
      </Card>
    </Box>
  );
};

export default SecurityMonitoringPage;
