"""
Demo Service
============

Core service for managing demo functionality and user detection.
Provides clean abstractions for demo vs production handling.
"""

import logging
from typing import Any

from fastapi import Request

logger = logging.getLogger(__name__)


class DemoService:
    """
    Core service for all demo functionality
    Handles demo user detection, context management, and service routing
    """

    @staticmethod
    def is_demo_request(request: Request) -> bool:
        """Check if request is from a demo user"""
        from apps.demo.config import demo_config

        if not demo_config.is_demo_enabled():
            return False

        # Check request state (set by middleware)
        if hasattr(request.state, "is_demo"):
            return request.state.is_demo

        # Fallback: check manually
        return DemoService._detect_demo_from_request(request)

    @staticmethod
    def get_demo_context(request: Request) -> dict[str, Any]:
        """Get complete demo context from request"""
        if not DemoService.is_demo_request(request):
            return {
                "is_demo": False,
                "demo_type": None,
                "demo_user_id": None,
                "quality_level": None,
            }

        # Get from request state (set by middleware)
        demo_type = getattr(request.state, "demo_type", "standard")
        demo_user_id = getattr(request.state, "demo_user_id", "demo_user")

        from apps.demo.config import demo_config

        quality_level = demo_config.get_demo_quality_level()

        return {
            "is_demo": True,
            "demo_type": demo_type,
            "demo_user_id": demo_user_id,
            "quality_level": quality_level,
        }

    @staticmethod
    def should_use_sample_service(request: Request, service_name: str) -> bool:
        """
        Determine if a specific service should use sample implementation
        for demo users based on request context and configuration
        """
        from apps.demo.config import demo_config

        if not demo_config.is_demo_enabled():
            return False

        if not DemoService.is_demo_request(request):
            return False

        return demo_config.should_use_sample_service(service_name)

    @staticmethod
    def get_effective_user_id(request: Request) -> str:
        """
        Get effective user ID for the request
        Returns demo user ID for demo requests, real user ID otherwise
        """
        if DemoService.is_demo_request(request):
            demo_context = DemoService.get_demo_context(request)
            return demo_context.get("demo_user_id", "demo_user_standard")

        # For real users, would extract from JWT or other auth mechanism
        # This is a placeholder - real implementation would decode JWT
        user_id = getattr(request.state, "user_id", None)
        return user_id if user_id else "anonymous"

    @staticmethod
    def get_demo_quality_settings(request: Request) -> dict[str, Any]:
        """Get demo quality settings based on user type"""
        demo_context = DemoService.get_demo_context(request)

        if not demo_context["is_demo"]:
            return {}

        from apps.demo.config import demo_config

        base_settings = {
            "success_rate": demo_config.DEMO_SUCCESS_RATE,
            "realistic_delays": demo_config.DEMO_REALISTIC_DELAYS,
            "error_simulation": demo_config.DEMO_ERROR_SIMULATION,
            "cache_enabled": demo_config.DEMO_CACHE_ENABLED,
            "quality_level": demo_config.get_demo_quality_level(),
        }

        # Adjust settings based on demo type
        demo_type = demo_context.get("demo_type", "standard")

        if demo_type == "showcase":
            # Best possible experience for showcase
            base_settings.update(
                {
                    "success_rate": 0.99,
                    "realistic_delays": False,  # Fast responses
                    "error_simulation": False,
                    "quality_level": "high",
                }
            )
        elif demo_type == "testing":
            # Include some errors for testing
            base_settings.update(
                {
                    "success_rate": 0.95,
                    "error_simulation": True,
                    "quality_level": "medium",
                }
            )
        elif demo_type == "limited":
            # Basic demo experience
            base_settings.update({"success_rate": 0.98, "quality_level": "basic"})

        return base_settings

    @staticmethod
    def log_demo_usage(request: Request, endpoint: str, action: str):
        """Log demo mode usage for monitoring and analytics"""
        if DemoService.is_demo_request(request):
            demo_context = DemoService.get_demo_context(request)
            logger.info(
                f"Demo showcase usage: endpoint={endpoint}, action={action}, "
                f"demo_type={demo_context['demo_type']}, "
                f"quality={demo_context['quality_level']}, "
                f"user_id={demo_context['demo_user_id']}"
            )

    @staticmethod
    def _detect_demo_from_request(request: Request) -> bool:
        """Manual demo detection fallback"""

        # Check URL path
        if str(request.url.path).startswith("/demo/"):
            return True

        # Check query parameters for demo indicators
        if request.query_params.get("demo") == "true":
            return True

        # Check for demo email in auth header (simplified)
        auth_header = request.headers.get("Authorization", "")
        if "demo" in auth_header.lower():
            return True

        return False


def is_demo_user_by_id(user_id: str | int) -> bool:
    """Check if user ID represents a demo user"""
    user_id_str = str(user_id)
    return user_id_str.startswith("demo_") or user_id_str in [
        "1",
        "demo",
        "showcase",
        "guest",
        "viewer",
    ]


def get_demo_type_from_user_id(user_id: str | int) -> str:
    """Extract demo type from user ID"""
    user_id_str = str(user_id)

    if "showcase" in user_id_str:
        return "showcase"
    elif "limited" in user_id_str or "viewer" in user_id_str:
        return "limited"
    elif "test" in user_id_str:
        return "testing"
    else:
        return "standard"


# Convenience instance
demo_service = DemoService()
