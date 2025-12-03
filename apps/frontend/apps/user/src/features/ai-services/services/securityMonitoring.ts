/**
 * Security Monitoring Service
 * Pure business logic for security threat detection and monitoring - NO React dependencies
 *
 * This service handles:
 * - Threat detection and analysis
 * - Security score calculation
 * - Monitor status management
 * - Alert generation and filtering
 */

import { SecurityMonitorAPI, AIServicesAPI } from '@features/ai-services/api';

/**
 * Security alert type
 */
export interface SecurityAlert {
  id: string | number;
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  timestamp: string;
  source: string;
  action: string;
  description: string;
  status?: 'new' | 'acknowledged' | 'resolved';
}

/**
 * Security monitor status
 */
export interface SecurityMonitor {
  name: string;
  status: 'active' | 'maintenance' | 'offline';
  lastUpdate: string;
  type?: string;
}

/**
 * Security statistics
 */
export interface SecurityStats {
  threatsBlocked: number;
  securityScore: number;
  activeMonitors: number;
  status: 'excellent' | 'good' | 'needs-attention' | 'poor';
  todayThreats: number;
  criticalAlerts: number;
}

/**
 * Security metrics
 */
export interface SecurityMetrics {
  firewallStatus: 'enabled' | 'disabled';
  encryptionLevel: string;
  lastScan: string;
  vulnerabilities: number;
  uptime: string;
}

/**
 * Content analysis result for security
 */
export interface SecurityAnalysisResult {
  safe: boolean;
  threats: string[];
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  recommendations: string[];
  score: number;
}

/**
 * Security Monitoring Service Class
 */
export class SecurityMonitoringService {
  /**
   * Analyze content for security threats
   */
  async analyzeContent(
    content: string,
    options: { userId?: string; channelId?: string } = {}
  ): Promise<SecurityAnalysisResult> {
    if (!content || content.trim().length === 0) {
      throw new Error('Content cannot be empty');
    }

    try {
      const result = await SecurityMonitorAPI.analyzeContent(content, options);

      return {
        safe: result.safe || false,
        threats: result.threats || [],
        riskLevel: result.risk_level || 'low',
        recommendations: result.recommendations || [],
        score: result.security_score || 0
      };
    } catch (error) {
      console.error('Security analysis failed:', error);
      throw new Error('Failed to analyze content for security threats');
    }
  }

  /**
   * Get security service statistics
   */
  async getStats(): Promise<SecurityStats> {
    try {
      const stats = await AIServicesAPI.getAllStats();
      const securityStats = stats.security_monitor || {};

      return {
        threatsBlocked: securityStats.threats_blocked || 0,
        securityScore: securityStats.security_score || 0,
        activeMonitors: securityStats.active_monitors || 0,
        status: this.calculateStatus(securityStats.security_score),
        todayThreats: securityStats.today_threats || 0,
        criticalAlerts: securityStats.critical_alerts || 0
      };
    } catch (error) {
      console.error('Failed to fetch security stats:', error);
      throw new Error('Failed to load security statistics');
    }
  }

  /**
   * Get active security monitors
   */
  getActiveMonitors(): SecurityMonitor[] {
    return [
      { name: 'Brute Force Detection', status: 'active', lastUpdate: '30s ago', type: 'authentication' },
      { name: 'SQL Injection Scanner', status: 'active', lastUpdate: '45s ago', type: 'database' },
      { name: 'DDoS Protection', status: 'active', lastUpdate: '1m ago', type: 'network' },
      { name: 'Malware Scanner', status: 'active', lastUpdate: '2m ago', type: 'content' },
      { name: 'Anomaly Detection', status: 'active', lastUpdate: '3m ago', type: 'behavior' },
      { name: 'Data Leak Monitor', status: 'maintenance', lastUpdate: '5m ago', type: 'privacy' }
    ];
  }

  /**
   * Calculate security status based on score
   */
  calculateStatus(score: number): 'excellent' | 'good' | 'needs-attention' | 'poor' {
    if (score >= 90) return 'excellent';
    if (score >= 75) return 'good';
    if (score >= 50) return 'needs-attention';
    return 'poor';
  }

