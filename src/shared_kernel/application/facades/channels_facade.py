"""
Channels Module Facade
Provides controlled access to channels module functionality
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from src.shared_kernel.domain.interfaces.channels_service import ChannelsService


class ChannelsFacade:
    """Facade for channels module"""
    
    def __init__(self, channels_service: ChannelsService):
        self._channels_service = channels_service
    
    async def execute_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute operation through the service interface"""
        try:
            if hasattr(self._channels_service, operation):
                method = getattr(self._channels_service, operation)
                result = await method(**kwargs)
                return {
                    "success": True,
                    "data": result
                }
            else:
                return {
                    "success": False,
                    "error": f"Operation '{operation}' not found"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_operations(self) -> List[str]:
        """Get list of available operations"""
        service_methods = [
            method for method in dir(self._channels_service)
            if not method.startswith('_') and callable(getattr(self._channels_service, method))
        ]
        return service_methods


# Factory function for creating facade instances
def create_channels_facade(channels_service: ChannelsService) -> ChannelsFacade:
    """Create channels facade instance"""
    return ChannelsFacade(channels_service)
