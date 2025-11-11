"""
Model Versioning Package
========================

Microservices for model version control, deployment management,
and model lifecycle tracking.

Architecture:
- VersionStorageService: File I/O and persistence
- VersionManager: Version lifecycle operations
- VersionComparator: Version comparison and analysis
- DeploymentManager: Deployment and rollback operations
- VersioningOrchestrator: Service coordinator

Usage:
    from core.services.adaptive_learning.versioning import VersioningOrchestrator

    orchestrator = VersioningOrchestrator()
    await orchestrator.initialize_versioning(config)
"""

# Import models and enums
from .comparison.version_comparator import VersionComparator
from .deployment.deployment_manager import DeploymentManager
from .management.version_manager import VersionManager
from .orchestrator.versioning_orchestrator import (
    ModelVersioningService,  # Backward compatibility alias
    VersioningOrchestrator,
)

# Import microservices
from .storage.version_storage_service import VersionStorageService

__all__ = [
    # Models and Enums
    "ModelVersion",
    "ModelStatus",
    "DeploymentStage",
    "ModelVersioningConfig",
    # Microservices
    "VersionStorageService",
    "VersionManager",
    "VersionComparator",
    "DeploymentManager",
    "VersioningOrchestrator",
    # Backward compatibility
    "ModelVersioningService",
]

# Import microservices

__all__ = [
    # Microservices
    "VersionStorageService",
    "VersionManager",
    "VersionComparator",
    "DeploymentManager",
    "VersioningOrchestrator",
    # Backward compatibility
    "ModelVersioningService",
]
