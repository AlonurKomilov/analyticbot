import React, { useEffect, useRef } from 'react';

interface AlertRule {
  id: string;
  enabled: boolean;
  type: 'growth' | 'engagement' | 'subscribers' | 'views';
  condition: 'greater_than' | 'less_than' | 'milestone' | 'surge';
  threshold: number;
  name: string;
  color?: string;
  icon?: string;
}

interface Alert {
  id: string;
  ruleId: string;
  title: string;
  message: string;
  type?: string;
  timestamp: string;
  icon?: string;
  read: boolean;
}

interface NotificationEngineProps {
  alertRules?: AlertRule[];
  onNewAlerts?: (alerts: Alert[]) => void;
  existingAlerts?: Alert[];
  checkInterval?: number;
}

/**
 * NotificationEngine - Handles real-time alert processing and WebSocket connections
 *
 * Optimized for high-frequency updates and memory management in multi-user scenarios.
 * Manages alert checking intervals, data simulation, and notification generation.
 */
const NotificationEngine: React.FC<NotificationEngineProps> = React.memo(({
  alertRules = [],
  onNewAlerts,
  existingAlerts = [],
  checkInterval = 30000
}) => {
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Alert checking logic
  const checkAlerts = React.useCallback(async () => {
    try {
      // In a real implementation, this would fetch actual analytics data
      // For now, simulate with random conditions to demonstrate functionality
      const simulatedData = {
        growth_rate: Math.random() * 25, // 0-25%
        engagement_rate: Math.random() * 10, // 0-10%
        subscribers: 850 + Math.floor(Math.random() * 200), // 850-1050
        views: 5000 + Math.floor(Math.random() * 3000), // 5000-8000
      };

      const newAlerts: Alert[] = [];
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

          default:
            break;
        }

        if (shouldAlert) {
          // Check if we haven't already shown this alert recently (prevent spam)
          const recentAlert = existingAlerts.find(alert =>
            alert.ruleId === rule.id &&
            (currentTime.getTime() - new Date(alert.timestamp).getTime()) < 300000 // 5 minutes
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
        onNewAlerts?.(newAlerts);
      }
    } catch (error) {
      console.error('NotificationEngine: Error checking alerts:', error);
    }
  }, [alertRules, existingAlerts, onNewAlerts]);

  // Setup and cleanup intervals
  useEffect(() => {
    if (alertRules.length === 0) return;

    // Initial check
    checkAlerts();

    // Setup interval for continuous checking
    intervalRef.current = setInterval(checkAlerts, checkInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [checkAlerts, checkInterval, alertRules.length]);

  // This component doesn't render anything - it's purely functional
  return null;
});

NotificationEngine.displayName = 'NotificationEngine';

export default NotificationEngine;
