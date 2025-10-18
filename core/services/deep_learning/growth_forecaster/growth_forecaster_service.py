"""
Growth Forecaster Service - Microservices Orchestrator
======================================================

Backwards compatible orchestrator that delegates to specialized microservices.
Maintains 100% API compatibility with the original fat service.

Microservices Architecture:
- PredictionEngine: Core ML prediction logic
- DataAnalyzer: Data processing and pattern analysis
- ModelManager: Model lifecycle management
- CacheService: Prediction result caching
- TaskProcessor: Async task processing
- ResultFormatter: Result processing and formatting
"""

import logging
from datetime import datetime
from typing import Any

import pandas as pd

from core.ports.task_client_port import TaskClientProtocol
from core.services.deep_learning.growth.data_processors.growth_data_processor import (
    GrowthDataProcessor,
)
from core.services.deep_learning.growth.models.gru_growth_model import (
    GRUGrowthModel,
    GRUGrowthModelConfig,
)
from core.services.deep_learning.infrastructure.gpu_config import GPUConfigService
from core.services.deep_learning.infrastructure.model_loader import ModelLoader

from .cache_service import CacheService
from .data_analyzer import DataAnalyzer
from .model_manager import ModelManager
from .models import PredictionRequest, PredictionResult
from .prediction_engine import PredictionEngine
from .result_formatter import ResultFormatter
from .task_processor import TaskProcessor

logger = logging.getLogger(__name__)


