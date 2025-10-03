"""
Task Creator
===========

Handles learning task creation, validation, and configuration.
Extracted from LearningTaskManager god object to focus on task creation concerns.
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..protocols.learning_protocols import (
    LearningTask,
    LearningStrategy,
    UpdateStatus
)

logger = logging.getLogger(__name__)


@dataclass
class TaskCreationConfig:
    """Configuration for task creation"""
    max_retries: int = 3
    default_batch_size: int = 32
    memory_limit_mb: int = 1024
    task_timeout_minutes: int = 60
    auto_resource_estimation: bool = True


class TaskCreator:
    """
    Handles learning task creation and validation.
    
    Focuses solely on:
    - Task creation and ID generation
    - Task validation and configuration
    - Resource requirement estimation
    - Task dependency resolution
    """
    
    def __init__(self, config: Optional[TaskCreationConfig] = None):
        self.config = config or TaskCreationConfig()
        
        # Validation rules
        self.required_fields = ['model_id', 'learning_strategy', 'data_source']
        self.strategy_configs = {
            LearningStrategy.INCREMENTAL: {
                'min_batch_size': 16,
                'max_batch_size': 128,
                'memory_factor': 1.0
            },
            LearningStrategy.BATCH_UPDATE: {
                'min_batch_size': 32,
                'max_batch_size': 512,
                'memory_factor': 2.0
            },
            LearningStrategy.ONLINE_SGD: {
                'min_batch_size': 1,
                'max_batch_size': 32,
                'memory_factor': 0.5
            },
            LearningStrategy.CONTINUAL_LEARNING: {
                'min_batch_size': 16,
                'max_batch_size': 64,
                'memory_factor': 1.5
            }
        }
        
        logger.info("🎨 Task Creator initialized")
    
    async def create_task(
        self,
        model_id: str,
        learning_strategy: LearningStrategy,
        task_config: Dict[str, Any],
        priority: str = "normal"
    ) -> Optional[LearningTask]:
        """Create a new learning task with validation"""
        try:
            # Generate unique task ID
            task_id = self._generate_task_id(model_id)
            
            # Prepare task configuration
            full_config = await self._prepare_task_config(
                model_id, learning_strategy, task_config
            )
            
            # Create task object
            task = LearningTask(
                task_id=task_id,
                model_id=model_id,
                strategy=learning_strategy,
                data_source=task_config.get('data_source', 'default'),
                parameters=full_config,
                status=UpdateStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            # Validate task
            if not await self._validate_task(task):
                logger.error(f"❌ Task validation failed for {task_id}")
                return None
            
            # Estimate resources
            resource_requirements = await self._estimate_resource_requirements(task)
            task.parameters['resource_requirements'] = resource_requirements
            
            # Set estimated duration
            estimated_duration = await self._estimate_task_duration(task)
            task.parameters['estimated_duration_minutes'] = estimated_duration.total_seconds() / 60
            
            logger.info(f"🎨 Created task {task_id} for model {model_id}")
            return task
            
        except Exception as e:
            logger.error(f"❌ Failed to create task: {e}")
            return None
    
    async def validate_task_config(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate task configuration and return validation result"""
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check required fields
            for field in self.required_fields:
                if field not in task_config:
                    validation_result['errors'].append(f"Missing required field: {field}")
                    validation_result['is_valid'] = False
            
            # Validate learning strategy
            if 'learning_strategy' in task_config:
                strategy = task_config['learning_strategy']
                if isinstance(strategy, str):
                    try:
                        strategy = LearningStrategy(strategy)
                    except ValueError:
                        validation_result['errors'].append(f"Invalid learning strategy: {strategy}")
                        validation_result['is_valid'] = False
                
                # Strategy-specific validation
                if strategy in self.strategy_configs:
                    await self._validate_strategy_config(task_config, strategy, validation_result)
            
            # Validate batch size
            if 'batch_size' in task_config:
                batch_size = task_config['batch_size']
                if not isinstance(batch_size, int) or batch_size <= 0:
                    validation_result['errors'].append("Batch size must be a positive integer")
                    validation_result['is_valid'] = False
                elif batch_size > 1024:
                    validation_result['warnings'].append("Large batch size may cause memory issues")
            
            # Validate memory limit
            if 'memory_limit_mb' in task_config:
                memory_limit = task_config['memory_limit_mb']
                if not isinstance(memory_limit, (int, float)) or memory_limit <= 0:
                    validation_result['errors'].append("Memory limit must be a positive number")
                    validation_result['is_valid'] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Failed to validate task config: {e}")
            return {
                'is_valid': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    async def estimate_task_resources(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resource requirements for a task configuration"""
        try:
            # Get base requirements
            base_memory_mb = self.config.memory_limit_mb
            base_cpu_cores = 1
            
            # Adjust based on learning strategy
            learning_strategy = task_config.get('learning_strategy')
            if isinstance(learning_strategy, str):
                learning_strategy = LearningStrategy(learning_strategy)
            
            if learning_strategy is not None:
                strategy_config = self.strategy_configs.get(learning_strategy, {})
                memory_factor = strategy_config.get('memory_factor', 1.0)
            else:
                memory_factor = 1.0
            
            # Adjust based on batch size
            batch_size = task_config.get('batch_size', self.config.default_batch_size)
            batch_factor = max(1.0, batch_size / self.config.default_batch_size)
            
            # Calculate final requirements
            estimated_memory = int(base_memory_mb * memory_factor * batch_factor)
            estimated_cpu = max(1, int(base_cpu_cores * batch_factor))
            
            # Estimate GPU requirements
            gpu_required = learning_strategy in [
                LearningStrategy.BATCH_UPDATE,
                LearningStrategy.CONTINUAL_LEARNING
            ]
            
            return {
                'memory_mb': estimated_memory,
                'cpu_cores': estimated_cpu,
                'gpu_required': gpu_required,
                'gpu_memory_mb': 2048 if gpu_required else 0,
                'estimated_duration_minutes': await self._estimate_duration_from_config(task_config)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate task resources: {e}")
            return {
                'memory_mb': self.config.memory_limit_mb,
                'cpu_cores': 1,
                'gpu_required': False,
                'gpu_memory_mb': 0,
                'estimated_duration_minutes': self.config.task_timeout_minutes
            }
    
    def _generate_task_id(self, model_id: str) -> str:
        """Generate unique task ID"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"task_{model_id}_{timestamp}_{unique_id}"
    
    async def _prepare_task_config(
        self,
        model_id: str,
        learning_strategy: LearningStrategy,
        task_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare complete task configuration with defaults"""
        try:
            # Start with provided config
            full_config = task_config.copy()
            
            # Add model and strategy
            full_config['model_id'] = model_id
            full_config['learning_strategy'] = learning_strategy
            
            # Apply strategy-specific defaults
            strategy_config = self.strategy_configs.get(learning_strategy, {})
            
            # Set default batch size if not provided
            if 'batch_size' not in full_config:
                full_config['batch_size'] = min(
                    self.config.default_batch_size,
                    strategy_config.get('max_batch_size', self.config.default_batch_size)
                )
            
            # Set memory limits
            if 'memory_limit_mb' not in full_config:
                full_config['memory_limit_mb'] = self.config.memory_limit_mb
            
            # Set timeout
            if 'timeout_minutes' not in full_config:
                full_config['timeout_minutes'] = self.config.task_timeout_minutes
            
            # Set retry configuration
            if 'max_retries' not in full_config:
                full_config['max_retries'] = self.config.max_retries
            
            # Add creation metadata
            full_config['created_at'] = datetime.utcnow().isoformat()
            full_config['config_version'] = '1.0'
            
            return full_config
            
        except Exception as e:
            logger.error(f"❌ Failed to prepare task config: {e}")
            return task_config
    
    async def _validate_task(self, task: LearningTask) -> bool:
        """Validate a complete learning task"""
        try:
            # Basic field validation
            if not task.task_id or not task.model_id:
                return False
            
            if not task.strategy or not task.parameters:
                return False
            
            # Validate configuration
            validation_result = await self.validate_task_config(task.parameters)
            
            return validation_result['is_valid']
            
        except Exception as e:
            logger.error(f"❌ Task validation error: {e}")
            return False
    
    async def _validate_strategy_config(
        self,
        task_config: Dict[str, Any],
        strategy: LearningStrategy,
        validation_result: Dict[str, Any]
    ) -> None:
        """Validate strategy-specific configuration"""
        try:
            strategy_config = self.strategy_configs[strategy]
            
            # Validate batch size for strategy
            if 'batch_size' in task_config:
                batch_size = task_config['batch_size']
                min_batch = strategy_config['min_batch_size']
                max_batch = strategy_config['max_batch_size']
                
                if batch_size < min_batch:
                    validation_result['errors'].append(
                        f"Batch size {batch_size} below minimum {min_batch} for {strategy.value}"
                    )
                    validation_result['is_valid'] = False
                elif batch_size > max_batch:
                    validation_result['warnings'].append(
                        f"Batch size {batch_size} above recommended maximum {max_batch} for {strategy.value}"
                    )
            
            # Strategy-specific validation
            if strategy == LearningStrategy.CONTINUAL_LEARNING:
                if 'memory_buffer_size' not in task_config:
                    validation_result['warnings'].append(
                        "Memory buffer size not specified for continual learning"
                    )
            
        except Exception as e:
            logger.error(f"❌ Strategy validation error: {e}")
    
    async def _estimate_resource_requirements(self, task: LearningTask) -> Dict[str, Any]:
        """Estimate resource requirements for a task"""
        return await self.estimate_task_resources(task.parameters)
    
    async def _estimate_task_duration(self, task: LearningTask) -> timedelta:
        """Estimate task duration based on configuration"""
        try:
            duration_minutes = await self._estimate_duration_from_config(task.parameters)
            return timedelta(minutes=duration_minutes)
            
        except Exception as e:
            logger.error(f"❌ Duration estimation error: {e}")
            return timedelta(minutes=self.config.task_timeout_minutes)
    
    async def _estimate_duration_from_config(self, task_config: Dict[str, Any]) -> float:
        """Estimate duration in minutes from task configuration"""
        try:
            # Base duration
            base_minutes = 30.0
            
            # Adjust for learning strategy
            learning_strategy = task_config.get('learning_strategy')
            if isinstance(learning_strategy, str):
                learning_strategy = LearningStrategy(learning_strategy)
            
            strategy_multipliers = {
                LearningStrategy.ONLINE_SGD: 0.5,
                LearningStrategy.INCREMENTAL: 1.0,
                LearningStrategy.BATCH_UPDATE: 2.0,
                LearningStrategy.CONTINUAL_LEARNING: 1.5,
                LearningStrategy.TRANSFER_LEARNING: 0.8,
                LearningStrategy.REINFORCEMENT: 3.0
            }
            
            if learning_strategy is not None:
                strategy_multiplier = strategy_multipliers.get(learning_strategy, 1.0)
            else:
                strategy_multiplier = 1.0
            
            # Adjust for batch size
            batch_size = task_config.get('batch_size', self.config.default_batch_size)
            batch_multiplier = max(0.5, batch_size / self.config.default_batch_size)
            
            # Calculate final duration
            estimated_minutes = base_minutes * strategy_multiplier * batch_multiplier
            
            # Cap at maximum timeout
            return min(estimated_minutes, self.config.task_timeout_minutes)
            
        except Exception as e:
            logger.error(f"❌ Duration calculation error: {e}")
            return 30.0
    
    async def get_creation_statistics(self) -> Dict[str, Any]:
        """Get task creation statistics"""
        return {
            'service': 'task_creator',
            'config': {
                'max_retries': self.config.max_retries,
                'default_batch_size': self.config.default_batch_size,
                'memory_limit_mb': self.config.memory_limit_mb,
                'auto_resource_estimation': self.config.auto_resource_estimation
            },
            'supported_strategies': [strategy.value for strategy in LearningStrategy],
            'strategy_configs': {
                strategy.value: config for strategy, config in self.strategy_configs.items()
            }
        }