"""
Bot_Service Module Facade
Provides controlled access to bot_service module functionality
"""

from typing import Any

from src.shared_kernel.domain.interfaces.bot_service_service import BotServiceService


class BotServiceFacade:
    """Facade for bot_service module"""

    def __init__(self, bot_service_service: BotServiceService):
        self._bot_service_service = bot_service_service

    async def execute_operation(self, operation: str, **kwargs) -> dict[str, Any]:
        """Execute operation through the service interface"""
        try:
            if hasattr(self._bot_service_service, operation):
                method = getattr(self._bot_service_service, operation)
                result = await method(**kwargs)
                return {"success": True, "data": result}
            else:
                return {"success": False, "error": f"Operation '{operation}' not found"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_available_operations(self) -> list[str]:
        """Get list of available operations"""
        service_methods = [
            method
            for method in dir(self._bot_service_service)
            if not method.startswith("_") and callable(getattr(self._bot_service_service, method))
        ]
        return service_methods


# Factory function for creating facade instances
def create_bot_service_facade(
    bot_service_service: BotServiceService,
) -> BotServiceFacade:
    """Create bot_service facade instance"""
    return BotServiceFacade(bot_service_service)
