"""
AI System - Dual-Layer Autonomous Intelligence
==============================================

Two-layer AI architecture:

1. **System AI** (apps.ai.system)
   - Infrastructure management
   - Worker scaling and health
   - Configured via environment
   - Admin-only access
   
2. **User AI** (apps.ai.user)
   - Per-user AI assistants
   - Analytics insights
   - Content generation
   - Marketplace service integration
   - Configured via database/frontend

Version: 2.0.0
Status: Phase 1 - Foundation + Separation
"""

# System AI - Infrastructure management
from apps.ai.system import (
    AIApprovalMode,
    SystemAIConfig,
    SystemAIController,
    get_system_ai_config,
)

# User AI - User-facing features
from apps.ai.user import UserAIAgent, UserAIConfig, UserAISettings

# Shared models
from apps.ai.shared.models import (
    Action,
    ActionResult,
    ActionStatus,
    ActionType,
    ApprovalLevel,
    Decision,
    DecisionType,
    WorkerDefinition,
    WorkerState,
    WorkerStatus,
    WorkerType,
)

# Legacy compatibility
from apps.ai.system.controller import SystemAIController as AIWorkerController
from apps.ai.system.registry import WorkerRegistry

__version__ = "2.0.0"
__all__ = [
    # System AI
    "SystemAIController",
    "SystemAIConfig",
    "AIApprovalMode",
    "get_system_ai_config",
    # User AI
    "UserAIAgent",
    "UserAIConfig",
    "UserAISettings",
    # Shared models
    "Action",
    "ActionResult",
    "ActionStatus",
    "ActionType",
    "Decision",
    "DecisionType",
    "ApprovalLevel",
    "WorkerDefinition",
    "WorkerState",
    "WorkerStatus",
    "WorkerType",
    # Legacy
    "AIWorkerController",
    "WorkerRegistry",
]
