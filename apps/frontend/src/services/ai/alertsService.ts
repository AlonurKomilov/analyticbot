/**
 * Alerts Service
 * Pure business logic for alerts and monitoring - NO React dependencies
 *
 * This service handles:
 * - Live monitoring metrics
 * - Alert checking and management
 * - Competitive monitoring
 * - Comprehensive workflow orchestration
 */

import { AlertsAPI } from '../aiServicesAPI.js';

/**
 * Live monitoring metrics
 */
export interface LiveMonitoringMetrics {
  channelId: string;
  timestamp: string;
  metrics: {
    engagement_rate: number;
    response_time: number;
    error_rate: number;
    active_users: number;
  };
  alerts: Alert[];
  status: 'healthy' | 'warning' | 'critical';
}

/**
 * Alert definition
 */
export interface Alert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  timestamp: string;
  channelId?: string;
  acknowledged?: boolean;
}

/**
 * Alert rule
 */
export interface AlertRule {
  id: string;
  channelId: string;
  name: string;
  condition: string;
  threshold: number;
  enabled: boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

/**
 * Competitive monitoring result
 */
export interface CompetitiveMonitoringResult {
  channelId: string;
  competitors: {
    id: string;
    name: string;
    metrics: Record<string, number>;
    trend: 'up' | 'down' | 'stable';
  }[];
  insights: string[];
  recommendations: string[];
}

/**
 * Comprehensive workflow result
 */
export interface ComprehensiveWorkflowResult {
  channelId: string;
  liveMetrics: any;
  alerts: Alert[];
  competitiveAnalysis?: any;
  status: 'success' | 'partial' | 'failed';
  executionTime: number;
}

/**
 * Alerts Service Class
 */
export class AlertsService {
  /**
   * Get live monitoring metrics for a channel
   */
  async getLiveMonitoring(
    channelId: string,
    hours: number = 6
  ): Promise<LiveMonitoringMetrics> {
    if (!channelId || channelId.trim().length === 0) {
      throw new Error('Channel ID is required');
    }

    try {
      const result = await AlertsAPI.getLiveMonitoring(channelId, hours);

      return {
        channelId: result.channel_id || channelId,
        timestamp: result.timestamp || new Date().toISOString(),
        metrics: result.metrics || {
          engagement_rate: 0,
          response_time: 0,
          error_rate: 0,
          active_users: 0
        },
        alerts: result.alerts || [],
        status: result.status || 'healthy'
      };
    } catch (error) {
      console.error('Live monitoring failed:', error);
      throw new Error('Failed to fetch live monitoring metrics');
    }
  }

  /**
   * Check alerts for a channel
   */
  async checkAlerts(
    channelId: string,
    analysisType: string = 'comprehensive'
  ): Promise<Alert[]> {
    if (!channelId || channelId.trim().length === 0) {
      throw new Error('Channel ID is required');
    }

    try {
      const result = await AlertsAPI.checkAlerts(channelId, analysisType);
      return result.alerts || [];
    } catch (error) {
      console.error('Alert check failed:', error);
      throw new Error('Failed to check alerts');
    }
  }

  /**
   * Get competitive monitoring analysis
   */
  async getCompetitiveMonitoring(
    channelId: string,
    options: {
      days?: number;
      includeCompetitors?: boolean;
      thresholds?: Record<string, number>;
    } = {}
  ): Promise<CompetitiveMonitoringResult> {
    if (!channelId || channelId.trim().length === 0) {
      throw new Error('Channel ID is required');
    }

    try {
      const result = await AlertsAPI.competitiveMonitoring(channelId, options);

      return {
        channelId: result.channel_id || channelId,
        competitors: result.competitors || [],
        insights: result.insights || [],
        recommendations: result.recommendations || []
      };
    } catch (error) {
      console.error('Competitive monitoring failed:', error);
      throw new Error('Failed to fetch competitive monitoring');
    }
  }

