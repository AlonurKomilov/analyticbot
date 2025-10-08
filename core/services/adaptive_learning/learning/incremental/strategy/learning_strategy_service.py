"""
Learning Strategy Service
=========================

Microservice responsible for implementing various incremental learning strategies.

Single Responsibility: Execute learning strategies only.
"""

import logging
from typing import Any

import torch
import torch.nn as nn
import torch.optim as optim

from core.services.adaptive_learning.protocols.learning_protocols import (
    LearningStrategy,
    LearningTask,
)

from ..models import (
    ImportanceWeights,
    IncrementalLearningConfig,
    LearningContext,
    LearningResult,
)

logger = logging.getLogger(__name__)


class LearningStrategyService:
    """
    Learning strategy implementation microservice.

    Responsibilities:
    - Incremental SGD learning
    - Online SGD with adaptive learning rate
    - Continual learning with regularization (EWC)
    - Transfer learning
    - Reinforcement learning
    """

    def __init__(self, config: IncrementalLearningConfig | None = None):
        self.config = config or IncrementalLearningConfig()
        logger.info("🎯 Learning Strategy Service initialized")

    async def execute_strategy(
        self,
        strategy: LearningStrategy,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device,
        importance_weights: ImportanceWeights | None = None,
        data_processor: Any = None,
    ) -> LearningResult:
        """
        Execute the specified learning strategy.

        Args:
            strategy: Learning strategy to execute
            task: Learning task with data and parameters
            model: PyTorch model to train
            context: Learning context with history
            device: Torch device (CPU/GPU)
            importance_weights: EWC importance weights (for continual learning)
            data_processor: Data processing service for batch creation

        Returns:
            LearningResult with metrics and status
        """
        try:
            logger.info(f"🎯 Executing strategy: {strategy.value}")

            # Route to appropriate strategy implementation
            if strategy == LearningStrategy.INCREMENTAL:
                return await self._incremental_sgd(task, model, context, device, data_processor)
            elif strategy == LearningStrategy.ONLINE_SGD:
                return await self._online_sgd(task, model, context, device, data_processor)
            elif strategy == LearningStrategy.CONTINUAL_LEARNING:
                return await self._continual_learning(
                    task, model, context, device, importance_weights, data_processor
                )
            elif strategy == LearningStrategy.TRANSFER_LEARNING:
                return await self._transfer_learning(task, model, context, device, data_processor)
            elif strategy == LearningStrategy.REINFORCEMENT:
                return await self._reinforcement_learning(
                    task, model, context, device, data_processor
                )
            else:
                logger.warning(f"⚠️ Unknown strategy {strategy}, defaulting to incremental SGD")
                return await self._incremental_sgd(task, model, context, device, data_processor)

        except Exception as e:
            logger.error(f"❌ Strategy execution failed: {e}")
            return LearningResult(
                success=False,
                final_loss=float("inf"),
                metrics={},
                error=str(e),
                strategy_used=strategy.value,
            )

    async def _incremental_sgd(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device,
        data_processor: Any,
    ) -> LearningResult:
        """Standard incremental SGD learning"""

        model.to(device)
        model.train()

        # Setup optimizer
        optimizer = optim.SGD(
            model.parameters(),
            lr=self.config.learning_rate,
            momentum=self.config.momentum,
            weight_decay=self.config.weight_decay,
        )

        epochs = task.parameters.get("epochs", 10)
        batch_size = task.parameters.get("batch_size", 32)

        epoch_losses = []
        processed_samples = 0

        for epoch in range(epochs):
            epoch_loss = 0.0
            num_batches = 0

            # Get batches from data processor
            if data_processor:
                batches = await data_processor.create_batches(
                    task.parameters.get("training_data", []), batch_size
                )
            else:
                # Fallback simple batching
                batches = self._simple_batching(
                    task.parameters.get("training_data", []), batch_size
                )

            for batch_data in batches:
                optimizer.zero_grad()

                # Forward pass
                inputs = batch_data.inputs.to(device)
                targets = batch_data.targets.to(device)
                outputs = model(inputs)

                # Calculate loss
                if hasattr(nn, "CrossEntropyLoss"):
                    loss = nn.CrossEntropyLoss()(outputs, targets)
                else:
                    loss = nn.MSELoss()(outputs, targets)

                # Backward pass
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                num_batches += 1
                processed_samples += batch_data.batch_size

            avg_epoch_loss = epoch_loss / max(num_batches, 1)
            epoch_losses.append(avg_epoch_loss)

            logger.debug(f"📈 Epoch {epoch + 1}/{epochs}, Loss: {avg_epoch_loss:.4f}")

        return LearningResult(
            success=True,
            final_loss=epoch_losses[-1] if epoch_losses else float("inf"),
            metrics={
                "epoch_losses": epoch_losses,
                "learning_rate": self.config.learning_rate,
                "momentum": self.config.momentum,
            },
            epochs_completed=epochs,
            processed_samples=processed_samples,
            strategy_used="incremental_sgd",
        )

    async def _online_sgd(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device,
        data_processor: Any,
    ) -> LearningResult:
        """Online SGD with adaptive learning rate"""

        model.to(device)
        model.train()

        # Adaptive learning rate based on performance
        base_lr = self.config.learning_rate
        recent_losses_raw = context.learning_statistics.get("recent_losses", [])
        recent_losses = (
            recent_losses_raw
            if isinstance(recent_losses_raw, list)
            else [recent_losses_raw]
            if recent_losses_raw is not None
            else []
        )

        if len(recent_losses) >= 2:
            if recent_losses[-1] > recent_losses[-2]:
                # Loss increased, reduce learning rate
                adaptive_lr = base_lr * 0.8
            else:
                # Loss decreased, can use normal or slightly higher rate
                adaptive_lr = base_lr * 1.1
        else:
            adaptive_lr = base_lr

        # Clamp learning rate
        adaptive_lr = max(min(adaptive_lr, base_lr * 2), base_lr * 0.1)

        optimizer = optim.SGD(model.parameters(), lr=adaptive_lr, momentum=self.config.momentum)

        # Process data in small online batches
        online_batch_size = task.parameters.get("online_batch_size", 1)
        processed_samples = 0
        losses = []

        # Get batches
        if data_processor:
            batches = await data_processor.create_batches(
                task.parameters.get("training_data", []), online_batch_size
            )
        else:
            batches = self._simple_batching(
                task.parameters.get("training_data", []), online_batch_size
            )

        for batch_data in batches:
            optimizer.zero_grad()

            inputs = batch_data.inputs.to(device)
            targets = batch_data.targets.to(device)
            outputs = model(inputs)

            # Calculate loss
            if hasattr(nn, "CrossEntropyLoss"):
                loss = nn.CrossEntropyLoss()(outputs, targets)
            else:
                loss = nn.MSELoss()(outputs, targets)

            # Backward pass
            loss.backward()
            optimizer.step()

            losses.append(loss.item())
            processed_samples += batch_data.batch_size

        return LearningResult(
            success=True,
            final_loss=losses[-1] if losses else float("inf"),
            metrics={
                "all_losses": losses,
                "adaptive_lr_used": adaptive_lr,
                "base_lr": base_lr,
                "lr_adjustment_factor": adaptive_lr / base_lr,
            },
            epochs_completed=1,  # Online learning processes once
            processed_samples=processed_samples,
            strategy_used="online_sgd",
        )

    async def _continual_learning(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device,
        importance_weights: ImportanceWeights | None,
        data_processor: Any,
    ) -> LearningResult:
        """Continual learning with EWC-style regularization"""

        model.to(device)
        model.train()

        # Setup optimizer
        optimizer = optim.Adam(model.parameters(), lr=self.config.learning_rate)

        # Store previous parameters for regularization
        prev_params = {name: param.clone() for name, param in model.named_parameters()}

        epochs = task.parameters.get("epochs", 5)
        batch_size = task.parameters.get("batch_size", 32)
        regularization_strength = task.parameters.get("regularization_strength", 1000.0)

        epoch_losses = []
        regularization_losses = []
        processed_samples = 0

        for epoch in range(epochs):
            epoch_loss = 0.0
            epoch_reg_loss = 0.0
            num_batches = 0

            # Get batches
            if data_processor:
                batches = await data_processor.create_batches(
                    task.parameters.get("training_data", []), batch_size
                )
            else:
                batches = self._simple_batching(
                    task.parameters.get("training_data", []), batch_size
                )

            for batch_data in batches:
                optimizer.zero_grad()

                # Forward pass
                inputs = batch_data.inputs.to(device)
                targets = batch_data.targets.to(device)
                outputs = model(inputs)

                # Task loss
                if hasattr(nn, "CrossEntropyLoss"):
                    task_loss = nn.CrossEntropyLoss()(outputs, targets)
                else:
                    task_loss = nn.MSELoss()(outputs, targets)

                # Regularization loss (EWC)
                reg_loss = 0.0
                if importance_weights and importance_weights.parameter_importance:
                    for name, param in model.named_parameters():
                        if name in importance_weights.parameter_importance and name in prev_params:
                            importance = importance_weights.parameter_importance[name].to(device)
                            reg_loss += (importance * (param - prev_params[name]).pow(2)).sum()

                reg_loss *= regularization_strength

                # Total loss
                total_loss = task_loss + reg_loss

                # Backward pass
                total_loss.backward()
                optimizer.step()

                epoch_loss += task_loss.item()
                epoch_reg_loss += (
                    reg_loss.item() if isinstance(reg_loss, torch.Tensor) else reg_loss
                )
                num_batches += 1
                processed_samples += batch_data.batch_size

            avg_epoch_loss = epoch_loss / max(num_batches, 1)
            avg_reg_loss = epoch_reg_loss / max(num_batches, 1)

            epoch_losses.append(avg_epoch_loss)
            regularization_losses.append(avg_reg_loss)

            logger.debug(
                f"📈 Epoch {epoch + 1}/{epochs}, Task Loss: {avg_epoch_loss:.4f}, Reg Loss: {avg_reg_loss:.4f}"
            )

        return LearningResult(
            success=True,
            final_loss=epoch_losses[-1] if epoch_losses else float("inf"),
            metrics={
                "epoch_losses": epoch_losses,
                "regularization_losses": regularization_losses,
                "regularization_strength": regularization_strength,
                "ewc_enabled": importance_weights is not None,
            },
            epochs_completed=epochs,
            processed_samples=processed_samples,
            strategy_used="continual_learning_ewc",
        )

    async def _transfer_learning(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device,
        data_processor: Any,
    ) -> LearningResult:
        """Transfer learning with frozen/unfrozen layers"""

        model.to(device)
        model.train()

        # Freeze early layers for transfer learning
        freeze_layers = task.parameters.get("freeze_layers", True)
        fine_tune_epochs = task.parameters.get("fine_tune_epochs", 5)

        if freeze_layers:
            # Freeze all but last few layers
            total_params = list(model.parameters())
            freeze_count = max(1, len(total_params) // 2)

            for i, param in enumerate(total_params):
                if i < freeze_count:
                    param.requires_grad = False

        # Setup optimizer for unfrozen parameters only
        trainable_params = [p for p in model.parameters() if p.requires_grad]
        optimizer = optim.Adam(
            trainable_params, lr=self.config.learning_rate * 0.1
        )  # Lower LR for transfer

        batch_size = task.parameters.get("batch_size", 32)
        epoch_losses = []
        processed_samples = 0

        for epoch in range(fine_tune_epochs):
            epoch_loss = 0.0
            num_batches = 0

            # Get batches
            if data_processor:
                batches = await data_processor.create_batches(
                    task.parameters.get("training_data", []), batch_size
                )
            else:
                batches = self._simple_batching(
                    task.parameters.get("training_data", []), batch_size
                )

            for batch_data in batches:
                optimizer.zero_grad()

                inputs = batch_data.inputs.to(device)
                targets = batch_data.targets.to(device)
                outputs = model(inputs)

                # Calculate loss
                if hasattr(nn, "CrossEntropyLoss"):
                    loss = nn.CrossEntropyLoss()(outputs, targets)
                else:
                    loss = nn.MSELoss()(outputs, targets)

                # Backward pass
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                num_batches += 1
                processed_samples += batch_data.batch_size

            avg_epoch_loss = epoch_loss / max(num_batches, 1)
            epoch_losses.append(avg_epoch_loss)

            logger.debug(
                f"📈 Transfer Epoch {epoch + 1}/{fine_tune_epochs}, Loss: {avg_epoch_loss:.4f}"
            )

        # Unfreeze all parameters after transfer learning
        for param in model.parameters():
            param.requires_grad = True

        return LearningResult(
            success=True,
            final_loss=epoch_losses[-1] if epoch_losses else float("inf"),
            metrics={
                "epoch_losses": epoch_losses,
                "freeze_layers_used": freeze_layers,
                "trainable_params": len(trainable_params),
                "transfer_lr": self.config.learning_rate * 0.1,
            },
            epochs_completed=fine_tune_epochs,
            processed_samples=processed_samples,
            strategy_used="transfer_learning",
        )

    async def _reinforcement_learning(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device,
        data_processor: Any,
    ) -> LearningResult:
        """Basic reinforcement learning (simplified implementation)"""

        model.to(device)
        model.train()

        # This is a simplified RL implementation
        # In practice, would need environment, replay buffer, etc.

        episodes = task.parameters.get("episodes", 100)
        learning_rate = task.parameters.get("rl_lr", self.config.learning_rate)

        optimizer = optim.Adam(model.parameters(), lr=learning_rate)

        episode_rewards = []
        processed_samples = 0

        for episode in range(episodes):
            episode_reward = 0.0

            # Simplified training on provided data
            batch_size = task.parameters.get("batch_size", 32)

            if data_processor:
                batches = await data_processor.create_batches(
                    task.parameters.get("training_data", []), batch_size
                )
            else:
                batches = self._simple_batching(
                    task.parameters.get("training_data", []), batch_size
                )

            for batch_data in batches:
                optimizer.zero_grad()

                inputs = batch_data.inputs.to(device)
                targets = batch_data.targets.to(device)

                # Forward pass
                q_values = model(inputs)

                # Simplified Q-learning loss
                if hasattr(nn, "MSELoss"):
                    loss = nn.MSELoss()(q_values, targets)
                else:
                    loss = torch.mean((q_values - targets) ** 2)

                # Backward pass
                loss.backward()
                optimizer.step()

                # Simplified reward (negative loss)
                episode_reward -= loss.item()
                processed_samples += batch_data.batch_size

            episode_rewards.append(episode_reward)

            if episode % 10 == 0:
                logger.debug(f"🎮 Episode {episode}/{episodes}, Reward: {episode_reward:.4f}")

        return LearningResult(
            success=True,
            final_loss=-episode_rewards[-1]
            if episode_rewards
            else float("inf"),  # Convert reward to loss
            metrics={
                "episode_rewards": episode_rewards,
                "average_reward": sum(episode_rewards) / len(episode_rewards)
                if episode_rewards
                else 0,
                "rl_learning_rate": learning_rate,
            },
            epochs_completed=episodes,
            processed_samples=processed_samples,
            strategy_used="reinforcement_learning",
        )

    def _simple_batching(self, data: list[dict[str, Any]], batch_size: int) -> list[Any]:
        """Fallback simple batching when data processor is not available"""
        # This is a simplified version - in real implementation would properly batch tensors
        batches = []

        for i in range(0, len(data), batch_size):
            batch_data = data[i : i + batch_size]

            # Create mock BatchData object
            class MockBatchData:
                def __init__(self, batch_data, batch_size):
                    # Mock implementation - would need real tensor conversion
                    self.inputs = torch.randn(len(batch_data), 10)  # Mock input
                    self.targets = torch.randn(len(batch_data), 1)  # Mock target
                    self.batch_size = len(batch_data)

            batches.append(MockBatchData(batch_data, len(batch_data)))

        return batches

    async def health_check(self) -> dict[str, Any]:
        """Health check for learning strategy service."""
        return {
            "service": "LearningStrategyService",
            "status": "healthy",
            "strategies_available": [strategy.value for strategy in LearningStrategy],
            "config_loaded": self.config is not None,
        }
