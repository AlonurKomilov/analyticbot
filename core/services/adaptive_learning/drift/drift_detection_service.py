"""
Drift Detection Service
======================

Clean architecture replacement for the monolithic DriftDetectionService.
Delegates to specialized analyzers while maintaining the original interface.
"""

import logging
from typing import Any

import numpy as np

from .drift_analysis import (
    ComprehensiveDriftAnalysis,
    DriftCoordinator,
    DriftCoordinatorConfig,
    MultivariateDriftAnalyzer,
    StatisticalDriftAnalyzer,
)
from .protocols.drift_protocols import DriftAlert, DriftDetectionProtocol
from .protocols.monitoring_protocols import MonitoringServiceProtocol

logger = logging.getLogger(__name__)


class DriftDetectionService(DriftDetectionProtocol):
    """
    Clean, focused drift detection service.

    Replaces the 1014-line god object with a clean coordinator pattern.
    Maintains compatibility while delegating to specialized analyzers.
    """

    def __init__(
        self,
        monitoring_service: MonitoringServiceProtocol,
        config: DriftCoordinatorConfig | None = None,
    ):
        # Create specialized analyzers
        self.statistical_analyzer = StatisticalDriftAnalyzer()
        self.multivariate_analyzer = MultivariateDriftAnalyzer()

        # Create coordinator
        self.coordinator = DriftCoordinator(
            statistical_analyzer=self.statistical_analyzer,
            multivariate_analyzer=self.multivariate_analyzer,
            monitoring_service=monitoring_service,
            config=config or DriftCoordinatorConfig(),
        )

        logger.info("🎯 Clean DriftDetectionService initialized")

    async def start_monitoring(self) -> bool:
        """Start drift monitoring"""
        return await self.coordinator.start_monitoring()

    async def stop_monitoring(self) -> bool:
        """Stop drift monitoring"""
        return await self.coordinator.stop_monitoring()

    async def add_model_monitoring(
        self, model_id: str, reference_data: np.ndarray | None = None
    ) -> bool:
        """Add model to monitoring"""
        return await self.coordinator.add_model_monitoring(model_id, reference_data)

    async def remove_model_monitoring(self, model_id: str) -> bool:
        """Remove model from monitoring"""
        return await self.coordinator.remove_model_monitoring(model_id)

    async def detect_data_drift(
        self,
        model_id: str,
        current_data: np.ndarray,
        feature_names: list[str] | None = None,
    ) -> ComprehensiveDriftAnalysis | None:
        """Detect data drift"""
        return await self.coordinator.detect_data_drift(model_id, current_data, feature_names)

    async def detect_concept_drift(
        self, model_id: str, current_performance: dict[str, float]
    ) -> ComprehensiveDriftAnalysis | None:
        """Detect concept drift"""
        return await self.coordinator.detect_concept_drift(model_id, current_performance)

    async def get_drift_status(self, model_id: str) -> dict[str, Any]:
        """Get drift status"""
        return await self.coordinator.get_drift_status(model_id)

    async def get_active_alerts(self, model_id: str | None = None) -> list[DriftAlert]:
        """Get active alerts"""
        return await self.coordinator.get_active_alerts(model_id)

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert"""
        return await self.coordinator.resolve_alert(alert_id)

    def get_service_health(self) -> dict[str, Any]:
        """Get service health"""
        return self.coordinator.get_service_health()

    async def shutdown(self) -> None:
        """Shutdown service"""
        await self.coordinator.shutdown()
