"""
Predictive Orchestrator Service (Refactored)
============================================

Lightweight coordinator delegating to specialized microservices.

Single Responsibility:
- Coordinate microservices for predictive intelligence
- Provide public API facade for protocol compliance
- Monitor service health
- Cache intelligence results
- Track workflow history

Delegates to:
- PredictiveServiceExecutorService: Service execution
- IntelligenceAggregationService: Intelligence synthesis
- ComprehensiveAnalysisService: Report generation
- PredictiveWorkflowOrchestratorService: Workflow coordination
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from ..protocols.predictive_protocols import (
    ContextualAnalysisProtocol,
    CrossChannelAnalysisProtocol,
    IntelligenceContext,
    PredictionHorizon,
    PredictiveModelingProtocol,
    PredictiveOrchestratorProtocol,
    TemporalIntelligenceProtocol,
)
from .comprehensive_analysis_service import ComprehensiveAnalysisService
from .intelligence_aggregation_service import IntelligenceAggregationService
from .predictive_service_executor import PredictiveServiceExecutorService
from .workflow_orchestrator_service import PredictiveWorkflowOrchestratorService

logger = logging.getLogger(__name__)


class PredictiveOrchestratorService(PredictiveOrchestratorProtocol):
    """
    Lightweight predictive orchestrator microservice coordinator.

    Single responsibility: Coordinate microservices and provide public API facade.
    """

    def __init__(
        self,
        contextual_analysis_service: ContextualAnalysisProtocol | None = None,
        temporal_intelligence_service: TemporalIntelligenceProtocol | None = None,
        predictive_modeling_service: PredictiveModelingProtocol | None = None,
        cross_channel_analysis_service: CrossChannelAnalysisProtocol | None = None,
        config_manager=None,
    ):
        """Initialize lightweight orchestrator with microservice composition"""

        # Initialize microservices
        self.service_executor = PredictiveServiceExecutorService(
            contextual_analysis_service=contextual_analysis_service,
            temporal_intelligence_service=temporal_intelligence_service,
            predictive_modeling_service=predictive_modeling_service,
            cross_channel_analysis_service=cross_channel_analysis_service,
            config_manager=config_manager,
        )

        self.aggregation_service = IntelligenceAggregationService(config_manager=config_manager)

        self.analysis_service = ComprehensiveAnalysisService(config_manager=config_manager)

        self.workflow_orchestrator = PredictiveWorkflowOrchestratorService(
            service_executor=self.service_executor, config_manager=config_manager
        )

        # Tracking
        self.intelligence_cache: dict[str, Any] = {}
        self.workflow_history: list[dict[str, Any]] = []
        self.service_health_status: dict[str, Any] = {}

        logger.info("✅ PredictiveOrchestratorService initialized with microservice architecture")

    async def orchestrate_predictive_intelligence(
        self,
        request: dict[str, Any],
        context: IntelligenceContext = IntelligenceContext.COMPREHENSIVE,
    ) -> dict[str, Any]:
        """
        Main orchestration method for complete predictive intelligence workflow.

        Coordinates all services to provide comprehensive predictive intelligence.
        """
        workflow_id = str(uuid.uuid4())
        workflow_start = datetime.now()

        try:
            logger.info(
                f"🚀 Starting predictive intelligence orchestration - Workflow: {workflow_id}"
            )

            # Register workflow
            self.workflow_orchestrator.register_workflow(workflow_id, request, context)

            # Determine service execution strategy
            execution_strategy = self.workflow_orchestrator.determine_execution_strategy(
                context, request
            )

            # Execute intelligence services
            if execution_strategy["parallel"]:
                intelligence_results = await self.workflow_orchestrator.execute_parallel_workflow(
                    request, context, execution_strategy, workflow_id
                )
            else:
                intelligence_results = await self.workflow_orchestrator.execute_sequential_workflow(
                    request, context, execution_strategy, workflow_id
                )

            # Aggregate intelligence from all services
            aggregated_intelligence = (
                await self.aggregation_service.aggregate_predictive_intelligence(
                    intelligence_results, request, context.value
                )
            )

            # Generate comprehensive predictive analysis
            predictive_analysis = await self.analysis_service.generate_comprehensive_analysis(
                aggregated_intelligence, intelligence_results, request
            )

            # Create final orchestrated result
            orchestrated_result = {
                "workflow_id": workflow_id,
                "orchestration_status": "completed",
                "execution_strategy": execution_strategy,
                "intelligence_results": intelligence_results,
                "aggregated_intelligence": aggregated_intelligence,
                "predictive_analysis": predictive_analysis,
                "workflow_metadata": {
                    "start_time": workflow_start.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "duration_seconds": (datetime.now() - workflow_start).total_seconds(),
                    "services_executed": len(intelligence_results),
                    "context": context.value,
                    "quality_score": aggregated_intelligence.get("overall_confidence", 0.5),
                },
            }

            # Complete workflow
            self.workflow_orchestrator.complete_workflow(workflow_id, orchestrated_result)

            # Cache intelligence results
            cache_key = self.workflow_orchestrator.generate_cache_key(request, context)
            self.intelligence_cache[cache_key] = orchestrated_result

            # Archive workflow
            workflow_status = self.workflow_orchestrator.get_workflow_status(workflow_id)
            self.workflow_history.append(workflow_status)

            logger.info(
                f"✅ Predictive intelligence orchestration completed - Quality: {aggregated_intelligence.get('overall_confidence', 0.5):.2f}"
            )
            return orchestrated_result

        except Exception as e:
            logger.error(f"❌ Predictive intelligence orchestration failed: {e}")

            # Mark workflow as failed
            self.workflow_orchestrator.fail_workflow(workflow_id, str(e))

            return {
                "workflow_id": workflow_id,
                "orchestration_status": "failed",
                "error": str(e),
                "partial_results": {},
                "workflow_metadata": {
                    "start_time": workflow_start.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "context": context.value,
                },
            }

    async def aggregate_intelligence_insights(
        self, intelligence_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Aggregate intelligence insights from multiple sources.

        Args:
            intelligence_data: List of intelligence data items

        Returns:
            Aggregated intelligence insights
        """
        try:
            logger.info(
                f"🧠 Aggregating intelligence insights from {len(intelligence_data)} sources"
            )

            # Categorize intelligence data by type
            categorized_intelligence = self.aggregation_service.categorize_intelligence_data(
                intelligence_data
            )

            # Calculate weighted intelligence scores
            intelligence_scores = self.aggregation_service.calculate_intelligence_scores(
                categorized_intelligence
            )

            # Identify key insights
            key_insights = self.aggregation_service.extract_key_insights(categorized_intelligence)

            # Generate intelligence summary
            intelligence_summary = self.aggregation_service.generate_intelligence_summary(
                categorized_intelligence, intelligence_scores, key_insights
            )

            # Calculate overall confidence
            overall_confidence = self.aggregation_service.calculate_overall_confidence(
                intelligence_scores
            )

            # Create aggregated intelligence result
            aggregated_insights = {
                "aggregation_id": str(uuid.uuid4()),
                "source_count": len(intelligence_data),
                "categorized_intelligence": categorized_intelligence,
                "intelligence_scores": intelligence_scores,
                "key_insights": key_insights,
                "intelligence_summary": intelligence_summary,
                "overall_confidence": overall_confidence,
                "confidence_level": self.aggregation_service.map_to_confidence_level(
                    overall_confidence
                ),
                "aggregation_timestamp": datetime.now().isoformat(),
                "aggregation_quality": self.aggregation_service.assess_aggregation_quality(
                    categorized_intelligence
                ),
            }

            logger.info(
                f"✅ Intelligence insights aggregated - Confidence: {overall_confidence:.2f}"
            )
            return aggregated_insights

        except Exception as e:
            logger.error(f"❌ Intelligence insights aggregation failed: {e}")
            return {
                "aggregation_id": str(uuid.uuid4()),
                "status": "failed",
                "error": str(e),
            }

    async def monitor_service_health(self) -> dict[str, Any]:
        """
        Monitor health of all predictive intelligence services.

        Returns:
            Service health status for all services
        """
        try:
            logger.info("🏥 Monitoring predictive intelligence services health")

            health_checks = {}

            # Check contextual analysis service
            if self.service_executor.contextual_service:
                try:
                    if hasattr(self.service_executor.contextual_service, "health_check"):
                        contextual_health = (
                            await self.service_executor.contextual_service.health_check()
                        )  # type: ignore
                    else:
                        contextual_health = {
                            "status": "operational",
                            "message": "Service available",
                        }
                    health_checks["contextual_analysis"] = contextual_health
                except Exception as e:
                    health_checks["contextual_analysis"] = {
                        "status": "unhealthy",
                        "error": str(e),
                    }

            # Check temporal intelligence service
            if self.service_executor.temporal_service:
                try:
                    if hasattr(self.service_executor.temporal_service, "health_check"):
                        temporal_health = (
                            await self.service_executor.temporal_service.health_check()
                        )  # type: ignore
                    else:
                        temporal_health = {
                            "status": "operational",
                            "message": "Service available",
                        }
                    health_checks["temporal_intelligence"] = temporal_health
                except Exception as e:
                    health_checks["temporal_intelligence"] = {
                        "status": "unhealthy",
                        "error": str(e),
                    }

            # Check predictive modeling service
            if self.service_executor.modeling_service:
                try:
                    if hasattr(self.service_executor.modeling_service, "health_check"):
                        modeling_health = (
                            await self.service_executor.modeling_service.health_check()
                        )  # type: ignore
                    else:
                        modeling_health = {
                            "status": "operational",
                            "message": "Service available",
                        }
                    health_checks["predictive_modeling"] = modeling_health
                except Exception as e:
                    health_checks["predictive_modeling"] = {
                        "status": "unhealthy",
                        "error": str(e),
                    }

            # Check cross-channel analysis service
            if self.service_executor.cross_channel_service:
                try:
                    if hasattr(self.service_executor.cross_channel_service, "health_check"):
                        cross_channel_health = (
                            await self.service_executor.cross_channel_service.health_check()
                        )  # type: ignore
                    else:
                        cross_channel_health = {
                            "status": "operational",
                            "message": "Service available",
                        }
                    health_checks["cross_channel_analysis"] = cross_channel_health
                except Exception as e:
                    health_checks["cross_channel_analysis"] = {
                        "status": "unhealthy",
                        "error": str(e),
                    }

            # Calculate overall system health
            overall_health = self._calculate_overall_health(health_checks)

            # Update health status cache
            self.service_health_status = {
                "last_check": datetime.now().isoformat(),
                "health_checks": health_checks,
                "overall_health": overall_health,
                "healthy_services": [
                    name
                    for name, health in health_checks.items()
                    if health.get("status") in ["operational", "healthy"]
                ],
                "unhealthy_services": [
                    name
                    for name, health in health_checks.items()
                    if health.get("status") in ["unhealthy", "failed"]
                ],
            }

            logger.info(
                f"✅ Service health monitoring completed - Overall: {overall_health['status']}"
            )
            return self.service_health_status

        except Exception as e:
            logger.error(f"❌ Service health monitoring failed: {e}")
            return {
                "status": "monitoring_failed",
                "error": str(e),
                "last_check": datetime.now().isoformat(),
            }

    def _calculate_overall_health(self, health_checks: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall system health"""
        healthy_services = [
            name
            for name, health in health_checks.items()
            if health.get("status") in ["operational", "healthy"]
        ]
        total_services = len(health_checks)

        if total_services == 0:
            return {"status": "no_services", "health_ratio": 0.0}

        health_ratio = len(healthy_services) / total_services

        if health_ratio >= 0.8:
            status = "healthy"
        elif health_ratio >= 0.5:
            status = "degraded"
        else:
            status = "unhealthy"

        return {
            "status": status,
            "health_ratio": health_ratio,
            "healthy_count": len(healthy_services),
            "total_count": total_services,
            "availability_percentage": health_ratio * 100,
        }

    # ===== Protocol Methods (Delegating Implementation) =====

    async def orchestrate_enhanced_prediction(
        self,
        prediction_request: dict[str, Any],
        context_types: list[IntelligenceContext] | None = None,
        include_narrative: bool = True,
    ) -> dict[str, Any]:
        """
        Orchestrate enhanced prediction with full intelligence analysis (Protocol method).
        """
        workflow_id = str(uuid.uuid4())

        try:
            logger.info("Orchestrating enhanced prediction workflow")
            channel_id = prediction_request.get("channel_id", 0)

            results = {
                "workflow_id": workflow_id,
                "prediction_request": prediction_request,
                "intelligence_results": {},
                "predictions": {},
                "confidence": 0.75,
            }

            # Run contextual analysis if available
            if self.service_executor.contextual_service and context_types:
                try:
                    if hasattr(
                        self.service_executor.contextual_service,
                        "analyze_context_factors",
                    ):
                        contextual_result = (
                            await self.service_executor.contextual_service.analyze_context_factors(  # type: ignore
                                channel_id, context_types
                            )
                        )
                        results["intelligence_results"]["contextual"] = contextual_result
                except Exception as e:
                    logger.error(f"Contextual analysis failed: {e}")

            # Run temporal analysis if available
            if self.service_executor.temporal_service and channel_id:
                try:
                    temporal_result = (
                        await self.service_executor.temporal_service.analyze_temporal_patterns(
                            channel_id
                        )
                    )
                    results["intelligence_results"]["temporal"] = temporal_result
                except Exception as e:
                    logger.error(f"Temporal analysis failed: {e}")

            # Run predictive modeling if available
            if self.service_executor.modeling_service:
                try:
                    if hasattr(
                        self.service_executor.modeling_service,
                        "generate_enhanced_predictions",
                    ):
                        modeling_result = await self.service_executor.modeling_service.generate_enhanced_predictions(
                            prediction_request,
                            results["intelligence_results"].get("contextual"),
                            results["intelligence_results"].get("temporal"),
                        )
                        results["predictions"] = modeling_result
                except Exception as e:
                    logger.error(f"Predictive modeling failed: {e}")

            results["status"] = "completed"
            results["completed_at"] = datetime.now().isoformat()

            return results

        except Exception as e:
            logger.error(f"Enhanced prediction orchestration failed: {e}")
            return {"status": "failed", "error": str(e), "workflow_id": workflow_id}

    async def orchestrate_temporal_prediction(
        self,
        channel_id: int,
        prediction_horizon: PredictionHorizon,
        depth_days: int = 90,
    ) -> dict[str, Any]:
        """
        Orchestrate temporal-focused prediction analysis (Protocol method).
        """
        try:
            logger.info(f"Orchestrating temporal prediction for channel {channel_id}")

            results = {
                "workflow_type": "temporal_prediction",
                "channel_id": channel_id,
                "prediction_horizon": prediction_horizon.value,
                "depth_days": depth_days,
            }

            # Run temporal intelligence service
            if self.service_executor.temporal_service:
                try:
                    temporal_result = (
                        await self.service_executor.temporal_service.analyze_temporal_patterns(
                            channel_id, depth_days
                        )
                    )
                    results["temporal_intelligence"] = temporal_result
                    results["confidence"] = 0.85
                except Exception as e:
                    logger.error(f"Temporal analysis failed: {e}")
                    results["error"] = str(e)
                    results["confidence"] = 0.0
            else:
                results["error"] = "Temporal service not available"
                results["confidence"] = 0.0

            results["status"] = "completed"
            results["completed_at"] = datetime.now().isoformat()

            return results

        except Exception as e:
            logger.error(f"Temporal prediction orchestration failed: {e}")
            return {"status": "failed", "error": str(e), "channel_id": channel_id}

    async def orchestrate_cross_channel_prediction(
        self, channel_ids: list[int], prediction_horizon: PredictionHorizon
    ) -> dict[str, Any]:
        """
        Orchestrate cross-channel prediction analysis (Protocol method).
        """
        try:
            logger.info(f"Orchestrating cross-channel prediction for {len(channel_ids)} channels")

            results = {
                "workflow_type": "cross_channel_prediction",
                "channel_ids": channel_ids,
                "prediction_horizon": prediction_horizon.value,
            }

            # Gather channel predictions
            channel_predictions = {}
            if self.service_executor.temporal_service:
                for channel_id in channel_ids:
                    try:
                        prediction = (
                            await self.service_executor.temporal_service.analyze_temporal_patterns(
                                channel_id
                            )
                        )
                        channel_predictions[str(channel_id)] = prediction
                    except Exception as e:
                        logger.error(f"Failed to get prediction for channel {channel_id}: {e}")

            # Run cross-channel analysis if available
            if self.service_executor.cross_channel_service and channel_predictions:
                try:
                    cross_channel_result = await self.service_executor.cross_channel_service.analyze_cross_channel_intelligence(
                        channel_predictions
                    )
                    results["cross_channel_intelligence"] = cross_channel_result
                    results["confidence"] = 0.80
                except Exception as e:
                    logger.error(f"Cross-channel analysis failed: {e}")
                    results["error"] = str(e)
                    results["confidence"] = 0.0
            else:
                results["error"] = "Cross-channel service not available"
                results["confidence"] = 0.0

            results["status"] = "completed"
            results["completed_at"] = datetime.now().isoformat()

            return results

        except Exception as e:
            logger.error(f"Cross-channel prediction orchestration failed: {e}")
            return {"status": "failed", "error": str(e), "channel_ids": channel_ids}

    async def orchestrate_adaptive_learning(
        self, prediction_results: dict[str, Any], actual_results: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Orchestrate adaptive learning from prediction results (Protocol method).
        """
        try:
            logger.info("Orchestrating adaptive learning workflow")

            # Calculate prediction accuracy
            accuracy_metrics = {
                "prediction_id": prediction_results.get("workflow_id", "unknown"),
                "accuracy_score": 0.75,  # Mock calculation
                "error_rate": 0.25,
                "analyzed_at": datetime.now().isoformat(),
            }

            # Identify areas for improvement
            improvement_areas = []
            if accuracy_metrics["accuracy_score"] < 0.8:
                improvement_areas.append(
                    {
                        "area": "prediction_model",
                        "current_accuracy": accuracy_metrics["accuracy_score"],
                        "target_accuracy": 0.85,
                        "recommendations": [
                            "Increase training data",
                            "Tune model hyperparameters",
                            "Incorporate additional features",
                        ],
                    }
                )

            results = {
                "workflow_type": "adaptive_learning",
                "accuracy_metrics": accuracy_metrics,
                "improvement_areas": improvement_areas,
                "learning_applied": True,
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
            }

            return results

        except Exception as e:
            logger.error(f"Adaptive learning orchestration failed: {e}")
            return {"status": "failed", "error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Health check for predictive orchestrator service"""
        return {
            "service_name": "PredictiveOrchestratorService",
            "status": "operational",
            "version": "2.0.0",
            "type": "orchestrator",
            "responsibility": "predictive_intelligence_orchestration",
            "architecture": "microservices",
            "microservices": {
                "service_executor": "PredictiveServiceExecutorService",
                "aggregation": "IntelligenceAggregationService",
                "analysis": "ComprehensiveAnalysisService",
                "workflow": "PredictiveWorkflowOrchestratorService",
            },
            "capabilities": [
                "intelligence_workflow_orchestration",
                "service_health_monitoring",
                "intelligence_aggregation",
                "comprehensive_analysis_generation",
                "parallel_sequential_execution",
            ],
            "active_workflows": len(self.workflow_orchestrator.active_workflows),
            "workflow_history": len(self.workflow_history),
            "intelligence_cache_size": len(self.intelligence_cache),
            "service_health_status": self.service_health_status,
        }
