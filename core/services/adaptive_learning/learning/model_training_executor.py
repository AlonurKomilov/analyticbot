"""
Model Training Executor
======================

Executes model training tasks with resource management and monitoring.
Extracted from LearningTaskService god object to focus on execution concerns.
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import psutil
import torch

from core.services.adaptive_learning.protocols.learning_protocols import (
    LearningContext,
    LearningTask,
)

from .incremental_learning_engine import IncrementalLearningEngine

logger = logging.getLogger(__name__)


class ExecutionPhase(Enum):
    """Training execution phases"""

    INITIALIZING = "initializing"
    LOADING_MODEL = "loading_model"
    PREPARING_DATA = "preparing_data"
    TRAINING = "training"
    VALIDATING = "validating"
    SAVING_MODEL = "saving_model"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ResourceUsage:
    """Resource usage tracking"""

    cpu_percent: float
    memory_mb: float
    gpu_memory_mb: float
    gpu_utilization: float
    disk_io_mb: float


@dataclass
class TrainingProgress:
    """Detailed training progress"""

    task_id: str
    phase: ExecutionPhase
    epoch: int
    total_epochs: int
    batch: int
    total_batches: int
    current_loss: float
    best_loss: float
    learning_rate: float
    elapsed_time: timedelta
    estimated_remaining: timedelta
    resource_usage: ResourceUsage


class ModelTrainingExecutor:
    """
    Executes model training tasks with comprehensive monitoring.

    Focuses solely on execution concerns:
    - Resource management and monitoring
    - Training progress tracking
    - Model loading/saving
    - Error handling and recovery
    """

    def __init__(self, learning_engine: IncrementalLearningEngine):
        self.learning_engine = learning_engine

        # Execution tracking
        self.active_executions: dict[str, TrainingProgress] = {}
        self.execution_callbacks: dict[str, list[Callable]] = {}

        # Resource monitoring
        self.resource_monitor_active = False
        self.resource_history: dict[str, list[ResourceUsage]] = {}

        # Model storage
        self.model_registry: dict[str, torch.nn.Module] = {}

        # Device management
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.gpu_available = torch.cuda.is_available()

        logger.info(f"🚀 Model Training Executor initialized (device: {self.device})")

    async def execute_training_task(
        self,
        task: LearningTask,
        progress_callback: Callable[[str, float, str], Any] | None = None,
    ) -> dict[str, Any]:
        """Execute training task with monitoring"""
        try:
            task_id = task.task_id

            # Initialize progress tracking
            progress = TrainingProgress(
                task_id=task_id,
                phase=ExecutionPhase.INITIALIZING,
                epoch=0,
                total_epochs=(task.parameters.get("epochs", 10) if task.parameters else 10),
                batch=0,
                total_batches=0,
                current_loss=float("inf"),
                best_loss=float("inf"),
                learning_rate=0.001,
                elapsed_time=timedelta(),
                estimated_remaining=timedelta(),
                resource_usage=ResourceUsage(0, 0, 0, 0, 0),
            )

            self.active_executions[task_id] = progress

            # Register progress callback
            if progress_callback:
                if task_id not in self.execution_callbacks:
                    self.execution_callbacks[task_id] = []
                self.execution_callbacks[task_id].append(progress_callback)

            # Start resource monitoring
            await self._start_resource_monitoring(task_id)

            start_time = datetime.utcnow()

            # Phase 1: Load or create model
            await self._update_phase(task_id, ExecutionPhase.LOADING_MODEL, "Loading model")
            model = await self._load_or_create_model(task.model_id)
            if not model:
                return await self._fail_execution(task_id, "Failed to load/create model")

            # Phase 2: Prepare data
            await self._update_phase(task_id, ExecutionPhase.PREPARING_DATA, "Preparing data")
            data_preparation_result = await self._prepare_training_data(task)
            if not data_preparation_result["success"]:
                return await self._fail_execution(
                    task_id,
                    f"Data preparation failed: {data_preparation_result['error']}",
                )

            # Phase 3: Training
            await self._update_phase(task_id, ExecutionPhase.TRAINING, "Training model")
            training_result = await self._execute_training_strategy(task, model)
            if not training_result["success"]:
                return await self._fail_execution(
                    task_id,
                    f"Training failed: {training_result.get('error', 'Unknown error')}",
                )

            # Phase 4: Validation
            validation_data = task.parameters.get("validation_data")
            if validation_data:
                await self._update_phase(task_id, ExecutionPhase.VALIDATING, "Validating model")
                validation_result = await self._validate_trained_model(model, validation_data)
                training_result["validation_metrics"] = validation_result

            # Phase 5: Save model
            await self._update_phase(task_id, ExecutionPhase.SAVING_MODEL, "Saving model")
            save_result = await self._save_model(task.model_id, model, training_result)
            if not save_result:
                logger.warning(f"⚠️ Failed to save model for task {task_id}")

            # Complete execution
            await self._update_phase(task_id, ExecutionPhase.COMPLETED, "Training completed")

            execution_time = datetime.utcnow() - start_time

            # Final result
            result = {
                "success": True,
                "task_id": task_id,
                "execution_time": execution_time.total_seconds(),
                "final_metrics": training_result.get("metrics", {}),
                "model_saved": save_result,
                "resource_usage_summary": await self._get_resource_summary(task_id),
                **training_result,
            }

            await self._cleanup_execution(task_id)
            return result

        except Exception as e:
            # Get task_id safely
            task_id = getattr(task, "task_id", "unknown")
            logger.error(f"❌ Training execution failed: {e}")
            return await self._fail_execution(task_id, f"Execution error: {e}")

    async def get_execution_progress(self, task_id: str) -> TrainingProgress | None:
        """Get current execution progress"""
        return self.active_executions.get(task_id)

    async def cancel_execution(self, task_id: str) -> bool:
        """Cancel active execution"""
        try:
            if task_id in self.active_executions:
                await self._update_phase(task_id, ExecutionPhase.FAILED, "Execution cancelled")
                await self._cleanup_execution(task_id)
                logger.info(f"🚫 Cancelled training execution: {task_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"❌ Failed to cancel execution: {e}")
            return False

    async def _load_or_create_model(self, model_id: str) -> torch.nn.Module | None:
        """Load existing model or create new one"""
        try:
            # Check if model is already loaded
            if model_id in self.model_registry:
                return self.model_registry[model_id]

            # Try to load existing model (simplified - would integrate with model versioning)
            model = await self._create_default_model()

            if model:
                self.model_registry[model_id] = model
                logger.info(f"📥 Loaded model: {model_id}")

            return model

        except Exception as e:
            logger.error(f"❌ Failed to load/create model {model_id}: {e}")
            return None

    async def _create_default_model(self) -> torch.nn.Module:
        """Create a default model (simplified)"""

        # Simple feedforward network
        model = torch.nn.Sequential(
            torch.nn.Linear(10, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 32),
            torch.nn.ReLU(),
            torch.nn.Linear(32, 2),  # Binary classification
        )

        return model

    async def _prepare_training_data(self, task: LearningTask) -> dict[str, Any]:
        """Prepare training data"""
        try:
            # Get training data from parameters
            training_data = task.parameters.get("training_data", [])
            validation_data = task.parameters.get("validation_data")

            # Validate data format
            if not training_data:
                return {"success": False, "error": "No training data provided"}

            # Check data consistency
            sample_data = training_data[0]
            required_keys = ["input", "target"]  # Simplified

            for key in required_keys:
                if key not in sample_data:
                    return {"success": False, "error": f"Missing required key: {key}"}

            # Data statistics
            data_stats = {
                "training_samples": len(training_data),
                "validation_samples": len(validation_data) if validation_data else 0,
                "input_shape": self._infer_input_shape(training_data),
                "output_shape": self._infer_output_shape(training_data),
            }

            return {"success": True, "data_stats": data_stats}

        except Exception as e:
            logger.error(f"❌ Data preparation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_training_strategy(
        self, task: LearningTask, model: torch.nn.Module
    ) -> dict[str, Any]:
        """Execute training using learning engine"""
        try:
            # Move model to device
            model.to(self.device)

            # Execute incremental learning
            # Create context for the learning task
            context = LearningContext(
                model_id=task.model_id,
                task_id=task.task_id,
                strategy=task.strategy,
                task_boundaries={},  # Add any task-specific boundaries
            )

            # Get training data from task parameters
            training_data = task.parameters.get("training_data", []) if task.parameters else []
            validation_data = task.parameters.get("validation_data") if task.parameters else None

            result = self.learning_engine.perform_incremental_update(
                context=context,
                training_data=training_data,
                validation_data=validation_data,
            )

            # Update progress throughout training (simplified)
            if result.get("success", False):
                # Simulate progress updates
                epochs = task.parameters.get("epochs", 10) if task.parameters else 10
                for epoch in range(epochs):
                    progress_percent = ((epoch + 1) / epochs) * 100
                    await self._notify_progress(
                        task.task_id, progress_percent, f"Epoch {epoch + 1}/{epochs}"
                    )
                    await asyncio.sleep(0.1)  # Simulate training time

            return result

        except Exception as e:
            logger.error(f"❌ Training strategy execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def _validate_trained_model(
        self, model: torch.nn.Module, validation_data: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Validate trained model"""
        try:
            model.eval()

            total_loss = 0.0
            correct = 0
            total = 0

            with torch.no_grad():
                for item in validation_data:
                    # Prepare single sample
                    if "input" in item and "target" in item:
                        input_data = item["input"]
                        target_data = item["target"]
                    else:
                        continue

                    # Convert to tensors
                    if isinstance(input_data, (list, tuple)):
                        input_tensor = torch.tensor(
                            [input_data], dtype=torch.float32, device=self.device
                        )
                    else:
                        input_tensor = torch.tensor(
                            [[input_data]], dtype=torch.float32, device=self.device
                        )

                    target_tensor = torch.tensor(
                        [target_data], dtype=torch.long, device=self.device
                    )

                    # Forward pass
                    outputs = model(input_tensor)

                    # Calculate loss
                    loss = torch.nn.CrossEntropyLoss()(outputs, target_tensor)
                    total_loss += loss.item()

                    # Calculate accuracy
                    _, predicted = torch.max(outputs.data, 1)
                    total += target_tensor.size(0)
                    correct += (predicted == target_tensor).sum().item()

            metrics = {
                "validation_loss": total_loss / len(validation_data),
                "validation_accuracy": 100.0 * correct / total if total > 0 else 0.0,
            }

            model.train()
            return metrics

        except Exception as e:
            logger.error(f"❌ Model validation failed: {e}")
            return {"validation_loss": float("inf"), "validation_accuracy": 0.0}

    async def _save_model(
        self, model_id: str, model: torch.nn.Module, training_result: dict[str, Any]
    ) -> bool:
        """Save trained model"""
        try:
            # Update model registry
            self.model_registry[model_id] = model

            # In a real implementation, would save to persistent storage
            # with version management and metadata

            logger.info(f"💾 Saved model: {model_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save model {model_id}: {e}")
            return False

    async def _start_resource_monitoring(self, task_id: str) -> None:
        """Start resource monitoring for task"""
        self.resource_history[task_id] = []

        async def monitor():
            while task_id in self.active_executions:
                try:
                    # CPU and Memory
                    cpu_percent = psutil.cpu_percent()
                    memory = psutil.virtual_memory()
                    memory_mb = (memory.total - memory.available) / (1024 * 1024)

                    # GPU monitoring (if available)
                    gpu_memory_mb = 0.0
                    gpu_utilization = 0.0
                    if self.gpu_available:
                        try:
                            gpu_memory_mb = torch.cuda.memory_allocated() / (1024 * 1024)
                            # GPU utilization would need nvidia-ml-py
                        except:
                            pass

                    # Disk I/O (simplified)
                    disk_io = psutil.disk_io_counters()
                    disk_io_mb = (
                        (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024)
                        if disk_io
                        else 0.0
                    )

                    usage = ResourceUsage(
                        cpu_percent=cpu_percent,
                        memory_mb=memory_mb,
                        gpu_memory_mb=gpu_memory_mb,
                        gpu_utilization=gpu_utilization,
                        disk_io_mb=disk_io_mb,
                    )

                    self.resource_history[task_id].append(usage)

                    # Update execution progress
                    if task_id in self.active_executions:
                        self.active_executions[task_id].resource_usage = usage

                    await asyncio.sleep(5)  # Monitor every 5 seconds

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"❌ Resource monitoring error: {e}")

        asyncio.create_task(monitor())

    async def _update_phase(self, task_id: str, phase: ExecutionPhase, description: str) -> None:
        """Update execution phase"""
        if task_id in self.active_executions:
            progress = self.active_executions[task_id]
            progress.phase = phase

            await self._notify_progress(
                task_id, progress.epoch / progress.total_epochs * 100, description
            )

    async def _notify_progress(
        self, task_id: str, progress_percent: float, description: str
    ) -> None:
        """Notify progress callbacks"""
        if task_id in self.execution_callbacks:
            for callback in self.execution_callbacks[task_id]:
                try:
                    # Handle both sync and async callbacks
                    if asyncio.iscoroutinefunction(callback):
                        await callback(task_id, progress_percent, description)
                    else:
                        callback(task_id, progress_percent, description)
                except Exception as e:
                    logger.error(f"❌ Progress callback error: {e}")

    async def _get_resource_summary(self, task_id: str) -> dict[str, Any]:
        """Get resource usage summary"""
        if task_id not in self.resource_history:
            return {}

        history = self.resource_history[task_id]
        if not history:
            return {}

        # Calculate averages and peaks
        avg_cpu = sum(r.cpu_percent for r in history) / len(history)
        peak_cpu = max(r.cpu_percent for r in history)
        avg_memory = sum(r.memory_mb for r in history) / len(history)
        peak_memory = max(r.memory_mb for r in history)
        avg_gpu_memory = sum(r.gpu_memory_mb for r in history) / len(history)
        peak_gpu_memory = max(r.gpu_memory_mb for r in history)

        return {
            "average_cpu_percent": avg_cpu,
            "peak_cpu_percent": peak_cpu,
            "average_memory_mb": avg_memory,
            "peak_memory_mb": peak_memory,
            "average_gpu_memory_mb": avg_gpu_memory,
            "peak_gpu_memory_mb": peak_gpu_memory,
            "total_samples": len(history),
        }

    async def _fail_execution(self, task_id: str, error_message: str) -> dict[str, Any]:
        """Handle execution failure"""
        if task_id in self.active_executions:
            self.active_executions[task_id].phase = ExecutionPhase.FAILED

        await self._cleanup_execution(task_id)

        return {
            "success": False,
            "task_id": task_id,
            "error": error_message,
            "phase": ExecutionPhase.FAILED.value,
        }

    async def _cleanup_execution(self, task_id: str) -> None:
        """Clean up execution resources"""
        # Remove from active executions
        if task_id in self.active_executions:
            del self.active_executions[task_id]

        # Clean up callbacks
        if task_id in self.execution_callbacks:
            del self.execution_callbacks[task_id]

        # Keep resource history for analysis
        # (could be cleaned up later or moved to persistent storage)

    def _infer_input_shape(self, training_data: list[dict[str, Any]]) -> tuple:
        """Infer input shape from training data"""
        if not training_data:
            return (0,)

        sample = training_data[0]
        if "input" in sample:
            input_data = sample["input"]
            if isinstance(input_data, (list, tuple)):
                return (len(input_data),)
            else:
                return (1,)

        return (0,)

    def _infer_output_shape(self, training_data: list[dict[str, Any]]) -> tuple:
        """Infer output shape from training data"""
        if not training_data:
            return (0,)

        sample = training_data[0]
        if "target" in sample:
            target_data = sample["target"]
            if isinstance(target_data, (list, tuple)):
                return (len(target_data),)
            else:
                return (1,)

        return (0,)

    def get_active_executions(self) -> list[str]:
        """Get list of active execution task IDs"""
        return list(self.active_executions.keys())

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""

        return {
            "service": "model_training_executor",
            "status": "healthy",
            "device": str(self.device),
            "gpu_available": self.gpu_available,
            "active_executions": len(self.active_executions),
            "models_loaded": len(self.model_registry),
            "resource_monitoring_active": len(self.resource_history),
        }
