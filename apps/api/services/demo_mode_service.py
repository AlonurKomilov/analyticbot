"""
Demo Mode Service
Clean abstraction for demo mode detection and handling
"""

import logging
from typing import Optional, Dict, Any
from fastapi import Request

from config import settings
from apps.api.deps_factory import (
    is_request_for_demo_user, 
    get_demo_type_from_request, 
    get_demo_user_id_from_request
)

logger = logging.getLogger(__name__)


class DemoModeService:
    """
    Service for handling demo mode detection and logic
    Provides clean abstractions for demo vs production handling
    """
    
    @staticmethod
    def is_demo_request(request: Request) -> bool:
        """Check if request is from a demo user"""
        if not settings.demo_mode.is_demo_enabled():
            return False
        return is_request_for_demo_user(request)
    
    @staticmethod
    def get_demo_context(request: Request) -> Dict[str, Any]:
        """Get complete demo context from request"""
        if not DemoModeService.is_demo_request(request):
            return {
                "is_demo": False,
                "demo_type": None,
                "demo_user_id": None
            }
        
        return {
            "is_demo": True,
            "demo_type": get_demo_type_from_request(request),
            "demo_user_id": get_demo_user_id_from_request(request)
        }
    
    @staticmethod
    def should_use_demo_service(request: Request, service_name: str) -> bool:
        """
        Determine if a specific service should use demo/mock implementation
        Based on request context and configuration
        """
        if not settings.demo_mode.is_demo_enabled():
            return False
        
        if not DemoModeService.is_demo_request(request):
            return False
        
        return settings.demo_mode.should_use_mock_service(service_name)
    
    @staticmethod
    def get_effective_user_id(request: Request) -> int:
        """
        Get effective user ID for the request
        Returns demo user ID for demo requests, real user ID otherwise
        """
        if DemoModeService.is_demo_request(request):
            demo_user_id = get_demo_user_id_from_request(request)
            if demo_user_id:
                # Extract numeric part from demo user ID
                if demo_user_id.startswith("demo_"):
                    return 1  # Standard demo user ID
            return 1
        
        # For real users, would extract from JWT or other auth mechanism
        # This is a placeholder - real implementation would decode JWT
        return 1
    
    @staticmethod
    def log_demo_usage(request: Request, endpoint: str, action: str):
        """Log demo mode usage for monitoring"""
        if DemoModeService.is_demo_request(request):
            demo_context = DemoModeService.get_demo_context(request)
            logger.info(
                f"Demo mode usage: endpoint={endpoint}, action={action}, "
                f"demo_type={demo_context['demo_type']}, "
                f"demo_user_id={demo_context['demo_user_id']}"
            )


# Convenience instance
demo_service = DemoModeService()