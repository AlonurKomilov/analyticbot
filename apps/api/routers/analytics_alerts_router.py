"""
Analytics Alerts Router - Alert Management Domain
=================================================

Analytics alerts router providing comprehensive alert management.
✅ REFACTORED (Oct 21, 2025): Now uses AlertsOrchestratorService for better architecture

Uses AlertsOrchestratorService to coordinate:
- LiveMonitoringService: Real-time metrics
- AlertsManagementService: Alert configuration and checking
- CompetitiveIntelligenceService: Market analysis

Domain: Analytics alerting, monitoring, and notification management
Path: /analytics/alerts/*
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from apps.api.middleware.auth import get_current_user, get_current_user_id
from apps.di import get_container

logger = logging.getLogger(__name__)

# ✅ FIXED: Removed prefix - now configured in main.py
router = APIRouter(tags=["analytics-alerts"])

# === ALERT MODELS ===


class AlertCheckResponse(BaseModel):
    """Response model for alert checking"""

    channel_id: int
    coordination_type: str
    coordinated_at: str
    services_used: list[str]
    live_metrics: dict[str, Any]
    alert_check: dict[str, Any] | None = None
    alert_setup: dict[str, Any] | None = None
    next_check: datetime
    summary: dict[str, Any]
    status: str


class LiveMonitoringResponse(BaseModel):
    """Response model for live monitoring"""

    channel_id: int
    coordination_type: str
    coordinated_at: str
    services_used: list[str]
    live_metrics: dict[str, Any]
    status: str


class ComprehensiveAlertsResponse(BaseModel):
    """Response model for comprehensive alerts workflow"""

    channel_id: int
    coordination_type: str
    coordinated_at: str
    services_used: list[str]
    workflow_results: dict[str, Any]
    workflow_summary: dict[str, Any]
    status: str


class AlertRuleRequest(BaseModel):
    """Request model for alert rule creation"""

    rule_name: str = Field(..., description="Name of the alert rule")
    metric_type: str = Field(..., description="Metric type: 'growth', 'engagement', 'views'")
    threshold_value: float = Field(..., description="Threshold value for alert")
    comparison: str = Field(..., description="Comparison: 'above', 'below', 'equals'")
    enabled: bool = Field(True, description="Whether rule is enabled")
    notification_channels: list[str] = Field([], description="Notification channels")


class CompetitiveMonitoringRequest(BaseModel):
    """Request model for competitive monitoring"""

    channel_id: int = Field(..., description="Channel ID to monitor")
    competitor_ids: list[int] | None = Field(None, description="Optional competitor channel IDs")
    analysis_depth: str = Field(
        "standard", description="Analysis depth: 'basic', 'standard', 'comprehensive'"
    )
    include_live_context: bool = Field(True, description="Include current performance context")


class HealthResponse(BaseModel):
    """Response model for health check"""

    service_name: str
    status: str
    version: str
    type: str
    responsibility: str
    coordinated_services: list[str]
    request_count: int
    last_request: str | None
    services_health: dict[str, Any]
    capabilities: list[str]


class StatsResponse(BaseModel):
    """Response model for service statistics"""

    service_name: str
    version: str
    type: str
    features: dict[str, str]
    coordinated_services: list[str]
    performance: dict[str, Any]
    status: str


# === DEPENDENCY INJECTION ===


async def get_alerts_orchestrator():
    """Get AlertsOrchestratorService from DI container"""
    try:
        container = get_container()
        orchestrator = await container.bot.alerts_orchestrator_service()
        return orchestrator
    except Exception as e:
        logger.error(f"Failed to get AlertsOrchestratorService: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Alerts Orchestrator Service unavailable",
        )


# === ORCHESTRATED ENDPOINTS ===


@router.get(
    "/monitor/live/{channel_id}",
    response_model=LiveMonitoringResponse,
    summary="Live Monitoring",
    description="""
    Get real-time live monitoring metrics for a channel.

    Uses AlertsOrchestratorService to coordinate LiveMonitoringService.

    Features:
    - Real-time metrics collection
    - Recent performance analysis
    - Live status tracking

    Returns current metrics with coordination metadata.
    """,
)
async def get_live_monitoring(
    channel_id: int,
    hours: int = Query(6, ge=1, le=24, description="Hours to monitor"),
    current_user: dict = Depends(get_current_user),
    orchestrator=Depends(get_alerts_orchestrator),
) -> LiveMonitoringResponse:
    """
    Get live monitoring metrics through orchestrator.

    Coordinates with LiveMonitoringService to provide real-time metrics.
    """
    try:
        logger.info(f"📊 Live monitoring request for channel {channel_id}, hours={hours}")

        # Coordinate live monitoring through orchestrator
        monitoring_config = {"hours": hours}
        result = await orchestrator.coordinate_live_monitoring(
            channel_id=channel_id, monitoring_config=monitoring_config
        )

        if result.get("status") == "coordination_failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Live monitoring failed: {result.get('error', 'Unknown error')}",
            )

        logger.info(f"✅ Live monitoring completed for channel {channel_id}")
        return LiveMonitoringResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Live monitoring failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Live monitoring failed: {str(e)}",
        )


@router.post(
    "/check/{channel_id}",
    response_model=AlertCheckResponse,
    summary="Check Channel Alerts",
    description="""
    Check for active alerts on a channel using orchestrated alert workflow.

    Uses AlertsOrchestratorService to coordinate:
    - Alert setup (if needed)
    - Live monitoring
    - Real-time alert checking

    Returns comprehensive alert status with recommendations.
    """,
)
async def check_channel_alerts(
    channel_id: int,
    analysis_type: str = Query(
        "comprehensive",
        description="Analysis type: 'setup', 'monitoring', 'checking', 'comprehensive'",
    ),
    current_user_id: int = Depends(get_current_user_id),
    orchestrator=Depends(get_alerts_orchestrator),
) -> AlertCheckResponse:
    """
    Check channel alerts through orchestrator.

    Coordinates alert analysis workflow including setup, monitoring, and checking.
    """
    try:
        logger.info(f"🚨 Alert check request for channel {channel_id}, type={analysis_type}")

        # Coordinate alert analysis through orchestrator
        result = await orchestrator.coordinate_alert_analysis(
            channel_id=channel_id, analysis_type=analysis_type
        )

        if result.get("status") == "coordination_failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Alert check failed: {result.get('error', 'Unknown error')}",
            )

        # Add next check time
        next_check = datetime.now() + timedelta(minutes=15)

        # Build summary
        results = result.get("results", {})
        summary = {
            "live_metrics_available": "live_metrics" in results,
            "alert_setup_completed": "alert_setup" in results,
            "alerts_checked": "alert_check" in results,
            "total_alerts": results.get("alert_check", {}).get("total_alerts", 0),
        }

        response = AlertCheckResponse(
            channel_id=result["channel_id"],
            coordination_type=result["coordination_type"],
            coordinated_at=result["coordinated_at"],
            services_used=result["services_used"],
            live_metrics=results.get("live_metrics", {}),
            alert_check=results.get("alert_check"),
            alert_setup=results.get("alert_setup"),
            next_check=next_check,
            summary=summary,
            status=result["status"],
        )

        logger.info(f"✅ Alert check completed for channel {channel_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Alert check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert check failed: {str(e)}",
        )


@router.post(
    "/competitive/monitor",
    response_model=dict[str, Any],
    summary="Competitive Monitoring",
    description="""
    Monitor channel performance with competitive intelligence context.

    Uses AlertsOrchestratorService to coordinate:
    - Current performance monitoring
    - Competitive intelligence analysis

    Provides insights on how channel performs relative to competitors.
    """,
)
async def competitive_monitoring(
    request: CompetitiveMonitoringRequest,
    current_user_id: int = Depends(get_current_user_id),
    orchestrator=Depends(get_alerts_orchestrator),
) -> dict[str, Any]:
    """
    Competitive monitoring through orchestrator.

    Coordinates performance monitoring with competitive intelligence.
    """
    try:
        logger.info(f"🏆 Competitive monitoring request for channel {request.channel_id}")

        # Build config
        competitive_config = {
            "competitor_ids": request.competitor_ids,
            "analysis_depth": request.analysis_depth,
        }

        # Coordinate competitive monitoring through orchestrator
        result = await orchestrator.coordinate_competitive_monitoring(
            channel_id=request.channel_id, competitive_config=competitive_config
        )

        if result.get("status") == "coordination_failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Competitive monitoring failed: {result.get('error', 'Unknown error')}",
            )

        logger.info(f"✅ Competitive monitoring completed for channel {request.channel_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Competitive monitoring failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Competitive monitoring failed: {str(e)}",
        )


@router.post(
    "/workflow/comprehensive/{channel_id}",
    response_model=ComprehensiveAlertsResponse,
    summary="Comprehensive Alerts Workflow",
    description="""
    Execute comprehensive alerts workflow coordinating all alert services.

    Uses AlertsOrchestratorService to coordinate:
    - Live monitoring
    - Alert setup and configuration
    - Real-time alert checking
    - Competitive analysis (optional)

    Provides complete alert management workflow in a single request.
    """,
)
async def comprehensive_alerts_workflow(
    channel_id: int,
    include_competitive: bool = Query(
        True, description="Include competitive intelligence analysis"
    ),
    current_user_id: int = Depends(get_current_user_id),
    orchestrator=Depends(get_alerts_orchestrator),
) -> ComprehensiveAlertsResponse:
    """
    Execute comprehensive alerts workflow.

    Full orchestration of all alert services for complete monitoring.
    """
    try:
        logger.info(f"🚀 Comprehensive workflow request for channel {channel_id}")

        # Build workflow config
        workflow_config = {"include_competitive": include_competitive}

        # Execute comprehensive workflow through orchestrator
        result = await orchestrator.coordinate_comprehensive_alerts_workflow(
            channel_id=channel_id, workflow_config=workflow_config
        )

        if result.get("status") == "workflow_failed":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Comprehensive workflow failed: {result.get('error', 'Unknown error')}",
            )

        logger.info(f"✅ Comprehensive workflow completed for channel {channel_id}")
        return ComprehensiveAlertsResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Comprehensive workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comprehensive workflow failed: {str(e)}",
        )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Health Check",
    description="Check Alerts Orchestrator Service health and all coordinated services",
)
async def health_check(orchestrator=Depends(get_alerts_orchestrator)) -> HealthResponse:
    """
    Health check endpoint for Alerts Orchestrator Service.

    Returns health status of orchestrator and all coordinated services.
    """
    try:
        health = await orchestrator.health_check()
        return HealthResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}",
        )


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Service Statistics",
    description="Get Alerts Orchestrator Service statistics and capabilities",
)
async def get_stats() -> StatsResponse:
    """
    Get service statistics and information.

    Returns metadata about the Alerts Orchestrator Service.
    """
    return StatsResponse(
        service_name="Alerts Orchestrator Service",
        version="1.0.0",
        type="orchestrator",
        features={
            "live_monitoring": "Real-time metrics coordination via LiveMonitoringService",
            "alert_management": "Alert setup and checking via AlertsManagementService",
            "competitive_intelligence": "Market analysis via CompetitiveIntelligenceService",
            "comprehensive_workflow": "Full alert workflow orchestration",
            "service_health": "Coordinated health monitoring across services",
        },
        coordinated_services=[
            "LiveMonitoringService",
            "AlertsManagementService",
            "CompetitiveIntelligenceService",
        ],
        performance={
            "live_monitoring_time": "1-3 seconds",
            "alert_check_time": "3-5 seconds",
            "comprehensive_workflow_time": "10-15 seconds",
        },
        status="active",
    )


# === LEGACY ENDPOINTS (Backward Compatibility) ===
# These endpoints maintain backward compatibility while using the orchestrator internally

# ⚠️ IMPORTANT: More specific routes MUST come before generic routes
# /rules/smart/{channel_id} must be before /rules/{channel_id}


@router.get("/rules/smart/{channel_id}")
async def get_smart_alert_rules(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    orchestrator=Depends(get_alerts_orchestrator),
):
    """
    Get personalized smart alert rules for a channel.

    Analyzes channel size, history, and performance to generate
    intelligent alert rules with appropriate thresholds.

    Returns:
    - 5 pre-configured smart rules personalized to channel
    - Each rule has thresholds based on channel's actual metrics
    - Rules marked as 'personalized': true
    """
    try:
        from core.services.alerts_fusion.alerts.smart_rules_generator import (
            SmartRulesGenerator,
        )

        # Get repositories from container
        container = get_container()
        channels_repo = await container.database.channel_repo()
        daily_repo = await container.database.channel_daily_repo()
        posts_repo = await container.database.post_repo()

        # Generate smart rules
        generator = SmartRulesGenerator(channels_repo, daily_repo, posts_repo)
        smart_rules = await generator.generate_smart_rules_for_channel(channel_id)

        logger.info(f"✅ Generated {len(smart_rules)} smart rules for channel {channel_id}")

        return {
            "channel_id": channel_id,
            "rules": smart_rules,
            "total_rules": len(smart_rules),
            "personalized": any(r.get("personalized", False) for r in smart_rules),
            "message": "Smart rules personalized to your channel's size and performance",
        }

    except Exception as e:
        logger.error(f"Smart rules generation failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate smart rules: {str(e)}")


@router.get("/rules/{channel_id}")
async def get_alert_rules(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    orchestrator=Depends(get_alerts_orchestrator),
):
    """
    Get all alert rules for a channel (legacy endpoint).

    Maintained for backward compatibility - uses orchestrator internally.
    """
    try:
        # Access alerts service through orchestrator
        rules = await orchestrator.alerts_service.get_channel_rules(channel_id=str(channel_id))

        return {
            "channel_id": channel_id,
            "rules": rules,
            "total_rules": len(rules),
            "active_rules": len([r for r in rules if r.get("enabled", False)]),
        }

    except Exception as e:
        logger.error(f"Alert rules fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alert rules")


@router.post("/rules/{channel_id}")
async def create_alert_rule(
    channel_id: int,
    rule_request: AlertRuleRequest,
    current_user: dict = Depends(get_current_user),
    orchestrator=Depends(get_alerts_orchestrator),
):
    """
    Create a new alert rule for a channel.

    Creates a custom alert rule with specified thresholds and conditions.
    """
    try:
        # Create rule in the alerts service
        rule = await orchestrator.alerts_service.create_alert_rule(
            channel_id=str(channel_id),
            rule_name=rule_request.rule_name,
            metric_type=rule_request.metric_type,
            threshold_value=rule_request.threshold_value,
            comparison=rule_request.comparison,
            enabled=rule_request.enabled,
            notification_channels=rule_request.notification_channels,
        )

        return {
            "channel_id": channel_id,
            "rule": rule,
            "status": "created",
            "message": f"Alert rule '{rule_request.rule_name}' created successfully",
        }

    except Exception as e:
        logger.error(f"Alert rule creation failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create alert rule: {str(e)}")


@router.put("/rules/{channel_id}/{rule_id}")
async def update_alert_rule(
    channel_id: int,
    rule_id: str,
    enabled: bool,
    current_user: dict = Depends(get_current_user),
    orchestrator=Depends(get_alerts_orchestrator),
):
    """
    Update an alert rule (toggle enabled/disabled).

    Updates the rule status in the alert configuration.
    """
    try:
        # Update rule in the alerts service
        rule = await orchestrator.alerts_service.update_alert_rule(
            channel_id=str(channel_id),
            rule_id=rule_id,
            enabled=enabled,
        )

        return {
            "channel_id": channel_id,
            "rule_id": rule_id,
            "rule": rule,
            "status": "updated",
            "message": f"Alert rule {'enabled' if enabled else 'disabled'} successfully",
        }

    except Exception as e:
        logger.error(f"Alert rule update failed for channel {channel_id}, rule {rule_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update alert rule: {str(e)}")


@router.get("/history/{channel_id}")
async def get_alert_history(
    channel_id: int,
    period: int = Query(default=30, ge=1, le=365, description="Period in days"),
    alert_type: str | None = Query(default=None, description="Filter by alert type"),
    current_user: dict = Depends(get_current_user),
    orchestrator=Depends(get_alerts_orchestrator),
):
    """
    Get historical alert data (legacy endpoint).

    Maintained for backward compatibility - uses orchestrator internally.
    """
    try:
        # Access event manager through orchestrator
        alerts = await orchestrator.alerts_service.get_alert_history(
            channel_id=str(channel_id),
            limit=1000,
        )

        # Analyze alert types by severity
        alert_types: dict[str, int] = {}
        for alert in alerts:
            severity = alert.get("severity", "unknown")
            alert_types[severity] = alert_types.get(severity, 0) + 1

        return {
            "channel_id": str(channel_id),
            "alerts": alerts[: min(len(alerts), 100)],  # Limit to 100 for response
            "period": f"{period}d",
            "total_alerts": len(alerts),
            "alert_types": alert_types,
        }

    except Exception as e:
        logger.error(f"Alert history fetch failed for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alert history")
