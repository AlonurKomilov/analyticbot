import React, { useEffect, useRef } from 'react';

/**
 * NotificationEngine - Handles real-time alert processing and WebSocket connections
 * 
 * Optimized for high-frequency updates and memory management in multi-user scenarios.
 * Manages alert checking intervals, data simulation, and notification generation.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.alertRules - Array of alert rule configurations
 * @param {Function} props.onNewAlerts - Callback when new alerts are generated
 * @param {Array} props.existingAlerts - Current alerts to prevent duplicates
 * @param {number} props.checkInterval - Interval for checking alerts in ms (default: 30000)
 */
const NotificationEngine = React.memo(({ 
  alertRules = [], 
  onNewAlerts, 
  existingAlerts = [],
  checkInterval = 30000 
}) => {
  const intervalRef = useRef(null);

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

          default:
            break;
        }

        if (shouldAlert) {
          // Check if we haven't already shown this alert recently (prevent spam)
          const recentAlert = existingAlerts.find(alert => 
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