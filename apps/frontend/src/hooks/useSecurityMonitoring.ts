/**
 * React Hook for Security Monitoring Service
 * Connects React components to the pure business logic service
 */

import { useState, useCallback, useEffect } from 'react';
import {
  securityMonitoringService,
  SecurityStats,
  SecurityAlert,
  SecurityMonitor,
  SecurityAnalysisResult
} from '@/services/ai/securityMonitoring';

export const useSecurityMonitoring = () => {
  const [stats, setStats] = useState<SecurityStats>({
    threatsBlocked: 0,
    securityScore: 0,
    activeMonitors: 0,
    status: 'good',
    todayThreats: 0,
    criticalAlerts: 0
  });
  const [monitors, setMonitors] = useState<SecurityMonitor[]>([]);
  const [realTimeMonitoring, setRealTimeMonitoring] = useState(true);
  const [threats, setThreats] = useState<SecurityAlert[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  /**
   * Load security statistics
   */
  const loadStats = useCallback(async () => {
    try {
      setError(null);
      const securityStats = await securityMonitoringService.getStats();
      setStats(securityStats);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load security statistics';
      setError(errorMessage);
      console.error('Failed to load security stats:', err);
    }
  }, []);

  /**
   * Load active monitors
   */
  const loadMonitors = useCallback(() => {
    try {
      const activeMonitors = securityMonitoringService.getActiveMonitors();
      setMonitors(activeMonitors);
    } catch (err) {
      console.error('Failed to load monitors:', err);
    }
  }, []);

  /**
   * Analyze content for security threats
   */
  const analyzeContent = useCallback(async (
    content: string,
    options?: { userId?: string; channelId?: string }
  ): Promise<SecurityAnalysisResult | null> => {
    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await securityMonitoringService.analyzeContent(content, options);

      // Refresh stats after analysis
      await loadStats();

      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Security analysis failed';
      setError(errorMessage);
      console.error('Security analysis error:', err);
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  }, [loadStats]);

  /**
   * Get recommendations based on current stats and monitors
   */
  const getRecommendations = useCallback(() => {
    return securityMonitoringService.generateRecommendations(stats, monitors);
  }, [stats, monitors]);

  /**
   * Filter alerts by severity
   */
  const filterAlerts = useCallback((
    alerts: SecurityAlert[],
    minSeverity: 'low' | 'medium' | 'high' | 'critical' = 'low'
  ) => {
    return securityMonitoringService.filterAlertsBySeverity(alerts, minSeverity);
  }, []);

  /**
   * Sort alerts by priority
   */
  const sortAlerts = useCallback((alerts: SecurityAlert[]) => {
    return securityMonitoringService.sortAlerts(alerts);
  }, []);

  /**
   * Simulate real-time threat updates
   */
  useEffect(() => {
    if (!realTimeMonitoring) return;

    const interval = setInterval(() => {
      if (Math.random() > 0.8) {
        const newThreat: SecurityAlert = {
          id: Date.now(),
          type: 'System Scan',
          severity: 'low',
          timestamp: 'Just now',
          source: 'Auto Scanner',
          action: 'Monitored',
          description: 'Routine security check completed',
          status: 'new'
        };
        setThreats(prev => [newThreat, ...prev.slice(0, 4)]);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [realTimeMonitoring]);

  return {
    // State
    stats,
    monitors,
    threats,
    realTimeMonitoring,
    isAnalyzing,
    error,

    // Actions
    loadStats,
    loadMonitors,
    analyzeContent,
    getRecommendations,
    filterAlerts,
    sortAlerts,
    setRealTimeMonitoring,
    clearError: () => setError(null)
  };
};

export default useSecurityMonitoring;
