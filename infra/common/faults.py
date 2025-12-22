"""
Fault injection utilities for MTProto resilience testing.
Only active in development/testing environments for chaos engineering.
"""

import asyncio
import logging
import os
import random
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class FaultType(Enum):
    """Types of faults that can be injected."""

    DELAY = "delay"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    NETWORK_ERROR = "network_error"
    FLOOD_WAIT = "flood_wait"


@dataclass
class FaultConfig:
    """Configuration for a specific fault injection."""

    fault_type: FaultType
    probability: float  # 0.0 to 1.0
    min_delay_ms: int = 100
    max_delay_ms: int = 5000
    error_message: str = "Injected fault"
    enabled: bool = True


class FaultInjector:
    """Fault injector for chaos engineering and resilience testing."""

    def __init__(self, enabled: bool = False):
        # Only enable in non-production environments
        self.enabled = enabled and self._is_development_environment()
        self.faults: dict[str, FaultConfig] = {}
        self.injection_count: dict[str, int] = {}

        if not self.enabled:
            logger.info("Fault injection disabled (production environment or disabled)")
            return

        # Default fault configurations for development
        self._setup_default_faults()
        logger.warning("FAULT INJECTION ENABLED - This should only be used in development/testing!")

    def _is_development_environment(self) -> bool:
        """Check if we're in a development environment."""
        env = os.getenv("ENVIRONMENT", "production").lower()
        debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
        testing = os.getenv("TESTING", "false").lower() in ("true", "1", "yes")

        return env in ("development", "dev", "test", "staging") or debug or testing

    def _setup_default_faults(self):
        """Setup default fault configurations."""
        # Network delays (5% chance)
        self.add_fault(
            "network_delay",
            FaultConfig(
                fault_type=FaultType.DELAY,
                probability=0.05,
                min_delay_ms=100,
                max_delay_ms=2000,
            ),
        )

        # Random errors (2% chance)
        self.add_fault(
            "random_error",
            FaultConfig(
                fault_type=FaultType.ERROR,
                probability=0.02,
                error_message="Connection temporarily unavailable",
            ),
        )

        # Simulate flood wait (1% chance)
        self.add_fault(
            "flood_wait",
            FaultConfig(
                fault_type=FaultType.FLOOD_WAIT,
                probability=0.01,
                min_delay_ms=5000,
                max_delay_ms=60000,
                error_message="FLOOD_WAIT_30",
            ),
        )

        # Rate limiting (3% chance)
        self.add_fault(
            "rate_limit",
            FaultConfig(
                fault_type=FaultType.RATE_LIMIT,
                probability=0.03,
                error_message="Rate limit exceeded",
            ),
        )

        # Network errors (1% chance)
        self.add_fault(
            "network_error",
            FaultConfig(
                fault_type=FaultType.NETWORK_ERROR,
                probability=0.01,
                error_message="Network unreachable",
            ),
        )

    def add_fault(self, name: str, config: FaultConfig) -> None:
        """Add a fault injection configuration."""
        if not self.enabled:
            return

        self.faults[name] = config
        self.injection_count[name] = 0
        logger.debug(
            f"Added fault injection: {name} ({config.fault_type.value}, "
            f"probability: {config.probability})"
        )

    def remove_fault(self, name: str) -> None:
        """Remove a fault injection configuration."""
        if name in self.faults:
            del self.faults[name]
            self.injection_count.pop(name, 0)
            logger.debug(f"Removed fault injection: {name}")

    def enable_fault(self, name: str) -> None:
        """Enable a specific fault injection."""
        if name in self.faults:
            self.faults[name].enabled = True
            logger.debug(f"Enabled fault injection: {name}")

    def disable_fault(self, name: str) -> None:
        """Disable a specific fault injection."""
        if name in self.faults:
            self.faults[name].enabled = False
            logger.debug(f"Disabled fault injection: {name}")

    async def inject_fault(self, operation: str = "default") -> None:
        """
        Inject faults based on configured probabilities.
        Call this at the beginning of operations you want to test.
        """
        if not self.enabled:
            return

        for name, config in self.faults.items():
            if not config.enabled:
                continue

            if random.random() < config.probability:
                await self._execute_fault(name, config, operation)
                self.injection_count[name] += 1

    async def _execute_fault(self, name: str, config: FaultConfig, operation: str) -> None:
        """Execute a specific fault injection."""
        logger.warning(
            f"INJECTING FAULT: {name} ({config.fault_type.value}) for operation: {operation}"
        )

        if config.fault_type == FaultType.DELAY:
            delay_ms = random.randint(config.min_delay_ms, config.max_delay_ms)
            logger.debug(f"Injecting delay: {delay_ms}ms")
            await asyncio.sleep(delay_ms / 1000.0)

        elif config.fault_type == FaultType.ERROR:
            raise RuntimeError(f"Fault injection: {config.error_message}")

        elif config.fault_type == FaultType.TIMEOUT:
            # Simulate timeout by sleeping longer than typical request timeout
            delay_ms = random.randint(10000, 30000)  # 10-30 seconds
            logger.debug(f"Injecting timeout: {delay_ms}ms")
            await asyncio.sleep(delay_ms / 1000.0)

        elif config.fault_type == FaultType.RATE_LIMIT:
            # Simulate rate limiting error
            raise Exception(f"Rate limit exceeded: {config.error_message}")

        elif config.fault_type == FaultType.NETWORK_ERROR:
            # Simulate network errors
            error_types = [
                "Connection refused",
                "Network unreachable",
                "DNS resolution failed",
                "Connection timed out",
            ]
            error_msg = random.choice(error_types)
            raise ConnectionError(f"Network fault injection: {error_msg}")

        elif config.fault_type == FaultType.FLOOD_WAIT:
            # Simulate Telegram flood wait
            wait_seconds = random.randint(config.min_delay_ms // 1000, config.max_delay_ms // 1000)
            raise Exception(f"FLOOD_WAIT_{wait_seconds}: Please wait {wait_seconds} seconds")

    def get_stats(self) -> dict[str, Any]:
        """Get fault injection statistics."""
        if not self.enabled:
            return {"enabled": False}

        total_injections = sum(self.injection_count.values())

        fault_stats = {}
        for name, config in self.faults.items():
            fault_stats[name] = {
                "type": config.fault_type.value,
                "probability": config.probability,
                "enabled": config.enabled,
                "injection_count": self.injection_count.get(name, 0),
            }

        return {
            "enabled": True,
            "total_injections": total_injections,
            "faults": fault_stats,
            "environment_checks": {
                "is_development": self._is_development_environment(),
                "environment": os.getenv("ENVIRONMENT", "unknown"),
                "debug": os.getenv("DEBUG", "false"),
                "testing": os.getenv("TESTING", "false"),
            },
        }

    def reset_stats(self) -> None:
        """Reset injection statistics."""
        self.injection_count = {name: 0 for name in self.faults.keys()}
        logger.info("Fault injection statistics reset")


# Decorator for easy fault injection
def inject_faults(operation_name: str = "operation", injector: FaultInjector | None = None):
    """
    Decorator to inject faults into async functions.

    Usage:
        @inject_faults("mtproto_request")
        async def make_request():
            ...
    """

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            fault_injector = injector or get_global_injector()
            await fault_injector.inject_fault(operation_name)
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Context manager for fault injection
class FaultInjectionContext:
    """Context manager for fault injection within a code block."""

    def __init__(self, operation: str = "operation", injector: FaultInjector | None = None):
        self.operation = operation
        self.injector = injector or get_global_injector()

    async def __aenter__(self):
        await self.injector.inject_fault(self.operation)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


# Global fault injector instance
_global_injector: FaultInjector | None = None


def get_global_injector() -> FaultInjector:
    """Get global fault injector instance."""
    global _global_injector
    if _global_injector is None:
        # Check environment variables for fault injection settings
        enabled = os.getenv("FAULT_INJECTION_ENABLED", "false").lower() in (
            "true",
            "1",
            "yes",
        )
        _global_injector = FaultInjector(enabled=enabled)
    return _global_injector


def initialize_fault_injection(enabled: bool = False) -> FaultInjector:
    """Initialize global fault injector."""
    global _global_injector
    _global_injector = FaultInjector(enabled=enabled)
    return _global_injector


# Convenience functions
async def inject_fault(operation: str = "default") -> None:
    """Inject fault using global injector."""
    injector = get_global_injector()
    await injector.inject_fault(operation)


def fault_injection_context(operation: str = "operation") -> FaultInjectionContext:
    """Create fault injection context manager."""
    return FaultInjectionContext(operation)


# Example usage patterns:
if __name__ == "__main__":

    async def example_usage():
        # Method 1: Direct injection
        injector = FaultInjector(enabled=True)
        await injector.inject_fault("test_operation")

        # Method 2: Decorator
        @inject_faults("api_request")
        async def make_api_request():
            print("Making API request...")
            return "success"

        # Method 3: Context manager
        async with fault_injection_context("database_query"):
            print("Executing database query...")

        # Method 4: Global injector
        await inject_fault("global_operation")

        print("Fault injection examples completed")

    # Run example
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(example_usage())
