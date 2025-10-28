"""
Data Processing Service
=======================

Microservice responsible for data preparation, batch creation,
and data quality management for incremental learning.

Single Responsibility: Process and prepare data only.
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np

from ..models import DataBatch, LearningConfig

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Data processing microservice for incremental learning.

    Responsibilities:
    - Create and manage data batches
    - Prepare data for learning
    - Validate data quality
    - Handle data transformations
    - Manage data streaming
    """

    def __init__(self, config: LearningConfig | None = None):
        self.config = config or LearningConfig()
        self.batch_history: list[DataBatch] = []
        self.data_statistics: dict[str, Any] = {}
        logger.info("📊 Data Processor initialized")

    def create_learning_batch(
        self, raw_data: list[dict[str, Any]], batch_config: dict[str, Any] | None = None
    ) -> DataBatch:
        """
        Create optimized learning batch from raw data.

        Args:
            raw_data: Raw input data
            batch_config: Configuration for batch creation

        Returns:
            DataBatch object with processed data
        """
        try:
            logger.info(f"📊 Creating learning batch from {len(raw_data)} samples")

            config = batch_config or {}
            batch_size = config.get("batch_size", self.config.batch_size)

            # Validate and clean data
            cleaned_data = self._validate_and_clean_data(raw_data)

            # Apply data transformations
            transformed_data = self._apply_transformations(cleaned_data, config)

            # Create batches
            batches = self._create_batches(transformed_data, batch_size)

            # Calculate batch statistics
            batch_stats = self._calculate_batch_statistics(batches)

            # Create DataBatch object
            data_batch = DataBatch(
                batch_id=self._generate_batch_id(),
                raw_data_size=len(raw_data),
                processed_data_size=len(cleaned_data),
                batch_count=len(batches),
                batch_size=batch_size,
                data_batches=batches,
                quality_score=batch_stats["quality_score"],
                processing_metadata=batch_stats,
                created_at=datetime.now().isoformat(),
            )

            # Store batch history
            self.batch_history.append(data_batch)

            # Update data statistics
            self._update_data_statistics(data_batch)

            logger.info(f"✅ Learning batch created: {data_batch.batch_id}")
            return data_batch

        except Exception as e:
            logger.error(f"❌ Batch creation failed: {e}")
            raise

    def prepare_incremental_data(
        self,
        new_data: list[dict[str, Any]],
        existing_data: list[dict[str, Any]] | None = None,
        preparation_strategy: str = "balanced",
    ) -> dict[str, Any]:
        """
        Prepare data for incremental learning with proper balancing.

        Args:
            new_data: New incoming data
            existing_data: Previously seen data for balancing
            preparation_strategy: Strategy ("balanced", "recent_focus", "all_data")

        Returns:
            Prepared data dictionary
        """
        logger.info(f"📊 Preparing incremental data: {preparation_strategy} strategy")

        # Apply preparation strategy
        if preparation_strategy == "balanced":
            prepared_data = self._balanced_preparation(new_data, existing_data)
        elif preparation_strategy == "recent_focus":
            prepared_data = self._recent_focus_preparation(new_data, existing_data)
        else:  # all_data
            prepared_data = self._all_data_preparation(new_data, existing_data)

        # Add metadata
        prepared_data["preparation_metadata"] = {
            "strategy": preparation_strategy,
            "new_data_count": len(new_data),
            "existing_data_count": len(existing_data) if existing_data else 0,
            "total_prepared": len(prepared_data["data"]),
            "preparation_timestamp": datetime.now().isoformat(),
        }

        return prepared_data

    def validate_data_quality(
        self,
        data: list[dict[str, Any]],
        quality_thresholds: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """
        Comprehensive data quality validation.

        Args:
            data: Data to validate
            quality_thresholds: Quality threshold configuration

        Returns:
            Quality validation report
        """
        logger.info(f"🔍 Validating data quality for {len(data)} samples")

        thresholds = quality_thresholds or self.config.quality_thresholds

        # Check completeness
        completeness_score = self._check_data_completeness(data)

        # Check consistency
        consistency_score = self._check_data_consistency(data)

        # Check validity
        validity_score = self._check_data_validity(data)

        # Check freshness
        freshness_score = self._check_data_freshness(data)

        # Calculate overall quality score
        overall_quality = (
            completeness_score * 0.3
            + consistency_score * 0.25
            + validity_score * 0.25
            + freshness_score * 0.2
        )

        # Generate quality report
        quality_report = {
            "overall_quality": overall_quality,
            "quality_breakdown": {
                "completeness": completeness_score,
                "consistency": consistency_score,
                "validity": validity_score,
                "freshness": freshness_score,
            },
            "quality_thresholds": thresholds,
            "passes_quality_check": overall_quality >= thresholds.get("minimum_quality", 0.7),
            "recommendations": self._generate_quality_recommendations(
                completeness_score, consistency_score, validity_score, freshness_score
            ),
        }

        return quality_report

    def transform_data_for_learning(
        self,
        data: list[dict[str, Any]],
        transformation_config: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Apply transformations to prepare data for learning.

        Args:
            data: Input data
            transformation_config: Configuration for transformations

        Returns:
            Transformed data
        """
        logger.info(f"🔄 Transforming {len(data)} samples for learning")

        config = transformation_config or {}
        transformed_data = data.copy()

        # Apply normalization if requested
        if config.get("normalize", True):
            transformed_data = self._normalize_data(transformed_data)

        # Apply feature engineering if requested
        if config.get("feature_engineering", True):
            transformed_data = self._engineer_features(transformed_data)

        # Apply data augmentation if requested
        if config.get("augment", False):
            transformed_data = self._augment_data(transformed_data, config)

        # Apply filtering if requested
        if config.get("filter", True):
            transformed_data = self._filter_data(transformed_data, config)

        logger.info(f"✅ Data transformation complete: {len(transformed_data)} samples")
        return transformed_data

    def create_streaming_batches(
        self,
        data_stream: list[dict[str, Any]],
        window_size: int | None = None,
        overlap: float = 0.1,
    ) -> list[DataBatch]:
        """
        Create streaming batches for continuous learning.

        Args:
            data_stream: Continuous data stream
            window_size: Size of each window
            overlap: Overlap between windows (0.0 to 0.5)

        Returns:
            List of streaming DataBatch objects
        """
        window_size = window_size or self.config.stream_window_size
        step_size = int(window_size * (1.0 - overlap))

        streaming_batches = []

        for i in range(0, len(data_stream) - window_size + 1, step_size):
            window_data = data_stream[i : i + window_size]

            # Create batch for this window
            batch = self.create_learning_batch(
                window_data, {"batch_size": min(window_size, self.config.batch_size)}
            )

            # Add streaming metadata
            batch.processing_metadata["stream_window"] = {
                "start_index": i,
                "end_index": i + window_size,
                "overlap_ratio": overlap,
            }

            streaming_batches.append(batch)

        logger.info(f"📈 Created {len(streaming_batches)} streaming batches")
        return streaming_batches

    def get_data_statistics(self) -> dict[str, Any]:
        """Get comprehensive data processing statistics."""
        return {
            "total_batches_processed": len(self.batch_history),
            "total_samples_processed": sum(
                batch.processed_data_size for batch in self.batch_history
            ),
            "average_batch_size": (
                np.mean([batch.batch_size for batch in self.batch_history])
                if self.batch_history
                else 0
            ),
            "average_quality_score": (
                np.mean([batch.quality_score for batch in self.batch_history])
                if self.batch_history
                else 0
            ),
            "data_statistics": self.data_statistics,
        }

    # Private helper methods

    def _validate_and_clean_data(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Validate and clean input data."""
        cleaned_data = []

        for item in data:
            # Remove items with missing required fields
            if self._has_required_fields(item):
                # Clean individual item
                cleaned_item = self._clean_data_item(item)
                if cleaned_item:
                    cleaned_data.append(cleaned_item)

        return cleaned_data

    def _apply_transformations(
        self, data: list[dict[str, Any]], config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Apply configured transformations to data."""
        # Mock transformation - in practice would apply real transformations
        return data

    def _create_batches(
        self, data: list[dict[str, Any]], batch_size: int
    ) -> list[list[dict[str, Any]]]:
        """Create batches from processed data."""
        batches = []
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            batches.append(batch)
        return batches

    def _calculate_batch_statistics(self, batches: list[list[dict[str, Any]]]) -> dict[str, Any]:
        """Calculate statistics for created batches."""
        total_samples = sum(len(batch) for batch in batches)
        avg_batch_size = total_samples / len(batches) if batches else 0

        # Mock quality score calculation
        quality_score = 0.85

        return {
            "total_samples": total_samples,
            "average_batch_size": avg_batch_size,
            "quality_score": quality_score,
            "batch_size_variance": np.var([len(batch) for batch in batches]),
        }

    def _generate_batch_id(self) -> str:
        """Generate unique batch ID."""
        from uuid import uuid4

        return f"batch_{uuid4().hex[:8]}"

    def _update_data_statistics(self, batch: DataBatch) -> None:
        """Update global data statistics."""
        if "total_processed" not in self.data_statistics:
            self.data_statistics["total_processed"] = 0

        self.data_statistics["total_processed"] += batch.processed_data_size
        self.data_statistics["last_update"] = datetime.now().isoformat()

    def _balanced_preparation(
        self,
        new_data: list[dict[str, Any]],
        existing_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Balanced preparation strategy."""
        if not existing_data:
            return {"data": new_data, "strategy_details": "new_data_only"}

        # Balance new vs existing data (e.g., 70% new, 30% existing)
        existing_sample_size = min(len(existing_data), int(len(new_data) * 0.43))
        sampled_existing = existing_data[:existing_sample_size]

        combined_data = new_data + sampled_existing

        return {
            "data": combined_data,
            "strategy_details": {
                "new_data_count": len(new_data),
                "existing_data_count": len(sampled_existing),
                "total_count": len(combined_data),
            },
        }

    def _recent_focus_preparation(
        self,
        new_data: list[dict[str, Any]],
        existing_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Recent focus preparation strategy."""
        # Focus heavily on new data (90% new, 10% existing)
        if not existing_data:
            return {"data": new_data, "strategy_details": "new_data_only"}

        existing_sample_size = min(len(existing_data), int(len(new_data) * 0.11))
        sampled_existing = existing_data[:existing_sample_size]

        combined_data = new_data + sampled_existing

        return {
            "data": combined_data,
            "strategy_details": {
                "focus": "recent",
                "new_data_ratio": 0.9,
                "total_count": len(combined_data),
            },
        }

    def _all_data_preparation(
        self,
        new_data: list[dict[str, Any]],
        existing_data: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """All data preparation strategy."""
        combined_data = new_data + (existing_data or [])

        return {
            "data": combined_data,
            "strategy_details": {
                "strategy": "all_data",
                "total_count": len(combined_data),
            },
        }

    def _check_data_completeness(self, data: list[dict[str, Any]]) -> float:
        """Check data completeness score."""
        if not data:
            return 0.0

        total_fields = 0
        complete_fields = 0

        for item in data:
            for key, value in item.items():
                total_fields += 1
                if value is not None and value != "":
                    complete_fields += 1

        return complete_fields / total_fields if total_fields > 0 else 0.0

    def _check_data_consistency(self, data: list[dict[str, Any]]) -> float:
        """Check data consistency score."""
        # Mock implementation - would check actual consistency
        return 0.9

    def _check_data_validity(self, data: list[dict[str, Any]]) -> float:
        """Check data validity score."""
        # Mock implementation - would validate data types, ranges, etc.
        return 0.85

    def _check_data_freshness(self, data: list[dict[str, Any]]) -> float:
        """Check data freshness score."""
        # Mock implementation - would check timestamps
        return 0.8

    def _generate_quality_recommendations(
        self, completeness: float, consistency: float, validity: float, freshness: float
    ) -> list[str]:
        """Generate quality improvement recommendations."""
        recommendations = []

        if completeness < 0.8:
            recommendations.append("Improve data completeness - many fields are missing")

        if consistency < 0.8:
            recommendations.append("Address data consistency issues")

        if validity < 0.8:
            recommendations.append("Validate data types and ranges")

        if freshness < 0.7:
            recommendations.append("Consider data freshness - some data may be stale")

        if not recommendations:
            recommendations.append("Data quality is good - no major issues detected")

        return recommendations

    def _has_required_fields(self, item: dict[str, Any]) -> bool:
        """Check if item has required fields."""
        required_fields = self.config.required_fields
        return all(field in item for field in required_fields)

    def _clean_data_item(self, item: dict[str, Any]) -> dict[str, Any] | None:
        """Clean individual data item."""
        # Mock cleaning - in practice would handle nulls, outliers, etc.
        return item if item else None

    def _normalize_data(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize data values."""
        # Mock normalization
        return data

    def _engineer_features(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply feature engineering."""
        # Mock feature engineering
        return data

    def _augment_data(
        self, data: list[dict[str, Any]], config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Apply data augmentation."""
        # Mock augmentation
        return data

    def _filter_data(
        self, data: list[dict[str, Any]], config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Apply data filtering."""
        # Mock filtering
        return data

    async def health_check(self) -> dict[str, Any]:
        """Health check for data processor."""
        stats = self.get_data_statistics()

        return {
            "service": "DataProcessor",
            "status": "healthy",
            "batches_processed": stats["total_batches_processed"],
            "samples_processed": stats["total_samples_processed"],
            "average_quality_score": stats["average_quality_score"],
        }
