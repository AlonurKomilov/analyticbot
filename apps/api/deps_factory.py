"""
Dependency Factory - Configuration-driven service creation
Replaces direct mock imports with proper DI container usage
"""

import logging
from typing import Optional
from fastapi import Depends, Request

from config import settings
from core.di_container import container
from core.protocols import DemoDataServiceProtocol
from apps.bot.models.twa import InitialDataResponse

logger = logging.getLogger(__name__)


async def get_demo_data_service() -> DemoDataServiceProtocol:
    """
    Get demo data service based on configuration
    This replaces direct imports of mock services
    """
    try:
        service = container.get_service(DemoDataServiceProtocol)
        return service
    except ValueError as e:
        logger.error(f"Failed to get demo data service from DI container: {e}")
        # Fallback only if container is not properly configured
        if settings.demo_mode.should_use_mock_service("demo_data"):
            from apps.api.__mocks__.services.mock_demo_data_service import MockDemoDataService
            return MockDemoDataService()
        else:
            raise ValueError("No demo data service available and not in demo mode")


def is_request_for_demo_user_proper(request: Request) -> bool:
    """
    Proper demo user detection that receives a Request object
    This fixes the architectural flaw of passing user_id instead of Request
    """
    return getattr(request.state, "is_demo", False)


def get_demo_type_from_request_proper(request: Request) -> Optional[str]:
    """
    Proper demo type extraction that receives a Request object  
    This fixes the architectural flaw of passing user_id instead of Request
    """
    return getattr(request.state, "demo_type", None)


async def get_initial_data_service(request: Request) -> InitialDataResponse:
    """
    Configuration-driven initial data service
    Routes to demo or real services based on demo mode detection
    """
    try:
        # Check if this is a demo user request using proper Request object
        if is_request_for_demo_user_proper(request):
            demo_type = get_demo_type_from_request_proper(request)
            demo_service = await get_demo_data_service()
            
            # Get user_id from request state or extract from auth
            user_id = getattr(request.state, "demo_user_id", None)
            if not user_id:
                # Extract from auth if available
                from apps.api.middleware.auth import get_current_user_id_from_request
                user_id = await get_current_user_id_from_request(request)
            
            return await demo_service.get_initial_data(user_id, demo_type)
        
        # For production users, use real services
        # This will be implemented with proper repository injection
        from apps.api.services.initial_data_service import get_real_initial_data
        from apps.api.middleware.auth import get_current_user_id_from_request
        
        user_id = await get_current_user_id_from_request(request)
        return await get_real_initial_data(user_id)
        
    except Exception as e:
        logger.error(f"Failed to get initial data: {e}")
        # In production, we should not fall back to demo data
        # but return proper HTTP error
        if not settings.demo_mode.is_demo_enabled():
            raise
        
        # Only fallback to demo if explicitly in demo mode
        demo_service = await get_demo_data_service()
        return await demo_service.get_initial_data(1, "limited")