"""
Learning Task Service
====================

Clean architecture replacement for the monolithic LearningTaskService.
Delegates to specialized components while maintaining the original interface.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .learning_tasks import (
    LearningTaskManager,
    LearningTaskConfig,
    IncrementalLearningEngine,
    ModelTrainingExecutor,
    TaskPriority
)
from .protocols.learning_protocols import (
    LearningProtocol,
    LearningTask,
    LearningStrategy,
    LearningProgress,
    UpdateStatus
)

logger = logging.getLogger(__name__)


class LearningTaskService(LearningProtocol):
    """
    Clean, focused learning task service.
    
    Replaces the 830-line god object with a clean coordinator pattern.
    Maintains compatibility while delegating to specialized components.
    """
    
    def __init__(self, config: Optional[LearningTaskConfig] = None):
        # Create specialized components
        self.task_manager = LearningTaskManager(config)
        self.learning_engine = IncrementalLearningEngine()
        self.training_executor = ModelTrainingExecutor(self.learning_engine)
        
        # Service state
        self.is_running = False
        
        logger.info("🎯 Clean LearningTaskService initialized")
    
    async def start_learning_service(self) -> bool:
        """Start learning service"""
        try:
            # Start task manager
            if not await self.task_manager.start_manager():
                return False
            
            self.is_running = True
            logger.info("✅ LearningTaskService started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start LearningTaskService: {e}")
            return False
    
    async def stop_learning_service(self) -> bool:
        """Stop learning service"""
        try:
            # Stop task manager
            await self.task_manager.stop_manager()
            
            self.is_running = False
            logger.info("⏹️ LearningTaskService stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop LearningTaskService: {e}")
            return False
    
    async def create_learning_task(
        self,
        model_id: str,
        strategy: LearningStrategy,
        training_data: List[Dict[str, Any]],
        validation_data: Optional[List[Dict[str, Any]]] = None,
        task_parameters: Optional[Dict[str, Any]] = None,
        priority: str = "normal"
    ) -> Optional[str]:
        """Create new learning task"""
        try:
            # Convert priority string to enum
            task_priority = TaskPriority.NORMAL
            try:
                task_priority = TaskPriority(priority.lower())
            except ValueError:
                logger.warning(f"⚠️ Unknown priority '{priority}', using normal")
            
            return await self.task_manager.create_task(
                model_id=model_id,
                strategy=strategy,
                training_data=training_data,
                validation_data=validation_data,
                priority=task_priority,
                dependencies=None,
                task_parameters=task_parameters
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create learning task: {e}")
            return None
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        return await self.task_manager.get_task_status(task_id)
    
    async def get_active_tasks(self, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active learning tasks"""
        return await self.task_manager.get_active_tasks(model_id)
    
    async def get_pending_tasks(self, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pending learning tasks"""
        return await self.task_manager.get_pending_tasks(model_id)
    
    async def cancel_task(self, task_id: str, reason: str = "User requested") -> bool:
        """Cancel learning task"""
        # Cancel in task manager
        manager_result = await self.task_manager.cancel_task(task_id, reason)
        
        # Cancel in training executor if active
        executor_result = await self.training_executor.cancel_execution(task_id)
        
        return manager_result or executor_result
    
    async def get_learning_statistics(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get learning statistics"""
        try:
            # Get statistics from task manager
            task_stats = await self.task_manager.get_task_statistics(model_id)
            
            # Get learning context information
            learning_contexts = {}
            if model_id:
                context = self.learning_engine.get_learning_context(model_id)
                if context:
                    learning_contexts[model_id] = {
                        'total_updates': context.learning_statistics.get('total_updates', 0),
                        'average_loss': context.learning_statistics.get('average_loss', 0.0),
                        'memory_buffer_size': len(context.memory_buffer),
                        'adaptation_history_length': len(context.adaptation_history)
                    }
            
            # Get execution statistics
            active_executions = self.training_executor.get_active_executions()
            
            return {
                'task_statistics': task_stats,
                'learning_contexts': learning_contexts,
                'active_executions': len(active_executions),
                'service_health': {
                    'task_manager': self.task_manager.get_service_health(),
                    'learning_engine': self.learning_engine.get_service_health(),
                    'training_executor': self.training_executor.get_service_health()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get learning statistics: {e}")
            return {}
    
    # LearningProtocol implementation
    
    async def train_model(
        self,
        model_id: str,
        training_data: List[Dict[str, Any]],
        validation_data: Optional[List[Dict[str, Any]]] = None,
        strategy: LearningStrategy = LearningStrategy.INCREMENTAL
    ) -> LearningProgress:
        """Train model using specified strategy"""
        try:
            # Create task
            task_id = await self.create_learning_task(
                model_id=model_id,
                strategy=strategy,
                training_data=training_data,
                validation_data=validation_data
            )
            
            if not task_id:
                return LearningProgress(
                    task_id="",
                    model_id=model_id,
                    strategy=strategy,
                    status=UpdateStatus.FAILED,
                    progress_percent=0.0,
                    current_epoch=0,
                    total_epochs=0,
                    loss=float('inf'),
                    metrics={},
                    started_at=datetime.utcnow(),
                    estimated_completion=None
                )
            
            # Wait for task to start and return initial progress
            await asyncio.sleep(0.1)  # Give task time to start
            
            status = await self.get_task_status(task_id)
            if status and 'progress' in status:
                progress_data = status['progress']
                return LearningProgress(
                    task_id=progress_data.get('task_id', task_id),
                    model_id=progress_data.get('model_id', model_id),
                    strategy=LearningStrategy(progress_data.get('strategy', strategy.value)),
                    status=UpdateStatus(progress_data.get('status', UpdateStatus.IN_PROGRESS.value)),
                    progress_percent=progress_data.get('progress_percent', 0.0),
                    current_epoch=progress_data.get('current_epoch', 0),
                    total_epochs=progress_data.get('total_epochs', 10),
                    loss=progress_data.get('loss', 0.0),
                    metrics=progress_data.get('metrics', {}),
                    started_at=datetime.fromisoformat(progress_data.get('started_at', datetime.utcnow().isoformat())),
                    estimated_completion=None
                )
            
            # Fallback progress
            return LearningProgress(
                task_id=task_id,
                model_id=model_id,
                strategy=strategy,
                status=UpdateStatus.IN_PROGRESS,
                progress_percent=0.0,
                current_epoch=0,
                total_epochs=10,
                loss=0.0,
                metrics={},
                started_at=datetime.utcnow(),
                estimated_completion=None
            )
            
        except Exception as e:
            logger.error(f"❌ Train model failed: {e}")
            return LearningProgress(
                task_id="",
                model_id=model_id,
                strategy=strategy,
                status=UpdateStatus.FAILED,
                progress_percent=0.0,
                current_epoch=0,
                total_epochs=0,
                loss=float('inf'),
                metrics={},
                started_at=datetime.utcnow(),
                estimated_completion=None
            )
    
    async def get_learning_progress(self, task_id: str) -> Optional[LearningProgress]:
        """Get learning progress for a task"""
        try:
            status = await self.get_task_status(task_id)
            if not status or 'progress' not in status:
                return None
            
            progress_data = status['progress']
            return LearningProgress(
                task_id=progress_data.get('task_id', task_id),
                model_id=progress_data.get('model_id', ''),
                strategy=LearningStrategy(progress_data.get('strategy', LearningStrategy.INCREMENTAL.value)),
                status=UpdateStatus(progress_data.get('status', UpdateStatus.PENDING.value)),
                progress_percent=progress_data.get('progress_percent', 0.0),
                current_epoch=progress_data.get('current_epoch', 0),
                total_epochs=progress_data.get('total_epochs', 0),
                loss=progress_data.get('loss', 0.0),
                metrics=progress_data.get('metrics', {}),
                started_at=datetime.fromisoformat(progress_data.get('started_at', datetime.utcnow().isoformat())),
                estimated_completion=None
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to get learning progress: {e}")
            return None
    
    async def update_model_incremental(
        self,
        model_id: str,
        new_data: List[Dict[str, Any]],
        learning_rate: float = 0.001
    ) -> bool:
        """Update model incrementally with new data"""
        try:
            task_id = await self.create_learning_task(
                model_id=model_id,
                strategy=LearningStrategy.INCREMENTAL,
                training_data=new_data,
                task_parameters={
                    'learning_rate': learning_rate,
                    'epochs': 1  # Single epoch for incremental update
                }
            )
            
            return task_id is not None
            
        except Exception as e:
            logger.error(f"❌ Incremental update failed: {e}")
            return False
    
    async def evaluate_model_performance(
        self,
        model_id: str,
        test_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Evaluate model performance on test data"""
        try:
            # Create evaluation task (using validation data field)
            task_id = await self.create_learning_task(
                model_id=model_id,
                strategy=LearningStrategy.INCREMENTAL,
                training_data=[],  # No training, just evaluation
                validation_data=test_data,
                task_parameters={'evaluation_only': True}
            )
            
            if not task_id:
                return {}
            
            # Wait for evaluation to complete (simplified)
            max_wait = 30  # 30 seconds
            wait_time = 0
            
            while wait_time < max_wait:
                status = await self.get_task_status(task_id)
                if status and status.get('status') == 'completed':
                    progress = status.get('progress', {})
                    return progress.get('metrics', {})
                elif status and status.get('status') == 'failed':
                    logger.error(f"❌ Evaluation failed: {status.get('error_message', 'Unknown error')}")
                    return {}
                
                await asyncio.sleep(1)
                wait_time += 1
            
            # Timeout
            await self.cancel_task(task_id, "Evaluation timeout")
            return {}
            
        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            return {}
    
    # Additional utility methods
    
    async def get_model_learning_context(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get learning context for a model"""
        try:
            context = self.learning_engine.get_learning_context(model_id)
            if not context:
                return None
            
            return {
                'model_id': context.model_id,
                'memory_buffer_size': len(context.memory_buffer),
                'task_boundaries': context.task_boundaries,
                'learning_statistics': context.learning_statistics,
                'adaptation_history_length': len(context.adaptation_history),
                'last_adaptation': context.adaptation_history[-1] if context.adaptation_history else None
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get learning context: {e}")
            return None
    
    async def clear_model_memory(self, model_id: str) -> bool:
        """Clear memory buffer for a model"""
        try:
            context = self.learning_engine.get_learning_context(model_id)
            if context:
                context.memory_buffer.clear()
                context.adaptation_history.clear()
                logger.info(f"🧹 Cleared memory for model: {model_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to clear model memory: {e}")
            return False
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            'service': 'learning_task_service',
            'status': 'healthy' if self.is_running else 'stopped',
            'component_health': {
                'task_manager': self.task_manager.get_service_health(),
                'learning_engine': self.learning_engine.get_service_health(),
                'training_executor': self.training_executor.get_service_health()
            }
        }
    
    async def shutdown(self) -> None:
        """Shutdown service"""
        try:
            await self.stop_learning_service()
            logger.info("🛑 LearningTaskService shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")