"""
Engagement Predictor Service
===========================

Microservice for engagement prediction using LSTM neural networks.
This service has a single responsibility: predicting engagement metrics.
"""

import asyncio
import logging
from datetime import datetime

import torch

from ..infrastructure.gpu_config import GPUConfigService
from ..infrastructure.model_loader import ModelLoader
from .data_processors.engagement_data_processor import EngagementDataProcessor
from .models.lstm_engagement_model import LSTMEngagementModel, LSTMEngagementModelConfig

logger = logging.getLogger(__name__)


class EngagementPredictorService:
    """Microservice for engagement prediction using LSTM neural networks"""

    def __init__(
        self,
        gpu_config: GPUConfigService,
        model_loader: ModelLoader,
        model_config: LSTMEngagementModelConfig | None = None,
    ):
        self.gpu_config = gpu_config
        self.model_loader = model_loader
        self.model_config = model_config or LSTMEngagementModelConfig()

        # Initialize components
        self.device = gpu_config.device
        self.data_processor = EngagementDataProcessor(
            sequence_length=self.model_config.sequence_length
        )

        # Model state
        self.model: LSTMEngagementModel | None = None
        self.model_loaded = False
        self.prediction_count = 0
        self.last_prediction_time: datetime | None = None

        # Performance tracking
        self.prediction_cache = {}
        self.cache_ttl_seconds = 300  # 5 minutes

        logger.info(f"🎯 EngagementPredictorService initialized on {self.device}")

        # Initialize model
        asyncio.create_task(self._initialize_model())

    async def _initialize_model(self) -> None:
        """Initialize the LSTM engagement model"""
        try:
            logger.info("🧠 Initializing LSTM engagement model...")

            # Try to load pre-trained model
            try:
                self.model = await self.model_loader.load_model(
                    "engagement/lstm_engagement_model.pth",
                    "pytorch",
                    model_class=LSTMEngagementModel,
                )
                logger.info("✅ Pre-trained engagement model loaded")
            except Exception as e:
                logger.info(f"ℹ️ No pre-trained model found, creating new model: {e}")

                # Create new model
                self.model = LSTMEngagementModel(
                    input_size=self.model_config.input_size,
                    hidden_size=self.model_config.hidden_size,
                    num_layers=self.model_config.num_layers,
                    dropout_rate=self.model_config.dropout_rate,
                )

                logger.info("✅ New engagement model created")

            # Move model to device and set to eval mode
            if self.model is not None:
                self.model.to(self.device)
                self.model.eval()
                self.model_loaded = True

                # Optimize for inference
                self.gpu_config.optimize_for_inference()

                logger.info(
                    f"🚀 Engagement model ready with {self.model.get_param_count()} parameters"
                )

        except Exception as e:
            logger.error(f"❌ Failed to initialize engagement model: {e}")
            self.model_loaded = False

    async def predict_engagement(
        self, channel_id: int, features: dict, include_confidence: bool = True
    ) -> dict:
        """Predict engagement for given channel and features

        Args:
            channel_id: Telegram channel ID
            features: Feature dictionary for prediction
            include_confidence: Whether to include confidence estimation

        Returns:
            Engagement prediction results
        """
        try:
            if not self.model_loaded or self.model is None:
                return {
                    "error": "Model not loaded",
                    "service": "engagement_predictor",
                    "channel_id": channel_id,
                }

            logger.info(f"🎯 Predicting engagement for channel {channel_id}")

            # Check cache first
            cache_key = f"{channel_id}:{hash(str(sorted(features.items())))}"
            if cache_key in self.prediction_cache:
                cached_result = self.prediction_cache[cache_key]
                if self._is_cache_valid(cached_result["timestamp"]):
                    logger.debug(f"📋 Returning cached prediction for channel {channel_id}")
                    return cached_result["result"]

            # Validate input features
            if not await self.validate_input_features(features):
                return {
                    "error": "Invalid input features",
                    "service": "engagement_predictor",
                    "channel_id": channel_id,
                }

            # Process features
            input_tensor = await self.data_processor.process_features(features)
            input_tensor = input_tensor.to(self.device)

            # Make prediction
            with torch.no_grad():
                if include_confidence:
                    prediction, confidence_std = self.model.predict_with_confidence(input_tensor)
                    confidence_score = float(
                        1.0 / (1.0 + confidence_std.item())
                    )  # Convert std to confidence
                else:
                    prediction = self.model(input_tensor)
                    confidence_score = 0.8  # Default confidence

                predicted_engagement = float(prediction.item())

            # Get feature importance (with better error handling)
            try:
                # Create a copy of input tensor with gradients for feature importance
                importance_tensor = input_tensor.detach().clone().requires_grad_(True)
                feature_importance = self.model.get_feature_importance(importance_tensor)
            except Exception as e:
                logger.debug(f"Feature importance calculation failed: {e}")
                feature_importance = {}

            # Create result
            result = {
                "channel_id": channel_id,
                "predicted_engagement": predicted_engagement,
                "confidence_score": confidence_score,
                "prediction_range": {
                    "min": max(0.0, predicted_engagement - 0.1),
                    "max": min(1.0, predicted_engagement + 0.1),
                },
                "feature_importance": feature_importance,
                "model_info": {
                    "version": self.model.version,
                    "architecture": "LSTM",
                    "parameters": self.model.get_param_count(),
                },
                "prediction_metadata": {
                    "timestamp": datetime.utcnow(),
                    "prediction_id": f"eng_{channel_id}_{int(datetime.utcnow().timestamp())}",
                    "processing_time_ms": 0,  # Will be updated
                    "device": str(self.device),
                },
                "service": "engagement_predictor",
            }

            # Cache result
            self.prediction_cache[cache_key] = {
                "result": result,
                "timestamp": datetime.utcnow(),
            }

            # Update counters
            self.prediction_count += 1
            self.last_prediction_time = datetime.utcnow()

            logger.info(
                f"✅ Engagement prediction completed: {predicted_engagement:.3f} (confidence: {confidence_score:.3f})"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Engagement prediction failed for channel {channel_id}: {e}")
            return {
                "error": str(e),
                "service": "engagement_predictor",
                "channel_id": channel_id,
                "timestamp": datetime.utcnow(),
            }

    async def batch_predict_engagement(self, requests: list[dict]) -> list[dict]:
        """Batch engagement prediction for multiple requests

        Args:
            requests: List of prediction requests, each containing 'channel_id' and 'features'

        Returns:
            List of prediction results
        """
        try:
            logger.info(f"📦 Processing batch prediction for {len(requests)} requests")

            if not self.model_loaded or self.model is None:
                return [
                    {"error": "Model not loaded", "service": "engagement_predictor"}
                    for _ in requests
                ]

            # Validate batch size
            max_batch_size = self.gpu_config.get_optimal_batch_size(model_size_mb=10)
            if len(requests) > max_batch_size:
                # Process in chunks
                results = []
                for i in range(0, len(requests), max_batch_size):
                    chunk = requests[i : i + max_batch_size]
                    chunk_results = await self.batch_predict_engagement(chunk)
                    results.extend(chunk_results)
                return results

            # Process all requests
            batch_tensors = []
            valid_requests = []

            for request in requests:
                channel_id = request.get("channel_id")
                features = request.get("features", {})

                if await self.validate_input_features(features):
                    input_tensor = await self.data_processor.process_features(features)
                    batch_tensors.append(input_tensor.squeeze(0))  # Remove batch dimension
                    valid_requests.append(request)
                else:
                    # Add error result for invalid request
                    valid_requests.append(
                        {
                            **request,
                            "error": "Invalid features",
                            "service": "engagement_predictor",
                        }
                    )

            if not batch_tensors:
                return [
                    {"error": "No valid requests", "service": "engagement_predictor"}
                    for _ in requests
                ]

            # Create batch tensor
            batch_tensor = torch.stack(batch_tensors).to(self.device)

            # Batch prediction
            with torch.no_grad():
                batch_predictions = self.model(batch_tensor)

            # Process results
            results = []
            prediction_idx = 0

            for i, request in enumerate(valid_requests):
                if "error" in request:
                    results.append(request)
                else:
                    channel_id = request["channel_id"]
                    predicted_engagement = float(batch_predictions[prediction_idx].item())

                    result = {
                        "channel_id": channel_id,
                        "predicted_engagement": predicted_engagement,
                        "confidence_score": 0.8,  # Default for batch processing
                        "model_info": {
                            "version": self.model.version,
                            "architecture": "LSTM",
                        },
                        "prediction_metadata": {
                            "timestamp": datetime.utcnow(),
                            "prediction_id": f"eng_batch_{channel_id}_{i}",
                            "batch_size": len(batch_tensors),
                        },
                        "service": "engagement_predictor",
                    }

                    results.append(result)
                    prediction_idx += 1

            self.prediction_count += len(results)
            logger.info(f"✅ Batch prediction completed: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"❌ Batch prediction failed: {e}")
            return [{"error": str(e), "service": "engagement_predictor"} for _ in requests]

    async def validate_input_features(self, features: dict) -> bool:
        """Validate input features format and content

        Args:
            features: Input features to validate

        Returns:
            True if valid, False otherwise
        """
        return self.data_processor.validate_features(features)

    async def get_model_info(self) -> dict:
        """Get model information and metadata

        Returns:
            Dictionary with model details
        """
        if not self.model_loaded or self.model is None:
            return {"error": "Model not loaded", "service": "engagement_predictor"}

        return {
            "service": "engagement_predictor",
            "model": self.model.get_model_info(),
            "configuration": self.model_config.to_dict(),
            "device": str(self.device),
            "data_processor": self.data_processor.get_service_health(),
            "performance": {
                "predictions_made": self.prediction_count,
                "last_prediction": self.last_prediction_time,
                "cache_size": len(self.prediction_cache),
            },
        }

    async def get_service_health(self) -> dict:
        """Get service health status

        Returns:
            Dictionary with health information
        """
        model_status = "healthy" if self.model_loaded else "unhealthy"

        return {
            "service": "engagement_predictor",
            "status": model_status,
            "model_loaded": self.model_loaded,
            "device": str(self.device),
            "device_available": self.gpu_config.is_gpu_available(),
            "predictions_made": self.prediction_count,
            "last_prediction": self.last_prediction_time,
            "cache_entries": len(self.prediction_cache),
            "model_parameters": self.model.get_param_count() if self.model else 0,
        }

    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cached result is still valid"""
        return (datetime.utcnow() - timestamp).total_seconds() < self.cache_ttl_seconds

    async def clear_cache(self) -> dict:
        """Clear prediction cache"""
        cache_size = len(self.prediction_cache)
        self.prediction_cache.clear()

        return {
            "cache_cleared": True,
            "entries_cleared": cache_size,
            "service": "engagement_predictor",
        }

    async def save_model(self, model_path: str | None = None) -> bool:
        """Save current model to file

        Args:
            model_path: Optional path to save model (default: engagement/lstm_engagement_model.pth)

        Returns:
            True if successful, False otherwise
        """
        if not self.model_loaded or self.model is None:
            logger.error("Cannot save model: model not loaded")
            return False

        if model_path is None:
            model_path = "engagement/lstm_engagement_model.pth"

        try:
            success = await self.model_loader.save_model(
                self.model,
                model_path,
                "pytorch",
                metadata={
                    "service": "engagement_predictor",
                    "configuration": self.model_config.to_dict(),
                    "predictions_made": self.prediction_count,
                    "saved_at": datetime.utcnow().isoformat(),
                },
            )

            if success:
                logger.info(f"✅ Model saved to {model_path}")
            else:
                logger.error(f"❌ Failed to save model to {model_path}")

            return success

        except Exception as e:
            logger.error(f"❌ Model save failed: {e}")
            return False
