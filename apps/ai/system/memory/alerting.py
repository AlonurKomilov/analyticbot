"""
Alerting System
===============

Integration with the alerting system for AI-generated alerts.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from apps.ai.system.memory.patterns import DetectedPattern, PatternSeverity

logger = logging.getLogger(__name__)


class AlertChannel(str, Enum):
    """Alert delivery channels"""
    TELEGRAM = "telegram"
    EMAIL = "email"
    WEBHOOK = "webhook"
    LOG = "log"
    DATABASE = "database"


class AlertStatus(str, Enum):
    """Alert status"""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AIAlert:
    """AI-generated alert"""
    alert_id: str
    title: str
    message: str
    severity: PatternSeverity
    source: str  # pattern_detector, tool, controller
    
    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime | None = None
    
    # Status
    status: AlertStatus = AlertStatus.PENDING
    
    # Related data
    pattern_id: str | None = None
    worker_name: str | None = None
    metric_name: str | None = None
    
    # Delivery
    channels: list[AlertChannel] = field(default_factory=list)
    sent_to: list[str] = field(default_factory=list)
    
    # Additional context
    context: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity.value,
            "source": self.source,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status.value,
            "pattern_id": self.pattern_id,
            "worker_name": self.worker_name,
            "metric_name": self.metric_name,
            "channels": [c.value for c in self.channels],
            "sent_to": self.sent_to,
            "context": self.context,
            "recommendations": self.recommendations,
        }


class AlertManager:
    """
    Manager for AI-generated alerts.
    
    Responsibilities:
    - Create alerts from patterns
    - Deduplicate similar alerts
    - Route alerts to channels
    - Track alert status
    - Integrate with existing alert system
    """
    
    _instance: "AlertManager | None" = None
    
    def __new__(cls) -> "AlertManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._alerts: dict[str, AIAlert] = {}
        self._recent_patterns: set[str] = set()  # For deduplication
        
        # Default channels by severity
        self._severity_channels = {
            PatternSeverity.CRITICAL: [AlertChannel.TELEGRAM, AlertChannel.DATABASE],
            PatternSeverity.WARNING: [AlertChannel.DATABASE, AlertChannel.LOG],
            PatternSeverity.INFO: [AlertChannel.LOG],
        }
        
        # Suppression settings
        self._suppression_window_minutes = 30
        
        self._initialized = True
        logger.info("🔔 Alert Manager initialized")
    
    def create_from_pattern(self, pattern: DetectedPattern) -> AIAlert | None:
        """
        Create an alert from a detected pattern.
        
        Handles deduplication - won't create duplicate alerts
        for the same pattern within suppression window.
        """
        # Create dedup key
        dedup_key = f"{pattern.pattern_type.value}:{pattern.metric_name}"
        
        if dedup_key in self._recent_patterns:
            logger.debug(f"Suppressing duplicate alert for {dedup_key}")
            return None
        
        # Create alert
        alert = AIAlert(
            alert_id=f"ai_alert_{datetime.utcnow().timestamp()}",
            title=self._generate_title(pattern),
            message=pattern.description,
            severity=pattern.severity,
            source="pattern_detector",
            pattern_id=pattern.pattern_id,
            worker_name=pattern.labels.get("worker"),
            metric_name=pattern.metric_name,
            channels=self._severity_channels.get(
                pattern.severity,
                [AlertChannel.LOG]
            ),
            context={
                "current_value": pattern.current_value,
                "baseline_value": pattern.baseline_value,
                "change_percent": pattern.change_percent,
            },
            recommendations=pattern.recommendations,
        )
        
        # Store and track
        self._alerts[alert.alert_id] = alert
        self._recent_patterns.add(dedup_key)
        
        # Send to channels
        self._send_alert(alert)
        
        return alert
    
    def _generate_title(self, pattern: DetectedPattern) -> str:
        """Generate alert title from pattern"""
        severity_emoji = {
            PatternSeverity.CRITICAL: "🚨",
            PatternSeverity.WARNING: "⚠️",
            PatternSeverity.INFO: "ℹ️",
        }
        
        emoji = severity_emoji.get(pattern.severity, "📢")
        worker = pattern.labels.get("worker", "")
        worker_str = f"[{worker}] " if worker else ""
        
        return f"{emoji} {worker_str}{pattern.pattern_type.value.replace('_', ' ').title()}"
    
    def _send_alert(self, alert: AIAlert):
        """Send alert to configured channels"""
        for channel in alert.channels:
            try:
                if channel == AlertChannel.LOG:
                    self._send_to_log(alert)
                elif channel == AlertChannel.DATABASE:
                    self._send_to_database(alert)
                elif channel == AlertChannel.TELEGRAM:
                    self._send_to_telegram(alert)
                elif channel == AlertChannel.WEBHOOK:
                    self._send_to_webhook(alert)
                
                alert.sent_to.append(channel.value)
                
            except Exception as e:
                logger.error(f"Failed to send alert to {channel.value}: {e}")
        
        alert.status = AlertStatus.SENT
    
    def _send_to_log(self, alert: AIAlert):
        """Send alert to log"""
        log_level = {
            PatternSeverity.CRITICAL: logging.ERROR,
            PatternSeverity.WARNING: logging.WARNING,
            PatternSeverity.INFO: logging.INFO,
        }.get(alert.severity, logging.INFO)
        
        logger.log(
            log_level,
            f"[AI Alert] {alert.title}: {alert.message}"
        )
    
    def _send_to_database(self, alert: AIAlert):
        """Send alert to database (existing alert system)"""
        # TODO: Integrate with existing alert system
        # This would use the AlertService from apps.shared.alerts
        logger.debug(f"Would store alert {alert.alert_id} to database")
    
    def _send_to_telegram(self, alert: AIAlert):
        """Send alert via Telegram"""
        # TODO: Integrate with Telegram bot
        # This would use the bot system to send to admin channel
        logger.debug(f"Would send alert {alert.alert_id} to Telegram")
    
    def _send_to_webhook(self, alert: AIAlert):
        """Send alert to webhook"""
        # TODO: Implement webhook delivery
        logger.debug(f"Would send alert {alert.alert_id} to webhook")
    
    def acknowledge(self, alert_id: str, by: str) -> bool:
        """Acknowledge an alert"""
        alert = self._alerts.get(alert_id)
        if not alert:
            return False
        
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.context["acknowledged_by"] = by
        alert.context["acknowledged_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Alert {alert_id} acknowledged by {by}")
        return True
    
    def resolve(self, alert_id: str, resolution: str | None = None) -> bool:
        """Resolve an alert"""
        alert = self._alerts.get(alert_id)
        if not alert:
            return False
        
        alert.status = AlertStatus.RESOLVED
        alert.context["resolved_at"] = datetime.utcnow().isoformat()
        if resolution:
            alert.context["resolution"] = resolution
        
        logger.info(f"Alert {alert_id} resolved")
        return True
    
    def get_active_alerts(self) -> list[AIAlert]:
        """Get all active (non-resolved) alerts"""
        return [
            alert for alert in self._alerts.values()
            if alert.status not in [AlertStatus.RESOLVED, AlertStatus.SUPPRESSED]
        ]
    
    def get_alert(self, alert_id: str) -> AIAlert | None:
        """Get alert by ID"""
        return self._alerts.get(alert_id)
    
    def get_alerts_for_worker(self, worker_name: str) -> list[AIAlert]:
        """Get alerts for a specific worker"""
        return [
            alert for alert in self._alerts.values()
            if alert.worker_name == worker_name
        ]
    
    def clear_suppression_cache(self):
        """Clear pattern suppression cache (for testing)"""
        self._recent_patterns.clear()
    
    def get_stats(self) -> dict[str, Any]:
        """Get alert manager statistics"""
        by_status = {}
        by_severity = {}
        
        for alert in self._alerts.values():
            status = alert.status.value
            severity = alert.severity.value
            
            by_status[status] = by_status.get(status, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "total_alerts": len(self._alerts),
            "active_alerts": len(self.get_active_alerts()),
            "by_status": by_status,
            "by_severity": by_severity,
            "suppression_cache_size": len(self._recent_patterns),
        }


def get_alert_manager() -> AlertManager:
    """Get the global alert manager instance"""
    return AlertManager()


def create_alert_from_pattern(pattern: DetectedPattern) -> AIAlert | None:
    """Convenience function to create alert from pattern"""
    return get_alert_manager().create_from_pattern(pattern)
