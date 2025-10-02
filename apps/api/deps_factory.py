"""
Dependency Factory - Configuration-driven service creation
Replaces direct mock imports with proper DI container usage
"""

import logging

from fastapi import Request

from apps.bot.models.twa import InitialDataResponse

logger = logging.getLogger(__name__)


async def get_demo_data_service():
    """
    Get demo data service based on configuration
    This replaces direct imports of mock services
    """
    try:
        # For now, return a simple fallback service
        # TODO: Implement proper DI container service resolution - PLACEHOLDER
        # For production: integrate with core DI container for proper service resolution
        # Current implementation uses demo config fallback pattern
        logger.info("Demo data service requested - using fallback implementation")

        from apps.demo.config import demo_config

        if demo_config.should_use_sample_service("demo_data"):
            from apps.demo.services.sample_data_service import SampleDataService

            return SampleDataService()
        else:
            raise ValueError("No demo data service available and not in demo mode")

    except Exception as e:
        logger.error(f"Failed to get demo data service: {e}")
        raise ValueError("Demo data service unavailable")


def is_request_for_demo_user(request: Request) -> bool:
    """
    Proper demo user detection that receives a Request object
    This fixes the architectural flaw of passing user_id instead of Request
    """
    return getattr(request.state, "is_demo", False)


def get_demo_type_from_request(request: Request) -> str | None:
    """
    Proper demo type extraction that receives a Request object
    This fixes the architectural flaw of passing user_id instead of Request
    """
    return getattr(request.state, "demo_type", None)


def get_demo_user_id_from_request(request: Request) -> str | None:
    """
    Get demo user ID from current request
    """
    return getattr(request.state, "demo_user_id", None)


async def get_initial_data_service(request: Request) -> InitialDataResponse:
    """
    Configuration-driven initial data service
    Routes to demo or real services based on demo mode detection
    """
    try:
        # Use clean demo mode service abstraction
        from apps.demo.services.demo_service import demo_service

        # Log demo usage for monitoring
        demo_service.log_demo_usage(request, "/initial-data", "fetch")

        # Check if this is a demo user request using proper Request object
        if demo_service.is_demo_request(request):
            demo_context = demo_service.get_demo_context(request)
            demo_data_service = await get_demo_data_service()

            user_id = demo_service.get_effective_user_id(request)
            demo_data = await demo_data_service.get_initial_data(user_id, demo_context["demo_type"])

            # Convert demo data dict to proper InitialDataResponse model
            from apps.bot.models.twa import Channel, User

            # Create demo user
            demo_user = User(id=1, username=demo_data.get("user", {}).get("username", "demo_user"))

            # Create demo channels
            demo_channels = []
            for channel_data in demo_data.get("channels", []):
                demo_channels.append(
                    Channel(
                        id=channel_data["id"],
                        title=channel_data["name"],
                        username=f"@{channel_data['name'].lower().replace(' ', '_')}",
                    )
                )

            return InitialDataResponse(
                user=demo_user,
                channels=demo_channels,
                scheduled_posts=[],  # Empty for demo
            )

        # For production users, use real services
        # This will be implemented with proper repository injection
        from apps.api.middleware.auth import get_current_user_id_from_request
        from apps.api.services.initial_data_service import get_real_initial_data

        user_id = await get_current_user_id_from_request(request)
        return await get_real_initial_data(user_id)

    except Exception as e:
        # ✅ FIXED: Comprehensive error handling with auditing
        from apps.api.services.database_error_handler import db_error_handler
        from apps.demo.services.demo_service import demo_service

        # Extract user_id if possible
        try:
            from apps.api.middleware.auth import get_current_user_id_from_request

            user_id = await get_current_user_id_from_request(request)
        except:
            user_id = None

        # Check if this is a demo user who can have fallback
        is_demo_user = demo_service.is_demo_request(request)

        # Handle the error with proper auditing
        try:
            db_error_handler.handle_database_error(
                request=request,
                error=e,
                operation="get_initial_data",
                user_id=user_id,
                allow_demo_fallback=is_demo_user,  # Only allow fallback for demo users
            )
        except Exception:
            # Error handler raised exception for real users
            raise

        # If we reach here, it means demo fallback is allowed
        if is_demo_user:
            logger.info(f"✅ Demo fallback activated for demo user {user_id}")
            demo_data_service = await get_demo_data_service()
            demo_data = await demo_data_service.get_initial_data(user_id or 1, "limited")

            # Convert to proper model for fallback case
            from apps.bot.models.twa import Channel, User

            demo_user = User(id=user_id or 1, username="demo_user_fallback")
            demo_channels = [Channel(id=1, title="Demo Channel", username="@demo")]

            return InitialDataResponse(user=demo_user, channels=demo_channels, scheduled_posts=[])

        # Should never reach here, but safety fallback
        raise Exception("Service temporarily unavailable")
