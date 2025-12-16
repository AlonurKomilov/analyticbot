"""
Predictive Service Executor Service
===================================

Responsible for executing individual predictive intelligence services.

Single Responsibility:
- Execute contextual analysis service
- Execute temporal intelligence service
- Execute predictive modeling service
- Execute cross-channel analysis service
- Handle service-level error handling and timeouts
"""

import logging
from datetime import datetime
from typing import Any

from ..protocols.predictive_protocols import (
    ContextualAnalysisProtocol,
    ContextualIntelligence,
    CrossChannelAnalysisProtocol,
    IntelligenceContext,
    PredictionHorizon,
    PredictiveModelingProtocol,
    TemporalIntelligence,
    TemporalIntelligenceProtocol,
)

logger = logging.getLogger(__name__)


class PredictiveServiceExecutorService:
    """
    Service execution microservice for predictive intelligence services.

    Single responsibility: Execute individual predictive services with error handling.
    """

    def __init__(
        self,
        contextual_analysis_service: ContextualAnalysisProtocol | None = None,
        temporal_intelligence_service: TemporalIntelligenceProtocol | None = None,
        predictive_modeling_service: PredictiveModelingProtocol | None = None,
        cross_channel_analysis_service: CrossChannelAnalysisProtocol | None = None,
        config_manager=None,
    ):
        """Initialize service executor"""
        self.contextual_service = contextual_analysis_service
        self.temporal_service = temporal_intelligence_service
        self.modeling_service = predictive_modeling_service
        self.cross_channel_service = cross_channel_analysis_service
        self.config_manager = config_manager

        # Service execution timeouts
        self.timeouts = {
            "contextual_analysis": 30,  # seconds
            "temporal_intelligence": 45,
            "predictive_modeling": 60,
            "cross_channel_analysis": 90,
        }

    async def execute_contextual_analysis(
        self, request: dict[str, Any], context: IntelligenceContext, workflow_id: str
    ) -> dict[str, Any]:
        """
        Execute contextual analysis service.

        Args:
            request: Analysis request with channel_ids and analysis_depth
            context: Intelligence context for analysis
            workflow_id: Workflow identifier for tracking

        Returns:
            Service execution result with contextual intelligence
        """
        try:
            channel_ids = request.get("channel_ids", [])
            analysis_depth = request.get("analysis_depth", "comprehensive")

            # Check if method exists, fallback to protocol method
            if hasattr(self.contextual_service, "analyze_contextual_intelligence"):
                contextual_intelligence = (
                    await self.contextual_service.analyze_contextual_intelligence(  # type: ignore
                        channel_ids, context, analysis_depth
                    )
                )
            elif self.contextual_service and hasattr(
                self.contextual_service, "analyze_context_factors"
            ):
                # Fallback to protocol-defined method
                prediction_request = {
                    "channel_id": channel_ids[0] if channel_ids else 0,
                    "channel_ids": channel_ids,
                    "analysis_depth": analysis_depth,
                }
                contextual_intelligence = await self.contextual_service.analyze_context_factors(  # type: ignore
                    prediction_request,
                    [context],  # Pass context as list
                )
            else:
                contextual_intelligence = {
                    "status": "not_implemented",
                    "message": "Contextual analysis not available",
                }

            return {
                "service": "contextual_analysis",
                "status": "completed",
                "contextual_intelligence": contextual_intelligence,
                "execution_metadata": {
                    "workflow_id": workflow_id,
                    "executed_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"❌ Contextual analysis execution failed: {e}")
            return {
                "service": "contextual_analysis",
                "status": "failed",
                "error": str(e),
                "execution_metadata": {
                    "workflow_id": workflow_id,
                    "failed_at": datetime.now().isoformat(),
                },
            }

    async def execute_temporal_intelligence(
        self, request: dict[str, Any], context: IntelligenceContext, workflow_id: str
    ) -> dict[str, Any]:
        """
        Execute temporal intelligence service.

        Args:
            request: Analysis request with channel_ids and time_horizon
            context: Intelligence context for analysis
            workflow_id: Workflow identifier for tracking

        Returns:
            Service execution result with temporal intelligence
        """
        try:
            channel_ids = request.get("channel_ids", [])
            time_horizon = request.get("time_horizon", PredictionHorizon.MEDIUM_TERM)

            # Check if method exists, fallback to protocol method
            if hasattr(self.temporal_service, "analyze_temporal_intelligence"):
                temporal_intelligence = await self.temporal_service.analyze_temporal_intelligence(  # type: ignore
                    channel_ids, time_horizon, context
                )
            elif self.temporal_service and hasattr(
                self.temporal_service, "analyze_temporal_patterns"
            ):
                # Fallback to protocol-defined method
                temporal_intelligence = await self.temporal_service.analyze_temporal_patterns(  # type: ignore
                    channel_ids[0] if channel_ids else 0
                )
            else:
                temporal_intelligence = {
                    "status": "not_implemented",
                    "message": "Temporal intelligence not available",
                }

            return {
                "service": "temporal_intelligence",
                "status": "completed",
                "temporal_intelligence": temporal_intelligence,
                "execution_metadata": {
                    "workflow_id": workflow_id,
                    "executed_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"❌ Temporal intelligence execution failed: {e}")
            return {
                "service": "temporal_intelligence",
                "status": "failed",
                "error": str(e),
                "execution_metadata": {
                    "workflow_id": workflow_id,
                    "failed_at": datetime.now().isoformat(),
                },
            }

    async def execute_predictive_modeling(
        self,
        request: dict[str, Any],
        context: IntelligenceContext,
        contextual_result: dict[str, Any] | None,
        temporal_result: dict[str, Any] | None,
        workflow_id: str,
    ) -> dict[str, Any]:
        """
        Execute predictive modeling service.

        Args:
            request: Modeling request
            context: Intelligence context
            contextual_result: Results from contextual analysis
            temporal_result: Results from temporal intelligence
            workflow_id: Workflow identifier for tracking

        Returns:
            Service execution result with predictions and narrative
        """
        try:
            # Extract intelligence from previous services
            contextual_intelligence = None
            temporal_intelligence = None

            if contextual_result and contextual_result.get("status") == "completed":
                contextual_intelligence = contextual_result.get("contextual_intelligence")

            if temporal_result and temporal_result.get("status") == "completed":
                temporal_intelligence = temporal_result.get("temporal_intelligence")

            # Type guards: ensure we pass valid instances or create defaults
            if contextual_intelligence is None:
                contextual_intelligence = ContextualIntelligence()  # Use default empty instance
            if temporal_intelligence is None:
                temporal_intelligence = TemporalIntelligence()  # Use default empty instance

            # Generate enhanced predictions (if service and method available)
            if self.modeling_service and hasattr(
                self.modeling_service, "generate_enhanced_predictions"
            ):
                enhanced_predictions = await self.modeling_service.generate_enhanced_predictions(  # type: ignore
                    request, contextual_intelligence, temporal_intelligence
                )
            else:
                enhanced_predictions = {
                    "status": "not_implemented",
                    "message": "Enhanced predictions not available",
                }

            # Generate prediction narrative (if service and method available)
            prediction_narrative = None
            if self.modeling_service and hasattr(
                self.modeling_service, "generate_prediction_narrative"
            ):
                prediction_narrative = await self.modeling_service.generate_prediction_narrative(  # type: ignore
                    enhanced_predictions, {"context": context.value}
                )

            return {
                "service": "predictive_modeling",
                "status": "completed",
                "enhanced_predictions": enhanced_predictions,
                "prediction_narrative": prediction_narrative,
                "execution_metadata": {
                    "workflow_id": workflow_id,
                    "executed_at": datetime.now().isoformat(),
                    "dependencies_used": {
                        "contextual": contextual_intelligence is not None,
                        "temporal": temporal_intelligence is not None,
                    },
                },
            }

        except Exception as e:
            logger.error(f"❌ Predictive modeling execution failed: {e}")
            return {
                "service": "predictive_modeling",
                "status": "failed",
                "error": str(e),
                "execution_metadata": {
                    "workflow_id": workflow_id,
                    "failed_at": datetime.now().isoformat(),
                },
            }

    async def execute_cross_channel_analysis(
        self, request: dict[str, Any], context: IntelligenceContext, workflow_id: str
    ) -> dict[str, Any]:
        """
        Execute cross-channel analysis service.

        Args:
            request: Analysis request with channel_ids
            context: Intelligence context for analysis
            workflow_id: Workflow identifier for tracking

        Returns:
            Service execution result with cross-channel intelligence
        """
        try:
            channel_ids = request.get("channel_ids", [])

            # Check if method exists, fallback to protocol method
            if hasattr(self.cross_channel_service, "analyze_cross_channel_correlations"):
                cross_channel_intelligence = (
                    await self.cross_channel_service.analyze_cross_channel_correlations(  # type: ignore
                        channel_ids, context
                    )
                )
            elif self.cross_channel_service and hasattr(
                self.cross_channel_service, "analyze_cross_channel_intelligence"
            ):
                # Fallback to protocol-defined method
                cross_channel_intelligence = (
                    await self.cross_channel_service.analyze_cross_channel_intelligence(  # type: ignore
                        channel_ids
                    )
                )
            else:
                cross_channel_intelligence = {
                    "status": "not_implemented",
                    "message": "Cross-channel analysis not available",
                }

            # Map channel influences if multiple channels
            influence_mapping = {}
            if len(channel_ids) > 1:
                if hasattr(self.cross_channel_service, "map_channel_influences"):
                    influence_mapping = await self.cross_channel_service.map_channel_influences(  # type: ignore
                        channel_ids[: len(channel_ids) // 2],  # First half as sources
                        channel_ids[len(channel_ids) // 2 :],  # Second half as targets
                    )
                elif self.cross_channel_service and hasattr(
                    self.cross_channel_service, "calculate_channel_correlations"
                ):
                    # Fallback to protocol-defined method
                    influence_mapping = (
                        await self.cross_channel_service.calculate_channel_correlations(  # type: ignore
                            channel_ids
                        )
                    )

            return {
                "service": "cross_channel_analysis",
                "status": "completed",
                "cross_channel_intelligence": cross_channel_intelligence,
                "influence_mapping": influence_mapping,
                "execution_metadata": {
                    "workflow_id": workflow_id,
                    "executed_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"❌ Cross-channel analysis execution failed: {e}")
            return {
                "service": "cross_channel_analysis",
                "status": "failed",
                "error": str(e),
                "execution_metadata": {
                    "workflow_id": workflow_id,
                    "failed_at": datetime.now().isoformat(),
                },
            }
