"""
Service Integration Service
==========================

Focused microservice for integrating with existing AI services.

Single Responsibility:
- Integration with NLG services
- Integration with AI chat services
- Integration with anomaly detection services
- Service coordination and data flow

Builds upon existing services: NLGIntegrationService, AIChatService, AnomalyAnalysisService
"""

import logging
from typing import Any

from ..protocols import ServiceIntegrationProtocol

logger = logging.getLogger(__name__)


class ServiceIntegrationService(ServiceIntegrationProtocol):
    """
    Service integration microservice for AI services coordination.

    Single responsibility: Integration with existing AI services only.
    Leverages already extracted services: NLG, AI Chat, Anomaly Detection.
    """

    def __init__(
        self, nlg_integration_service=None, ai_chat_service=None, anomaly_analysis_service=None
    ):
        # Use existing extracted services
        self.nlg_integration = nlg_integration_service
        self.ai_chat = ai_chat_service
        self.anomaly_analysis = anomaly_analysis_service

        # Integration configuration
        self.integration_config = {
            "nlg_enabled": nlg_integration_service is not None,
            "chat_enabled": ai_chat_service is not None,
            "anomaly_enabled": anomaly_analysis_service is not None,
            "default_narrative_style": "executive",
        }

        logger.info("🔗 Service Integration Service initialized - AI services integration focus")

    async def integrate_nlg_services(
        self, insights_data: dict[str, Any], narrative_style: str = "executive"
    ) -> dict[str, Any]:
        """
        Integrate with NLG services for narrative generation.

        Delegates to existing NLGIntegrationService.
        """
        try:
            if not self.integration_config["nlg_enabled"]:
                return {
                    "status": "nlg_not_available",
                    "narrative": "NLG service not configured",
                    "insights_data": insights_data,
                }

            logger.info("📝 Integrating with NLG services")

            # Check if NLG service is available
            if self.nlg_integration is None:
                logger.warning("NLG integration service not available")
                return {
                    **insights_data,
                    "nlg_integration": {
                        "narrative_style": narrative_style,
                        "integration_status": "skipped",
                        "reason": "NLG service not configured",
                    },
                    "narrative_enhanced": False,
                }

            # Use existing NLG integration service
            narrative_result = await self.nlg_integration.generate_insights_with_narrative(
                insights_data.get("channel_id", 0),
                narrative_style,
                insights_data.get("analysis_period", {}).get("days_analyzed", 30),
            )

            # Enhance with integration metadata
            integrated_result = {
                **insights_data,
                "nlg_integration": {
                    "narrative_style": narrative_style,
                    "narrative_result": narrative_result,
                    "integration_status": "completed",
                    "service_used": "NLGIntegrationService",
                },
                "narrative_enhanced": True,
            }

            logger.info("✅ NLG services integration completed")
            return integrated_result

        except Exception as e:
            logger.error(f"❌ NLG integration failed: {e}")
            return {
                **insights_data,
                "nlg_integration": {"integration_status": "failed", "error": str(e)},
                "narrative_enhanced": False,
            }

    async def integrate_chat_services(
        self, user_query: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Integrate with AI chat services.

        Delegates to existing AIChatService.
        """
        try:
            if not self.integration_config["chat_enabled"]:
                return {
                    "status": "chat_not_available",
                    "response": "AI chat service not configured",
                    "query": user_query,
                }

            logger.info("💬 Integrating with AI chat services")

            # Check if AI chat service is available
            if self.ai_chat is None:
                logger.warning("AI chat service not available")
                return {
                    "status": "chat_not_available",
                    "response": "AI chat service not configured",
                    "query": user_query,
                }

            # Use existing AI chat service
            chat_response = await self.ai_chat.ai_chat_response(
                user_query, context.get("channel_id", 0), context
            )

            # Enhance with integration metadata
            integrated_response = {
                "query": user_query,
                "context": context,
                "chat_integration": {
                    "response": chat_response,
                    "integration_status": "completed",
                    "service_used": "AIChatService",
                },
                "chat_enhanced": True,
            }

            logger.info("✅ Chat services integration completed")
            return integrated_response

        except Exception as e:
            logger.error(f"❌ Chat integration failed: {e}")
            return {
                "query": user_query,
                "context": context,
                "chat_integration": {"integration_status": "failed", "error": str(e)},
                "chat_enhanced": False,
            }

    async def integrate_anomaly_services(
        self, channel_id: int, time_period: str = "24h"
    ) -> dict[str, Any]:
        """
        Integrate with anomaly detection services.

        Delegates to existing AnomalyAnalysisService.
        """
        try:
            if not self.integration_config["anomaly_enabled"]:
                return {
                    "status": "anomaly_not_available",
                    "anomalies": [],
                    "channel_id": channel_id,
                }

            logger.info(f"🔍 Integrating with anomaly detection services for channel {channel_id}")

            # Check if anomaly analysis service is available
            if self.anomaly_analysis is None:
                logger.warning("Anomaly analysis service not available")
                return {
                    "status": "anomaly_not_available",
                    "anomalies": [],
                    "channel_id": channel_id,
                }

            # Use existing anomaly analysis service
            anomaly_result = await self.anomaly_analysis.explain_performance_anomaly(
                channel_id, time_period
            )

            # Enhance with integration metadata
            integrated_result = {
                "channel_id": channel_id,
                "time_period": time_period,
                "anomaly_integration": {
                    "anomaly_result": anomaly_result,
                    "integration_status": "completed",
                    "service_used": "AnomalyAnalysisService",
                },
                "anomaly_enhanced": True,
            }

            logger.info("✅ Anomaly services integration completed")
            return integrated_result

        except Exception as e:
            logger.error(f"❌ Anomaly integration failed: {e}")
            return {
                "channel_id": channel_id,
                "time_period": time_period,
                "anomaly_integration": {"integration_status": "failed", "error": str(e)},
                "anomaly_enhanced": False,
            }

    async def integrate_all_services(
        self,
        insights_data: dict[str, Any],
        include_narrative: bool = True,
        include_anomaly: bool = True,
    ) -> dict[str, Any]:
        """
        Integrate with all available AI services.

        Comprehensive integration workflow.
        """
        try:
            logger.info("🎭 Integrating with all AI services")

            integrated_data = insights_data.copy()

            # NLG integration
            if include_narrative and self.integration_config["nlg_enabled"]:
                nlg_result = await self.integrate_nlg_services(
                    integrated_data, self.integration_config["default_narrative_style"]
                )
                integrated_data.update(nlg_result)

            # Anomaly detection integration
            if include_anomaly and self.integration_config["anomaly_enabled"]:
                channel_id = insights_data.get("channel_id", 0)
                anomaly_result = await self.integrate_anomaly_services(channel_id)
                integrated_data["anomaly_analysis"] = anomaly_result

            # Integration summary
            integrated_data["service_integration_summary"] = {
                "nlg_integrated": include_narrative and self.integration_config["nlg_enabled"],
                "anomaly_integrated": include_anomaly
                and self.integration_config["anomaly_enabled"],
                "chat_available": self.integration_config["chat_enabled"],
                "integration_timestamp": insights_data.get("generated_at", ""),
                "services_used": self._get_active_services(),
            }

            logger.info("✅ All AI services integration completed")
            return integrated_data

        except Exception as e:
            logger.error(f"❌ Full integration failed: {e}")
            return {
                **insights_data,
                "service_integration_summary": {"integration_status": "failed", "error": str(e)},
            }

    def _get_active_services(self) -> list[str]:
        """Get list of active/available services"""
        active_services = []

        if self.integration_config["nlg_enabled"]:
            active_services.append("NLGIntegrationService")
        if self.integration_config["chat_enabled"]:
            active_services.append("AIChatService")
        if self.integration_config["anomaly_enabled"]:
            active_services.append("AnomalyAnalysisService")

        return active_services

    async def health_check(self) -> dict[str, Any]:
        """Health check for service integration"""
        # Check individual service health
        service_health = {}

        try:
            if self.nlg_integration:
                service_health["nlg_integration"] = "available"
            if self.ai_chat:
                service_health["ai_chat"] = "available"
            if self.anomaly_analysis:
                service_health["anomaly_analysis"] = "available"
        except Exception as e:
            service_health["health_check_error"] = str(e)

        return {
            "service_name": "ServiceIntegrationService",
            "status": "operational",
            "version": "1.0.0",
            "type": "microservice",
            "responsibility": "service_integration",
            "active_services": self._get_active_services(),
            "service_health": service_health,
            "capabilities": [
                "nlg_integration",
                "chat_integration",
                "anomaly_integration",
                "comprehensive_integration",
            ],
            "configuration": self.integration_config,
        }
