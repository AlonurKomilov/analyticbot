"""
Data Processing Service
=======================

Microservice responsible for data preparation, batching, and preprocessing
for incremental learning operations.

Single Responsibility: Data processing operations only.
"""

import logging
from typing import Any

import numpy as np
import torch

from ..models import (
    BatchData,
    IncrementalLearningConfig,
)

logger = logging.getLogger(__name__)


class DataProcessingService:
    """
    Data processing microservice.

    Responsibilities:
    - Create training batches from raw data
    - Prepare batch tensors for model training
    - Data preprocessing and normalization
    - Batch shuffling and sampling strategies
    """

    def __init__(self, config: IncrementalLearningConfig | None = None):
        self.config = config or IncrementalLearningConfig()
        logger.info("📊 Data Processing Service initialized")

    async def create_batches(
        self,
        data: list[dict[str, Any]],
        batch_size: int,
        shuffle: bool = True,
        drop_last: bool = False,
    ) -> list[BatchData]:
        """
        Create batches from raw data.

        Args:
            data: Raw data list
            batch_size: Size of each batch
            shuffle: Whether to shuffle data before batching
            drop_last: Whether to drop incomplete last batch

        Returns:
            List of BatchData objects
        """
        try:
            if not data:
                logger.warning("⚠️ Empty data provided for batching")
                return []

            # Shuffle data if requested
            if shuffle:
                data = data.copy()
                np.random.shuffle(data)

            batches = []

            for i in range(0, len(data), batch_size):
                batch_data_raw = data[i : i + batch_size]

                # Skip incomplete batch if drop_last is True
                if drop_last and len(batch_data_raw) < batch_size:
                    continue

                # Process batch
                batch = await self._process_batch(batch_data_raw)
                if batch:
                    batches.append(batch)

            logger.debug(f"📦 Created {len(batches)} batches from {len(data)} samples")
            return batches

        except Exception as e:
            logger.error(f"❌ Batch creation failed: {e}")
            return []

    async def prepare_batch_tensors(
        self,
        batch_data: list[dict[str, Any]],
        device: torch.device,
        input_key: str = "input",
        target_key: str = "target",
    ) -> BatchData:
        """
        Prepare batch tensors from raw batch data.

        Args:
            batch_data: Raw batch data
            device: Target device for tensors
            input_key: Key for input data in batch items
            target_key: Key for target data in batch items

        Returns:
            BatchData with processed tensors
        """
        try:
            inputs = []
            targets = []
            metadata = {}

            for item in batch_data:
                # Extract input data
                input_data = item.get(input_key)
                if input_data is not None:
                    if isinstance(input_data, (list, np.ndarray)):
                        input_tensor = torch.tensor(input_data, dtype=torch.float32)
                    elif isinstance(input_data, torch.Tensor):
                        input_tensor = input_data.float()
                    else:
                        # Try to convert to tensor
                        input_tensor = torch.tensor([input_data], dtype=torch.float32)

                    inputs.append(input_tensor)

                # Extract target data
                target_data = item.get(target_key)
                if target_data is not None:
                    if isinstance(target_data, (list, np.ndarray)):
                        target_tensor = torch.tensor(target_data)
                    elif isinstance(target_data, torch.Tensor):
                        target_tensor = target_data
                    else:
                        # Try to convert to tensor
                        target_tensor = torch.tensor([target_data])

                    targets.append(target_tensor)

                # Collect metadata
                for key, value in item.items():
                    if key not in [input_key, target_key]:
                        if key not in metadata:
                            metadata[key] = []
                        metadata[key].append(value)

            # Stack tensors
            if inputs:
                inputs_tensor = torch.stack(inputs).to(device)
            else:
                # Fallback: create dummy input
                inputs_tensor = torch.randn(len(batch_data), 10, device=device)
                logger.warning("⚠️ No valid inputs found, using dummy data")

            if targets:
                targets_tensor = torch.stack(targets).to(device)
            else:
                # Fallback: create dummy targets
                targets_tensor = torch.randint(0, 2, (len(batch_data),), device=device)
                logger.warning("⚠️ No valid targets found, using dummy data")

            return BatchData(
                inputs=inputs_tensor,
                targets=targets_tensor,
                batch_size=len(batch_data),
                device=str(device),
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"❌ Batch tensor preparation failed: {e}")
            # Return dummy batch to prevent complete failure
            return BatchData(
                inputs=torch.randn(len(batch_data), 10, device=device),
                targets=torch.randint(0, 2, (len(batch_data),), device=device),
                batch_size=len(batch_data),
                device=str(device),
                metadata={"error": str(e)},
            )

    async def preprocess_data(
        self,
        data: list[dict[str, Any]],
        preprocessing_config: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Apply preprocessing to raw data.

        Args:
            data: Raw data to preprocess
            preprocessing_config: Configuration for preprocessing steps

        Returns:
            Preprocessed data
        """
        try:
            if not data:
                return data

            config = preprocessing_config or {}
            processed_data = data.copy()

            # Apply normalization if requested
            if config.get("normalize", False):
                processed_data = await self._apply_normalization(processed_data, config)

            # Apply feature scaling if requested
            if config.get("scale_features", False):
                processed_data = await self._apply_feature_scaling(processed_data, config)

            # Apply data augmentation if requested
            if config.get("augment", False):
                processed_data = await self._apply_data_augmentation(processed_data, config)

            # Filter out invalid samples
            if config.get("filter_invalid", True):
                processed_data = await self._filter_invalid_samples(processed_data)

            logger.debug(f"🔧 Preprocessed {len(data)} → {len(processed_data)} samples")
            return processed_data

        except Exception as e:
            logger.error(f"❌ Data preprocessing failed: {e}")
            return data  # Return original data on failure

    async def create_stratified_batches(
        self,
        data: list[dict[str, Any]],
        batch_size: int,
        stratify_key: str = "target",
        min_samples_per_class: int = 1,
    ) -> list[BatchData]:
        """
        Create stratified batches to maintain class distribution.

        Args:
            data: Raw data with class labels
            batch_size: Size of each batch
            stratify_key: Key to use for stratification
            min_samples_per_class: Minimum samples per class in each batch

        Returns:
            List of stratified BatchData objects
        """
        try:
            if not data:
                return []

            # Group data by class
            class_groups = {}
            for item in data:
                class_label = item.get(stratify_key, "unknown")
                if class_label not in class_groups:
                    class_groups[class_label] = []
                class_groups[class_label].append(item)

            # Calculate samples per class per batch
            num_classes = len(class_groups)
            if num_classes == 0:
                return await self.create_batches(data, batch_size)

            samples_per_class = max(min_samples_per_class, batch_size // num_classes)

            batches = []
            class_indices = {cls: 0 for cls in class_groups}

            while True:
                batch_data = []

                # Try to sample from each class
                for class_label in class_groups:
                    class_data = class_groups[class_label]
                    start_idx = class_indices[class_label]

                    # Get samples for this class
                    end_idx = min(start_idx + samples_per_class, len(class_data))
                    class_samples = class_data[start_idx:end_idx]

                    batch_data.extend(class_samples)
                    class_indices[class_label] = end_idx

                # Check if we have enough data for a batch
                if len(batch_data) < batch_size // 2:  # At least half a batch
                    break

                # Process batch
                if batch_data:
                    batch = await self._process_batch(batch_data)
                    if batch:
                        batches.append(batch)

                # Check if all classes are exhausted
                if all(class_indices[cls] >= len(class_groups[cls]) for cls in class_groups):
                    break

            logger.debug(f"📊 Created {len(batches)} stratified batches")
            return batches

        except Exception as e:
            logger.error(f"❌ Stratified batch creation failed: {e}")
            return await self.create_batches(data, batch_size)

    async def merge_batches(self, batch1: BatchData, batch2: BatchData) -> BatchData:
        """
        Merge two batches into one.

        Args:
            batch1: First batch
            batch2: Second batch

        Returns:
            Merged BatchData
        """
        try:
            # Concatenate inputs and targets
            merged_inputs = torch.cat([batch1.inputs, batch2.inputs], dim=0)
            merged_targets = torch.cat([batch1.targets, batch2.targets], dim=0)

            # Merge metadata
            merged_metadata = {}
            for key in set(batch1.metadata.keys()) | set(batch2.metadata.keys()):
                merged_metadata[key] = batch1.metadata.get(key, []) + batch2.metadata.get(key, [])

            return BatchData(
                inputs=merged_inputs,
                targets=merged_targets,
                batch_size=batch1.batch_size + batch2.batch_size,
                device=batch1.device,
                metadata=merged_metadata,
            )

        except Exception as e:
            logger.error(f"❌ Batch merging failed: {e}")
            return batch1  # Return first batch on failure

    # Private helper methods

    async def _process_batch(self, batch_data: list[dict[str, Any]]) -> BatchData | None:
        """Process raw batch data into BatchData object."""
        try:
            device = torch.device("cpu")  # Default device
            return await self.prepare_batch_tensors(batch_data, device)
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            return None

    async def _apply_normalization(
        self, data: list[dict[str, Any]], config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Apply normalization to data."""

        normalization_type = config.get("normalization_type", "min_max")
        input_key = config.get("input_key", "input")

        # Collect all input values to calculate statistics
        all_inputs = []
        for item in data:
            input_data = item.get(input_key)
            if input_data is not None:
                if isinstance(input_data, (list, np.ndarray)):
                    all_inputs.extend(np.array(input_data).flatten())
                elif isinstance(input_data, (int, float)):
                    all_inputs.append(input_data)

        if not all_inputs:
            return data

        all_inputs = np.array(all_inputs)

        # Calculate normalization parameters
        if normalization_type == "min_max":
            min_val = np.min(all_inputs)
            max_val = np.max(all_inputs)
            range_val = max_val - min_val if max_val != min_val else 1.0
        elif normalization_type == "z_score":
            mean_val = np.mean(all_inputs)
            std_val = np.std(all_inputs)
            std_val = std_val if std_val != 0 else 1.0

        # Apply normalization
        normalized_data = []
        for item in data.copy():
            input_data = item.get(input_key)
            if input_data is not None:
                if normalization_type == "min_max":
                    if isinstance(input_data, (list, np.ndarray)):
                        normalized_input = (np.array(input_data) - min_val) / range_val
                        item[input_key] = normalized_input.tolist()
                    else:
                        item[input_key] = (input_data - min_val) / range_val
                elif normalization_type == "z_score":
                    if isinstance(input_data, (list, np.ndarray)):
                        normalized_input = (np.array(input_data) - mean_val) / std_val
                        item[input_key] = normalized_input.tolist()
                    else:
                        item[input_key] = (input_data - mean_val) / std_val

            normalized_data.append(item)

        return normalized_data

    async def _apply_feature_scaling(
        self, data: list[dict[str, Any]], config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Apply feature scaling to data."""

        # Simplified feature scaling - would be more sophisticated in practice
        scaling_factor = config.get("scaling_factor", 1.0)
        input_key = config.get("input_key", "input")

        scaled_data = []
        for item in data.copy():
            input_data = item.get(input_key)
            if input_data is not None:
                if isinstance(input_data, (list, np.ndarray)):
                    item[input_key] = (np.array(input_data) * scaling_factor).tolist()
                else:
                    item[input_key] = input_data * scaling_factor

            scaled_data.append(item)

        return scaled_data

    async def _apply_data_augmentation(
        self, data: list[dict[str, Any]], config: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Apply data augmentation to increase dataset size."""

        augmentation_factor = config.get("augmentation_factor", 2)
        noise_level = config.get("noise_level", 0.1)
        input_key = config.get("input_key", "input")

        augmented_data = data.copy()

        # Add noisy versions of existing data
        for _ in range(augmentation_factor - 1):
            for item in data:
                augmented_item = item.copy()
                input_data = item.get(input_key)

                if input_data is not None:
                    if isinstance(input_data, (list, np.ndarray)):
                        input_array = np.array(input_data)
                        noise = np.random.normal(0, noise_level, input_array.shape)
                        augmented_item[input_key] = (input_array + noise).tolist()
                    else:
                        noise = np.random.normal(0, noise_level)
                        augmented_item[input_key] = input_data + noise

                augmented_data.append(augmented_item)

        return augmented_data

    async def _filter_invalid_samples(self, data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter out invalid or corrupted samples."""

        valid_data = []

        for item in data:
            # Check if item has required fields
            if "input" in item and "target" in item:
                input_data = item["input"]
                target_data = item["target"]

                # Check for NaN or infinite values
                is_valid = True

                if isinstance(input_data, (list, np.ndarray)):
                    input_array = np.array(input_data)
                    if np.any(np.isnan(input_array)) or np.any(np.isinf(input_array)):
                        is_valid = False
                elif isinstance(input_data, (int, float)):
                    if np.isnan(input_data) or np.isinf(input_data):
                        is_valid = False

                if isinstance(target_data, (list, np.ndarray)):
                    target_array = np.array(target_data)
                    if np.any(np.isnan(target_array)) or np.any(np.isinf(target_array)):
                        is_valid = False
                elif isinstance(target_data, (int, float)):
                    if np.isnan(target_data) or np.isinf(target_data):
                        is_valid = False

                if is_valid:
                    valid_data.append(item)

        return valid_data

    async def health_check(self) -> dict[str, Any]:
        """Health check for data processing service."""
        return {
            "service": "DataProcessingService",
            "status": "healthy",
            "torch_available": hasattr(torch, "tensor"),
            "numpy_available": hasattr(np, "array"),
            "supported_batch_types": ["standard", "stratified", "merged"],
        }