class GrowthForecasterService:
    """
    Backwards compatible growth forecaster orchestrator.

    Delegates to specialized microservices while maintaining original API.
    """

    def __init__(
        self,
        gpu_config: GPUConfigService,
        model_loader: ModelLoader,
        task_client: TaskClientProtocol | None = None,
        model_config: GRUGrowthModelConfig | None = None,
        cache_predictions: bool = True,
        max_cache_size: int = 1000,
    ):
        # Store original dependencies
        self.gpu_config = gpu_config
        self.model_loader = model_loader
        self.task_client = task_client
        self.model_config = model_config or GRUGrowthModelConfig()

        # Initialize components
        self._initialize_components()

        # Initialize microservices
        self._initialize_microservices(cache_predictions, max_cache_size)

        # Legacy health stats for backwards compatibility
        self.health_stats = {
            "predictions_made": 0,
            "errors": 0,
            "model_loaded": False,
            "last_prediction_time": None,
            "uncertainty_estimations": 0,
        }

        # Legacy cache stats
        self.prediction_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.max_cache_size = max_cache_size

        logger.info("🎭 Growth Forecaster Service orchestrator initialized")

    def _initialize_components(self):
        """Initialize neural network components"""
        try:
            logger.info("🔧 Initializing growth forecaster components...")

            # Set device
            self.device = self.gpu_config.device

            # Initialize model
            self.model = GRUGrowthModel(
                input_size=self.model_config.input_size,
                hidden_size=self.model_config.hidden_size,
                num_layers=self.model_config.num_layers,
                dropout_rate=self.model_config.dropout_rate,
                output_size=self.model_config.output_size,
                use_attention=self.model_config.use_attention,
            ).to(self.device)

            # Initialize data processor
            self.data_processor = GrowthDataProcessor(
                sequence_length=self.model_config.sequence_length,
            )

            logger.info("✅ Growth forecaster components initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize components: {e}")
            raise

    def _initialize_microservices(self, cache_predictions: bool, max_cache_size: int):
        """Initialize all microservices"""
        try:
            logger.info("🏗️ Initializing microservices...")

            # Initialize microservices
            self.prediction_engine = PredictionEngine(
                model=self.model, device=self.device, data_processor=self.data_processor
            )

            self.data_analyzer = DataAnalyzer(data_processor=self.data_processor)

            self.model_manager = ModelManager(
                model_loader=self.model_loader,
                gpu_config=self.gpu_config,
                model_config=self.model_config,
            )

            self.cache_service = (
                CacheService(max_cache_size=max_cache_size) if cache_predictions else None
            )

            self.task_processor = (
                TaskProcessor(task_client=self.task_client) if self.task_client else None
            )

            self.result_formatter = ResultFormatter()

            # Set cross-references
            self.model_manager.set_data_processor(self.data_processor)

            logger.info("✅ All microservices initialized successfully")

        except Exception as e:
            logger.error(f"❌ Microservices initialization failed: {e}")
            raise

    # ===== BACKWARDS COMPATIBLE API METHODS =====

    async def predict_growth(
        self,
        data: pd.DataFrame | list[dict] | dict,
        forecast_horizon: int = 1,
        include_uncertainty: bool = True,
        return_attention: bool = False,
    ) -> dict[str, Any]:
        """
        Predict growth with uncertainty estimation (BACKWARDS COMPATIBLE)

        Original API maintained - delegates to microservices internally.
        """
        try:
            logger.info(f"🎯 Orchestrating growth prediction for horizon: {forecast_horizon}")

            # Check cache first
            cache_key = None
            if self.cache_service:
                request = PredictionRequest(
                    data=data,
                    forecast_periods=forecast_horizon,
                    include_uncertainty=include_uncertainty,
                )
                cache_key = self.cache_service.generate_key(request)
                cached_result = self.cache_service.get_cached_result(cache_key)

                if cached_result:
                    self.cache_hits += 1
                    return self._convert_to_legacy_format(cached_result, return_attention)

            self.cache_misses += 1

            # Create prediction request
            prediction_request = PredictionRequest(
                data=data,
                forecast_periods=forecast_horizon,
                include_uncertainty=include_uncertainty,
            )

            # Execute prediction via microservice
            result = await self.prediction_engine.predict_growth(prediction_request)

            # Format result
            metadata = {
                "model_version": result.model_version,
                "execution_time_ms": result.execution_time_ms,
                "uncertainty_score": result.uncertainty_score,
                "confidence_lower": result.confidence_lower,
                "confidence_upper": result.confidence_upper,
                "cached": result.cached,
                "confidence_interval": prediction_request.confidence_interval,
            }

            formatted_result = self.result_formatter.format_result(result.predictions, metadata)

            # Cache result if enabled
            if self.cache_service and cache_key:
                self.cache_service.cache_result(cache_key, result)

            # Update legacy health stats
            self.health_stats["predictions_made"] += 1
            self.health_stats["last_prediction_time"] = datetime.now().isoformat()
            if include_uncertainty:
                self.health_stats["uncertainty_estimations"] += 1

            # Convert to legacy format
            legacy_result = self._convert_formatted_to_legacy(formatted_result, return_attention)

            logger.info("✅ Growth prediction orchestration completed")
            return legacy_result

        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Growth prediction orchestration failed: {e}")
            raise

    async def predict_growth_batch(
        self,
        data_batch: list[pd.DataFrame | dict],
        forecast_horizon: int = 1,
        include_uncertainty: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Predict growth for multiple datasets (BACKWARDS COMPATIBLE)
        """
        try:
            logger.info(f"🔄 Orchestrating batch of {len(data_batch)} predictions")

            # Create prediction requests
            requests = []
            for data in data_batch:
                request = PredictionRequest(
                    data=data,
                    forecast_periods=forecast_horizon,
                    include_uncertainty=include_uncertainty,
                )
                requests.append(request)

            # Execute batch prediction
            results = await self.prediction_engine.predict_batch(requests)

            # Format results
            legacy_results = []
            for result in results:
                metadata = {
                    "model_version": result.model_version,
                    "execution_time_ms": result.execution_time_ms,
                    "uncertainty_score": result.uncertainty_score,
                    "confidence_lower": result.confidence_lower,
                    "confidence_upper": result.confidence_upper,
                }

                formatted = self.result_formatter.format_result(result.predictions, metadata)
                legacy_format = self._convert_formatted_to_legacy(formatted, return_attention=False)
                legacy_results.append(legacy_format)

            logger.info(
                f"✅ Batch prediction orchestration completed: {len(legacy_results)} results"
            )
            return legacy_results

        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Batch prediction orchestration failed: {e}")
            raise

    def analyze_growth_patterns(self, data: pd.DataFrame) -> dict[str, Any]:
        """
        Analyze growth patterns and trends (BACKWARDS COMPATIBLE)
        """
        try:
            logger.info("📊 Orchestrating growth pattern analysis")

            # Delegate to data analyzer microservice
            analysis_result = self.data_analyzer.analyze_patterns(data)

            logger.info("✅ Growth pattern analysis orchestration completed")
            return analysis_result

        except Exception as e:
            logger.error(f"❌ Growth pattern analysis orchestration failed: {e}")
            raise

    async def predict_growth_via_celery(
        self,
        data: pd.DataFrame | list[dict] | dict,
        forecast_horizon: int = 1,
        include_uncertainty: bool = True,
        task_priority: str = "normal",
    ) -> str:
        """
        Submit prediction task via Celery (BACKWARDS COMPATIBLE)
        """
        try:
            logger.info("📤 Orchestrating async prediction task")

            if not self.task_processor:
                raise RuntimeError("Task processor not available")

            # Create request and submit to task processor
            request = PredictionRequest(
                data=data,
                forecast_periods=forecast_horizon,
                include_uncertainty=include_uncertainty,
            )

            task_id = await self.task_processor.process_async_prediction(request)

            logger.info(f"✅ Async task orchestration completed: {task_id}")
            return task_id

        except Exception as e:
            logger.error(f"❌ Async task orchestration failed: {e}")
            raise

    def predict_growth_sync(
        self,
        data: pd.DataFrame | list[dict] | dict,
        forecast_horizon: int = 1,
        include_uncertainty: bool = True,
    ) -> dict[str, Any]:
        """
        Synchronous prediction (BACKWARDS COMPATIBLE)
        """
        try:
            logger.info("🔄 Orchestrating synchronous prediction")

            # Create request
            request = PredictionRequest(
                data=data,
                forecast_periods=forecast_horizon,
                include_uncertainty=include_uncertainty,
            )

            # Execute sync prediction
            result = self.prediction_engine.predict_sync(request)

            # Format result
            metadata = {
                "model_version": result.model_version,
                "execution_time_ms": result.execution_time_ms,
                "uncertainty_score": result.uncertainty_score,
            }

            formatted_result = self.result_formatter.format_result(result.predictions, metadata)
            legacy_result = self._convert_formatted_to_legacy(
                formatted_result, return_attention=False
            )

            logger.info("✅ Synchronous prediction orchestration completed")
            return legacy_result

        except Exception as e:
            logger.error(f"❌ Synchronous prediction orchestration failed: {e}")
            raise

    async def load_pretrained_model(self, model_path: str) -> bool:
        """
        Load a pre-trained model (BACKWARDS COMPATIBLE)
        """
        try:
            logger.info(f"📥 Orchestrating model loading: {model_path}")

            success = await self.model_manager.load_model(model_path)

            if success:
                # Update current model reference in prediction engine
                self.model = self.model_manager.get_model()
                self.prediction_engine.model = self.model
                self.health_stats["model_loaded"] = True

            logger.info(f"✅ Model loading orchestration completed: {success}")
            return success

        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Model loading orchestration failed: {e}")
            return False

    async def save_model(self, model_path: str, include_processor: bool = True) -> bool:
        """
        Save current model (BACKWARDS COMPATIBLE)
        """
        try:
            logger.info(f"💾 Orchestrating model saving: {model_path}")

            success = await self.model_manager.save_model(model_path, include_processor)

            logger.info(f"✅ Model saving orchestration completed: {success}")
            return success

        except Exception as e:
            self.health_stats["errors"] += 1
            logger.error(f"❌ Model saving orchestration failed: {e}")
            return False

    def get_service_health(self) -> dict[str, Any]:
        """
        Get service health status (BACKWARDS COMPATIBLE)
        """
        try:
            # Aggregate health from all microservices
            service_healths = {
                "prediction_engine": self.prediction_engine.get_health(),
                "data_analyzer": self.data_analyzer.get_health(),
                "model_manager": self.model_manager.get_health(),
            }

            if self.cache_service:
                service_healths["cache_service"] = self.cache_service.get_health()

            if self.task_processor:
                service_healths["task_processor"] = self.task_processor.get_health()

            service_healths["result_formatter"] = self.result_formatter.get_health()

            # Calculate overall health
            all_healthy = all(health.is_healthy for health in service_healths.values())

            # Return legacy format
            legacy_health = {
                **self.health_stats,
                "overall_healthy": all_healthy,
                "microservices": {
                    name: health.is_healthy for name, health in service_healths.items()
                },
                "cache_stats": (self.cache_service.get_cache_stats() if self.cache_service else {}),
                "last_health_check": datetime.utcnow().isoformat(),
            }

            return legacy_health

        except Exception as e:
            logger.error(f"❌ Health check orchestration failed: {e}")
            return {**self.health_stats, "error": str(e)}

    def clear_cache(self):
        """
        Clear prediction cache (BACKWARDS COMPATIBLE)
        """
        try:
            if self.cache_service:
                self.cache_service.clear_cache()

            # Reset legacy counters
            self.cache_hits = 0
            self.cache_misses = 0
            self.prediction_cache.clear()

            logger.info("🧹 Cache clearing orchestration completed")

        except Exception as e:
            logger.error(f"❌ Cache clearing orchestration failed: {e}")

    # ===== PRIVATE HELPER METHODS =====

    def _convert_to_legacy_format(
        self, result: PredictionResult, return_attention: bool
    ) -> dict[str, Any]:
        """Convert microservice result to legacy API format"""
        try:
            legacy_result = {
                "predictions": (result.predictions.tolist() if result.predictions.size > 0 else []),
                "execution_time_ms": result.execution_time_ms,
                "model_version": result.model_version,
                "cached": result.cached,
            }

            if result.uncertainty_score is not None:
                legacy_result["uncertainty_score"] = result.uncertainty_score

            if result.confidence_lower is not None:
                legacy_result["confidence_intervals"] = {
                    "lower": result.confidence_lower.tolist(),
                    "upper": (
                        result.confidence_upper.tolist()
                        if result.confidence_upper is not None
                        else []
                    ),
                }

            if return_attention:
                # Attention weights not implemented in microservice version
                legacy_result["attention_weights"] = []

            return legacy_result

        except Exception as e:
            logger.error(f"❌ Legacy format conversion failed: {e}")
            return {"error": str(e)}

    def _convert_formatted_to_legacy(
        self, formatted_result: dict[str, Any], return_attention: bool
    ) -> dict[str, Any]:
        """Convert formatted result to legacy format"""
        try:
            predictions = formatted_result.get("predictions", {})
            metadata = formatted_result.get("metadata", {})

            legacy_result = {
                "predictions": predictions.get("values", []),
                "execution_time_ms": metadata.get("execution_time_ms", 0),
                "model_version": metadata.get("model_version", "unknown"),
                "cached": metadata.get("cached", False),
            }

            # Add uncertainty if available
            if metadata.get("uncertainty_score"):
                legacy_result["uncertainty_score"] = metadata["uncertainty_score"]

            # Add confidence intervals if available
            confidence = formatted_result.get("confidence", {})
            if "lower_bounds" in confidence:
                legacy_result["confidence_intervals"] = {
                    "lower": confidence["lower_bounds"],
                    "upper": confidence.get("upper_bounds", []),
                }

            if return_attention:
                legacy_result["attention_weights"] = []

            return legacy_result

        except Exception as e:
            logger.error(f"❌ Formatted to legacy conversion failed: {e}")
            return {"error": str(e)}
