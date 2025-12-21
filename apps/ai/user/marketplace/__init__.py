"""
User AI Marketplace Integration
===============================

Marketplace adapter system for AI-powered service integration.
Any marketplace service can be AI-enhanced through this interface.
"""

from apps.ai.user.marketplace.adapter import (
    MarketplaceServiceAdapter,
    ServiceCapability,
    ServiceDefinition,
    ServiceExecutionContext,
    ServiceResult,
)
from apps.ai.user.marketplace.registry import (
    MarketplaceServiceRegistry,
    get_marketplace_registry,
)
from apps.ai.user.marketplace.services import (
    ContentSchedulerAdapter,
    AutoPostingAdapter,
    CompetitorAnalysisAdapter,
)

__all__ = [
    # Base adapter
    "MarketplaceServiceAdapter",
    "ServiceCapability",
    "ServiceDefinition",
    "ServiceExecutionContext",
    "ServiceResult",
    # Registry
    "MarketplaceServiceRegistry",
    "get_marketplace_registry",
    # Concrete adapters
    "ContentSchedulerAdapter",
    "AutoPostingAdapter",
    "CompetitorAnalysisAdapter",
]
