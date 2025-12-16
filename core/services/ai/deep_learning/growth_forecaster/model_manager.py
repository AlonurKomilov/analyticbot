"""
Model Manager Service
====================

Microservice responsible for model lifecycle management.
Handles model loading, saving, versioning, and initialization.
"""

import logging
from datetime import datetime
from typing import Any

from .models import (
    HealthMetrics,
    ModelInfo,
    ModelManagerProtocol,
    ServiceHealth,
)

logger = logging.getLogger(__name__)


class ModelManager(ModelManagerProtocol):
    """
    Model lifecycle management service.

    Single responsibility: Model persistence, loading, and metadata management.
    """

    def __init__(
        self,
        model_loader: Any,  # ModelLoader service
        gpu_config: Any,  # GPUConfigService
        model_config: Any = None,  # GRUGrowthModelConfig
    ):
        self.model_loader = model_loader
        self.gpu_config = gpu_config
        self.model_config = model_config

        # Model state
        self.current_model = None
        self.model_metadata: ModelInfo | None = None

        # Health tracking
        self.health_metrics = HealthMetrics()

        logger.info("🗄️ Model Manager initialized")

    async def load_model(self, model_path: str) -> bool:
        """
        Load a pretrained model from disk

        Args:
            model_path: Path to the saved model file

        Returns:
            True if loading successful, False otherwise
        """
        try:
            logger.info(f"📥 Loading model from: {model_path}")

            # Load model using model loader service
            model_info = await self.model_loader.load_model(model_path, "pytorch")

            if model_info and "model" in model_info:
                # Move model to appropriate device
                device = self.gpu_config.device if self.gpu_config else "cpu"
                self.current_model = model_info["model"].to(device)

                if self.current_model:
                    self.current_model.eval()

                    # Create model metadata
                    self.model_metadata = ModelInfo(
                        model_path=model_path,
                        version=model_info.get("version", "unknown"),
                        created_at=datetime.utcnow(),
                        metrics=model_info.get("metrics", {}),
                        config=model_info.get("config", {}),
                    )

                    # Update health metrics
                    self.health_metrics.successful_predictions += 1
                    self.health_metrics.last_prediction_time = datetime.utcnow()

                    logger.info(f"✅ Model loaded successfully from: {model_path}")
                    return True
                else:
                    logger.error("❌ Failed to initialize loaded model")
                    return False
            else:
                logger.error(f"❌ Invalid model data loaded from: {model_path}")
                return False

        except Exception as e:
            self.health_metrics.failed_predictions += 1
            logger.error(f"❌ Model loading failed: {e}")
            return False

    async def save_model(self, model_path: str, include_processor: bool = True) -> bool:
        """
        Save current model to disk

        Args:
            model_path: Path where model should be saved
            include_processor: Whether to include data processor in save

        Returns:
            True if saving successful, False otherwise
        """
        try:
            logger.info(f"💾 Saving model to: {model_path}")

            if self.current_model is None:
                raise RuntimeError("No model loaded to save")

            # Prepare model information for saving
            model_info = {
                "model": self.current_model,
                "version": self.model_metadata.version if self.model_metadata else "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "config": self.model_config.to_dict() if self.model_config else {},
                "model_state": self._get_model_state_info(),
                "health_metrics": {
                    "total_predictions": self.health_metrics.total_predictions,
                    "successful_predictions": self.health_metrics.successful_predictions,
                    "average_response_time": self.health_metrics.average_response_time_ms,
                },
            }

            # Add processor if requested and available
            if include_processor and hasattr(self, "data_processor") and self.data_processor:
                model_info["data_processor"] = self.data_processor

            # Save using model loader service
            success = await self.model_loader.save_model(model_info, model_path, "pytorch")

            if success:
                # Update metadata
                if self.model_metadata:
                    self.model_metadata.model_path = model_path
                    self.model_metadata.created_at = datetime.utcnow()

                self.health_metrics.successful_predictions += 1
                logger.info(f"✅ Model saved successfully to: {model_path}")
                return True
            else:
                logger.error(f"❌ Model saving failed for path: {model_path}")
                return False

        except Exception as e:
            self.health_metrics.failed_predictions += 1
            logger.error(f"❌ Model saving failed: {e}")
            return False

    def get_model_info(self) -> ModelInfo:
        """
        Get information about currently loaded model

        Returns:
            Model information and metadata
        """
        try:
            if self.model_metadata:
                return self.model_metadata

            # Create basic info if no metadata available
            return ModelInfo(
                model_path="unknown",
                version="unknown",
                created_at=datetime.utcnow(),
                metrics={},
                config={},
            )

        except Exception as e:
            logger.error(f"❌ Failed to get model info: {e}")
            return ModelInfo(
                model_path="error",
                version="error",
                created_at=datetime.utcnow(),
                metrics={},
                config={},
            )

    def initialize_model(self, model_class: Any, **kwargs) -> bool:
        """
        Initialize a new model instance

        Args:
            model_class: Model class to instantiate
            **kwargs: Model initialization parameters

        Returns:
            True if initialization successful
        """
        try:
            logger.info("🔧 Initializing new model instance")

            # Get device configuration
            device = self.gpu_config.device if self.gpu_config else "cpu"

            # Create model instance
            if self.model_config:
                model = model_class(self.model_config, **kwargs)
            else:
                model = model_class(**kwargs)

            # Move to appropriate device
            self.current_model = model.to(device)

            # Create metadata
            self.model_metadata = ModelInfo(
                model_path="initialized",
                version="new",
                created_at=datetime.utcnow(),
                metrics={},
                config=kwargs,
            )

            logger.info("✅ Model initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Model initialization failed: {e}")
            return False

    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded"""
        return self.current_model is not None

    def get_model(self) -> Any:
        """Get reference to current model (use with caution)"""
        return self.current_model

    def set_data_processor(self, processor: Any):
        """Set data processor reference for saving"""
        self.data_processor = processor

    def get_health(self) -> ServiceHealth:
        """Get model manager health status"""
        try:
            is_healthy = (
                self.current_model is not None
                and self.model_loader is not None
                and self.health_metrics.failed_predictions
                <= self.health_metrics.successful_predictions
            )

            return ServiceHealth(
                service_name="model_manager",
                is_healthy=is_healthy,
                metrics=self.health_metrics,
                last_check=datetime.utcnow(),
            )

        except Exception as e:
            return ServiceHealth(
                service_name="model_manager",
                is_healthy=False,
                metrics=HealthMetrics(),
                error_message=str(e),
            )

    # Private helper methods

    def _get_model_state_info(self) -> dict[str, Any]:
        """Extract model state information"""
        try:
            if self.current_model is None:
                return {}

            state_info = {
                "model_type": type(self.current_model).__name__,
                "parameters": sum(p.numel() for p in self.current_model.parameters()),
                "trainable_parameters": sum(
                    p.numel() for p in self.current_model.parameters() if p.requires_grad
                ),
                "device": str(next(self.current_model.parameters()).device)
                if list(self.current_model.parameters())
                else "unknown",
                "training_mode": self.current_model.training,
            }

            # Add model-specific info if available
            if hasattr(self.current_model, "get_model_info"):
                model_specific = self.current_model.get_model_info()
                state_info.update(model_specific)

            return state_info

        except Exception as e:
            logger.error(f"❌ Failed to get model state info: {e}")
            return {"error": str(e)}
