/**
 * useAlerts Hook
 * React hook for managing alerts and monitoring using the new AlertsAPI
 */

import { useState, useEffect, useCallback } from 'react';
import { alertsService, Alert, AlertRule, LiveMonitoringMetrics } from '@features/ai-services/services';

export interface UseAlertsOptions {
  channelId?: string;
  autoFetch?: boolean;
  refreshInterval?: number; // in milliseconds
}

export interface UseAlertsReturn {
  // Data
  alerts: Alert[];
  alertRules: AlertRule[];
  liveMetrics: LiveMonitoringMetrics | null;

  // Loading states
  loading: boolean;
  loadingAlerts: boolean;
  loadingRules: boolean;
  loadingMetrics: boolean;

  // Error states
  error: string | null;

  // Actions
  fetchAlerts: (channelId: string) => Promise<void>;
  fetchAlertRules: (channelId: string) => Promise<void>;
  fetchLiveMetrics: (channelId: string, hours?: number) => Promise<void>;
  executeComprehensiveWorkflow: (channelId: string, includeCompetitive?: boolean) => Promise<any>;
  checkHealth: () => Promise<any>;

  // Utilities
  countAlertsBySeverity: () => Record<string, number>;
  getMostCriticalAlert: () => Alert | null;
  filterAlertsByType: (type: Alert['type']) => Alert[];
  refresh: () => Promise<void>;
}

/**
 * useAlerts Hook
 * Provides alert management functionality
 */
export function useAlerts(options: UseAlertsOptions = {}): UseAlertsReturn {
  const { channelId: initialChannelId, autoFetch = false, refreshInterval } = options;

  // State
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [liveMetrics, setLiveMetrics] = useState<LiveMonitoringMetrics | null>(null);

  const [loading, setLoading] = useState(false);
  const [loadingAlerts, setLoadingAlerts] = useState(false);
  const [loadingRules, setLoadingRules] = useState(false);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch alerts for a channel
   */
  const fetchAlerts = useCallback(async (channelId: string) => {
    if (!channelId) {
      setError('Channel ID is required');
      return;
    }

    setLoadingAlerts(true);
    setError(null);

    try {
      const result = await alertsService.checkAlerts(channelId, 'comprehensive');
      setAlerts(result);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch alerts';
      setError(errorMessage);
      console.error('Failed to fetch alerts:', err);
    } finally {
      setLoadingAlerts(false);
    }
  }, []);

  /**
   * Fetch alert rules for a channel
   */
  const fetchAlertRules = useCallback(async (channelId: string) => {
    if (!channelId) {
      setError('Channel ID is required');
      return;
    }

    setLoadingRules(true);
    setError(null);

    try {
      const rules = await alertsService.getAlertRules(channelId);
      setAlertRules(rules);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch alert rules';
      setError(errorMessage);
      console.error('Failed to fetch alert rules:', err);
    } finally {
      setLoadingRules(false);
    }
  }, []);

  /**
   * Fetch live monitoring metrics
   */
  const fetchLiveMetrics = useCallback(async (channelId: string, hours: number = 6) => {
    if (!channelId) {
      setError('Channel ID is required');
      return;
    }

    setLoadingMetrics(true);
    setError(null);

    try {
      const metrics = await alertsService.getLiveMonitoring(channelId, hours);
      setLiveMetrics(metrics);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch live metrics';
      setError(errorMessage);
      console.error('Failed to fetch live metrics:', err);
    } finally {
      setLoadingMetrics(false);
    }
  }, []);

  /**
   * Execute comprehensive workflow
   */
  const executeComprehensiveWorkflow = useCallback(async (
    channelId: string,
    includeCompetitive: boolean = true
  ) => {
    if (!channelId) {
      throw new Error('Channel ID is required');
    }

    setLoading(true);
    setError(null);

    try {
      const result = await alertsService.executeComprehensiveWorkflow(channelId, includeCompetitive);

      // Update state with workflow results
      if (result.alerts) {
        setAlerts(result.alerts);
      }
      if (result.liveMetrics) {
        setLiveMetrics(result.liveMetrics);
      }

      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Workflow execution failed';
      setError(errorMessage);
      console.error('Workflow execution failed:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Check service health
   */
  const checkHealth = useCallback(async () => {
    try {
      return await alertsService.healthCheck();
    } catch (err) {
      console.error('Health check failed:', err);
      return { status: 'unavailable', services: {} };
    }
  }, []);

  /**
   * Refresh all data for current channel
   */
  const refresh = useCallback(async () => {
    if (!initialChannelId) {
      console.warn('No channel ID provided for refresh');
      return;
    }

    setLoading(true);

    await Promise.all([
      fetchAlerts(initialChannelId),
      fetchAlertRules(initialChannelId),
      fetchLiveMetrics(initialChannelId)
    ]);

    setLoading(false);
  }, [initialChannelId, fetchAlerts, fetchAlertRules, fetchLiveMetrics]);

  /**
   * Count alerts by severity
   */
  const countAlertsBySeverity = useCallback(() => {
    return alertsService.countAlertsBySeverity(alerts);
  }, [alerts]);

  /**
   * Get most critical alert
   */
  const getMostCriticalAlert = useCallback(() => {
    return alertsService.getMostCriticalAlert(alerts);
  }, [alerts]);

  /**
   * Filter alerts by type
   */
  const filterAlertsByType = useCallback((type: Alert['type']) => {
    return alertsService.filterAlertsByType(alerts, type);
  }, [alerts]);

  /**
   * Auto-fetch on mount if enabled
   */
  useEffect(() => {
    if (autoFetch && initialChannelId) {
      refresh();
    }
  }, [autoFetch, initialChannelId, refresh]);

  /**
   * Set up refresh interval if specified
   */
  useEffect(() => {
    if (!refreshInterval || !initialChannelId) {
      return;
    }

    const intervalId = setInterval(() => {
      refresh();
    }, refreshInterval);

    return () => clearInterval(intervalId);
  }, [refreshInterval, initialChannelId, refresh]);

  return {
    // Data
    alerts,
    alertRules,
    liveMetrics,

    // Loading states
    loading,
    loadingAlerts,
    loadingRules,
    loadingMetrics,

    // Error
    error,

    // Actions
    fetchAlerts,
    fetchAlertRules,
    fetchLiveMetrics,
    executeComprehensiveWorkflow,
    checkHealth,

    // Utilities
    countAlertsBySeverity,
    getMostCriticalAlert,
    filterAlertsByType,
    refresh
  };
}

export default useAlerts;
