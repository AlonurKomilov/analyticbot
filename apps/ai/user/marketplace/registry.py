"""
Marketplace Service Registry
============================

Central registry for all marketplace services available for AI integration.
"""

import logging
from typing import Any

from apps.ai.user.marketplace.adapter import (
    DemoServiceAdapter,
    MarketplaceServiceAdapter,
    ServiceCapability,
    ServiceDefinition,
)

logger = logging.getLogger(__name__)


# Import concrete service adapters
def _get_service_adapters():
    """Lazy import of service adapters to avoid circular imports"""
    from apps.ai.user.marketplace.services import (
        AutoPostingAdapter,
        CompetitorAnalysisAdapter,
        ContentSchedulerAdapter,
    )

    return [
        DemoServiceAdapter,
        ContentSchedulerAdapter,
        AutoPostingAdapter,
        CompetitorAnalysisAdapter,
    ]


class MarketplaceServiceRegistry:
    """
    Registry for marketplace services.

    Manages:
    - Service discovery
    - Service registration
    - Service lookup
    - Capability filtering

    Usage:
        registry = MarketplaceServiceRegistry()
        registry.register(MyServiceAdapter())

        # Find services by capability
        services = registry.find_by_capability(ServiceCapability.AUTO_POSTING)

        # Execute a service
        adapter = registry.get("my_service_v1")
        result = await adapter.execute(context)
    """

    _instance: "MarketplaceServiceRegistry | None" = None

    def __new__(cls) -> "MarketplaceServiceRegistry":
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._services: dict[str, MarketplaceServiceAdapter] = {}
        self._initialized = True

        # Register built-in services
        self._register_builtin_services()

        logger.info("🏪 Marketplace Service Registry initialized")

    def _register_builtin_services(self):
        """Register built-in services"""
        try:
            adapter_classes = _get_service_adapters()
            for adapter_cls in adapter_classes:
                self.register(adapter_cls())
        except Exception as e:
            logger.warning(f"Could not register all built-in services: {e}")
            # At minimum register demo service
            self.register(DemoServiceAdapter())

    def register(self, adapter: MarketplaceServiceAdapter) -> bool:
        """
        Register a marketplace service.

        Args:
            adapter: Service adapter to register

        Returns:
            True if registered successfully
        """
        try:
            service_id = adapter.definition.service_id

            if service_id in self._services:
                logger.warning(f"Service {service_id} already registered, overwriting")

            self._services[service_id] = adapter
            logger.info(f"✅ Registered marketplace service: {adapter.definition.name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to register service: {e}")
            return False

    def unregister(self, service_id: str) -> bool:
        """Unregister a service"""
        if service_id in self._services:
            del self._services[service_id]
            logger.info(f"Unregistered service: {service_id}")
            return True
        return False

    def get(self, service_id: str) -> MarketplaceServiceAdapter | None:
        """Get a service adapter by ID"""
        return self._services.get(service_id)

    def list_all(self) -> list[ServiceDefinition]:
        """List all registered services"""
        return [adapter.definition for adapter in self._services.values()]

    def find_by_capability(
        self,
        capability: ServiceCapability,
    ) -> list[MarketplaceServiceAdapter]:
        """Find services with a specific capability"""
        return [
            adapter
            for adapter in self._services.values()
            if capability in adapter.definition.capabilities
        ]

    def find_by_tier(self, tier: str) -> list[MarketplaceServiceAdapter]:
        """Find services available for a specific tier"""
        tier_order = ["free", "basic", "pro", "enterprise"]

        try:
            tier_idx = tier_order.index(tier)
        except ValueError:
            return []

        return [
            adapter
            for adapter in self._services.values()
            if tier_order.index(adapter.definition.required_tier) <= tier_idx
        ]

    def search(
        self,
        query: str | None = None,
        capabilities: list[ServiceCapability] | None = None,
        tier: str | None = None,
        free_only: bool = False,
    ) -> list[ServiceDefinition]:
        """
        Search for services with filters.

        Args:
            query: Text search in name/description
            capabilities: Filter by capabilities
            tier: Filter by tier availability
            free_only: Only free services

        Returns:
            List of matching service definitions
        """
        results = list(self._services.values())

        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                adapter
                for adapter in results
                if query_lower in adapter.definition.name.lower()
                or query_lower in adapter.definition.description.lower()
            ]

        # Filter by capabilities
        if capabilities:
            results = [
                adapter
                for adapter in results
                if any(cap in adapter.definition.capabilities for cap in capabilities)
            ]

        # Filter by tier
        if tier:
            results = [adapter for adapter in results if adapter.check_tier(tier)]

        # Filter by free
        if free_only:
            results = [adapter for adapter in results if adapter.definition.is_free]

        return [adapter.definition for adapter in results]

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics"""
        all_capabilities = set()
        for adapter in self._services.values():
            all_capabilities.update(adapter.definition.capabilities)

        return {
            "total_services": len(self._services),
            "free_services": len([a for a in self._services.values() if a.definition.is_free]),
            "capabilities_available": [c.value for c in all_capabilities],
            "services_by_tier": {
                "free": len(
                    [a for a in self._services.values() if a.definition.required_tier == "free"]
                ),
                "basic": len(
                    [a for a in self._services.values() if a.definition.required_tier == "basic"]
                ),
                "pro": len(
                    [a for a in self._services.values() if a.definition.required_tier == "pro"]
                ),
                "enterprise": len(
                    [
                        a
                        for a in self._services.values()
                        if a.definition.required_tier == "enterprise"
                    ]
                ),
            },
        }


# Global registry instance
def get_marketplace_registry() -> MarketplaceServiceRegistry:
    """Get the global marketplace registry instance"""
    return MarketplaceServiceRegistry()
