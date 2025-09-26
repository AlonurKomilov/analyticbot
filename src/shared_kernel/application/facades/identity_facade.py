"""
Identity Module Facade
Provides controlled access to identity module functionality
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from src.shared_kernel.domain.interfaces.identity_service import IdentityService


class IdentityFacade:
    """Facade for identity module"""
    
    def __init__(self, identity_service: IdentityService):
        self._identity_service = identity_service
    
    async def execute_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute operation through the service interface"""
        try:
            if hasattr(self._identity_service, operation):
                method = getattr(self._identity_service, operation)
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
            method for method in dir(self._identity_service)
            if not method.startswith('_') and callable(getattr(self._identity_service, method))
        ]
        return service_methods


# Factory function for creating facade instances
def create_identity_facade(identity_service: IdentityService) -> IdentityFacade:
    """Create identity facade instance"""
    return IdentityFacade(identity_service)
