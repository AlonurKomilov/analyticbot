"""
Prediction Engine Service
========================

Microservice responsible for core ML prediction functionality.
Handles neural network inference and growth forecasting logic.
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import torch

from core.services.deep_learning.growth.models.gru_growth_model import GRUGrowthModel

from .models import (
    HealthMetrics,
    PredictionEngineProtocol,
    PredictionRequest,
    PredictionResult,
    ServiceHealth,
)

logger = logging.getLogger(__name__)


class PredictionEngine(PredictionEngineProtocol):
    """
    Neural network prediction engine for growth forecasting.

    Single responsibility: Execute ML predictions using GRU + Attention models.
    """

    def __init__(
        self,
        model: GRUGrowthModel,
        device: torch.device,
        data_processor: Any,  # GrowthDataProcessor
    ):
        self.model = model
        self.device = device
        self.data_processor = data_processor

        # Health tracking
        self.health_metrics = HealthMetrics()

        logger.info("🧠 Prediction Engine initialized")

    async def predict_growth(self, request: PredictionRequest) -> PredictionResult:
        """
        Make growth prediction using neural network

        Args:
            request: Prediction request with data and parameters

        Returns:
            Prediction result with forecasts and metadata
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"🎯 Making growth prediction for {request.forecast_periods} periods")

            # Prepare input data
            df = self._prepare_input_data(request.data)

            # Validate model is ready
            if self.model is None or self.data_processor is None:
                raise RuntimeError("Prediction engine not properly initialized")

            # Process data for model
            if not self.data_processor.is_fitted:
                X_scaled, _ = self.data_processor.fit_transform(df)
            else:
                X_sequences, _ = self.data_processor.create_sequences(df)
                X_scaled = self.data_processor._transform_sequences(X_sequences)

            # Convert to tensor
            X_tensor = torch.FloatTensor(X_scaled).to(self.device)

            # Generate predictions
            predictions = []
            uncertainty_list = []

            current_sequence = X_tensor[-1:].clone()

            self.model.eval()
            with torch.no_grad():
                for step in range(request.forecast_periods):
                    # Single prediction
                    pred, _ = self.model(current_sequence)
                    predictions.append(pred.cpu().numpy())

                    # Uncertainty estimation if requested
                    if request.include_uncertainty:
                        _, uncertainty, _ = self.model.predict_with_uncertainty(
                            current_sequence, mc_samples=30
                        )
                        uncertainty_list.append(uncertainty.cpu().numpy())

                    # Update sequence for next prediction
                    if step < request.forecast_periods - 1:
                        new_features = self._create_features_from_prediction(pred.cpu().numpy())
                        new_sequence = torch.cat(
                            [
                                current_sequence[:, 1:, :],
                                torch.FloatTensor(new_features).unsqueeze(0).to(self.device),
                            ],
                            dim=1,
                        )
                        current_sequence = new_sequence

            # Process results
            result = self._create_prediction_result(
                predictions, uncertainty_list if request.include_uncertainty else None, start_time
            )

            # Update health metrics
            self.health_metrics.total_predictions += 1
            self.health_metrics.successful_predictions += 1
            self.health_metrics.last_prediction_time = datetime.utcnow()

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_response_time(execution_time)

            logger.info(f"✅ Prediction completed in {execution_time:.1f}ms")
            return result

        except Exception as e:
            self.health_metrics.total_predictions += 1
            self.health_metrics.failed_predictions += 1
            logger.error(f"❌ Prediction failed: {e}")
            raise

    async def predict_batch(self, requests: list[PredictionRequest]) -> list[PredictionResult]:
        """
        Make batch predictions for multiple requests

        Args:
            requests: List of prediction requests

        Returns:
            List of prediction results
        """
        try:
            logger.info(f"🔄 Processing batch of {len(requests)} predictions")

            results = []
            for i, request in enumerate(requests):
                try:
                    result = await self.predict_growth(request)
                    results.append(result)

                except Exception as e:
                    logger.error(f"❌ Batch prediction {i} failed: {e}")
                    # Create error result
                    error_result = PredictionResult(
                        predictions=np.array([]), execution_time_ms=0, model_version="error"
                    )
                    results.append(error_result)

            logger.info(f"✅ Batch processing completed: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"❌ Batch prediction failed: {e}")
            raise

    def predict_sync(self, request: PredictionRequest) -> PredictionResult:
        """
        Synchronous prediction (blocking call)

        Args:
            request: Prediction request

        Returns:
            Prediction result
        """
        try:
            logger.info("🔄 Making synchronous prediction")

            # Use asyncio to run async method synchronously
            import asyncio

            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in a loop, create a task
                task = loop.create_task(self.predict_growth(request))
                return task.result()  # This will block until complete
            except RuntimeError:
                # No event loop running, create one
                return asyncio.run(self.predict_growth(request))

        except Exception as e:
            logger.error(f"❌ Sync prediction failed: {e}")
            raise

    def get_health(self) -> ServiceHealth:
        """Get prediction engine health status"""
        try:
            success_rate = (
                self.health_metrics.successful_predictions / self.health_metrics.total_predictions
                if self.health_metrics.total_predictions > 0
                else 1.0
            )

            is_healthy = (
                success_rate >= 0.95 and self.model is not None and self.data_processor is not None
            )

            return ServiceHealth(
                service_name="prediction_engine",
                is_healthy=is_healthy,
                metrics=self.health_metrics,
                last_check=datetime.utcnow(),
            )

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return ServiceHealth(
                service_name="prediction_engine",
                is_healthy=False,
                metrics=HealthMetrics(),
                error_message=str(e),
            )

    # Private helper methods

    def _prepare_input_data(self, data) -> pd.DataFrame:
        """Prepare and validate input data"""
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

    def _create_features_from_prediction(self, prediction: np.ndarray) -> np.ndarray:
        """Create features from prediction for next step"""
        try:
            # Extract prediction value
            pred_value = float(prediction.flatten()[0])

            # Create basic features (can be enhanced based on model requirements)
            features = np.array(
                [
                    pred_value,
                    pred_value * 0.1,  # Derived feature 1
                    pred_value * 0.05,  # Derived feature 2
                ]
            ).reshape(1, -1)

            return features

        except Exception as e:
            logger.error(f"❌ Feature creation failed: {e}")
            # Return zero features as fallback
            return np.zeros((1, 3))

    def _create_prediction_result(
        self,
        predictions: list[np.ndarray],
        uncertainties: list[np.ndarray] | None,
        start_time: datetime,
    ) -> PredictionResult:
        """Create formatted prediction result"""
        try:
            # Stack predictions
            pred_array = np.vstack(predictions) if predictions else np.array([])

            # Calculate confidence intervals if uncertainty is available
            confidence_lower = None
            confidence_upper = None
            uncertainty_score = None

            if uncertainties:
                uncertainty_array = np.vstack(uncertainties)
                uncertainty_score = float(np.mean(uncertainty_array))

                # Simple confidence intervals (can be enhanced)
                confidence_lower = pred_array - 1.96 * uncertainty_array
                confidence_upper = pred_array + 1.96 * uncertainty_array

            # Calculate execution time
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            return PredictionResult(
                predictions=pred_array,
                confidence_lower=confidence_lower,
                confidence_upper=confidence_upper,
                uncertainty_score=uncertainty_score,
                execution_time_ms=execution_time,
                model_version=getattr(self.model, "version", "unknown"),
                cached=False,
            )

        except Exception as e:
            logger.error(f"❌ Result creation failed: {e}")
            return PredictionResult(
                predictions=np.array([]), execution_time_ms=0, model_version="error"
            )

    def _update_response_time(self, execution_time_ms: float):
        """Update average response time metric"""
        if self.health_metrics.average_response_time_ms == 0:
            self.health_metrics.average_response_time_ms = execution_time_ms
        else:
            # Moving average
            total_predictions = self.health_metrics.total_predictions
            self.health_metrics.average_response_time_ms = (
                self.health_metrics.average_response_time_ms * (total_predictions - 1)
                + execution_time_ms
            ) / total_predictions
