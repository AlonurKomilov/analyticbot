"""
Analytics Module Facade
Provides controlled access to analytics module functionality
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from src.shared_kernel.domain.interfaces.analytics_service import AnalyticsService


class AnalyticsFacade:
    """Facade for analytics module"""
    
    def __init__(self, analytics_service: AnalyticsService):
        self._analytics_service = analytics_service
    
    async def execute_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """Execute operation through the service interface"""
        try:
            if hasattr(self._analytics_service, operation):
                method = getattr(self._analytics_service, operation)
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
            method for method in dir(self._analytics_service)
            if not method.startswith('_') and callable(getattr(self._analytics_service, method))
        ]
        return service_methods


# Factory function for creating facade instances
def create_analytics_facade(analytics_service: AnalyticsService) -> AnalyticsFacade:
    """Create analytics facade instance"""
    return AnalyticsFacade(analytics_service)
