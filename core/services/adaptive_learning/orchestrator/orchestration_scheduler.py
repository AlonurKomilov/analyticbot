"""
Orchestration Scheduler
======================

Handles scheduling and background tasks for adaptive learning orchestration.
Manages periodic checks, monitoring loops, and automated workflow triggers.
"""

import logging
import asyncio
from typing import Dict, Any, Set, List
from datetime import datetime, timedelta

from .workflow_models import OrchestrationStrategy, OrchestrationConfig
from .workflow_manager import WorkflowManager
from ..protocols.monitoring_protocols import MonitoringServiceProtocol

logger = logging.getLogger(__name__)


class OrchestrationScheduler:
    """
    Manages scheduling and background tasks for orchestration.
    
    Handles periodic drift checks, feedback collection triggers,
    and automated workflow scheduling based on configured strategies.
    """
    
    def __init__(
        self,
        workflow_manager: WorkflowManager,
        monitoring_service: MonitoringServiceProtocol,
        config: OrchestrationConfig
    ):
        self.workflow_manager = workflow_manager
        self.monitoring_service = monitoring_service
        self.config = config
        
        # Scheduling state
        self.is_running = False
        self.monitored_models: Set[str] = set()
        self.scheduled_updates: Dict[str, Dict[str, Any]] = {}
        self.last_drift_check: Dict[str, datetime] = {}
        self.last_feedback_collection: Dict[str, datetime] = {}
        
        # Background tasks
        self.scheduler_tasks: List[asyncio.Task] = []
        
        logger.info("📅 Orchestration Scheduler initialized")
    
    async def start_scheduling(self) -> bool:
        """Start scheduling and background tasks"""
        try:
            if self.is_running:
                logger.warning("⚠️ Scheduler already running")
                return True
            
            # Start background loops
            monitor_task = asyncio.create_task(self._monitoring_loop())
            self.scheduler_tasks.append(monitor_task)
            
            scheduler_task = asyncio.create_task(self._scheduling_loop())
            self.scheduler_tasks.append(scheduler_task)
            
            workflow_task = asyncio.create_task(self._workflow_cleanup_loop())
            self.scheduler_tasks.append(workflow_task)
            
            self.is_running = True
            logger.info("✅ Orchestration scheduling started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduling: {e}")
            return False
    
    async def stop_scheduling(self) -> bool:
        """Stop scheduling and background tasks"""
        try:
            # Cancel all scheduler tasks
            for task in self.scheduler_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self.scheduler_tasks.clear()
            self.is_running = False
            
            logger.info("⏹️ Orchestration scheduling stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduling: {e}")
            return False
    
    async def add_model_scheduling(
        self,
        model_id: str,
        strategy: OrchestrationStrategy = OrchestrationStrategy.HYBRID,
        auto_learning: bool = True
    ) -> bool:
        """Add a model to scheduled orchestration"""
        try:
            if model_id in self.monitored_models:
                logger.warning(f"⚠️ Model {model_id} already scheduled")
                return True
            
            # Add to scheduled updates
            self.scheduled_updates[model_id] = {
                'strategy': strategy,
                'auto_learning': auto_learning,
                'next_drift_check': datetime.utcnow() + timedelta(hours=self.config.drift_check_frequency_hours),
                'next_feedback_check': datetime.utcnow() + timedelta(minutes=self.config.monitoring_interval_minutes)
            }
            
            # Initialize tracking
            self.last_drift_check[model_id] = datetime.utcnow()
            self.last_feedback_collection[model_id] = datetime.utcnow()
            
            self.monitored_models.add(model_id)
            
            logger.info(f"📅 Added model {model_id} to scheduling (strategy: {strategy.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add model scheduling: {e}")
            return False
    
    async def remove_model_scheduling(self, model_id: str) -> bool:
        """Remove a model from scheduled orchestration"""
        try:
            if model_id not in self.monitored_models:
                logger.warning(f"⚠️ Model {model_id} not scheduled")
                return True
            
            # Clean up scheduling data
            self.monitored_models.discard(model_id)
            if model_id in self.scheduled_updates:
                del self.scheduled_updates[model_id]
            if model_id in self.last_drift_check:
                del self.last_drift_check[model_id]
            if model_id in self.last_feedback_collection:
                del self.last_feedback_collection[model_id]
            
            logger.info(f"🗑️ Removed model {model_id} from scheduling")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove model scheduling: {e}")
            return False
    
    async def trigger_scheduled_check(self, model_id: str, check_type: str) -> bool:
        """Trigger a scheduled check for a model"""
        try:
            if model_id not in self.monitored_models:
                logger.error(f"❌ Model {model_id} not under scheduling")
                return False
            
            model_config = self.scheduled_updates[model_id]
            
            if check_type == "drift":
                return await self._check_drift_trigger(model_id, model_config)
            elif check_type == "feedback":
                return await self._check_feedback_trigger(model_id, model_config)
            else:
                logger.error(f"❌ Unknown check type: {check_type}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to trigger scheduled check: {e}")
            return False
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.monitoring_interval_minutes * 60)
                
                # Check all monitored models
                for model_id in list(self.monitored_models):
                    try:
                        await self._check_model_status(model_id)
                    except Exception as e:
                        logger.error(f"❌ Error checking model {model_id}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
    
    async def _scheduling_loop(self) -> None:
        """Background scheduling loop"""
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.utcnow()
                
                # Check scheduled updates
                for model_id, schedule_config in list(self.scheduled_updates.items()):
                    try:
                        # Check if drift check is due
                        if current_time >= schedule_config.get('next_drift_check', current_time):
                            await self._check_drift_trigger(model_id, schedule_config)
                        
                        # Check if feedback check is due
                        if current_time >= schedule_config.get('next_feedback_check', current_time):
                            await self._check_feedback_trigger(model_id, schedule_config)
                    
                    except Exception as e:
                        logger.error(f"❌ Error in scheduled check for {model_id}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in scheduling loop: {e}")
    
    async def _workflow_cleanup_loop(self) -> None:
        """Background workflow cleanup loop"""
        while self.is_running:
            try:
                # Clean up old workflows every hour
                await asyncio.sleep(3600)
                
                await self.workflow_manager.cleanup_old_workflows()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in workflow cleanup loop: {e}")
    
    async def _check_model_status(self, model_id: str) -> None:
        """Check status of a monitored model"""
        try:
            # Get model performance summary
            model_summary = await self.monitoring_service.get_performance_summary(model_id)
            
            if 'error' in model_summary:
                logger.warning(f"⚠️ Could not get performance summary for {model_id}")
                return
            
            # Check for performance issues
            health_status = model_summary.get('health_status', 'unknown')
            
            if health_status in ['critical', 'warning']:
                logger.info(f"🚨 Performance issues detected for model {model_id}: {health_status}")
                
                # Trigger reactive workflow if not already active
                active_workflows = await self.workflow_manager.get_active_workflows_for_model(model_id)
                if not active_workflows:
                    workflow_id = await self.workflow_manager.create_workflow(
                        model_id=model_id,
                        strategy=OrchestrationStrategy.REACTIVE,
                        triggered_by="performance_monitoring"
                    )
                    
                    if workflow_id:
                        logger.info(f"🎯 Created reactive workflow {workflow_id} for model {model_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to check model status for {model_id}: {e}")
    
    async def _check_drift_trigger(self, model_id: str, schedule_config: Dict[str, Any]) -> bool:
        """Check if drift-based workflow should be triggered"""
        try:
            strategy = schedule_config['strategy']
            
            # Skip if not a drift-checking strategy
            if strategy not in [OrchestrationStrategy.REACTIVE, OrchestrationStrategy.HYBRID]:
                return False
            
            # Check if enough time has passed since last drift check
            last_check = self.last_drift_check.get(model_id, datetime.min)
            check_interval = timedelta(hours=self.config.drift_check_frequency_hours)
            
            if datetime.utcnow() - last_check < check_interval:
                return False
            
            # Check if workflow is already active
            active_workflows = await self.workflow_manager.get_active_workflows_for_model(model_id)
            if active_workflows:
                return False
            
            # Trigger drift-based workflow
            workflow_id = await self.workflow_manager.create_workflow(
                model_id=model_id,
                strategy=strategy,
                triggered_by="scheduled_drift_check"
            )
            
            if workflow_id:
                # Update last check time and next check
                self.last_drift_check[model_id] = datetime.utcnow()
                schedule_config['next_drift_check'] = datetime.utcnow() + check_interval
                
                logger.info(f"📅 Triggered scheduled drift check workflow {workflow_id} for model {model_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to check drift trigger for {model_id}: {e}")
            return False
    
    async def _check_feedback_trigger(self, model_id: str, schedule_config: Dict[str, Any]) -> bool:
        """Check if feedback-based workflow should be triggered"""
        try:
            strategy = schedule_config['strategy']
            
            # Skip if not a feedback-checking strategy
            if strategy not in [OrchestrationStrategy.CONTINUOUS, OrchestrationStrategy.HYBRID]:
                return False
            
            # Check if enough time has passed since last feedback check
            last_check = self.last_feedback_collection.get(model_id, datetime.min)
            check_interval = timedelta(minutes=self.config.monitoring_interval_minutes)
            
            if datetime.utcnow() - last_check < check_interval:
                return False
            
            # Check for sufficient feedback (this would need to be implemented)
            # For now, we'll use a simple time-based trigger
            
            # Check if workflow is already active
            active_workflows = await self.workflow_manager.get_active_workflows_for_model(model_id)
            if active_workflows:
                return False
            
            # Update next check time
            self.last_feedback_collection[model_id] = datetime.utcnow()
            schedule_config['next_feedback_check'] = datetime.utcnow() + check_interval
            
            # We'll skip creating workflows for now unless there's actual feedback
            logger.debug(f"📅 Checked feedback trigger for model {model_id} - no action needed")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to check feedback trigger for {model_id}: {e}")
            return False
    
    async def get_scheduling_status(self) -> Dict[str, Any]:
        """Get scheduling status"""
        try:
            return {
                'service': 'orchestration_scheduler',
                'is_running': self.is_running,
                'monitored_models': len(self.monitored_models),
                'active_tasks': len([t for t in self.scheduler_tasks if not t.done()]),
                'scheduled_updates': {
                    model_id: {
                        'strategy': config['strategy'].value,
                        'auto_learning': config['auto_learning'],
                        'next_drift_check': config.get('next_drift_check', '').isoformat() if config.get('next_drift_check') else None,
                        'next_feedback_check': config.get('next_feedback_check', '').isoformat() if config.get('next_feedback_check') else None
                    }
                    for model_id, config in self.scheduled_updates.items()
                },
                'config': {
                    'monitoring_interval_minutes': self.config.monitoring_interval_minutes,
                    'drift_check_frequency_hours': self.config.drift_check_frequency_hours,
                    'auto_learning_enabled': self.config.auto_learning_enabled
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get scheduling status: {e}")
            return {'error': str(e)}