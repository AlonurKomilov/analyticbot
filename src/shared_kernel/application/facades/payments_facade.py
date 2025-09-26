"""
Payments Module Facade
Provides controlled access to payments module functionality
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from src.shared_kernel.domain.interfaces.payments_service import PaymentsService


class PaymentsFacade:
    """Facade for payments module"""
    
    def __init__(self, payments_service: PaymentsService):
        self._payments_service = payments_service
    
    async def execute_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute operation through the service interface"""
        try:
            if hasattr(self._payments_service, operation):
                method = getattr(self._payments_service, operation)
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
            method for method in dir(self._payments_service)
            if not method.startswith('_') and callable(getattr(self._payments_service, method))
        ]
        return service_methods


# Factory function for creating facade instances
def create_payments_facade(payments_service: PaymentsService) -> PaymentsFacade:
    """Create payments facade instance"""
    return PaymentsFacade(payments_service)
