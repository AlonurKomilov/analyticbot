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

import { useSecurityMonitoring } from '@/hooks/useSecurityMonitoring';
import { SecurityHeader } from './SecurityHeader';
import { SecurityStatsCards } from './SecurityStatsCards';
import { ThreatAlerts } from './ThreatAlerts';
import { SecurityMetrics } from './SecurityMetrics';
import { ActiveMonitors } from './ActiveMonitors';
import { SecuritySettings } from './SecuritySettings';
import { SecurityAlert } from '@/services/ai/securityMonitoring';
import { useDemoMode, loadMockData } from '@/__mocks__/utils/demoGuard';

// Mock data will be loaded dynamically based on demo mode
// No top-level imports to prevent loading in real API mode

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
  const isDemo = useDemoMode();

  // State for dynamically loaded mock data
  const [mockSecurityAlerts, setMockSecurityAlerts] = useState<SecurityAlert[]>([]);
  const [securityMetrics, setSecurityMetrics] = useState<any[]>([]);

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

  // Load data reactively when demo mode changes
  useEffect(() => {
    loadStats();
    loadMonitors();
  }, [loadStats, loadMonitors, isDemo]);

  // Load mock data dynamically only in demo mode
  useEffect(() => {
    const loadDemoData = async () => {
      if (isDemo) {
        const mockModule = await loadMockData(
          () => import('@/__mocks__/aiServices/securityMonitor')
        );

        if (mockModule) {
          // Transform mock data to match our types
          const transformedAlerts: SecurityAlert[] = mockModule.mockSecurityAlerts.map((alert: any) => ({
            id: alert.id,
            type: alert.type,
            severity: alert.severity.toLowerCase() as 'critical' | 'high' | 'medium' | 'low',
            timestamp: alert.timestamp,
            source: alert.source,
            action: alert.status || 'Monitored',
            description: alert.description,
            status: alert.status === 'Investigating' ? 'new' : alert.status === 'Resolved' ? 'resolved' : 'acknowledged'
          }));

          const transformedMetrics = mockModule.securityMetrics.map((metric: any) => ({
            metric: metric.metric,
            score: parseInt(metric.value) || 0,
            status: metric.status
          }));

          setMockSecurityAlerts(transformedAlerts);
          setSecurityMetrics(transformedMetrics);
          console.log('✅ Loaded demo data for Security Monitoring Page');
        }
      } else {
        // Clear mock data in real API mode
        setMockSecurityAlerts([]);
        setSecurityMetrics([]);
        console.log('🔄 Using real API data for Security Monitoring Page');
      }
    };

    loadDemoData();
  }, [isDemo]);

  // Combine and sort alerts (only includes mock alerts in demo mode)
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
