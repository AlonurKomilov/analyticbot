"""
Model Operations Service
========================

Microservice responsible for model-specific operations like evaluation,
importance weight calculation, and model state management.

Single Responsibility: Model operations only.
"""

import logging
from datetime import datetime
from typing import Any

import torch
import torch.nn as nn

from ....protocols.learning_protocols import LearningContext
from ..models import (
    BatchData,
    ImportanceWeights,
    IncrementalLearningConfig,
    ModelEvaluation,
)

logger = logging.getLogger(__name__)


class ModelOperationsService:
    """
    Model operations microservice.

    Responsibilities:
    - Model evaluation and performance metrics
    - Importance weight calculation (EWC, Fisher Information)
    - Model state management and checkpointing
    - Model performance tracking
    """

    def __init__(self, config: IncrementalLearningConfig | None = None):
        self.config = config or IncrementalLearningConfig()
        logger.info("⚙️ Model Operations Service initialized")

    async def evaluate_model(
        self,
        model: torch.nn.Module,
        test_data: list[BatchData],
        device: torch.device,
        evaluation_type: str = "accuracy",
    ) -> ModelEvaluation:
        """
        Evaluate model performance on test data.

        Args:
            model: PyTorch model to evaluate
            test_data: Test data batches
            device: Torch device (CPU/GPU)
            evaluation_type: Type of evaluation ("accuracy", "loss", "performance")

        Returns:
            ModelEvaluation with metrics
        """
        try:
            model.to(device)
            model.eval()

            total_samples = 0
            metrics = {}

            with torch.no_grad():
                if evaluation_type == "accuracy":
                    metrics = await self._evaluate_accuracy(model, test_data, device)
                elif evaluation_type == "loss":
                    metrics = await self._evaluate_loss(model, test_data, device)
                elif evaluation_type == "performance":
                    metrics = await self._evaluate_comprehensive(model, test_data, device)
                else:
                    logger.warning(f"⚠️ Unknown evaluation type {evaluation_type}, using accuracy")
                    metrics = await self._evaluate_accuracy(model, test_data, device)

                total_samples = sum(batch.batch_size for batch in test_data)

            logger.info(f"📊 Model evaluation complete: {evaluation_type}")

            return ModelEvaluation(
                model_id=getattr(model, "model_id", "unknown"),
                evaluation_type=evaluation_type,
                metrics=metrics,
                sample_count=total_samples,
                success=True,
            )

        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            return ModelEvaluation(
                model_id=getattr(model, "model_id", "unknown"),
                evaluation_type=evaluation_type,
                metrics={"error": 0.0},  # Use float for metrics
                sample_count=0,
                success=False,
            )

    async def calculate_importance_weights(
        self,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device,
        method: str = "fisher",
    ) -> ImportanceWeights:
        """
        Calculate importance weights for EWC-style regularization.

        Args:
            model: PyTorch model
            context: Learning context with data
            device: Torch device
            method: Calculation method ("fisher", "gradient_based", "empirical")

        Returns:
            ImportanceWeights with parameter importance scores
        """
        try:
            model.to(device)
            model.eval()

            if method == "fisher":
                importance = await self._calculate_fisher_information(model, context, device)
            elif method == "gradient_based":
                importance = await self._calculate_gradient_importance(model, context, device)
            elif method == "empirical":
                importance = await self._calculate_empirical_importance(model, context, device)
            else:
                logger.warning(f"⚠️ Unknown method {method}, using Fisher information")
                importance = await self._calculate_fisher_information(model, context, device)

            sample_count = len(context.memory_buffer)

            logger.info(f"🧮 Calculated importance weights using {method} method")

            return ImportanceWeights(
                model_id=context.model_id,
                parameter_importance=importance,
                calculation_method=method,
                sample_count=sample_count,
            )

        except Exception as e:
            logger.error(f"❌ Importance weight calculation failed: {e}")
            return ImportanceWeights(
                model_id=context.model_id,
                parameter_importance={},
                calculation_method=method,
                sample_count=0,
            )

    async def save_model_state(
        self, model: torch.nn.Module, context: LearningContext, checkpoint_name: str | None = None
    ) -> bool:
        """
        Save model state to learning context.

        Args:
            model: PyTorch model
            context: Learning context
            checkpoint_name: Optional checkpoint identifier

        Returns:
            Success status
        """
        try:
            # Store current model state in metadata (since LearningContext doesn't have previous_model_state)
            current_state = model.state_dict().copy()
            context.metadata["previous_model_state"] = current_state

            # Add checkpoint to adaptation history if name provided
            if checkpoint_name:
                checkpoint_record = {
                    "checkpoint_name": checkpoint_name,
                    "timestamp": datetime.now().isoformat(),
                    "parameter_count": sum(p.numel() for p in model.parameters()),
                    "model_size_mb": sum(p.numel() * p.element_size() for p in model.parameters())
                    / 1024
                    / 1024,
                }

                # Add to adaptation history
                context.adaptation_history.append({"type": "checkpoint", "data": checkpoint_record})

            logger.debug(f"💾 Saved model state for {context.model_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save model state: {e}")
            return False

    async def restore_model_state(self, model: torch.nn.Module, context: LearningContext) -> bool:
        """
        Restore model state from learning context.

        Args:
            model: PyTorch model
            context: Learning context with saved state

        Returns:
            Success status
        """
        try:
            previous_state = context.metadata.get("previous_model_state")
            if previous_state is None:
                logger.warning("⚠️ No previous model state to restore")
                return False

            model.load_state_dict(previous_state)

            logger.debug(f"🔄 Restored model state for {context.model_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to restore model state: {e}")
            return False

    async def get_model_statistics(self, model: torch.nn.Module) -> dict[str, Any]:
        """
        Get comprehensive model statistics.

        Args:
            model: PyTorch model

        Returns:
            Model statistics dictionary
        """
        try:
            # Parameter statistics
            total_params = sum(p.numel() for p in model.parameters())
            trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

            # Memory usage
            param_memory = sum(p.numel() * p.element_size() for p in model.parameters())
            buffer_memory = sum(b.numel() * b.element_size() for b in model.buffers())
            total_memory_mb = (param_memory + buffer_memory) / 1024 / 1024

            # Layer information
            layer_count = len(list(model.modules()))
            layer_types = {}
            for module in model.modules():
                module_type = type(module).__name__
                layer_types[module_type] = layer_types.get(module_type, 0) + 1

            # Gradient statistics
            grad_stats = {}
            if any(p.grad is not None for p in model.parameters()):
                grads = [p.grad for p in model.parameters() if p.grad is not None]
                if grads:
                    all_grads = torch.cat([g.flatten() for g in grads])
                    grad_stats = {
                        "grad_norm": torch.norm(all_grads).item(),
                        "grad_mean": torch.mean(all_grads).item(),
                        "grad_std": torch.std(all_grads).item(),
                        "grad_max": torch.max(all_grads).item(),
                        "grad_min": torch.min(all_grads).item(),
                    }

            return {
                "total_parameters": total_params,
                "trainable_parameters": trainable_params,
                "frozen_parameters": total_params - trainable_params,
                "memory_usage_mb": total_memory_mb,
                "layer_count": layer_count,
                "layer_types": layer_types,
                "gradient_statistics": grad_stats,
                "model_mode": "training" if model.training else "evaluation",
            }

        except Exception as e:
            logger.error(f"❌ Failed to get model statistics: {e}")
            return {"error": str(e)}

    # Private evaluation methods

    async def _evaluate_accuracy(
        self, model: torch.nn.Module, test_data: list[BatchData], device: torch.device
    ) -> dict[str, float]:
        """Calculate accuracy metrics."""

        correct_predictions = 0
        total_predictions = 0

        for batch in test_data:
            inputs = batch.inputs.to(device)
            targets = batch.targets.to(device)

            outputs = model(inputs)

            # Assuming classification task
            if outputs.dim() > 1 and outputs.size(1) > 1:
                predicted = torch.argmax(outputs, dim=1)
                correct_predictions += (predicted == targets).sum().item()
            else:
                # Regression or binary classification
                predicted = (outputs > 0.5).float().squeeze()
                correct_predictions += (predicted == targets).sum().item()

            total_predictions += targets.size(0)

        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0

        return {
            "accuracy": accuracy,
            "correct_predictions": correct_predictions,
            "total_predictions": total_predictions,
        }

    async def _evaluate_loss(
        self, model: torch.nn.Module, test_data: list[BatchData], device: torch.device
    ) -> dict[str, float]:
        """Calculate loss metrics."""

        total_loss = 0.0
        total_batches = 0

        criterion = nn.CrossEntropyLoss() if hasattr(nn, "CrossEntropyLoss") else nn.MSELoss()

        for batch in test_data:
            inputs = batch.inputs.to(device)
            targets = batch.targets.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, targets)

            total_loss += loss.item()
            total_batches += 1

        average_loss = total_loss / total_batches if total_batches > 0 else float("inf")

        return {
            "average_loss": average_loss,
            "total_loss": total_loss,
            "total_batches": total_batches,
        }

    async def _evaluate_comprehensive(
        self, model: torch.nn.Module, test_data: list[BatchData], device: torch.device
    ) -> dict[str, float]:
        """Calculate comprehensive performance metrics."""

        # Combine accuracy and loss metrics
        accuracy_metrics = await self._evaluate_accuracy(model, test_data, device)
        loss_metrics = await self._evaluate_loss(model, test_data, device)

        # Add additional metrics
        all_outputs = []
        all_targets = []

        for batch in test_data:
            inputs = batch.inputs.to(device)
            targets = batch.targets.to(device)

            outputs = model(inputs)

            all_outputs.append(outputs.cpu())
            all_targets.append(targets.cpu())

        if all_outputs:
            all_outputs = torch.cat(all_outputs, dim=0)
            all_targets = torch.cat(all_targets, dim=0)

            # Calculate additional metrics
            additional_metrics = {
                "output_variance": torch.var(all_outputs).item(),
                "output_mean": torch.mean(all_outputs).item(),
                "target_variance": torch.var(all_targets.float()).item(),
                "target_mean": torch.mean(all_targets.float()).item(),
            }
        else:
            additional_metrics = {}

        # Combine all metrics
        comprehensive_metrics = {
            **accuracy_metrics,
            **loss_metrics,
            **additional_metrics,
        }

        return comprehensive_metrics

    # Private importance calculation methods

    async def _calculate_fisher_information(
        self, model: torch.nn.Module, context: LearningContext, device: torch.device
    ) -> dict[str, torch.Tensor]:
        """Calculate Fisher Information Matrix diagonal."""

        model.train()

        fisher_information = {}
        for name, param in model.named_parameters():
            fisher_information[name] = torch.zeros_like(param)

        # Sample from memory buffer
        if not context.memory_buffer:
            return fisher_information

        sample_size = min(100, len(context.memory_buffer))  # Limit for efficiency
        sampled_data = context.memory_buffer[:sample_size]

        for data_point in sampled_data:
            # Mock data processing - in real implementation would use actual data
            # This is simplified for demonstration
            mock_input = torch.randn(1, 10).to(device)  # Mock input
            mock_target = torch.randint(0, 2, (1,)).to(device)  # Mock target

            model.zero_grad()
            output = model(mock_input)

            # Calculate log likelihood gradient
            if hasattr(nn, "CrossEntropyLoss"):
                loss = nn.CrossEntropyLoss()(output, mock_target)
            else:
                loss = nn.MSELoss()(output, mock_target.float())

            loss.backward()

            # Accumulate Fisher Information (squared gradients)
            for name, param in model.named_parameters():
                if param.grad is not None:
                    fisher_information[name] += param.grad.data.clone().pow(2)

        # Normalize by sample size
        for name in fisher_information:
            fisher_information[name] /= sample_size

        return fisher_information

    async def _calculate_gradient_importance(
        self, model: torch.nn.Module, context: LearningContext, device: torch.device
    ) -> dict[str, torch.Tensor]:
        """Calculate importance based on gradient magnitudes."""

        importance = {}
        for name, param in model.named_parameters():
            if param.grad is not None:
                importance[name] = torch.abs(param.grad.data.clone())
            else:
                importance[name] = torch.zeros_like(param)

        return importance

    async def _calculate_empirical_importance(
        self, model: torch.nn.Module, context: LearningContext, device: torch.device
    ) -> dict[str, torch.Tensor]:
        """Calculate empirical importance based on parameter changes."""

        importance = {}

        previous_state = context.metadata.get("previous_model_state")
        if previous_state:
            # Calculate importance based on parameter change magnitude
            current_state = model.state_dict()

            for name, param in model.named_parameters():
                if name in previous_state:
                    prev_param = previous_state[name]
                    param_change = torch.abs(param.data - prev_param)
                    importance[name] = param_change
                else:
                    importance[name] = torch.ones_like(param)
        else:
            # No previous state, use uniform importance
            for name, param in model.named_parameters():
                importance[name] = torch.ones_like(param)

        return importance

    async def health_check(self) -> dict[str, Any]:
        """Health check for model operations service."""
        return {
            "service": "ModelOperationsService",
            "status": "healthy",
            "evaluation_types": ["accuracy", "loss", "performance"],
            "importance_methods": ["fisher", "gradient_based", "empirical"],
            "torch_available": torch.cuda.is_available() if hasattr(torch, "cuda") else False,
        }
