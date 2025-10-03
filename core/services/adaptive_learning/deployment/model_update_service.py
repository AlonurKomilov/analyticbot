"""
Model Update Service
===================

Clean architecture replacement for the monolithic ModelUpdateService.
Delegates to specialized deployment components while maintaining the original interface.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .deployment import (
    DeploymentPlanManager,
    DeploymentExecutor,
    RollbackManager,
    DeploymentPlan,
    PerformanceRequirement,
    DeploymentConstraint
)
from .protocols.learning_protocols import (
    ModelUpdateProtocol,
    DeploymentStrategy,
    DeploymentStatus,
    ModelMetadata,
    ValidationResult
)
from .protocols.monitoring_protocols import MonitoringServiceProtocol

logger = logging.getLogger(__name__)


class ModelUpdateService(ModelUpdateProtocol):
    """
    Clean, focused model update service.
    
    Replaces the 959-line god object with a clean coordinator pattern.
    Maintains compatibility while delegating to specialized components.
    """
    
    def __init__(self, monitoring_service: MonitoringServiceProtocol):
        # Create specialized components
        self.plan_manager = DeploymentPlanManager()
        self.executor = DeploymentExecutor(monitoring_service)
        self.rollback_manager = RollbackManager(monitoring_service)
        
        # Service state
        self.is_running = False
        
        logger.info("🎯 Clean ModelUpdateService initialized")
    
    async def start_service(self) -> bool:
        """Start model update service"""
        try:
            # Start rollback monitoring
            await self.rollback_manager.start_monitoring()
            
            self.is_running = True
            logger.info("✅ ModelUpdateService started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start ModelUpdateService: {e}")
            return False
    
    async def stop_service(self) -> bool:
        """Stop model update service"""
        try:
            # Stop rollback monitoring
            await self.rollback_manager.stop_monitoring()
            
            self.is_running = False
            logger.info("⏹️ ModelUpdateService stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop ModelUpdateService: {e}")
            return False
    
    async def plan_deployment(
        self,
        model_id: str,
        source_version: str,
        target_version: str,
        target_metadata: ModelMetadata,
        requirements: Optional[List[PerformanceRequirement]] = None,
        constraints: Optional[List[DeploymentConstraint]] = None
    ) -> Optional[str]:
        """Plan model deployment"""
        try:
            plan = await self.plan_manager.create_deployment_plan(
                model_id=model_id,
                source_version=source_version,
                target_version=target_version,
                target_metadata=target_metadata,
                requirements=requirements,
                constraints=constraints
            )
            
            if plan:
                logger.info(f"📋 Deployment plan created: {plan.plan_id}")
                return plan.plan_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Deployment planning failed: {e}")
            return None
    
    async def validate_deployment_plan(self, plan_id: str) -> ValidationResult:
        """Validate deployment plan"""
        return await self.plan_manager.validate_deployment_plan(plan_id)
    
    async def approve_deployment_plan(self, plan_id: str, approver: str) -> bool:
        """Approve deployment plan"""
        return await self.plan_manager.approve_deployment_plan(plan_id, approver)
    
    async def execute_deployment(self, plan_id: str) -> Optional[str]:
        """Execute deployment plan"""
        try:
            # Get plan
            plan = await self.plan_manager.get_deployment_plan(plan_id)
            if not plan:
                logger.error(f"❌ Plan {plan_id} not found")
                return None
            
            # Validate plan
            validation = await self.validate_deployment_plan(plan_id)
            if not validation.is_valid:
                logger.error(f"❌ Plan validation failed: {validation.errors}")
                return None
            
            # Check approval if required
            if plan.approval_required and not plan.approved_by:
                logger.error(f"❌ Plan {plan_id} requires approval")
                return None
            
            # Add model to rollback monitoring
            await self.rollback_manager.add_model_monitoring(
                model_id=plan.model_id,
                current_version=plan.source_version,
                version_history=[plan.source_version, plan.target_version]
            )
            
            # Execute deployment
            execution_id = await self.executor.execute_deployment(plan)
            if execution_id:
                logger.info(f"🚀 Deployment execution started: {execution_id}")
                return execution_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Deployment execution failed: {e}")
            return None
    
    async def get_deployment_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment execution status"""
        try:
            progress = await self.executor.get_execution_status(execution_id)
            if progress:
                return {
                    'execution_id': execution_id,
                    'phase': progress.phase.value,
                    'progress_percent': progress.progress_percent,
                    'current_step': progress.current_step,
                    'success': progress.success,
                    'error_message': progress.error_message,
                    'estimated_completion': progress.estimated_completion.isoformat() if progress.estimated_completion else None
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get deployment status: {e}")
            return None
    
    async def cancel_deployment(self, execution_id: str, reason: str = "User requested") -> bool:
        """Cancel deployment execution"""
        return await self.executor.cancel_deployment(execution_id, reason)
    
    async def trigger_rollback(
        self,
        model_id: str,
        target_version: str,
        reason: str,
        strategy: Optional[str] = None
    ) -> Optional[str]:
        """Trigger manual rollback"""
        from .deployment.rollback_manager import RollbackStrategy
        
        rollback_strategy = None
        if strategy:
            try:
                rollback_strategy = RollbackStrategy(strategy)
            except ValueError:
                logger.warning(f"⚠️ Unknown rollback strategy: {strategy}")
        
        return await self.rollback_manager.trigger_manual_rollback(
            model_id=model_id,
            target_version=target_version,
            reason=reason,
            strategy=rollback_strategy
        )
    
    async def get_rollback_status(self, rollback_id: str) -> Optional[Dict[str, Any]]:
        """Get rollback status"""
        try:
            rollback = await self.rollback_manager.get_rollback_status(rollback_id)
            if rollback:
                return {
                    'rollback_id': rollback_id,
                    'model_id': rollback.model_id,
                    'trigger': rollback.trigger.value,
                    'strategy': rollback.strategy.value,
                    'status': rollback.status,
                    'success': rollback.success,
                    'from_version': rollback.from_version,
                    'to_version': rollback.to_version,
                    'triggered_at': rollback.triggered_at.isoformat(),
                    'duration': rollback.duration.total_seconds() if rollback.duration else None,
                    'error_message': rollback.error_message
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get rollback status: {e}")
            return None
    
    async def list_deployments(self, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List deployment history"""
        try:
            history = await self.executor.get_deployment_history(model_id)
            
            return [
                {
                    'execution_id': exec.execution_id,
                    'plan_id': exec.plan.plan_id,
                    'model_id': exec.plan.model_id,
                    'strategy': exec.plan.strategy.value,
                    'status': exec.status.value,
                    'started_at': exec.started_at.isoformat(),
                    'completed_at': exec.completed_at.isoformat() if exec.completed_at else None,
                    'duration': exec.duration.total_seconds() if exec.duration else None,
                    'success': exec.progress.success,
                    'rollback_triggered': exec.rollback_triggered
                }
                for exec in history
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to list deployments: {e}")
            return []
    
    async def list_rollbacks(self, model_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List rollback history"""
        try:
            history = await self.rollback_manager.get_rollback_history(model_id)
            
            return [
                {
                    'rollback_id': rollback.rollback_id,
                    'model_id': rollback.model_id,
                    'trigger': rollback.trigger.value,
                    'strategy': rollback.strategy.value,
                    'status': rollback.status,
                    'success': rollback.success,
                    'from_version': rollback.from_version,
                    'to_version': rollback.to_version,
                    'triggered_at': rollback.triggered_at.isoformat(),
                    'duration': rollback.duration.total_seconds() if rollback.duration else None
                }
                for rollback in history
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to list rollbacks: {e}")
            return []
    
    async def get_model_deployment_status(self, model_id: str) -> Dict[str, Any]:
        """Get overall model deployment status"""
        try:
            # Get active deployments
            active_deployments = [
                progress for progress in await self.executor.get_active_deployments()
                if progress.plan_id.startswith(f"plan_{model_id}_")
            ]
            
            # Get active rollbacks
            active_rollbacks = [
                rollback for rollback in await self.rollback_manager.list_active_rollbacks()
                if rollback.model_id == model_id
            ]
            
            # Get recent history
            recent_deployments = await self.executor.get_deployment_history(model_id, limit=5)
            recent_rollbacks = await self.rollback_manager.get_rollback_history(model_id, limit=5)
            
            return {
                'model_id': model_id,
                'active_deployments': len(active_deployments),
                'active_rollbacks': len(active_rollbacks),
                'recent_deployments': len(recent_deployments),
                'recent_rollbacks': len(recent_rollbacks),
                'last_deployment': recent_deployments[0].started_at.isoformat() if recent_deployments else None,
                'last_rollback': recent_rollbacks[0].triggered_at.isoformat() if recent_rollbacks else None,
                'rollback_monitoring_enabled': model_id in self.rollback_manager.monitored_models
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get model deployment status: {e}")
            return {'error': str(e)}
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            'service': 'model_update_service',
            'status': 'healthy' if self.is_running else 'stopped',
            'component_health': {
                'plan_manager': self.plan_manager.get_service_health(),
                'executor': self.executor.get_service_health(),
                'rollback_manager': self.rollback_manager.get_service_health()
            }
        }
    
    async def shutdown(self) -> None:
        """Shutdown service"""
        try:
            await self.stop_service()
            logger.info("🛑 ModelUpdateService shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")