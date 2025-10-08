"""
Engagement Data Processor
========================

Data processing specifically for engagement prediction features.
Handles feature extraction, normalization, and validation.
"""

import logging
from datetime import datetime

import numpy as np
import torch

logger = logging.getLogger(__name__)


class EngagementDataProcessor:
    """Data processor specifically for engagement prediction"""

    def __init__(self, sequence_length: int = 30):
        self.sequence_length = sequence_length

        # Define expected features
        self.feature_names = [
            "views",
            "forwards",
            "replies",
            "reactions",
            "hour_of_day",
            "day_of_week",
            "content_length",
            "has_media",
        ]

        # Normalization parameters (will be learned from data)
        self.normalization_params = {
            "views": {"mean": 1000, "std": 2000, "min": 0, "max": 50000},
            "forwards": {"mean": 50, "std": 100, "min": 0, "max": 2000},
            "replies": {"mean": 20, "std": 50, "min": 0, "max": 1000},
            "reactions": {"mean": 100, "std": 200, "min": 0, "max": 5000},
            "hour_of_day": {"mean": 12, "std": 6.9, "min": 0, "max": 23},
            "day_of_week": {"mean": 3, "std": 2, "min": 0, "max": 6},
            "content_length": {"mean": 200, "std": 150, "min": 0, "max": 4096},
            "has_media": {"mean": 0.3, "std": 0.46, "min": 0, "max": 1},
        }

        logger.info(
            f"📊 EngagementDataProcessor initialized with sequence length: {sequence_length}"
        )

    async def process_features(self, raw_features: dict) -> torch.Tensor:
        """Process raw features into model-ready tensor

        Args:
            raw_features: Dictionary containing raw feature data

        Returns:
            Processed tensor ready for LSTM model
        """
        try:
            # Extract and validate features
            if not self.validate_features(raw_features):
                raise ValueError("Invalid feature data provided")

            # Create feature vector
            feature_vector = []

            for feature_name in self.feature_names:
                value = raw_features.get(feature_name, 0.0)
                normalized_value = self._normalize_feature(feature_name, value)
                feature_vector.append(normalized_value)

            # Create sequence tensor
            # For real-time prediction, we might only have current features
            # So we'll create a sequence by repeating the current features
            sequence_data = []
            for _ in range(self.sequence_length):
                sequence_data.append(feature_vector)

            # Convert to tensor
            tensor = torch.tensor([sequence_data], dtype=torch.float32)

            logger.debug(f"Features processed: shape {tensor.shape}")
            return tensor

        except Exception as e:
            logger.error(f"Feature processing failed: {e}")
            raise

    async def process_historical_features(
        self, historical_data: list[dict], target_engagement: list[float] | None = None
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        """Process historical data for training/validation

        Args:
            historical_data: List of historical feature dictionaries
            target_engagement: Optional list of target engagement values

        Returns:
            Tuple of (features_tensor, targets_tensor)
        """
        try:
            if len(historical_data) < self.sequence_length:
                raise ValueError(f"Need at least {self.sequence_length} historical data points")

            # Create sequences
            sequences = []
            targets = []

            for i in range(len(historical_data) - self.sequence_length + 1):
                # Create sequence
                sequence = []
                for j in range(i, i + self.sequence_length):
                    feature_vector = []
                    for feature_name in self.feature_names:
                        value = historical_data[j].get(feature_name, 0.0)
                        normalized_value = self._normalize_feature(feature_name, value)
                        feature_vector.append(normalized_value)
                    sequence.append(feature_vector)

                sequences.append(sequence)

                # Add target if provided
                if target_engagement and i + self.sequence_length < len(target_engagement):
                    targets.append(target_engagement[i + self.sequence_length])

            # Convert to tensors
            features_tensor = torch.tensor(sequences, dtype=torch.float32)
            targets_tensor = (
                torch.tensor(targets, dtype=torch.float32).unsqueeze(1) if targets else None
            )

            logger.info(f"Historical data processed: {len(sequences)} sequences")
            return features_tensor, targets_tensor

        except Exception as e:
            logger.error(f"Historical data processing failed: {e}")
            raise

    def _normalize_feature(self, feature_name: str, value: float) -> float:
        """Normalize individual feature value using z-score normalization

        Args:
            feature_name: Name of the feature
            value: Raw feature value

        Returns:
            Normalized feature value
        """
        params = self.normalization_params.get(feature_name, {"mean": 0, "std": 1})

        # Special handling for specific features
        if feature_name == "has_media":
            return float(bool(value))  # Binary 0/1
        elif feature_name in ["hour_of_day", "day_of_week"]:
            # Cyclical encoding for time features
            if feature_name == "hour_of_day":
                return np.sin(2 * np.pi * value / 24)  # 24-hour cycle
            else:  # day_of_week
                return np.sin(2 * np.pi * value / 7)  # 7-day cycle
        else:
            # Z-score normalization with clipping
            normalized = (value - params["mean"]) / (params["std"] + 1e-8)
            return np.clip(normalized, -3, 3)  # Clip to ±3 standard deviations

    def validate_features(self, features: dict) -> bool:
        """Validate that all required features are present and valid

        Args:
            features: Feature dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check all required features are present
            for feature_name in self.feature_names:
                if feature_name not in features:
                    logger.warning(f"Missing required feature: {feature_name}")
                    return False

                value = features[feature_name]

                # Check value is numeric
                if not isinstance(value, (int, float, np.number)):
                    logger.warning(f"Feature {feature_name} is not numeric: {type(value)}")
                    return False

                # Check value is within reasonable bounds
                params = self.normalization_params.get(feature_name, {})
                if "min" in params and value < params["min"]:
                    logger.warning(
                        f"Feature {feature_name} below minimum: {value} < {params['min']}"
                    )
                    return False

                if "max" in params and value > params["max"]:
                    logger.warning(
                        f"Feature {feature_name} above maximum: {value} > {params['max']}"
                    )
                    # Don't fail for this, just warn (outliers might be valid)

            return True

        except Exception as e:
            logger.error(f"Feature validation failed: {e}")
            return False

    def get_feature_names(self) -> list[str]:
        """Get list of expected feature names"""
        return self.feature_names.copy()

    def get_feature_statistics(self) -> dict:
        """Get feature normalization statistics"""
        return self.normalization_params.copy()

    def update_normalization_params(self, training_data: list[dict]) -> None:
        """Update normalization parameters from training data

        Args:
            training_data: List of training feature dictionaries
        """
        try:
            logger.info("📊 Updating normalization parameters from training data")

            # Collect feature values
            feature_values = {name: [] for name in self.feature_names}

            for data_point in training_data:
                for feature_name in self.feature_names:
                    if feature_name in data_point:
                        feature_values[feature_name].append(data_point[feature_name])

            # Calculate statistics
            for feature_name in self.feature_names:
                if feature_values[feature_name]:
                    values = np.array(feature_values[feature_name])

                    self.normalization_params[feature_name] = {
                        "mean": float(np.mean(values)),
                        "std": float(np.std(values) + 1e-8),  # Add small epsilon
                        "min": float(np.min(values)),
                        "max": float(np.max(values)),
                    }

            logger.info("✅ Normalization parameters updated")

        except Exception as e:
            logger.error(f"Failed to update normalization parameters: {e}")

    def create_feature_vector_from_channel_data(
        self, channel_id: int, current_metrics: dict, timestamp: datetime | None = None
    ) -> dict:
        """Create feature vector from channel data and metrics

        Args:
            channel_id: Telegram channel ID
            current_metrics: Current engagement metrics
            timestamp: Timestamp for time-based features

        Returns:
            Feature dictionary ready for processing
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        features = {
            "views": current_metrics.get("views", 0),
            "forwards": current_metrics.get("forwards", 0),
            "replies": current_metrics.get("replies", 0),
            "reactions": current_metrics.get("reactions", 0),
            "hour_of_day": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "content_length": len(current_metrics.get("content", "")),
            "has_media": 1 if current_metrics.get("has_media", False) else 0,
        }

        return features

    def get_service_health(self) -> dict:
        """Get data processor health status"""
        return {
            "service": "engagement_data_processor",
            "status": "healthy",
            "sequence_length": self.sequence_length,
            "feature_count": len(self.feature_names),
            "features": self.feature_names,
            "normalization_ready": bool(self.normalization_params),
        }
