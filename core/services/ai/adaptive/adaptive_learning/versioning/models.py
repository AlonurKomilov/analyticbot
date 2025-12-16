"""
Model Versioning Models & Enums
==============================

Dataclasses and enums for model versioning microservices.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ModelStatus(Enum):
    TRAINING = "training"
    READY = "ready"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class DeploymentStage(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    CANARY = "canary"
    ROLLBACK = "rollback"


@dataclass
class ModelVersion:
    version_id: str
    model_id: str
    version_number: str
    status: ModelStatus
    deployment_stage: DeploymentStage
    model_path: str
    metadata_path: str
    checksum: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    description: str
    tags: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    dependencies: dict[str, str] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)
    deployment_config: dict[str, Any] = field(default_factory=dict)
    parent_version: str | None = None
    size_bytes: int = 0
    is_active: bool = False


@dataclass
class ModelVersioningConfig:
    storage_path: str = "model_versions/"
    max_versions_per_model: int = 10
    auto_cleanup_enabled: bool = True
    backup_enabled: bool = True
    backup_path: str = "model_backups/"
    compression_enabled: bool = True
    retention_days: int = 90
    versioning_strategy: str = "semantic"
    enable_rollback: bool = True
    enable_canary_deployments: bool = True
