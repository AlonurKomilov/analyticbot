"""
Memory Management Service
=========================

Microservice responsible for managing memory buffers for experience replay
and continual learning.

Single Responsibility: Memory buffer operations only.
"""

import logging
import random
from typing import Any

import numpy as np

from ....protocols.learning_protocols import LearningContext
from ..models import (
    IncrementalLearningConfig,
    MemoryOperation,
    MemoryStrategy,
)

logger = logging.getLogger(__name__)


class MemoryManagementService:
    """
    Memory buffer management microservice.

    Responsibilities:
    - Memory buffer updates (add, remove, sample)
    - Importance-based sampling
    - Random sampling
    - Gradient-based memory selection
    - Clustering-based memory selection
    """

    def __init__(self, config: IncrementalLearningConfig | None = None):
        self.config = config or IncrementalLearningConfig()
        logger.info("🧠 Memory Management Service initialized")

    async def update_memory_buffer(
        self,
        context: LearningContext,
        new_data: list[dict[str, Any]],
        strategy: MemoryStrategy = MemoryStrategy.RANDOM_SAMPLING,
    ) -> MemoryOperation:
        """
        Update memory buffer with new data using specified strategy.

        Args:
            context: Learning context containing memory buffer
            new_data: New data items to add
            strategy: Memory management strategy to use

        Returns:
            MemoryOperation result with status and metrics
        """
        try:
            initial_size = len(context.memory_buffer)

            if strategy == MemoryStrategy.RANDOM_SAMPLING:
                await self._update_random_sampling(context, new_data)
            elif strategy == MemoryStrategy.IMPORTANCE_SAMPLING:
                await self._update_importance_sampling(context, new_data)
            elif strategy == MemoryStrategy.GRADIENT_BASED:
                await self._update_gradient_based(context, new_data)
            elif strategy == MemoryStrategy.CLUSTERING_BASED:
                await self._update_clustering_based(context, new_data)
            else:
                logger.warning(f"⚠️ Unknown strategy {strategy}, using random sampling")
                await self._update_random_sampling(context, new_data)

            final_size = len(context.memory_buffer)

            logger.info(f"💾 Memory buffer updated: {initial_size} → {final_size} items")

            return MemoryOperation(
                operation_type="update_buffer",
                items_processed=len(new_data),
                buffer_size_after=final_size,
                success=True,
            )

        except Exception as e:
            logger.error(f"❌ Memory buffer update failed: {e}")
            return MemoryOperation(
                operation_type="update_buffer",
                items_processed=0,
                buffer_size_after=len(context.memory_buffer),
                success=False,
                error=str(e),
            )

    async def sample_replay_data(
        self,
        context: LearningContext,
        sample_size: int,
        strategy: MemoryStrategy = MemoryStrategy.RANDOM_SAMPLING,
    ) -> tuple[list[dict[str, Any]], MemoryOperation]:
        """
        Sample data from memory buffer for replay.

        Args:
            context: Learning context with memory buffer
            sample_size: Number of items to sample
            strategy: Sampling strategy

        Returns:
            Tuple of (sampled_data, operation_result)
        """
        try:
            if not context.memory_buffer:
                return [], MemoryOperation(
                    operation_type="sample",
                    items_processed=0,
                    buffer_size_after=0,
                    success=True,
                )

            # Limit sample size to available data
            actual_sample_size = min(sample_size, len(context.memory_buffer))

            if strategy == MemoryStrategy.RANDOM_SAMPLING:
                sampled_data = self._sample_random(context.memory_buffer, actual_sample_size)
            elif strategy == MemoryStrategy.IMPORTANCE_SAMPLING:
                sampled_data = self._sample_by_importance(context.memory_buffer, actual_sample_size)
            elif strategy == MemoryStrategy.GRADIENT_BASED:
                sampled_data = self._sample_gradient_based(
                    context.memory_buffer, actual_sample_size
                )
            elif strategy == MemoryStrategy.CLUSTERING_BASED:
                sampled_data = self._sample_clustering_based(
                    context.memory_buffer, actual_sample_size
                )
            else:
                sampled_data = self._sample_random(context.memory_buffer, actual_sample_size)

            logger.debug(f"🎯 Sampled {len(sampled_data)} items using {strategy.value}")

            return sampled_data, MemoryOperation(
                operation_type="sample",
                items_processed=len(sampled_data),
                buffer_size_after=len(context.memory_buffer),
                success=True,
            )

        except Exception as e:
            logger.error(f"❌ Memory sampling failed: {e}")
            return [], MemoryOperation(
                operation_type="sample",
                items_processed=0,
                buffer_size_after=len(context.memory_buffer),
                success=False,
                error=str(e),
            )

    async def update_importance_weights(
        self,
        context: LearningContext,
        item_indices: list[int],
        importance_scores: list[float],
    ) -> MemoryOperation:
        """
        Update importance weights for memory buffer items.

        Args:
            context: Learning context
            item_indices: Indices of items to update
            importance_scores: New importance scores

        Returns:
            MemoryOperation result
        """
        try:
            updated_count = 0

            for idx, score in zip(item_indices, importance_scores, strict=False):
                if 0 <= idx < len(context.memory_buffer):
                    if "importance" not in context.memory_buffer[idx]:
                        context.memory_buffer[idx]["importance"] = score
                    else:
                        # Update with exponential moving average
                        old_importance = context.memory_buffer[idx]["importance"]
                        context.memory_buffer[idx]["importance"] = (
                            0.7 * old_importance + 0.3 * score
                        )
                    updated_count += 1

            logger.debug(f"📊 Updated importance for {updated_count} items")

            return MemoryOperation(
                operation_type="update_importance",
                items_processed=updated_count,
                buffer_size_after=len(context.memory_buffer),
                success=True,
            )

        except Exception as e:
            logger.error(f"❌ Importance update failed: {e}")
            return MemoryOperation(
                operation_type="update_importance",
                items_processed=0,
                buffer_size_after=len(context.memory_buffer),
                success=False,
                error=str(e),
            )

    async def clear_memory_buffer(self, context: LearningContext) -> MemoryOperation:
        """Clear all items from memory buffer."""
        try:
            initial_size = len(context.memory_buffer)
            context.memory_buffer.clear()

            logger.info(f"🗑️ Cleared memory buffer ({initial_size} items removed)")

            return MemoryOperation(
                operation_type="clear",
                items_processed=initial_size,
                buffer_size_after=0,
                success=True,
            )

        except Exception as e:
            logger.error(f"❌ Memory buffer clear failed: {e}")
            return MemoryOperation(
                operation_type="clear",
                items_processed=0,
                buffer_size_after=len(context.memory_buffer),
                success=False,
                error=str(e),
            )

    async def get_memory_statistics(self, context: LearningContext) -> dict[str, Any]:
        """Get statistics about the memory buffer."""
        try:
            buffer = context.memory_buffer

            if not buffer:
                return {
                    "total_items": 0,
                    "has_importance_weights": False,
                    "average_importance": 0.0,
                    "memory_utilization": 0.0,
                }

            # Check if items have importance weights
            has_importance = any("importance" in item for item in buffer)

            # Calculate average importance if available
            avg_importance = 0.0
            if has_importance:
                importance_values = [
                    item.get("importance", 0.0) for item in buffer if "importance" in item
                ]
                avg_importance = (
                    sum(importance_values) / len(importance_values) if importance_values else 0.0
                )

            # Memory utilization
            utilization = len(buffer) / self.config.memory_buffer_size

            return {
                "total_items": len(buffer),
                "has_importance_weights": has_importance,
                "average_importance": avg_importance,
                "memory_utilization": utilization,
                "max_capacity": self.config.memory_buffer_size,
                "items_with_importance": sum(1 for item in buffer if "importance" in item),
            }

        except Exception as e:
            logger.error(f"❌ Memory statistics calculation failed: {e}")
            return {"error": str(e)}

    # Private implementation methods

    async def _update_random_sampling(
        self, context: LearningContext, new_data: list[dict[str, Any]]
    ) -> bool:
        """Update buffer using random sampling strategy."""

        # Add new data
        for item in new_data:
            if len(context.memory_buffer) < self.config.memory_buffer_size:
                context.memory_buffer.append(item)
            else:
                # Replace random item
                random_idx = random.randint(0, len(context.memory_buffer) - 1)
                context.memory_buffer[random_idx] = item

        return True

    async def _update_importance_sampling(
        self, context: LearningContext, new_data: list[dict[str, Any]]
    ) -> bool:
        """Update buffer using importance-based sampling."""

        for item in new_data:
            # Assign default importance if not present
            if "importance" not in item:
                item["importance"] = 1.0  # Default importance

            if len(context.memory_buffer) < self.config.memory_buffer_size:
                context.memory_buffer.append(item)
            else:
                # Find item with lowest importance to replace
                min_importance_idx = 0
                min_importance = float("inf")

                for i, buffer_item in enumerate(context.memory_buffer):
                    importance = buffer_item.get("importance", 0.0)
                    if importance < min_importance:
                        min_importance = importance
                        min_importance_idx = i

                # Replace if new item has higher importance
                if item["importance"] > min_importance:
                    context.memory_buffer[min_importance_idx] = item

        return True

    async def _update_gradient_based(
        self, context: LearningContext, new_data: list[dict[str, Any]]
    ) -> bool:
        """Update buffer using gradient-based selection."""

        # Simplified gradient-based selection
        # In practice, would use actual gradient magnitudes

        for item in new_data:
            # Mock gradient magnitude (would be calculated from actual gradients)
            gradient_magnitude = random.uniform(0.1, 2.0)
            item["gradient_magnitude"] = gradient_magnitude

            if len(context.memory_buffer) < self.config.memory_buffer_size:
                context.memory_buffer.append(item)
            else:
                # Replace item with smallest gradient magnitude
                min_grad_idx = 0
                min_grad = float("inf")

                for i, buffer_item in enumerate(context.memory_buffer):
                    grad_mag = buffer_item.get("gradient_magnitude", 0.0)
                    if grad_mag < min_grad:
                        min_grad = grad_mag
                        min_grad_idx = i

                if gradient_magnitude > min_grad:
                    context.memory_buffer[min_grad_idx] = item

        return True

    async def _update_clustering_based(
        self, context: LearningContext, new_data: list[dict[str, Any]]
    ) -> bool:
        """Update buffer using clustering-based diversity selection."""

        # Simplified clustering approach
        # In practice, would use actual feature clustering

        for item in new_data:
            # Mock cluster assignment
            cluster_id = random.randint(0, 9)  # 10 clusters
            item["cluster_id"] = cluster_id

            if len(context.memory_buffer) < self.config.memory_buffer_size:
                context.memory_buffer.append(item)
            else:
                # Try to maintain diversity by replacing from over-represented clusters
                cluster_counts = {}
                for buffer_item in context.memory_buffer:
                    cid = buffer_item.get("cluster_id", 0)
                    cluster_counts[cid] = cluster_counts.get(cid, 0) + 1

                # Find most represented cluster - handle empty clusters case
                if not cluster_counts:
                    logger.warning("No clusters found for clustering-based memory update")
                    return False

                max_cluster = max(cluster_counts.keys(), key=lambda k: cluster_counts[k])

                # Replace random item from over-represented cluster
                candidates = [
                    i
                    for i, buffer_item in enumerate(context.memory_buffer)
                    if buffer_item.get("cluster_id", 0) == max_cluster
                ]

                if candidates:
                    replace_idx = random.choice(candidates)
                    context.memory_buffer[replace_idx] = item

        return True

    def _sample_random(
        self, buffer: list[dict[str, Any]], sample_size: int
    ) -> list[dict[str, Any]]:
        """Random sampling from buffer."""
        return random.sample(buffer, sample_size)

    def _sample_by_importance(
        self, buffer: list[dict[str, Any]], sample_size: int
    ) -> list[dict[str, Any]]:
        """Importance-weighted sampling."""

        # Extract importance weights
        weights = [item.get("importance", 1.0) for item in buffer]
        total_weight = sum(weights)

        if total_weight == 0:
            return self._sample_random(buffer, sample_size)

        # Normalize weights
        probabilities = [w / total_weight for w in weights]

        # Sample based on probabilities
        indices = np.random.choice(
            len(buffer),
            size=min(sample_size, len(buffer)),
            replace=False,
            p=probabilities,
        )

        return [buffer[i] for i in indices]

    def _sample_gradient_based(
        self, buffer: list[dict[str, Any]], sample_size: int
    ) -> list[dict[str, Any]]:
        """Gradient magnitude-based sampling."""

        # Sort by gradient magnitude (descending)
        sorted_items = sorted(buffer, key=lambda x: x.get("gradient_magnitude", 0.0), reverse=True)

        # Take top items by gradient magnitude
        return sorted_items[:sample_size]

    def _sample_clustering_based(
        self, buffer: list[dict[str, Any]], sample_size: int
    ) -> list[dict[str, Any]]:
        """Diversity-based sampling using clusters."""

        # Group by cluster
        clusters = {}
        for item in buffer:
            cluster_id = item.get("cluster_id", 0)
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(item)

        # Sample evenly from clusters
        sampled = []
        cluster_list = list(clusters.keys())

        while len(sampled) < sample_size and cluster_list:
            for cluster_id in cluster_list[:]:
                if len(sampled) >= sample_size:
                    break

                cluster_items = clusters[cluster_id]
                if cluster_items:
                    sampled.append(cluster_items.pop())

                # Remove empty clusters
                if not cluster_items:
                    cluster_list.remove(cluster_id)

        return sampled

    async def health_check(self) -> dict[str, Any]:
        """Health check for memory management service."""
        return {
            "service": "MemoryManagementService",
            "status": "healthy",
            "max_buffer_size": self.config.memory_buffer_size,
            "strategies_available": [strategy.value for strategy in MemoryStrategy],
        }
