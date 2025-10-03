"""
Incremental Learning Engine
==========================

Implements incremental learning algorithms and strategies.
Extracted from LearningTaskService god object to focus on learning algorithm concerns.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from ..protocols.learning_protocols import LearningStrategy, LearningTask

logger = logging.getLogger(__name__)


class MemoryStrategy(Enum):
    """Memory strategies for continual learning"""
    RANDOM_SAMPLING = "random_sampling"
    IMPORTANCE_SAMPLING = "importance_sampling"
    GRADIENT_BASED = "gradient_based"
    CLUSTERING_BASED = "clustering_based"


@dataclass
class IncrementalLearningConfig:
    """Configuration for incremental learning"""
    memory_buffer_size: int = 1000
    rehearsal_ratio: float = 0.2
    learning_rate: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 1e-4
    temperature: float = 3.0  # For knowledge distillation
    alpha: float = 0.5  # Balance between old and new knowledge
    plasticity_factor: float = 0.1  # Control plasticity vs stability


@dataclass
class LearningContext:
    """Learning context for incremental updates"""
    model_id: str
    previous_model_state: Optional[Dict[str, torch.Tensor]]
    memory_buffer: List[Dict[str, Any]]
    task_boundaries: List[int]
    learning_statistics: Dict[str, float]
    adaptation_history: List[Dict[str, Any]]


class IncrementalLearningEngine:
    """
    Implements various incremental learning strategies.
    
    Focuses solely on learning algorithm implementation:
    - Online SGD updates
    - Elastic Weight Consolidation (EWC)
    - Learning without Forgetting (LwF)
    - Experience Replay
    - Progressive Networks
    """
    
    def __init__(self, config: Optional[IncrementalLearningConfig] = None):
        self.config = config or IncrementalLearningConfig()
        
        # Learning contexts for different models
        self.learning_contexts: Dict[str, LearningContext] = {}
        
        # Algorithm implementations
        self.strategy_implementations = {
            LearningStrategy.INCREMENTAL: self._incremental_sgd,
            LearningStrategy.ONLINE_SGD: self._online_sgd,
            LearningStrategy.CONTINUAL_LEARNING: self._continual_learning,
            LearningStrategy.TRANSFER_LEARNING: self._transfer_learning,
            LearningStrategy.REINFORCEMENT: self._reinforcement_learning
        }
        
        logger.info("🧠 Incremental Learning Engine initialized")
    
    async def initialize_model_context(
        self,
        model_id: str,
        initial_model: torch.nn.Module,
        initial_data: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Initialize learning context for a model"""
        try:
            # Create learning context
            context = LearningContext(
                model_id=model_id,
                previous_model_state=initial_model.state_dict().copy() if initial_model else None,
                memory_buffer=initial_data[:self.config.memory_buffer_size] if initial_data else [],
                task_boundaries=[],
                learning_statistics={
                    'total_updates': 0,
                    'average_loss': 0.0,
                    'forgetting_measure': 0.0,
                    'forward_transfer': 0.0
                },
                adaptation_history=[]
            )
            
            self.learning_contexts[model_id] = context
            
            logger.info(f"🎯 Initialized learning context for model: {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize model context: {e}")
            return False
    
    async def perform_incremental_update(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        device: torch.device = torch.device('cpu')
    ) -> Dict[str, Any]:
        """Perform incremental learning update"""
        try:
            if task.model_id not in self.learning_contexts:
                await self.initialize_model_context(task.model_id, model, task.training_data)
            
            context = self.learning_contexts[task.model_id]
            
            # Select strategy implementation
            if task.strategy in self.strategy_implementations:
                result = await self.strategy_implementations[task.strategy](
                    task, model, context, device
                )
            else:
                logger.warning(f"⚠️ Strategy {task.strategy} not implemented, using incremental SGD")
                result = await self._incremental_sgd(task, model, context, device)
            
            # Update context
            await self._update_learning_context(context, result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Incremental update failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'final_loss': float('inf'),
                'metrics': {}
            }
    
    async def _incremental_sgd(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device
    ) -> Dict[str, Any]:
        """Incremental SGD with experience replay"""
        
        model.to(device)
        model.train()
        
        # Setup optimizer
        optimizer = optim.SGD(
            model.parameters(),
            lr=self.config.learning_rate,
            momentum=self.config.momentum,
            weight_decay=self.config.weight_decay
        )
        
        # Prepare data
        new_data = task.training_data
        replay_data = self._sample_replay_data(context, len(new_data))
        combined_data = new_data + replay_data
        
        # Training parameters
        epochs = task.parameters.get('epochs', 5)
        batch_size = task.parameters.get('batch_size', 32)
        
        epoch_losses = []
        training_metrics = {}
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            num_batches = 0
            
            # Create batches
            batches = self._create_batches(combined_data, batch_size)
            
            for batch in batches:
                optimizer.zero_grad()
                
                # Forward pass
                inputs, targets = self._prepare_batch(batch, device)
                outputs = model(inputs)
                
                # Calculate loss
                loss = self._calculate_loss(outputs, targets)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                num_batches += 1
            
            avg_epoch_loss = epoch_loss / num_batches if num_batches > 0 else 0.0
            epoch_losses.append(avg_epoch_loss)
            
            # Update progress (would be called by task manager)
            progress = ((epoch + 1) / epochs) * 100
            await asyncio.sleep(0.01)  # Yield control
        
        # Evaluate on validation data
        if task.validation_data:
            validation_metrics = await self._evaluate_model(model, task.validation_data, device)
            training_metrics.update(validation_metrics)
        
        # Update memory buffer
        await self._update_memory_buffer(context, new_data)
        
        return {
            'success': True,
            'strategy': 'incremental_sgd',
            'final_loss': epoch_losses[-1] if epoch_losses else 0.0,
            'epoch_losses': epoch_losses,
            'metrics': training_metrics,
            'model_state': model.state_dict(),
            'training_samples': len(new_data),
            'replay_samples': len(replay_data)
        }
    
    async def _online_sgd(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device
    ) -> Dict[str, Any]:
        """Online SGD - update on each sample"""
        
        model.to(device)
        model.train()
        
        # Setup optimizer with adaptive learning rate
        base_lr = self.config.learning_rate
        optimizer = optim.SGD(model.parameters(), lr=base_lr)
        
        sample_losses = []
        processed_samples = 0
        
        for sample in task.training_data:
            # Adaptive learning rate
            lr = base_lr / (1 + processed_samples * 0.001)
            for param_group in optimizer.param_groups:
                param_group['lr'] = lr
            
            optimizer.zero_grad()
            
            # Process single sample
            inputs, targets = self._prepare_batch([sample], device)
            outputs = model(inputs)
            loss = self._calculate_loss(outputs, targets)
            
            loss.backward()
            optimizer.step()
            
            sample_losses.append(loss.item())
            processed_samples += 1
            
            # Periodic yield
            if processed_samples % 10 == 0:
                await asyncio.sleep(0.001)
        
        # Validation
        validation_metrics = {}
        if task.validation_data:
            validation_metrics = await self._evaluate_model(model, task.validation_data, device)
        
        return {
            'success': True,
            'strategy': 'online_sgd',
            'final_loss': np.mean(sample_losses[-10:]) if sample_losses else 0.0,
            'sample_losses': sample_losses,
            'metrics': validation_metrics,
            'model_state': model.state_dict(),
            'processed_samples': processed_samples,
            'adaptive_lr_used': True
        }
    
    async def _continual_learning(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device
    ) -> Dict[str, Any]:
        """Continual learning with regularization"""
        
        model.to(device)
        model.train()
        
        # Calculate importance weights (EWC-style)
        importance_weights = await self._calculate_importance_weights(model, context, device)
        
        # Setup optimizer
        optimizer = optim.Adam(model.parameters(), lr=self.config.learning_rate)
        
        # Store previous parameters
        prev_params = {name: param.clone() for name, param in model.named_parameters()}
        
        epochs = task.parameters.get('epochs', 5)
        batch_size = task.parameters.get('batch_size', 32)
        regularization_strength = task.parameters.get('regularization_strength', 1000.0)
        
        epoch_losses = []
        regularization_losses = []
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            epoch_reg_loss = 0.0
            num_batches = 0
            
            # Create batches
            batches = self._create_batches(task.training_data, batch_size)
            
            for batch in batches:
                optimizer.zero_grad()
                
                # Forward pass
                inputs, targets = self._prepare_batch(batch, device)
                outputs = model(inputs)
                
                # Task loss
                task_loss = self._calculate_loss(outputs, targets)
                
                # Regularization loss (EWC)
                reg_loss = torch.tensor(0.0, device=device)
                for name, param in model.named_parameters():
                    if name in importance_weights and name in prev_params:
                        reg_loss += (importance_weights[name] * (param - prev_params[name])**2).sum()
                
                # Combined loss
                total_loss = task_loss + (regularization_strength * reg_loss)
                
                total_loss.backward()
                optimizer.step()
                
                epoch_loss += task_loss.item()
                epoch_reg_loss += reg_loss.item()
                num_batches += 1
            
            avg_epoch_loss = epoch_loss / num_batches if num_batches > 0 else 0.0
            avg_reg_loss = epoch_reg_loss / num_batches if num_batches > 0 else 0.0
            
            epoch_losses.append(avg_epoch_loss)
            regularization_losses.append(avg_reg_loss)
            
            await asyncio.sleep(0.01)
        
        # Validation
        validation_metrics = {}
        if task.validation_data:
            validation_metrics = await self._evaluate_model(model, task.validation_data, device)
        
        # Update memory buffer with importance sampling
        await self._update_memory_buffer_importance(context, task.training_data, importance_weights)
        
        return {
            'success': True,
            'strategy': 'continual_learning',
            'final_loss': epoch_losses[-1] if epoch_losses else 0.0,
            'epoch_losses': epoch_losses,
            'regularization_losses': regularization_losses,
            'metrics': validation_metrics,
            'model_state': model.state_dict(),
            'importance_weights_computed': len(importance_weights),
            'regularization_strength': regularization_strength
        }
    
    async def _transfer_learning(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device
    ) -> Dict[str, Any]:
        """Transfer learning with fine-tuning"""
        
        model.to(device)
        
        # Freeze early layers (transfer learning)
        freeze_ratio = task.parameters.get('freeze_ratio', 0.5)
        total_params = len(list(model.parameters()))
        freeze_count = int(total_params * freeze_ratio)
        
        for i, param in enumerate(model.parameters()):
            param.requires_grad = i >= freeze_count
        
        model.train()
        
        # Use lower learning rate for fine-tuning
        fine_tune_lr = self.config.learning_rate * 0.1
        optimizer = optim.Adam(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=fine_tune_lr
        )
        
        epochs = task.parameters.get('epochs', 3)  # Fewer epochs for transfer learning
        batch_size = task.parameters.get('batch_size', 32)
        
        epoch_losses = []
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            num_batches = 0
            
            batches = self._create_batches(task.training_data, batch_size)
            
            for batch in batches:
                optimizer.zero_grad()
                
                inputs, targets = self._prepare_batch(batch, device)
                outputs = model(inputs)
                loss = self._calculate_loss(outputs, targets)
                
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                num_batches += 1
            
            avg_epoch_loss = epoch_loss / num_batches if num_batches > 0 else 0.0
            epoch_losses.append(avg_epoch_loss)
            
            await asyncio.sleep(0.01)
        
        # Unfreeze all parameters for future updates
        for param in model.parameters():
            param.requires_grad = True
        
        # Validation
        validation_metrics = {}
        if task.validation_data:
            validation_metrics = await self._evaluate_model(model, task.validation_data, device)
        
        return {
            'success': True,
            'strategy': 'transfer_learning',
            'final_loss': epoch_losses[-1] if epoch_losses else 0.0,
            'epoch_losses': epoch_losses,
            'metrics': validation_metrics,
            'model_state': model.state_dict(),
            'frozen_parameters': freeze_count,
            'fine_tune_lr': fine_tune_lr
        }
    
    async def _reinforcement_learning(
        self,
        task: LearningTask,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device
    ) -> Dict[str, Any]:
        """Reinforcement learning from feedback"""
        
        # Simplified RL update based on feedback
        model.to(device)
        model.train()
        
        optimizer = optim.Adam(model.parameters(), lr=self.config.learning_rate)
        
        # Process feedback data (assuming reward-based feedback)
        feedback_data = task.training_data
        episode_rewards = []
        
        for episode_data in feedback_data:
            optimizer.zero_grad()
            
            # Extract state, action, reward from feedback
            state = episode_data.get('state', episode_data.get('input'))
            action = episode_data.get('action', episode_data.get('output'))
            reward = episode_data.get('reward', episode_data.get('feedback', 0.0))
            
            # Simple policy gradient update
            if isinstance(state, (list, np.ndarray)):
                state_tensor = torch.tensor(state, dtype=torch.float32, device=device)
            else:
                state_tensor = torch.tensor([state], dtype=torch.float32, device=device)
            
            # Forward pass
            action_probs = model(state_tensor)
            
            # Calculate policy loss (simplified)
            if isinstance(action, (int, float)):
                action_tensor = torch.tensor([action], dtype=torch.long, device=device)
                log_prob = torch.log(action_probs + 1e-8).gather(1, action_tensor.unsqueeze(0))
                loss = -log_prob * reward
            else:
                # Continuous action space (simplified)
                loss = torch.mean((action_probs - torch.tensor(action, device=device))**2) * (-reward)
            
            loss.backward()
            optimizer.step()
            
            episode_rewards.append(reward)
        
        # Validation (if applicable)
        validation_metrics = {}
        if task.validation_data:
            validation_metrics = await self._evaluate_model(model, task.validation_data, device)
        
        return {
            'success': True,
            'strategy': 'reinforcement_learning',
            'final_loss': -np.mean(episode_rewards) if episode_rewards else 0.0,
            'episode_rewards': episode_rewards,
            'metrics': validation_metrics,
            'model_state': model.state_dict(),
            'total_episodes': len(feedback_data),
            'average_reward': np.mean(episode_rewards) if episode_rewards else 0.0
        }
    
    async def _calculate_importance_weights(
        self,
        model: torch.nn.Module,
        context: LearningContext,
        device: torch.device
    ) -> Dict[str, torch.Tensor]:
        """Calculate parameter importance weights (Fisher Information)"""
        
        importance_weights = {}
        
        if not context.memory_buffer:
            # Return uniform importance if no previous data
            for name, param in model.named_parameters():
                importance_weights[name] = torch.ones_like(param, device=device)
            return importance_weights
        
        model.eval()
        
        # Sample from memory buffer
        sample_size = min(100, len(context.memory_buffer))
        samples = np.random.choice(context.memory_buffer, sample_size, replace=False)
        
        # Calculate Fisher Information approximation
        for name, param in model.named_parameters():
            importance_weights[name] = torch.zeros_like(param, device=device)
        
        for sample in samples:
            model.zero_grad()
            
            inputs, targets = self._prepare_batch([sample], device)
            outputs = model(inputs)
            loss = self._calculate_loss(outputs, targets)
            
            loss.backward()
            
            for name, param in model.named_parameters():
                if param.grad is not None:
                    importance_weights[name] += param.grad.data ** 2
        
        # Normalize by sample size
        for name in importance_weights:
            importance_weights[name] /= sample_size
        
        model.train()
        return importance_weights
    
    def _sample_replay_data(
        self,
        context: LearningContext,
        target_size: int
    ) -> List[Dict[str, Any]]:
        """Sample replay data from memory buffer"""
        
        if not context.memory_buffer:
            return []
        
        replay_size = int(target_size * self.config.rehearsal_ratio)
        replay_size = min(replay_size, len(context.memory_buffer))
        
        if replay_size == 0:
            return []
        
        # Random sampling (can be enhanced with importance sampling)
        indices = np.random.choice(len(context.memory_buffer), replay_size, replace=False)
        return [context.memory_buffer[i] for i in indices]
    
    def _create_batches(
        self,
        data: List[Dict[str, Any]],
        batch_size: int
    ) -> List[List[Dict[str, Any]]]:
        """Create batches from data"""
        
        batches = []
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batches.append(batch)
        
        return batches
    
    def _prepare_batch(
        self,
        batch: List[Dict[str, Any]],
        device: torch.device
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Prepare batch for training"""
        
        # Extract inputs and targets
        inputs = []
        targets = []
        
        for item in batch:
            # Handle different data formats
            if 'input' in item and 'target' in item:
                inputs.append(item['input'])
                targets.append(item['target'])
            elif 'x' in item and 'y' in item:
                inputs.append(item['x'])
                targets.append(item['y'])
            else:
                # Assume first key is input, second is target
                keys = list(item.keys())
                if len(keys) >= 2:
                    inputs.append(item[keys[0]])
                    targets.append(item[keys[1]])
        
        # Convert to tensors
        if inputs and isinstance(inputs[0], (list, np.ndarray)):
            input_tensor = torch.tensor(inputs, dtype=torch.float32, device=device)
        else:
            input_tensor = torch.tensor([[x] for x in inputs], dtype=torch.float32, device=device)
        
        if targets and isinstance(targets[0], (list, np.ndarray)):
            target_tensor = torch.tensor(targets, dtype=torch.float32, device=device)
        else:
            target_tensor = torch.tensor(targets, dtype=torch.long, device=device)
        
        return input_tensor, target_tensor
    
    def _calculate_loss(
        self,
        outputs: torch.Tensor,
        targets: torch.Tensor
    ) -> torch.Tensor:
        """Calculate loss based on task type"""
        
        if targets.dtype == torch.long:
            # Classification
            return nn.CrossEntropyLoss()(outputs, targets)
        else:
            # Regression
            return nn.MSELoss()(outputs, targets)
    
    async def _evaluate_model(
        self,
        model: torch.nn.Module,
        validation_data: List[Dict[str, Any]],
        device: torch.device
    ) -> Dict[str, float]:
        """Evaluate model on validation data"""
        
        model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for item in validation_data:
                inputs, targets = self._prepare_batch([item], device)
                outputs = model(inputs)
                
                loss = self._calculate_loss(outputs, targets)
                total_loss += loss.item()
                
                # Calculate accuracy for classification
                if targets.dtype == torch.long:
                    _, predicted = torch.max(outputs.data, 1)
                    total += targets.size(0)
                    correct += (predicted == targets).sum().item()
        
        metrics = {
            'validation_loss': total_loss / len(validation_data),
        }
        
        if total > 0:
            metrics['accuracy'] = 100.0 * correct / total
        
        model.train()
        return metrics
    
    async def _update_memory_buffer(
        self,
        context: LearningContext,
        new_data: List[Dict[str, Any]]
    ) -> None:
        """Update memory buffer with new data"""
        
        # Add new data to buffer
        context.memory_buffer.extend(new_data)
        
        # Maintain buffer size limit
        if len(context.memory_buffer) > self.config.memory_buffer_size:
            # Remove oldest data (FIFO)
            excess = len(context.memory_buffer) - self.config.memory_buffer_size
            context.memory_buffer = context.memory_buffer[excess:]
    
    async def _update_memory_buffer_importance(
        self,
        context: LearningContext,
        new_data: List[Dict[str, Any]],
        importance_weights: Dict[str, torch.Tensor]
    ) -> None:
        """Update memory buffer with importance-based sampling"""
        
        # For now, use simple update (can be enhanced with importance scores)
        await self._update_memory_buffer(context, new_data)
        
        # Store importance information in context
        context.learning_statistics['importance_weights_norm'] = sum(
            torch.norm(w).item() for w in importance_weights.values()
        )
    
    async def _update_learning_context(
        self,
        context: LearningContext,
        result: Dict[str, Any]
    ) -> None:
        """Update learning context with results"""
        
        context.learning_statistics['total_updates'] += 1
        
        if 'final_loss' in result:
            # Update running average of loss
            current_avg = context.learning_statistics.get('average_loss', 0.0)
            total_updates = context.learning_statistics['total_updates']
            new_avg = (current_avg * (total_updates - 1) + result['final_loss']) / total_updates
            context.learning_statistics['average_loss'] = new_avg
        
        # Store adaptation history
        adaptation_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'strategy': result.get('strategy', 'unknown'),
            'final_loss': result.get('final_loss', 0.0),
            'success': result.get('success', False)
        }
        
        context.adaptation_history.append(adaptation_record)
        
        # Keep only recent history
        if len(context.adaptation_history) > 100:
            context.adaptation_history = context.adaptation_history[-100:]
    
    def get_learning_context(self, model_id: str) -> Optional[LearningContext]:
        """Get learning context for a model"""
        return self.learning_contexts.get(model_id)
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        
        total_contexts = len(self.learning_contexts)
        total_updates = sum(
            ctx.learning_statistics.get('total_updates', 0)
            for ctx in self.learning_contexts.values()
        )
        
        return {
            'service': 'incremental_learning_engine',
            'status': 'healthy',
            'active_contexts': total_contexts,
            'total_updates_performed': total_updates,
            'strategies_available': len(self.strategy_implementations),
            'memory_buffer_total_size': sum(
                len(ctx.memory_buffer) for ctx in self.learning_contexts.values()
            )
        }