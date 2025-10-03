"""
Model Deployment Microservice
=============================

Complete model deployment capabilities with clean architecture.
All deployment-related services and components are contained within this microservice.
"""

from .model_update_service import ModelUpdateService
from .deployment_plan_manager import (
    DeploymentPlanManager,
    DeploymentPlan,
    PerformanceRequirement,
    DeploymentConstraint,
    RiskAssessmentResult,
    DeploymentRisk
)
from .deployment_executor import (
    DeploymentExecutor,
    ExecutionPhase,
    ExecutionProgress,
    DeploymentExecution
)
from .rollback_manager import (
    RollbackManager,
    RollbackTrigger,
    RollbackStrategy,
    RollbackRule,
    RollbackExecution
)

__all__ = [
    # Main service
    'ModelUpdateService',
    
    # Plan management
    'DeploymentPlanManager',
    'DeploymentPlan',
    'PerformanceRequirement',
    'DeploymentConstraint',
    'RiskAssessmentResult',
    'DeploymentRisk',
    
    # Execution
    'DeploymentExecutor',
    'ExecutionPhase',
    'ExecutionProgress',
    'DeploymentExecution',
    
    # Rollback management
    'RollbackManager',
    'RollbackTrigger',
    'RollbackStrategy',
    'RollbackRule',
    'RollbackExecution'
]

# Microservice metadata
__microservice__ = {
    'name': 'model_deployment',
    'version': '1.0.0',
    'description': 'Complete model deployment with planning, execution, and rollback capabilities',
    'components': [
        'ModelUpdateService',
        'DeploymentPlanManager',
        'DeploymentExecutor',
        'RollbackManager'
    ]
}