  /**
   * Get severity color for UI
   */
  getSeverityLevel(severity: string): {
    color: 'error' | 'warning' | 'info' | 'success' | 'default';
    priority: number;
  } {
    const levels = {
      critical: { color: 'error' as const, priority: 4 },
      high: { color: 'warning' as const, priority: 3 },
      medium: { color: 'info' as const, priority: 2 },
      low: { color: 'success' as const, priority: 1 }
    };
    return levels[severity as keyof typeof levels] || { color: 'default' as const, priority: 0 };
  }

  /**
   * Filter alerts by severity
   */
  filterAlertsBySeverity(
    alerts: SecurityAlert[],
    minSeverity: 'low' | 'medium' | 'high' | 'critical' = 'low'
  ): SecurityAlert[] {
    const severityOrder = { low: 1, medium: 2, high: 3, critical: 4 };
    const minLevel = severityOrder[minSeverity];

    return alerts.filter(alert =>
      severityOrder[alert.severity] >= minLevel
    );
  }

  /**
   * Sort alerts by severity and timestamp
   */
  sortAlerts(alerts: SecurityAlert[]): SecurityAlert[] {
    return [...alerts].sort((a, b) => {
      const aSeverity = this.getSeverityLevel(a.severity).priority;
      const bSeverity = this.getSeverityLevel(b.severity).priority;

      if (aSeverity !== bSeverity) {
        return bSeverity - aSeverity; // Higher severity first
      }

      // If same severity, sort by timestamp (newest first)
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });
  }

  /**
   * Generate security recommendations
   */
  generateRecommendations(stats: SecurityStats, monitors: SecurityMonitor[]): string[] {
    const recommendations: string[] = [];

    if (stats.securityScore < 75) {
      recommendations.push('Security score is below optimal. Review and address security alerts.');
    }

    if (stats.criticalAlerts > 0) {
      recommendations.push(`You have ${stats.criticalAlerts} critical alerts requiring immediate attention.`);
    }

    const offlineMonitors = monitors.filter(m => m.status === 'offline');
    if (offlineMonitors.length > 0) {
      recommendations.push(`${offlineMonitors.length} security monitor(s) are offline. Restore them immediately.`);
    }

    const maintenanceMonitors = monitors.filter(m => m.status === 'maintenance');
    if (maintenanceMonitors.length > 0) {
      recommendations.push(`${maintenanceMonitors.length} monitor(s) in maintenance mode.`);
    }

    if (stats.todayThreats > 10) {
      recommendations.push('High threat activity detected today. Consider increasing security measures.');
    }

    if (recommendations.length === 0) {
      recommendations.push('All security systems operating normally. Continue monitoring.');
    }

    return recommendations;
  }

  /**
   * Validate alert data
   */
  validateAlert(alert: Partial<SecurityAlert>): {
    valid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (!alert.type) {
      errors.push('Alert type is required');
    }

    if (!alert.severity || !['low', 'medium', 'high', 'critical'].includes(alert.severity)) {
      errors.push('Invalid severity level');
    }

    if (!alert.description || alert.description.trim().length === 0) {
      errors.push('Alert description is required');
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Calculate threat trend
   */
  calculateThreatTrend(
    currentThreats: number,
    previousThreats: number
  ): {
    trend: 'increasing' | 'decreasing' | 'stable';
    percentage: number;
  } {
    if (previousThreats === 0) {
      return { trend: 'stable', percentage: 0 };
    }

    const change = ((currentThreats - previousThreats) / previousThreats) * 100;

    if (Math.abs(change) < 5) {
      return { trend: 'stable', percentage: change };
    }

    return {
      trend: change > 0 ? 'increasing' : 'decreasing',
      percentage: Math.abs(change)
    };
  }
}

// Export singleton instance
export const securityMonitoringService = new SecurityMonitoringService();

export default securityMonitoringService;
