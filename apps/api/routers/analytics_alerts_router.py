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

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from apps.api.middleware.auth import get_current_user

# Services
from apps.shared.clients.analytics_client import AnalyticsClient
# FIXME: AlertingService is deprecated and removed. Need to migrate to new alert services
# from apps.bot.services.alerting_service import AlertingService
from apps.shared.models.alerts import AlertEvent, AlertRule
from typing import Any

logger = logging.getLogger(__name__)


# Temporary stub until alert services are properly migrated
class AlertingServiceStub:
    """Temporary stub for deprecated AlertingService"""

    def __init__(self):
        logger.warning("Using AlertingService stub - alerts functionality disabled until migration")

    async def check_alert_conditions(self, *args: Any, **kwargs: Any) -> list[Any]:
        """Stub for checking alert conditions"""
        return []

    async def create_alert_rule(self, *args: Any, **kwargs: Any) -> str:
        """Stub for creating alert rule"""
        raise HTTPException(status_code=501, detail="Alert rule creation not yet migrated")

    async def get_channel_alert_rules(self, *args: Any, **kwargs: Any) -> list[Any]:
        """Stub for getting channel alert rules"""
        return []

    async def update_alert_rule(self, *args: Any, **kwargs: Any) -> bool:
        """Stub for updating alert rule"""
        raise HTTPException(status_code=501, detail="Alert rule update not yet migrated")

    async def delete_alert_rule(self, *args: Any, **kwargs: Any) -> bool:
        """Stub for deleting alert rule"""
        raise HTTPException(status_code=501, detail="Alert rule deletion not yet migrated")

    async def get_alert_history(self, *args: Any, **kwargs: Any) -> list[Any]:
        """Stub for getting alert history"""
        return []

    async def get_alert_statistics(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Stub for getting alert statistics"""
        return {}

    async def send_alert_notification(self, *args: Any, **kwargs: Any) -> bool:
        """Stub for sending alert notification"""
        raise HTTPException(status_code=501, detail="Alert notification sending not yet migrated")

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


def get_alerting_service() -> AlertingServiceStub:
    """Get alerting service - Using temporary stub until migration is complete"""
    # FIXME: AlertingService was deprecated and removed
    # Need to migrate to new alert services from apps.di:
    # - alert_condition_evaluator
    # - alert_rule_manager
    # - alert_event_manager
    # - telegram_alert_notifier
    return AlertingServiceStub()


# === ALERT CHECKING ===


@router.get("/check/{channel_id}", response_model=AlertCheckResponse)
async def check_channel_alerts(
    channel_id: int,
    check_period: int = Query(default=1, ge=1, le=7, description="Period to check in days"),
    current_user: dict = Depends(get_current_user),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
    alerting_service: AlertingServiceStub = Depends(get_alerting_service),
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

        # Check alert conditions
        alerts = await alerting_service.check_alert_conditions(combined_metrics, str(channel_id))

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
    alerting_service: AlertingServiceStub = Depends(get_alerting_service),
):
    """
    ## ⚙️ Create Alert Rule

    Create custom alert rules for channel monitoring:
    - Threshold-based alerts (growth, engagement, views)
    - Custom notification channels
    - Alert severity levels
    """
    try:
        # Create AlertRule object with correct field names
        rule = AlertRule(
            id=f"rule-{channel_id}-{int(datetime.utcnow().timestamp())}",
            channel_id=str(channel_id),
            metric=alert_rule.metric_type,
            condition=alert_rule.comparison,
            threshold=alert_rule.threshold_value,
            enabled=alert_rule.enabled,
            description=alert_rule.rule_name,
        )

        # Save alert rule
        rule_id = await alerting_service.create_alert_rule(rule)

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
    alerting_service: AlertingServiceStub = Depends(get_alerting_service),
):
    """Get all alert rules for a channel"""
    try:
        rules = await alerting_service.get_channel_alert_rules(str(channel_id))

        return {
            "channel_id": channel_id,
            "rules": [rule.dict() for rule in rules],
            "total_rules": len(rules),
            "active_rules": len([r for r in rules if r.enabled]),
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
    alerting_service: AlertingServiceStub = Depends(get_alerting_service),
):
    """Update an existing alert rule"""
    try:
        success = await alerting_service.update_alert_rule(
            rule_id=rule_id, updates=alert_rule.dict()
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
    alerting_service: AlertingServiceStub = Depends(get_alerting_service),
):
    """Delete an alert rule"""
    try:
        success = await alerting_service.delete_alert_rule(rule_id, str(channel_id))

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
    alerting_service: AlertingServiceStub = Depends(get_alerting_service),
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
        from_date = datetime.utcnow() - timedelta(days=period)
        to_date = datetime.utcnow()

        # Get alert history (alert_type filter not supported yet)
        alerts = await alerting_service.get_alert_history(
            channel_id=str(channel_id), from_date=from_date, to_date=to_date
        )

        # Analyze alert types by rule_id (AlertEvent doesn't have alert_type)
        alert_types = {}
        for alert in alerts:
            alert_type_name = alert.rule_id
            alert_types[alert_type_name] = alert_types.get(alert_type_name, 0) + 1

        return AlertHistoryResponse(
            channel_id=str(channel_id),
            alerts=alerts,
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
    alerting_service: AlertingServiceStub = Depends(get_alerting_service),
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
        from_date = datetime.utcnow() - timedelta(days=period)

        # Get alert statistics
        stats = await alerting_service.get_alert_statistics(
            channel_id=str(channel_id), period_days=period
        )

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
    alerting_service: AlertingServiceStub = Depends(get_alerting_service),
):
    """Test alert notification delivery"""
    try:
        # Create test notification with correct model
        from apps.shared.models.alerts import AlertNotification

        test_notification = AlertNotification(
            id=f"test-{int(datetime.utcnow().timestamp())}",
            rule_id="test-rule",
            title="Test Alert",
            message="This is a test alert notification",
            triggered_value=0.0,
            threshold=0.0,
            channel_id=str(channel_id),
            timestamp=datetime.utcnow(),
            severity="info",
        )

        # Send test notification
        success = await alerting_service.send_alert_notification(
            notification=test_notification
        )

        return {
            "channel_id": channel_id,
            "notification_channel": notification_channel,
            "test_status": "success" if success else "failed",
            "sent_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Alert notification test failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to test alert notification")
