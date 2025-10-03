"""
Rollback Manager
===============

Manages rollback operations with automatic triggers and manual controls.
Extracted from ModelUpdateService god object to focus on rollback concerns.
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from .deployment_plan_manager import DeploymentPlan
from ..protocols.learning_protocols import (
    DeploymentStrategy,
    DeploymentStatus,
    ModelMetadata
)
from ..protocols.monitoring_protocols import MonitoringServiceProtocol

logger = logging.getLogger(__name__)


class RollbackTrigger(Enum):
    """Rollback trigger types"""
    MANUAL = "manual"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ERROR_RATE_SPIKE = "error_rate_spike"
    HEALTH_CHECK_FAILURE = "health_check_failure"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTION = "resource_exhaustion"


class RollbackStrategy(Enum):
    """Rollback strategy types"""
    INSTANT_SWITCH = "instant_switch"
    TRAFFIC_REDUCTION = "traffic_reduction"
    REVERSE_ROLLING = "reverse_rolling"
    VERSION_REVERT = "version_revert"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class RollbackRule:
    """Rollback rule configuration"""
    rule_id: str
    trigger_type: RollbackTrigger
    condition: str
    threshold: float
    strategy: RollbackStrategy
    auto_execute: bool
    priority: int
    description: str


@dataclass
class RollbackExecution:
    """Rollback execution record"""
    rollback_id: str
    model_id: str
    deployment_id: Optional[str]
    trigger: RollbackTrigger
    strategy: RollbackStrategy
    
    # Execution details
    triggered_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration: Optional[timedelta]
    
    # Status
    status: str  # triggered, executing, completed, failed
    success: bool
    error_message: Optional[str]
    
    # Versions
    from_version: str
    to_version: str
    
    # Metadata
    trigger_details: Dict[str, Any]
    execution_log: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class RollbackManager:
    """
    Manages rollback operations with automatic monitoring and manual controls.
    
    Provides comprehensive rollback capabilities including:
    - Automatic rollback triggers based on performance metrics
    - Manual rollback controls
    - Rollback strategy execution
    - Rollback monitoring and validation
    """
    
    def __init__(self, monitoring_service: MonitoringServiceProtocol):
        self.monitoring_service = monitoring_service
        
        # Rollback tracking
        self.active_rollbacks: Dict[str, RollbackExecution] = {}
        self.rollback_history: List[RollbackExecution] = []
        
        # Rules and configuration
        self.rollback_rules: Dict[str, RollbackRule] = {}
        self.monitored_models: Set[str] = set()
        
        # Version tracking
        self.model_versions: Dict[str, List[str]] = {}
        self.version_metadata: Dict[str, Dict[str, ModelMetadata]] = {}
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_tasks: List[asyncio.Task] = []
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info("🔄 Rollback Manager initialized")
    
    async def start_monitoring(self) -> bool:
        """Start automatic rollback monitoring"""
        try:
            if self.monitoring_active:
                logger.warning("⚠️ Rollback monitoring already active")
                return True
            
            # Start monitoring task
            monitor_task = asyncio.create_task(self._monitoring_loop())
            self.monitoring_tasks.append(monitor_task)
            
            self.monitoring_active = True
            logger.info("👁️ Rollback monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start rollback monitoring: {e}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop automatic rollback monitoring"""
        try:
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            self.monitoring_tasks.clear()
            self.monitoring_active = False
            
            logger.info("⏹️ Rollback monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop rollback monitoring: {e}")
            return False
    
    async def add_model_monitoring(
        self,
        model_id: str,
        current_version: str,
        version_history: List[str]
    ) -> bool:
        """Add model to rollback monitoring"""
        try:
            self.monitored_models.add(model_id)
            self.model_versions[model_id] = version_history
            
            logger.info(f"📊 Added model {model_id} to rollback monitoring (current: {current_version})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add model monitoring: {e}")
            return False
    
    async def remove_model_monitoring(self, model_id: str) -> bool:
        """Remove model from rollback monitoring"""
        try:
            self.monitored_models.discard(model_id)
            if model_id in self.model_versions:
                del self.model_versions[model_id]
            if model_id in self.version_metadata:
                del self.version_metadata[model_id]
            
            logger.info(f"🗑️ Removed model {model_id} from rollback monitoring")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove model monitoring: {e}")
            return False
    
    async def trigger_manual_rollback(
        self,
        model_id: str,
        target_version: str,
        reason: str,
        strategy: Optional[RollbackStrategy] = None
    ) -> Optional[str]:
        """Trigger manual rollback"""
        try:
            if model_id not in self.monitored_models:
                logger.error(f"❌ Model {model_id} not monitored")
                return None
            
            if model_id not in self.model_versions or target_version not in self.model_versions[model_id]:
                logger.error(f"❌ Target version {target_version} not available for {model_id}")
                return None
            
            # Get current version
            current_version = self.model_versions[model_id][0] if self.model_versions[model_id] else "unknown"
            
            # Select strategy
            rollback_strategy = strategy or RollbackStrategy.VERSION_REVERT
            
            # Create rollback execution
            rollback_id = await self._create_rollback_execution(
                model_id=model_id,
                trigger=RollbackTrigger.MANUAL,
                strategy=rollback_strategy,
                from_version=current_version,
                to_version=target_version,
                trigger_details={'reason': reason, 'manual_trigger': True}
            )
            
            if rollback_id:
                # Execute rollback
                await self._execute_rollback(rollback_id)
                logger.info(f"🔄 Manual rollback triggered: {rollback_id}")
                return rollback_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Manual rollback failed: {e}")
            return None
    
    async def check_rollback_conditions(self, model_id: str) -> List[RollbackRule]:
        """Check if rollback conditions are met"""
        try:
            if model_id not in self.monitored_models:
                return []
            
            triggered_rules = []
            
            # Get current metrics
            try:
                metrics = await self.monitoring_service.get_current_metrics(model_id)
                if not metrics:
                    return []
            except Exception:
                return []
            
            # Check each rule
            for rule in self.rollback_rules.values():
                if await self._evaluate_rollback_rule(rule, model_id, metrics):
                    triggered_rules.append(rule)
            
            return triggered_rules
            
        except Exception as e:
            logger.error(f"❌ Failed to check rollback conditions: {e}")
            return []
    
    async def get_rollback_status(self, rollback_id: str) -> Optional[RollbackExecution]:
        """Get rollback execution status"""
        
        # Check active rollbacks
        if rollback_id in self.active_rollbacks:
            return self.active_rollbacks[rollback_id]
        
        # Check history
        for rollback in self.rollback_history:
            if rollback.rollback_id == rollback_id:
                return rollback
        
        return None
    
    async def list_active_rollbacks(self) -> List[RollbackExecution]:
        """List active rollback executions"""
        return list(self.active_rollbacks.values())
    
    async def get_rollback_history(
        self,
        model_id: Optional[str] = None,
        limit: int = 20
    ) -> List[RollbackExecution]:
        """Get rollback history"""
        
        history = self.rollback_history.copy()
        
        if model_id:
            history = [r for r in history if r.model_id == model_id]
        
        return sorted(history, key=lambda r: r.triggered_at, reverse=True)[:limit]
    
    async def add_rollback_rule(self, rule: RollbackRule) -> bool:
        """Add rollback rule"""
        try:
            self.rollback_rules[rule.rule_id] = rule
            logger.info(f"📋 Added rollback rule: {rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add rollback rule: {e}")
            return False
    
    async def remove_rollback_rule(self, rule_id: str) -> bool:
        """Remove rollback rule"""
        try:
            if rule_id in self.rollback_rules:
                del self.rollback_rules[rule_id]
                logger.info(f"🗑️ Removed rollback rule: {rule_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to remove rollback rule: {e}")
            return False
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for model_id in list(self.monitored_models):
                    try:
                        # Check rollback conditions
                        triggered_rules = await self.check_rollback_conditions(model_id)
                        
                        for rule in triggered_rules:
                            if rule.auto_execute:
                                await self._auto_trigger_rollback(model_id, rule)
                            else:
                                logger.warning(f"⚠️ Rollback condition met but auto-execute disabled: {rule.rule_id}")
                    
                    except Exception as e:
                        logger.error(f"❌ Monitoring failed for {model_id}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in rollback monitoring loop: {e}")
    
    async def _auto_trigger_rollback(self, model_id: str, rule: RollbackRule) -> None:
        """Auto-trigger rollback based on rule"""
        try:
            # Get target version (previous version)
            if model_id not in self.model_versions or len(self.model_versions[model_id]) < 2:
                logger.error(f"❌ No previous version available for {model_id}")
                return
            
            current_version = self.model_versions[model_id][0]
            target_version = self.model_versions[model_id][1]
            
            # Create rollback execution
            rollback_id = await self._create_rollback_execution(
                model_id=model_id,
                trigger=rule.trigger_type,
                strategy=rule.strategy,
                from_version=current_version,
                to_version=target_version,
                trigger_details={
                    'rule_id': rule.rule_id,
                    'auto_triggered': True,
                    'condition': rule.condition,
                    'threshold': rule.threshold
                }
            )
            
            if rollback_id:
                await self._execute_rollback(rollback_id)
                logger.warning(f"🚨 Auto-rollback triggered: {rollback_id} (rule: {rule.rule_id})")
            
        except Exception as e:
            logger.error(f"❌ Auto-rollback failed: {e}")
    
    async def _create_rollback_execution(
        self,
        model_id: str,
        trigger: RollbackTrigger,
        strategy: RollbackStrategy,
        from_version: str,
        to_version: str,
        trigger_details: Dict[str, Any],
        deployment_id: Optional[str] = None
    ) -> Optional[str]:
        """Create rollback execution record"""
        try:
            rollback_id = f"rollback_{model_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            rollback = RollbackExecution(
                rollback_id=rollback_id,
                model_id=model_id,
                deployment_id=deployment_id,
                trigger=trigger,
                strategy=strategy,
                triggered_at=datetime.utcnow(),
                started_at=None,
                completed_at=None,
                duration=None,
                status="triggered",
                success=False,
                error_message=None,
                from_version=from_version,
                to_version=to_version,
                trigger_details=trigger_details,
                execution_log=[],
                metadata={
                    'rollback_manager_version': '1.0.0',
                    'creation_context': {
                        'created_at': datetime.utcnow().isoformat(),
                        'trigger_source': trigger.value
                    }
                }
            )
            
            self.active_rollbacks[rollback_id] = rollback
            return rollback_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create rollback execution: {e}")
            return None
    
    async def _execute_rollback(self, rollback_id: str) -> bool:
        """Execute rollback"""
        try:
            if rollback_id not in self.active_rollbacks:
                logger.error(f"❌ Rollback {rollback_id} not found")
                return False
            
            rollback = self.active_rollbacks[rollback_id]
            rollback.status = "executing"
            rollback.started_at = datetime.utcnow()
            
            # Log start
            rollback.execution_log.append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'execution_started',
                'details': f'Starting {rollback.strategy.value} rollback'
            })
            
            # Execute strategy
            success = await self._execute_rollback_strategy(rollback)
            
            # Update status
            rollback.completed_at = datetime.utcnow()
            rollback.duration = rollback.completed_at - rollback.started_at
            rollback.success = success
            rollback.status = "completed" if success else "failed"
            
            # Log completion
            rollback.execution_log.append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'execution_completed',
                'success': success,
                'duration': rollback.duration.total_seconds() if rollback.duration else 0
            })
            
            # Move to history
            del self.active_rollbacks[rollback_id]
            self.rollback_history.append(rollback)
            
            # Update version tracking if successful
            if success and rollback.model_id in self.model_versions:
                versions = self.model_versions[rollback.model_id]
                if rollback.to_version in versions:
                    # Move target version to front
                    versions.remove(rollback.to_version)
                    versions.insert(0, rollback.to_version)
            
            logger.info(f"{'✅' if success else '❌'} Rollback execution completed: {rollback_id}")
            return success
            
        except Exception as e:
            logger.error(f"❌ Rollback execution failed: {e}")
            if rollback_id in self.active_rollbacks:
                rollback = self.active_rollbacks[rollback_id]
                rollback.status = "failed"
                rollback.error_message = str(e)
                rollback.completed_at = datetime.utcnow()
                del self.active_rollbacks[rollback_id]
                self.rollback_history.append(rollback)
            return False
    
    async def _execute_rollback_strategy(self, rollback: RollbackExecution) -> bool:
        """Execute specific rollback strategy"""
        try:
            strategy = rollback.strategy
            
            if strategy == RollbackStrategy.INSTANT_SWITCH:
                return await self._instant_switch_rollback(rollback)
            elif strategy == RollbackStrategy.TRAFFIC_REDUCTION:
                return await self._traffic_reduction_rollback(rollback)
            elif strategy == RollbackStrategy.REVERSE_ROLLING:
                return await self._reverse_rolling_rollback(rollback)
            elif strategy == RollbackStrategy.VERSION_REVERT:
                return await self._version_revert_rollback(rollback)
            elif strategy == RollbackStrategy.EMERGENCY_STOP:
                return await self._emergency_stop_rollback(rollback)
            else:
                logger.error(f"❌ Unknown rollback strategy: {strategy}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Rollback strategy execution failed: {e}")
            return False
    
    async def _instant_switch_rollback(self, rollback: RollbackExecution) -> bool:
        """Execute instant switch rollback"""
        rollback.execution_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'instant_switch_started',
            'from_version': rollback.from_version,
            'to_version': rollback.to_version
        })
        
        # Mock instant switch - in real implementation, update load balancer
        await asyncio.sleep(1)
        
        rollback.execution_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'instant_switch_completed',
            'details': 'Traffic switched to previous version'
        })
        
        return True
    
    async def _traffic_reduction_rollback(self, rollback: RollbackExecution) -> bool:
        """Execute traffic reduction rollback"""
        # Gradually reduce traffic to new version
        traffic_levels = [80, 60, 40, 20, 0]
        
        for level in traffic_levels:
            rollback.execution_log.append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'traffic_reduction',
                'traffic_level': level,
                'details': f'Reduced traffic to {level}%'
            })
            await asyncio.sleep(1)
        
        return True
    
    async def _reverse_rolling_rollback(self, rollback: RollbackExecution) -> bool:
        """Execute reverse rolling rollback"""
        # Mock reverse rolling update
        rollback.execution_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'reverse_rolling_started',
            'details': 'Starting reverse rolling update'
        })
        
        await asyncio.sleep(3)
        
        rollback.execution_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'reverse_rolling_completed',
            'details': 'Reverse rolling update completed'
        })
        
        return True
    
    async def _version_revert_rollback(self, rollback: RollbackExecution) -> bool:
        """Execute version revert rollback"""
        rollback.execution_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'version_revert_started',
            'details': f'Reverting to version {rollback.to_version}'
        })
        
        # Mock version revert
        await asyncio.sleep(2)
        
        rollback.execution_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'version_revert_completed',
            'details': 'Version successfully reverted'
        })
        
        return True
    
    async def _emergency_stop_rollback(self, rollback: RollbackExecution) -> bool:
        """Execute emergency stop rollback"""
        rollback.execution_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'emergency_stop_started',
            'details': 'Emergency stop initiated'
        })
        
        # Mock emergency stop
        await asyncio.sleep(0.5)
        
        rollback.execution_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'emergency_stop_completed',
            'details': 'Model deployment stopped'
        })
        
        return True
    
    async def _evaluate_rollback_rule(self, rule: RollbackRule, model_id: str, metrics) -> bool:
        """Evaluate if rollback rule is triggered"""
        try:
            if rule.trigger_type == RollbackTrigger.PERFORMANCE_DEGRADATION:
                # Check for accuracy degradation
                if hasattr(metrics, 'accuracy') and metrics.accuracy < rule.threshold:
                    return True
            
            elif rule.trigger_type == RollbackTrigger.ERROR_RATE_SPIKE:
                # Check for error rate spike
                if hasattr(metrics, 'error_rate') and metrics.error_rate > rule.threshold:
                    return True
            
            elif rule.trigger_type == RollbackTrigger.HEALTH_CHECK_FAILURE:
                # Check for health failures
                if hasattr(metrics, 'health_score') and metrics.health_score < rule.threshold:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Rule evaluation failed: {e}")
            return False
    
    def _initialize_default_rules(self) -> None:
        """Initialize default rollback rules"""
        
        default_rules = [
            RollbackRule(
                rule_id="error_rate_spike",
                trigger_type=RollbackTrigger.ERROR_RATE_SPIKE,
                condition="error_rate > threshold",
                threshold=0.05,  # 5%
                strategy=RollbackStrategy.INSTANT_SWITCH,
                auto_execute=True,
                priority=1,
                description="Auto-rollback on error rate spike"
            ),
            RollbackRule(
                rule_id="performance_degradation",
                trigger_type=RollbackTrigger.PERFORMANCE_DEGRADATION,
                condition="accuracy < threshold",
                threshold=0.7,  # 70%
                strategy=RollbackStrategy.TRAFFIC_REDUCTION,
                auto_execute=True,
                priority=2,
                description="Auto-rollback on performance degradation"
            ),
            RollbackRule(
                rule_id="health_check_failure",
                trigger_type=RollbackTrigger.HEALTH_CHECK_FAILURE,
                condition="health_score < threshold",
                threshold=0.5,
                strategy=RollbackStrategy.EMERGENCY_STOP,
                auto_execute=True,
                priority=1,
                description="Emergency stop on health failure"
            )
        ]
        
        for rule in default_rules:
            self.rollback_rules[rule.rule_id] = rule
        
        logger.info(f"📋 Initialized {len(default_rules)} default rollback rules")
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        
        return {
            'service': 'rollback_manager',
            'status': 'healthy',
            'monitoring_active': self.monitoring_active,
            'monitored_models': len(self.monitored_models),
            'active_rollbacks': len(self.active_rollbacks),
            'rollback_rules': len(self.rollback_rules),
            'total_rollbacks': len(self.rollback_history) + len(self.active_rollbacks)
        }