  /**
   * Execute comprehensive workflow
   */
  async executeComprehensiveWorkflow(
    channelId: string,
    includeCompetitive: boolean = true
  ): Promise<ComprehensiveWorkflowResult> {
    if (!channelId || channelId.trim().length === 0) {
      throw new Error('Channel ID is required');
    }

    const startTime = Date.now();

    try {
      const result = await AlertsAPI.comprehensiveWorkflow(channelId, includeCompetitive);

      return {
        channelId: result.channel_id || channelId,
        liveMetrics: result.live_metrics || {},
        alerts: result.alerts || [],
        competitiveAnalysis: result.competitive_analysis,
        status: result.status || 'success',
        executionTime: Date.now() - startTime
      };
    } catch (error) {
      console.error('Comprehensive workflow failed:', error);
      throw new Error('Failed to execute comprehensive workflow');
    }
  }

  /**
   * Get alert rules for a channel
   */
  async getAlertRules(channelId: string): Promise<AlertRule[]> {
    if (!channelId || channelId.trim().length === 0) {
      throw new Error('Channel ID is required');
    }

    try {
      const result = await AlertsAPI.getAlertRules(channelId);
      return result.rules || [];
    } catch (error) {
      console.error('Failed to fetch alert rules:', error);
      throw new Error('Failed to load alert rules');
    }
  }

  /**
   * Get alert history for a channel
   */
  async getAlertHistory(channelId: string, days: number = 30): Promise<Alert[]> {
    if (!channelId || channelId.trim().length === 0) {
      throw new Error('Channel ID is required');
    }

    try {
      const result = await AlertsAPI.getAlertHistory(channelId, days);
      return result.history || [];
    } catch (error) {
      console.error('Failed to fetch alert history:', error);
      throw new Error('Failed to load alert history');
    }
  }

  /**
   * Check service health
   */
  async healthCheck(): Promise<{
    status: string;
    services: Record<string, string>;
  }> {
    try {
      const result = await AlertsAPI.healthCheck();
      return {
        status: result.status || 'unknown',
        services: result.coordinated_services || {}
      };
    } catch (error) {
      console.error('Health check failed:', error);
      return {
        status: 'unavailable',
        services: {}
      };
    }
  }

  /**
   * Get service statistics
   */
  async getStats(): Promise<any> {
    try {
      return await AlertsAPI.getStats();
    } catch (error) {
      console.error('Failed to fetch stats:', error);
      throw new Error('Failed to load service statistics');
    }
  }

  /**
   * Count active alerts by severity
   */
  countAlertsBySeverity(alerts: Alert[]): Record<string, number> {
    const counts: Record<string, number> = {
      info: 0,
      warning: 0,
      error: 0,
      critical: 0
    };

    alerts.forEach(alert => {
      if (counts[alert.type] !== undefined) {
        counts[alert.type]++;
      }
    });

    return counts;
  }

  /**
   * Get most critical alert
   */
  getMostCriticalAlert(alerts: Alert[]): Alert | null {
    if (alerts.length === 0) return null;

    const severityOrder = { critical: 4, error: 3, warning: 2, info: 1 };

    return alerts.reduce((mostCritical, alert) => {
      const currentSeverity = severityOrder[alert.type] || 0;
      const mostCriticalSeverity = severityOrder[mostCritical.type] || 0;
      return currentSeverity > mostCriticalSeverity ? alert : mostCritical;
    });
  }

  /**
   * Filter alerts by type
   */
  filterAlertsByType(alerts: Alert[], type: Alert['type']): Alert[] {
    return alerts.filter(alert => alert.type === type);
  }

  /**
   * Format alert timestamp for display
   */
  formatAlertTime(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  }

  /**
   * Get status color for UI
   */
  getStatusColor(status: string): string {
    const colors: Record<string, string> = {
      healthy: 'green',
      warning: 'yellow',
      critical: 'red',
      unknown: 'gray'
    };
    return colors[status] || 'gray';
  }

  /**
   * Validate alert rule
   */
  validateAlertRule(rule: Partial<AlertRule>): {
    valid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!rule.name || rule.name.trim().length === 0) {
      errors.push('Alert rule name is required');
    }

    if (!rule.condition || rule.condition.trim().length === 0) {
      errors.push('Alert condition is required');
    }

    if (rule.threshold !== undefined && rule.threshold < 0) {
      errors.push('Threshold must be a positive number');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }
}

// Export singleton instance
export const alertsService = new AlertsService();

export default alertsService;
