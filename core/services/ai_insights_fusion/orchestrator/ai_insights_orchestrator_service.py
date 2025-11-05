"""
AI Insights Orchestrator Service
=================================

Main orchestrator for AI insights microservices workflow.

Single Responsibility:
- Orchestrate insights generation workflow
- Coordinate between microservices
- Manage insights workflow logic
- Provide unified AI insights interface

Coordinates: CoreInsightsService, PatternAnalysisService, PredictiveAnalysisService, ServiceIntegrationService
"""

import logging
from datetime import datetime
from typing import Any

from ..protocols import AIInsightsOrchestratorProtocol

logger = logging.getLogger(__name__)


class AIInsightsOrchestratorService(AIInsightsOrchestratorProtocol):
    """
    AI insights orchestrator microservice.

    Single responsibility: Orchestrate AI insights workflow only.
    Coordinates all AI insights microservices for complete insights generation.
    """

    def __init__(
        self,
        core_insights_service=None,
        pattern_analysis_service=None,
        predictive_analysis_service=None,
        service_integration_service=None,
    ):
        # Microservices dependencies
        self.core_insights = core_insights_service
        self.pattern_analysis = pattern_analysis_service
        self.predictive_analysis = predictive_analysis_service
        self.service_integration = service_integration_service

        # Orchestration configuration
        self.orchestration_config = {
            "default_workflow": "comprehensive",
            "enable_predictions": True,
            "enable_patterns": True,
            "enable_service_integration": True,
            "max_parallel_operations": 3,
            "workflow_timeout": 300,  # 5 minutes
        }

        logger.info(
            "🎼 AI Insights Orchestrator Service initialized - workflow orchestration focus"
        )

    async def orchestrate_comprehensive_insights(
        self,
        channel_id: int,
        narrative_style: str = "executive",
        days_analyzed: int = 30,
        include_predictions: bool = True,
        include_patterns: bool = True,
    ) -> dict[str, Any]:
        """
        Orchestrate comprehensive AI insights generation.

        Full workflow: Core insights → Pattern analysis → Predictions → Service integration
        """
        try:
            logger.info(f"🎭 Orchestrating comprehensive insights for channel {channel_id}")

            workflow_start = datetime.now()
            orchestration_result = {
                "channel_id": channel_id,
                "workflow_type": "comprehensive",
                "workflow_start": workflow_start.isoformat(),
                "parameters": {
                    "narrative_style": narrative_style,
                    "days_analyzed": days_analyzed,
                    "include_predictions": include_predictions,
                    "include_patterns": include_patterns,
                },
            }

            # Step 1: Generate core insights
            if self.core_insights:
                logger.info("📊 Step 1: Generating core insights")
                core_insights_result = await self.core_insights.generate_ai_insights(
                    channel_id, days_analyzed
                )
                orchestration_result["core_insights"] = core_insights_result
                logger.info("✅ Core insights generated")
            else:
                logger.warning("⚠️ Core insights service not available")
                orchestration_result["core_insights"] = {"status": "service_unavailable"}

            # Step 2: Pattern analysis (if enabled)
            if include_patterns and self.pattern_analysis:
                logger.info("🔍 Step 2: Analyzing patterns")
                patterns_result = await self.pattern_analysis.analyze_content_patterns(
                    channel_id, days_analyzed
                )
                orchestration_result["pattern_analysis"] = patterns_result
                logger.info("✅ Pattern analysis completed")
            else:
                logger.info("⏭️ Pattern analysis skipped")
                orchestration_result["pattern_analysis"] = {"status": "skipped"}

            # Step 3: Predictive analysis (if enabled)
            if include_predictions and self.predictive_analysis:
                logger.info("🔮 Step 3: Generating predictions")
                predictions_result = await self.predictive_analysis.generate_ai_predictions(
                    channel_id, days_analyzed
                )
                orchestration_result["predictive_analysis"] = predictions_result
                logger.info("✅ Predictions generated")
            else:
                logger.info("⏭️ Predictive analysis skipped")
                orchestration_result["predictive_analysis"] = {"status": "skipped"}

            # Step 4: Service integration
            if self.service_integration:
                logger.info("🔗 Step 4: Integrating with AI services")
                integration_result = await self.service_integration.integrate_all_services(
                    orchestration_result,
                    include_narrative=True,
                    include_anomaly=True,
                )
                orchestration_result["service_integration"] = integration_result.get(
                    "service_integration_summary", {}
                )

                # Merge integrated data
                for key, value in integration_result.items():
                    if key not in orchestration_result:
                        orchestration_result[key] = value

                logger.info("✅ Service integration completed")
            else:
                logger.info("⏭️ Service integration skipped")
                orchestration_result["service_integration"] = {"status": "skipped"}

            # Workflow completion
            workflow_end = datetime.now()
            orchestration_result["workflow_completion"] = {
                "status": "completed",
                "duration_seconds": (workflow_end - workflow_start).total_seconds(),
                "workflow_end": workflow_end.isoformat(),
                "steps_completed": self._count_completed_steps(orchestration_result),
                "orchestration_summary": self._generate_orchestration_summary(orchestration_result),
            }

            logger.info("🎉 Comprehensive insights orchestration completed")
            return orchestration_result

        except Exception as e:
            logger.error(f"❌ Orchestration failed: {e}")
            return {
                "channel_id": channel_id,
                "workflow_type": "comprehensive",
                "workflow_completion": {
                    "status": "failed",
                    "error": str(e),
                    "workflow_end": datetime.now().isoformat(),
                },
            }

    async def orchestrate_quick_insights(
        self, channel_id: int, focus_area: str = "performance"
    ) -> dict[str, Any]:
        """
        Orchestrate quick insights generation.

        Focused workflow: Core insights only or single analysis type
        """
        try:
            logger.info(
                f"⚡ Orchestrating quick insights for channel {channel_id} - focus: {focus_area}"
            )

            workflow_start = datetime.now()

            if focus_area == "patterns" and self.pattern_analysis:
                # Pattern-focused workflow
                result = await self.pattern_analysis.extract_key_patterns(channel_id, 7)
                result["workflow_type"] = "quick_patterns"

            elif focus_area == "predictions" and self.predictive_analysis:
                # Prediction-focused workflow
                result = await self.predictive_analysis.generate_ai_recommendations(channel_id, 7)
                result["workflow_type"] = "quick_predictions"

            elif self.core_insights:
                # Default: core insights
                result = await self.core_insights.generate_ai_insights(channel_id, 7)
                result["workflow_type"] = "quick_core"

            else:
                result = {
                    "channel_id": channel_id,
                    "workflow_type": "quick_unavailable",
                    "status": "services_unavailable",
                }

            # Add workflow metadata
            result["workflow_completion"] = {
                "status": "completed",
                "duration_seconds": (datetime.now() - workflow_start).total_seconds(),
                "focus_area": focus_area,
                "workflow_end": datetime.now().isoformat(),
            }

            logger.info("✅ Quick insights orchestration completed")
            return result

        except Exception as e:
            logger.error(f"❌ Quick orchestration failed: {e}")
            return {
                "channel_id": channel_id,
                "workflow_type": "quick_failed",
                "workflow_completion": {
                    "status": "failed",
                    "error": str(e),
                    "focus_area": focus_area,
                },
            }

    async def orchestrate_custom_workflow(self, workflow_config: dict[str, Any]) -> dict[str, Any]:
        """
        Orchestrate custom insights workflow.

        Flexible workflow based on configuration
        """
        try:
            logger.info("🎨 Orchestrating custom workflow")

            channel_id = workflow_config.get("channel_id", 0)
            workflow_steps = workflow_config.get("steps", [])

            workflow_result = {
                "channel_id": channel_id,
                "workflow_type": "custom",
                "workflow_config": workflow_config,
                "step_results": {},
            }

            # Execute configured steps
            for step in workflow_steps:
                step_name = step.get("name", "unknown")
                step_service = step.get("service", "")
                step_params = step.get("parameters", {})

                logger.info(f"🔄 Executing step: {step_name}")

                if step_service == "core_insights" and self.core_insights:
                    result = await self.core_insights.generate_ai_insights(
                        channel_id, step_params.get("days_analyzed", 30)
                    )
                elif step_service == "pattern_analysis" and self.pattern_analysis:
                    result = await self.pattern_analysis.analyze_content_patterns(
                        channel_id, step_params.get("days_analyzed", 30)
                    )
                elif step_service == "predictive_analysis" and self.predictive_analysis:
                    result = await self.predictive_analysis.generate_ai_predictions(
                        channel_id, step_params.get("days_analyzed", 30)
                    )
                else:
                    result = {"status": "service_unavailable", "service": step_service}

                workflow_result["step_results"][step_name] = result
                logger.info(f"✅ Step completed: {step_name}")

            workflow_result["workflow_completion"] = {
                "status": "completed",
                "steps_executed": len(workflow_steps),
                "workflow_end": datetime.now().isoformat(),
            }

            logger.info("✅ Custom workflow orchestration completed")
            return workflow_result

        except Exception as e:
            logger.error(f"❌ Custom orchestration failed: {e}")
            return {
                "workflow_type": "custom_failed",
                "workflow_completion": {"status": "failed", "error": str(e)},
            }

    def _count_completed_steps(self, orchestration_result: dict[str, Any]) -> int:
        """Count successfully completed workflow steps"""
        completed_steps = 0

        if orchestration_result.get("core_insights", {}).get("status") != "service_unavailable":
            completed_steps += 1
        if orchestration_result.get("pattern_analysis", {}).get("status") != "skipped":
            completed_steps += 1
        if orchestration_result.get("predictive_analysis", {}).get("status") != "skipped":
            completed_steps += 1
        if orchestration_result.get("service_integration", {}).get("status") != "skipped":
            completed_steps += 1

        return completed_steps

    def _generate_orchestration_summary(
        self, orchestration_result: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate orchestration summary"""
        return {
            "total_steps": 4,
            "completed_steps": self._count_completed_steps(orchestration_result),
            "services_used": self._get_active_services(),
            "workflow_efficiency": self._calculate_workflow_efficiency(orchestration_result),
            "data_quality": {
                "has_core_insights": "core_insights" in orchestration_result,
                "has_patterns": "pattern_analysis" in orchestration_result,
                "has_predictions": "predictive_analysis" in orchestration_result,
                "has_integration": "service_integration" in orchestration_result,
            },
        }

    def _calculate_workflow_efficiency(self, orchestration_result: dict[str, Any]) -> str:
        """Calculate workflow efficiency rating"""
        completed_steps = self._count_completed_steps(orchestration_result)
        total_steps = 4

        efficiency_ratio = completed_steps / total_steps

        if efficiency_ratio >= 0.9:
            return "excellent"
        elif efficiency_ratio >= 0.75:
            return "good"
        elif efficiency_ratio >= 0.5:
            return "moderate"
        else:
            return "limited"

    def _get_active_services(self) -> list[str]:
        """Get list of active orchestrated services"""
        active_services = []

        if self.core_insights:
            active_services.append("CoreInsightsService")
        if self.pattern_analysis:
            active_services.append("PatternAnalysisService")
        if self.predictive_analysis:
            active_services.append("PredictiveAnalysisService")
        if self.service_integration:
            active_services.append("ServiceIntegrationService")

        return active_services

    async def health_check(self) -> dict[str, Any]:
        """Health check for orchestrator and all microservices"""
        # Check all microservices health
        service_health = {}

        try:
            if self.core_insights:
                core_health = await self.core_insights.health_check()
                service_health["core_insights"] = core_health.get("status", "unknown")

            if self.pattern_analysis:
                pattern_health = await self.pattern_analysis.health_check()
                service_health["pattern_analysis"] = pattern_health.get("status", "unknown")

            if self.predictive_analysis:
                predictive_health = await self.predictive_analysis.health_check()
                service_health["predictive_analysis"] = predictive_health.get("status", "unknown")

            if self.service_integration:
                integration_health = await self.service_integration.health_check()
                service_health["service_integration"] = integration_health.get("status", "unknown")

        except Exception as e:
            service_health["health_check_error"] = str(e)

        return {
            "service_name": "AIInsightsOrchestratorService",
            "status": "operational",
            "version": "1.0.0",
            "type": "orchestrator_microservice",
            "responsibility": "ai_insights_orchestration",
            "orchestrated_services": self._get_active_services(),
            "service_health": service_health,
            "capabilities": [
                "comprehensive_insights_workflow",
                "quick_insights_workflow",
                "custom_workflow_orchestration",
                "microservices_coordination",
            ],
            "configuration": self.orchestration_config,
        }

    # Protocol method aliases for AIInsightsOrchestratorProtocol compliance

    async def coordinate_comprehensive_analysis(
        self, channel_id: int, analysis_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Protocol method: Coordinate comprehensive AI analysis.
        Delegates to orchestrate_comprehensive_insights.
        """
        config = analysis_config or {}
        narrative_style = config.get("narrative_style", "executive")
        days_analyzed = config.get("days_analyzed", 30)
        include_predictions = config.get("include_predictions", True)
        include_patterns = config.get("include_patterns", True)

        return await self.orchestrate_comprehensive_insights(
            channel_id=channel_id,
            narrative_style=narrative_style,
            days_analyzed=days_analyzed,
            include_predictions=include_predictions,
            include_patterns=include_patterns,
        )

    async def coordinate_pattern_insights(
        self, channel_id: int, pattern_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Protocol method: Coordinate pattern analysis workflow.
        Delegates to pattern-focused workflow.
        """
        config = pattern_config or {}
        config.get("days_analyzed", 30)

        # Use custom workflow focused on patterns
        workflow_config = {
            "channel_id": channel_id,
            "steps": ["core_insights", "pattern_analysis"],
            "narrative_style": "technical",
            "enable_predictions": False,
            "enable_patterns": True,
        }

        return await self.orchestrate_custom_workflow(workflow_config)

    async def coordinate_predictive_workflow(
        self, channel_id: int, prediction_config: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Protocol method: Coordinate predictive analysis workflow.
        Delegates to prediction-focused workflow.
        """
        config = prediction_config or {}
        config.get("days_analyzed", 30)

        # Use custom workflow focused on predictions
        workflow_config = {
            "channel_id": channel_id,
            "steps": ["core_insights", "predictive_analysis"],
            "narrative_style": "technical",
            "enable_predictions": True,
            "enable_patterns": False,
        }

        return await self.orchestrate_custom_workflow(workflow_config)
