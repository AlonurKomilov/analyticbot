"""AI Agent Module - Deprecated, use controller from system root"""

from apps.ai.system.controller import SystemAIController

# Backwards compatibility
AIWorkerController = SystemAIController

__all__ = ["SystemAIController", "AIWorkerController"]
