"""
Webhook Router for Multi-Tenant Bot System
Receives and processes Telegram webhook updates for user bots
"""

import logging
from typing import Annotated

from aiogram.types import Update
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from apps.bot.multi_tenant.webhook_manager import get_webhook_manager
from apps.di import get_container
from core.ports.user_bot_repository import IUserBotRepository

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/webhook",
    tags=["Telegram Webhooks"],
)


# ==================== Dependency Injection ====================


async def get_user_bot_repository() -> IUserBotRepository:
    """Get user bot repository from DI container."""
    container = get_container()
    return await container.database.user_bot_repo()


async def get_bot_manager():
    """Get bot manager from DI container."""
    container = get_container()
    return await container.bot.bot_manager()


# ==================== Webhook Endpoints ====================


@router.post(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Update processed successfully"},
        401: {"description": "Invalid webhook secret"},
        404: {"description": "Bot not found or webhook not configured"},
        500: {"description": "Internal server error"},
    },
)
async def receive_telegram_webhook(
    user_id: int,
    request: Request,
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)] = None,
    bot_manager=Depends(get_bot_manager),
):
    """
    Receive Telegram webhook updates for user's bot
    
    Called by Telegram when a user sends a message to the bot.
    
    Args:
        user_id: User ID (from URL path)
        request: FastAPI request object
        x_telegram_bot_api_secret_token: Webhook secret from Telegram headers
        repository: User bot repository
        bot_manager: Bot manager instance
        
    Returns:
        {"ok": True} on success
        
    Raises:
        HTTPException: On validation or processing errors
    """
    # 1. Get user's bot credentials
    try:
        credentials = await repository.get_by_user_id(user_id)
    except Exception as e:
        logger.error(f"Error fetching credentials for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bot credentials",
        )

    if not credentials:
        logger.warning(f"Webhook received for non-existent user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found for this user"
        )

    # 2. Check if webhook is enabled for this user
    if not getattr(credentials, "webhook_enabled", False):
        logger.warning(
            f"Webhook received for user {user_id} but webhook not enabled in database"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not configured for this bot",
        )

    # 3. Validate webhook secret
    expected_secret = getattr(credentials, "webhook_secret", None)
    if not expected_secret:
        logger.error(f"No webhook secret found for user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured",
        )

    webhook_manager = get_webhook_manager()
    if not webhook_manager.validate_webhook_secret(
        x_telegram_bot_api_secret_token or "", expected_secret
    ):
        logger.warning(
            f"Invalid webhook secret for user {user_id} from IP {request.client.host}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook secret"
        )

    # 4. Parse update from request body
    try:
        update_data = await request.json()
        update = Update(**update_data)
    except Exception as e:
        logger.error(f"Failed to parse update for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid update format"
        )

    # 5. Get bot instance from manager
    try:
        bot_instance = await bot_manager.get_user_bot(user_id)
    except ValueError as e:
        logger.error(f"Failed to get bot instance for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bot instance not available"
        )
    except Exception as e:
        logger.error(f"Error getting bot instance for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get bot instance",
        )

    # 6. Process update through dispatcher
    try:
        if not bot_instance.bot or not bot_instance.dp:
            logger.error(f"Bot or dispatcher not initialized for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bot not properly initialized",
            )

        # Feed update to dispatcher for processing
        await bot_instance.dp.feed_update(bot_instance.bot, update)

        logger.debug(f"✅ Processed webhook update for user {user_id}")
        return {"ok": True}

    except Exception as e:
        logger.error(f"Error processing update for user {user_id}: {e}")
        # Return 200 to Telegram even on processing errors
        # to prevent webhook from being disabled
        return {"ok": True, "error": "processing_failed"}


@router.get(
    "/{user_id}/info",
    responses={
        200: {"description": "Webhook information"},
        404: {"description": "Bot not found"},
    },
)
async def get_webhook_status(
    user_id: int,
    repository: Annotated[IUserBotRepository, Depends(get_user_bot_repository)] = None,
):
    """
    Get webhook configuration status for user's bot
    
    Args:
        user_id: User ID
        repository: User bot repository
        
    Returns:
        Webhook status information
        
    Raises:
        HTTPException: If bot not found
    """
    credentials = await repository.get_by_user_id(user_id)

    if not credentials:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    return {
        "user_id": user_id,
        "webhook_enabled": getattr(credentials, "webhook_enabled", False),
        "webhook_url": getattr(credentials, "webhook_url", None),
        "bot_username": credentials.bot_username,
        "bot_status": credentials.status.value,
    }


@router.post(
    "/{user_id}/test",
    responses={
        200: {"description": "Test message sent"},
        404: {"description": "Bot not found"},
    },
)
async def test_webhook(
    user_id: int,
    bot_manager=Depends(get_bot_manager),
):
    """
    Test webhook by sending a message from bot
    (For debugging purposes)
    
    Args:
        user_id: User ID
        bot_manager: Bot manager instance
        
    Returns:
        Test result
    """
    try:
        bot_instance = await bot_manager.get_user_bot(user_id)

        # Get bot info to verify it's working
        bot_info = await bot_instance.get_bot_info()

        return {
            "success": True,
            "message": "Bot is accessible",
            "bot_info": bot_info,
        }

    except Exception as e:
        logger.error(f"Error testing webhook for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test failed: {str(e)}",
        )
