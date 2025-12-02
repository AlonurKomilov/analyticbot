"""
Alerts Orchestrator Service
===========================

Lightweight coordinator for alerts fusion microservices.

Single Responsibility: Service coordination only.
NO BUSINESS LOGIC - only service coordination and routing.

Coordinates:
- LiveMonitoringService: Real-time metrics
- AlertsManagementService: Alert configuration and checking
- CompetitiveIntelligenceService: Market analysis
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

from ..protocols import (
    AlertsManagementProtocol,
    AlertsOrchestratorProtocol,
    CompetitiveIntelligenceProtocol,
    LiveMonitoringProtocol,
)

logger = logging.getLogger(__name__)


class AlertsOrchestratorService(AlertsOrchestratorProtocol):
    """
    Lightweight alerts orchestrator service.

    Single responsibility: Service coordination only.
    Follows the successful pattern from analytics_fusion orchestrator.
    """

    def __init__(
        self,
        live_monitoring_service: LiveMonitoringProtocol,
        alerts_management_service: AlertsManagementProtocol,
        competitive_intelligence_service: CompetitiveIntelligenceProtocol,
    ):
        self.monitoring_service = live_monitoring_service
        self.alerts_service = alerts_management_service
        self.competitive_service = competitive_intelligence_service

        # Orchestrator state
        self.is_running = False
        self.request_count = 0
        self.last_request_time: datetime | None = None

        # Service registry for health monitoring
        self.services = {
            "monitoring": live_monitoring_service,
            "alerts": alerts_management_service,
            "competitive": competitive_intelligence_service,
        }

        logger.info("🎭 Alerts Orchestrator Service initialized - lightweight coordinator")

    async def coordinate_live_monitoring(
        self, channel_id: int, monitoring_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Coordinate live monitoring across services.

        Pure coordination - delegates to monitoring service.
        """
        try:
            start_time = datetime.now()
            self.request_count += 1
            self.last_request_time = start_time

            logger.info(f"🎯 Coordinating live monitoring for channel {channel_id}")

            # Delegate to monitoring service
            hours = monitoring_config.get("hours", 6) if monitoring_config else 6
            live_metrics = await self.monitoring_service.get_live_metrics(channel_id, hours)

            # Add coordination metadata
            coordination_result = {
                "coordination_type": "live_monitoring",
                "channel_id": channel_id,
                "coordinated_at": start_time.isoformat(),
                "services_used": ["monitoring"],
                "live_metrics": live_metrics,
                "status": "coordination_complete",
            }

            logger.info(f"✅ Live monitoring coordinated for channel {channel_id}")
            return coordination_result

        except Exception as e:
            logger.error(f"❌ Live monitoring coordination failed: {e}")
            return {
                "coordination_type": "live_monitoring",
                "channel_id": channel_id,
                "coordinated_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "coordination_failed",
            }

    async def coordinate_alert_analysis(
        self, channel_id: int, analysis_type: str = "comprehensive"
    ) -> dict[str, Any]:
        """
        Coordinate comprehensive alert analysis.

        Orchestrates multiple services for complete alert workflow.
        """
        try:
            start_time = datetime.now()
            self.request_count += 1
            self.last_request_time = start_time

            logger.info(f"🔍 Coordinating alert analysis for channel {channel_id}")

            results = {}

            if analysis_type in ["comprehensive", "setup"]:
                # Setup intelligent alerts
                alert_setup = await self.alerts_service.setup_intelligent_alerts(channel_id)
                results["alert_setup"] = alert_setup

            if analysis_type in ["comprehensive", "monitoring"]:
                # Get live metrics
                live_metrics = await self.monitoring_service.get_live_metrics(channel_id)
                results["live_metrics"] = live_metrics

            if analysis_type in ["comprehensive", "checking"]:
                # Check real-time alerts
                alert_check = await self.alerts_service.check_real_time_alerts(channel_id)
                results["alert_check"] = alert_check

            # Coordination result
            coordination_result = {
                "coordination_type": "alert_analysis",
                "analysis_type": analysis_type,
                "channel_id": channel_id,
                "coordinated_at": start_time.isoformat(),
                "services_used": ["alerts", "monitoring"],
                "results": results,
                "status": "coordination_complete",
            }

            logger.info(f"✅ Alert analysis coordinated for channel {channel_id}")
            return coordination_result

        except Exception as e:
            logger.error(f"❌ Alert analysis coordination failed: {e}")
            return {
                "coordination_type": "alert_analysis",
                "channel_id": channel_id,
                "coordinated_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "coordination_failed",
            }

    async def coordinate_competitive_monitoring(
        self, channel_id: int, competitive_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Coordinate competitive monitoring workflow.

        Orchestrates competitive analysis with live monitoring context.
        """
        try:
            start_time = datetime.now()
            self.request_count += 1
            self.last_request_time = start_time

            logger.info(f"🏆 Coordinating competitive monitoring for channel {channel_id}")

            # Get current performance context
            current_metrics = await self.monitoring_service.get_current_metrics(channel_id)

            # Generate competitive intelligence
            competitor_ids = (
                competitive_config.get("competitor_ids") if competitive_config else None
            )
            analysis_depth = (
                competitive_config.get("analysis_depth", "standard")
                if competitive_config
                else "standard"
            )

            competitive_analysis = await self.competitive_service.generate_competitive_intelligence(
                channel_id, competitor_ids, analysis_depth
            )

            # Coordination result
            coordination_result = {
                "coordination_type": "competitive_monitoring",
                "channel_id": channel_id,
                "coordinated_at": start_time.isoformat(),
                "services_used": ["monitoring", "competitive"],
                "current_context": current_metrics,
                "competitive_analysis": competitive_analysis,
                "status": "coordination_complete",
            }

            logger.info(f"✅ Competitive monitoring coordinated for channel {channel_id}")
            return coordination_result

        except Exception as e:
            logger.error(f"❌ Competitive monitoring coordination failed: {e}")
            return {
                "coordination_type": "competitive_monitoring",
                "channel_id": channel_id,
                "coordinated_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "coordination_failed",
            }

    async def coordinate_comprehensive_alerts_workflow(
        self, channel_id: int, workflow_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Coordinate comprehensive alerts workflow across all services.

        Full orchestration using all three microservices.
        """
        try:
            start_time = datetime.now()
            self.request_count += 1
            self.last_request_time = start_time

            logger.info(f"🚀 Coordinating comprehensive alerts workflow for channel {channel_id}")

            # Execute workflow in parallel where possible
            tasks = []

            # Live monitoring (always needed)
            tasks.append(self.monitoring_service.get_live_metrics(channel_id))

            # Alert setup and checking
            tasks.append(self.alerts_service.setup_intelligent_alerts(channel_id))

            # Competitive analysis (if requested)
            include_competitive = (
                workflow_config.get("include_competitive", True) if workflow_config else True
            )
            if include_competitive:
                tasks.append(self.competitive_service.generate_competitive_intelligence(channel_id))

            # Execute tasks
            if include_competitive:
                live_metrics, alert_setup, competitive_analysis = await asyncio.gather(*tasks)
            else:
                live_metrics, alert_setup = await asyncio.gather(*tasks[:2])
                competitive_analysis = None

            # After setup, check alerts
            alert_check = await self.alerts_service.check_real_time_alerts(channel_id)

            # Comprehensive result
            comprehensive_result = {
                "coordination_type": "comprehensive_alerts_workflow",
                "channel_id": channel_id,
                "coordinated_at": start_time.isoformat(),
                "services_used": ["monitoring", "alerts"]
                + (["competitive"] if include_competitive else []),
                "workflow_results": {
                    "live_metrics": live_metrics,
                    "alert_setup": alert_setup,
                    "alert_check": alert_check,
                    "competitive_analysis": competitive_analysis,
                },
                "workflow_summary": self._summarize_workflow_results(
                    live_metrics, alert_setup, alert_check, competitive_analysis
                ),
                "status": "workflow_complete",
            }

            logger.info(f"✅ Comprehensive alerts workflow completed for channel {channel_id}")
            return comprehensive_result

        except Exception as e:
            logger.error(f"❌ Comprehensive workflow coordination failed: {e}")
            return {
                "coordination_type": "comprehensive_alerts_workflow",
                "channel_id": channel_id,
                "coordinated_at": datetime.now().isoformat(),
                "error": str(e),
                "status": "workflow_failed",
            }

    async def get_services_health(self) -> dict[str, Any]:
        """Get health status of all coordinated services"""
        try:
            health_checks = {}

            for service_name, service in self.services.items():
                try:
                    health_checks[service_name] = await service.health_check()
                except Exception as e:
                    health_checks[service_name] = {"status": "error", "error": str(e)}

            return {
                "orchestrator_health": "operational",
                "services_health": health_checks,
                "total_services": len(self.services),
                "healthy_services": len(
                    [h for h in health_checks.values() if h.get("status") != "error"]
                ),
                "last_request": (
                    self.last_request_time.isoformat() if self.last_request_time else None
                ),
                "request_count": self.request_count,
            }

        except Exception as e:
            logger.error(f"Health check coordination failed: {e}")
            return {"orchestrator_health": "error", "error": str(e)}

    def _summarize_workflow_results(
        self,
        live_metrics: dict[str, Any],
        alert_setup: dict[str, Any],
        alert_check: dict[str, Any],
        competitive_analysis: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Summarize workflow results"""
        try:
            summary = {
                "live_metrics_status": live_metrics.get("status", "unknown"),
                "alert_setup_status": alert_setup.get("status", "unknown"),
                "alert_check_status": alert_check.get("status", "unknown"),
                "active_alerts_count": alert_check.get("total_alerts", 0),
                "monitoring_operational": live_metrics.get("status") == "success",
                "alerts_configured": alert_setup.get("status") == "alerts_configured",
            }

            if competitive_analysis:
                summary.update(
                    {
                        "competitive_analysis_status": competitive_analysis.get(
                            "status", "unknown"
                        ),
                        "competitors_analyzed": competitive_analysis.get("competitors_analyzed", 0),
                        "competitive_opportunities": len(
                            competitive_analysis.get("opportunities", [])
                        ),
                    }
                )

            return summary

        except Exception as e:
            logger.error(f"Workflow summary failed: {e}")
            return {"summary_status": "error", "error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Health check for alerts orchestrator service"""
        services_health = await self.get_services_health()

        return {
            "service_name": "AlertsOrchestratorService",
            "status": "operational",
            "version": "1.0.0",
            "type": "orchestrator",
            "responsibility": "alerts_coordination",
            "coordinated_services": list(self.services.keys()),
            "request_count": self.request_count,
            "last_request": (
                self.last_request_time.isoformat() if self.last_request_time else None
            ),
            "services_health": services_health,
            "capabilities": [
                "live_monitoring_coordination",
                "alert_analysis_coordination",
                "competitive_monitoring_coordination",
                "comprehensive_workflow_orchestration",
            ],
        }
