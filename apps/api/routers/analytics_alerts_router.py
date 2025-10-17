"""
Analytics Alerts Router - Alert Management Domain
=================================================

Analytics alerts router providing comprehensive alert management.
Handles alert checking, rule management, and notification systems

Domain: Analytics alerting, monitoring, and notification management
Path: /analytics/alerts/*
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from apps.api.middleware.auth import get_current_user

# Services
from apps.di import (
    get_alert_condition_evaluator,
    get_alert_event_manager,
    get_alert_rule_manager,
    get_telegram_alert_notifier,
)
from apps.shared.clients.analytics_client import AnalyticsClient
from apps.shared.models.alerts import AlertEvent
from core.services.bot.alerts import (
    AlertConditionEvaluator,
    AlertEventManager,
    AlertRuleManager,
)

logger = logging.getLogger(__name__)

# Create alerts router
router = APIRouter(prefix="/analytics/alerts", tags=["Analytics Alerts"])

# === ALERT MODELS ===


class AlertCheckResponse(BaseModel):
    channel_id: str
    alerts: list[AlertEvent]
    check_timestamp: datetime
    next_check: datetime
    alert_count: int


class AlertRuleRequest(BaseModel):
    rule_name: str
    metric_type: str  # 'growth', 'engagement', 'views'
    threshold_value: float
    comparison: str  # 'above', 'below', 'equals'
    enabled: bool = True
    notification_channels: list[str] = []


class AlertHistoryResponse(BaseModel):
    channel_id: str
    alerts: list[AlertEvent]
    period: str
    total_alerts: int
    alert_types: dict[str, int]


# === DEPENDENCY INJECTION ===


def get_analytics_client() -> AnalyticsClient:
    """Get analytics client for alert data"""
    from config import settings

    return AnalyticsClient(settings.ANALYTICS_V2_BASE_URL)


def get_alert_services() -> dict[str, Any]:
    """
    Get alert services from DI container

    Returns dict with:
    - condition_evaluator: AlertConditionEvaluator
    - rule_manager: AlertRuleManager
    - event_manager: AlertEventManager
    - notifier: TelegramAlertNotifier
    """
    return {
        "condition_evaluator": get_alert_condition_evaluator(),
        "rule_manager": get_alert_rule_manager(),
        "event_manager": get_alert_event_manager(),
        "notifier": get_telegram_alert_notifier(),
    }


# === ALERT CHECKING ===


@router.get("/check/{channel_id}", response_model=AlertCheckResponse)
async def check_channel_alerts(
    channel_id: int,
    check_period: int = Query(default=1, ge=1, le=7, description="Period to check in days"),
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
    alert_services: dict[str, Any] = Depends(get_alert_services),
):
    """
    ## 🚨 Check Channel Alerts

    Check for active alerts on a channel based on:
    - Growth rate thresholds
    - Engagement rate limits
    - View count anomalies
    - Performance degradation

    **Returns**: List of active alerts with severity and recommendations
    """
    try:
        condition_evaluator: AlertConditionEvaluator = alert_services["condition_evaluator"]

        # Get current metrics for alert evaluation
        overview_data = await analytics_client.overview(str(channel_id), check_period)
        growth_data = await analytics_client.growth(str(channel_id), check_period)
        reach_data = await analytics_client.reach(str(channel_id), check_period)

        # Build metrics for alert checking
        combined_metrics = {
            "channel_id": channel_id,
            "total_views": getattr(overview_data, "total_views", 0),
            "growth_rate": getattr(growth_data, "growth_rate", 0),
            "engagement_rate": getattr(overview_data, "engagement_rate", 0),
            "reach_score": getattr(reach_data, "reach_score", 0),
            "unique_viewers": getattr(reach_data, "unique_viewers", 0),
            "timestamp": datetime.utcnow(),
        }

        # Check alert conditions using new service
        alerts = await condition_evaluator.check_alert_conditions(
            channel_id=str(channel_id), metrics=combined_metrics
        )

        # Calculate next check time (usually 15-30 minutes for alerts)
        next_check = datetime.utcnow() + timedelta(minutes=15)

        return AlertCheckResponse(
            channel_id=str(channel_id),
            alerts=alerts,
            check_timestamp=datetime.utcnow(),
            next_check=next_check,
            alert_count=len(alerts),
        )

    except Exception as e:
        logger.error(f"Alert checking failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to check channel alerts")


# === ALERT RULE MANAGEMENT ===


@router.post("/rules/{channel_id}")
async def create_alert_rule(
    channel_id: int,
    alert_rule: AlertRuleRequest,
    current_user: dict = Depends(get_current_user),
    alert_services: dict[str, Any] = Depends(get_alert_services),
):
    """
    ## ⚙️ Create Alert Rule

    Create custom alert rules for channel monitoring:
    - Threshold-based alerts (growth, engagement, views)
    - Custom notification channels
    - Alert severity levels
    """
    try:
        rule_manager: AlertRuleManager = alert_services["rule_manager"]

        # Create alert rule using new service
        rule_id = await rule_manager.create_rule(
            channel_id=str(channel_id),
            name=alert_rule.rule_name,
            metric_type=alert_rule.metric_type,
            condition=alert_rule.comparison,
            threshold=alert_rule.threshold_value,
            severity="medium",  # Default severity
            enabled=alert_rule.enabled,
        )

        return {
            "rule_id": rule_id,
            "channel_id": channel_id,
            "status": "created",
            "rule_name": alert_rule.rule_name,
            "enabled": alert_rule.enabled,
            "created_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Alert rule creation failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alert rule")


@router.get("/rules/{channel_id}")
async def get_alert_rules(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    alert_services: dict[str, Any] = Depends(get_alert_services),
):
    """Get all alert rules for a channel"""
    try:
        rule_manager: AlertRuleManager = alert_services["rule_manager"]
        rules = await rule_manager.get_channel_rules(channel_id=str(channel_id))

        return {
            "channel_id": channel_id,
            "rules": rules,
            "total_rules": len(rules),
            "active_rules": len([r for r in rules if r.get("enabled", False)]),
        }

    except Exception as e:
        logger.error(f"Alert rules fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alert rules")


@router.put("/rules/{channel_id}/{rule_id}")
async def update_alert_rule(
    channel_id: int,
    rule_id: str,
    alert_rule: AlertRuleRequest,
    current_user: dict = Depends(get_current_user),
    alert_services: dict[str, Any] = Depends(get_alert_services),
):
    """Update an existing alert rule"""
    try:
        rule_manager: AlertRuleManager = alert_services["rule_manager"]
        success = await rule_manager.update_rule(
            rule_id=rule_id,
            updates={
                "threshold": alert_rule.threshold_value,
                "enabled": alert_rule.enabled,
            },
        )

        if not success:
            raise HTTPException(status_code=404, detail="Alert rule not found")

        return {
            "rule_id": rule_id,
            "channel_id": channel_id,
            "status": "updated",
            "updated_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Alert rule update failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to update alert rule")


@router.delete("/rules/{channel_id}/{rule_id}")
async def delete_alert_rule(
    channel_id: int,
    rule_id: str,
    current_user: dict = Depends(get_current_user),
    alert_services: dict[str, Any] = Depends(get_alert_services),
):
    """Delete an alert rule"""
    try:
        rule_manager: AlertRuleManager = alert_services["rule_manager"]
        success = await rule_manager.delete_rule(
            rule_id=rule_id,
            channel_id=str(channel_id),
        )

        if not success:
            raise HTTPException(status_code=404, detail="Alert rule not found")

        return {
            "rule_id": rule_id,
            "channel_id": channel_id,
            "status": "deleted",
            "deleted_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Alert rule deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete alert rule")


# === ALERT HISTORY ===


@router.get("/history/{channel_id}", response_model=AlertHistoryResponse)
async def get_alert_history(
    channel_id: int,
    period: int = Query(default=30, ge=1, le=365, description="Period in days"),
    alert_type: str | None = Query(default=None, description="Filter by alert type"),
    current_user: dict = Depends(get_current_user),
    alert_services: dict[str, Any] = Depends(get_alert_services),
):
    """
    ## 📚 Alert History

    Get historical alert data for analysis:
    - Alert frequency patterns
    - Alert type distribution
    - Resolution tracking
    - Performance impact correlation
    """
    try:
        event_manager: AlertEventManager = alert_services["event_manager"]

        # Get alert history for channel
        alerts = await event_manager.get_alert_history(
            channel_id=str(channel_id),
            limit=1000,
        )

        # Analyze alert types by severity
        alert_types = {}
        for alert in alerts:
            severity = alert.get("severity", "unknown")
            alert_types[severity] = alert_types.get(severity, 0) + 1

        # Convert dict alerts to AlertEvent objects for response
        alert_events = [
            AlertEvent(
                id=a.get("id", ""),
                rule_id=a.get("rule_id", ""),
                triggered_at=a.get("triggered_at", datetime.utcnow()),
                severity=a.get("severity", "medium"),
                message=a.get("message", ""),
                metric_value=a.get("metric_value", 0.0),
                threshold=a.get("threshold", 0.0),
                channel_id=str(channel_id),
            )
            for a in alerts[: min(len(alerts), 100)]  # Limit to 100 for response
        ]

        return AlertHistoryResponse(
            channel_id=str(channel_id),
            alerts=alert_events,
            period=f"{period}d",
            total_alerts=len(alerts),
            alert_types=alert_types,
        )

    except Exception as e:
        logger.error(f"Alert history fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alert history")


# === ALERT STATISTICS ===


@router.get("/stats/{channel_id}")
async def get_alert_statistics(
    channel_id: int,
    period: int = Query(default=30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    alert_services: dict[str, Any] = Depends(get_alert_services),
):
    """
    ## 📊 Alert Statistics

    Get comprehensive alert statistics:
    - Alert frequency trends
    - Most common alert types
    - Response time metrics
    - Alert resolution rates
    """
    try:
        event_manager: AlertEventManager = alert_services["event_manager"]

        # Get alert statistics
        stats = await event_manager.get_alert_statistics(channel_id=str(channel_id))

        return {
            "channel_id": channel_id,
            "period": f"{period}d",
            "statistics": stats,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Alert statistics fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alert statistics")


# === NOTIFICATION MANAGEMENT ===


@router.post("/notifications/{channel_id}/test")
async def test_alert_notification(
    channel_id: int,
    notification_channel: str = Query(description="Notification channel to test"),
    current_user: dict = Depends(get_current_user),
    alert_services: dict[str, Any] = Depends(get_alert_services),
):
    """Test alert notification delivery"""
    try:
        from apps.bot.adapters.alert_adapters import TelegramAlertNotifier

        notifier: TelegramAlertNotifier = alert_services["notifier"]

        # Send test alert notification
        test_notification = {
            "channel_id": str(channel_id),
            "message": "🔔 Test Alert: This is a test notification from AnalyticBot",
            "severity": "info",
            "metric_value": 100.0,
            "threshold": 90.0,
        }
        await notifier.send_alert(notification=test_notification)

        return {
            "channel_id": channel_id,
            "notification_channel": notification_channel,
            "test_status": "success",
            "sent_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Alert notification test failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to test alert notification")
