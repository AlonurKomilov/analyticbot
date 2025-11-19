"""
Webhook Manager for Multi-Tenant Bot System
Manages webhook setup and validation for user bots
"""

import logging
import secrets
from typing import Optional

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

logger = logging.getLogger(__name__)


class WebhookManager:
    """
    Manages Telegram webhook configuration for user bots
    
    Features:
    - Setup webhooks with unique secrets per bot
    - Remove webhooks (fallback to polling)
    - Validate webhook configuration
    - Support for single domain with multiple user paths
    """

    def __init__(self, base_url: str):
        """
        Initialize webhook manager
        
        Args:
            base_url: Base URL for webhooks (e.g., "https://bot.analyticbot.org")
        """
        self.base_url = base_url.rstrip("/")  # Remove trailing slash
        logger.info(f"WebhookManager initialized with base URL: {self.base_url}")

    def generate_webhook_secret(self) -> str:
        """
        Generate a secure random webhook secret token
        
        Returns:
            32-character URL-safe random string
        """
        return secrets.token_urlsafe(32)

    def get_webhook_url(self, user_id: int) -> str:
        """
        Get webhook URL for specific user
        
        Args:
            user_id: User ID
            
        Returns:
            Full webhook URL (e.g., "https://bot.analyticbot.org/webhook/123")
        """
        return f"{self.base_url}/webhook/{user_id}"

    async def setup_webhook(
        self,
        bot_token: str,
        user_id: int,
        webhook_secret: Optional[str] = None,
        drop_pending_updates: bool = True,
    ) -> dict:
        """
        Configure webhook for user's bot
        
        Args:
            bot_token: Telegram bot token
            user_id: User ID
            webhook_secret: Optional webhook secret (generates new if not provided)
            drop_pending_updates: Whether to drop pending updates
            
        Returns:
            Dictionary with setup results:
            - success: bool
            - webhook_url: str
            - webhook_secret: str
            - message: str
            - error: Optional[str]
        """
        # Generate secret if not provided
        if not webhook_secret:
            webhook_secret = self.generate_webhook_secret()

        webhook_url = self.get_webhook_url(user_id)

        try:
            # Create temporary bot instance for webhook setup
            # Use session with timeout for webhook configuration
            session = AiohttpSession()
            bot = Bot(token=bot_token, session=session)

            try:
                # Set webhook with Telegram
                success = await bot.set_webhook(
                    url=webhook_url,
                    secret_token=webhook_secret,
                    allowed_updates=[
                        "message",
                        "edited_message",
                        "channel_post",
                        "edited_channel_post",
                        "inline_query",
                        "chosen_inline_result",
                        "callback_query",
                        "shipping_query",
                        "pre_checkout_query",
                        "poll",
                        "poll_answer",
                        "my_chat_member",
                        "chat_member",
                        "chat_join_request",
                    ],
                    drop_pending_updates=drop_pending_updates,
                    max_connections=100,  # Allow more concurrent connections
                )

                if success:
                    logger.info(
                        f"✅ Webhook configured successfully for user {user_id}: {webhook_url}"
                    )
                    return {
                        "success": True,
                        "webhook_url": webhook_url,
                        "webhook_secret": webhook_secret,
                        "message": f"Webhook configured at {webhook_url}",
                    }
                else:
                    logger.error(f"❌ Failed to set webhook for user {user_id}")
                    return {
                        "success": False,
                        "webhook_url": webhook_url,
                        "webhook_secret": webhook_secret,
                        "message": "Telegram API returned false",
                        "error": "webhook_setup_failed",
                    }

            finally:
                # Always close the bot session
                await bot.session.close()

        except Exception as e:
            logger.error(f"❌ Error setting up webhook for user {user_id}: {e}")
            return {
                "success": False,
                "webhook_url": webhook_url,
                "webhook_secret": webhook_secret if webhook_secret else "",
                "message": f"Error: {str(e)}",
                "error": str(e),
            }

    async def remove_webhook(
        self, bot_token: str, user_id: int, drop_pending_updates: bool = False
    ) -> dict:
        """
        Remove webhook configuration (switch to polling mode)
        
        Args:
            bot_token: Telegram bot token
            user_id: User ID
            drop_pending_updates: Whether to drop pending updates
            
        Returns:
            Dictionary with removal results:
            - success: bool
            - message: str
            - error: Optional[str]
        """
        try:
            # Create temporary bot instance
            session = AiohttpSession()
            bot = Bot(token=bot_token, session=session)

            try:
                success = await bot.delete_webhook(drop_pending_updates=drop_pending_updates)

                if success:
                    logger.info(f"✅ Webhook removed for user {user_id}")
                    return {"success": True, "message": "Webhook removed successfully"}
                else:
                    logger.error(f"❌ Failed to remove webhook for user {user_id}")
                    return {
                        "success": False,
                        "message": "Telegram API returned false",
                        "error": "webhook_removal_failed",
                    }

            finally:
                await bot.session.close()

        except Exception as e:
            logger.error(f"❌ Error removing webhook for user {user_id}: {e}")
            return {"success": False, "message": f"Error: {str(e)}", "error": str(e)}

    async def get_webhook_info(self, bot_token: str, user_id: int) -> dict:
        """
        Get current webhook configuration from Telegram
        
        Args:
            bot_token: Telegram bot token
            user_id: User ID
            
        Returns:
            Dictionary with webhook info or error
        """
        try:
            session = AiohttpSession()
            bot = Bot(token=bot_token, session=session)

            try:
                webhook_info = await bot.get_webhook_info()

                return {
                    "success": True,
                    "url": webhook_info.url,
                    "has_custom_certificate": webhook_info.has_custom_certificate,
                    "pending_update_count": webhook_info.pending_update_count,
                    "ip_address": webhook_info.ip_address,
                    "last_error_date": webhook_info.last_error_date,
                    "last_error_message": webhook_info.last_error_message,
                    "last_synchronization_error_date": webhook_info.last_synchronization_error_date,
                    "max_connections": webhook_info.max_connections,
                    "allowed_updates": webhook_info.allowed_updates,
                }

            finally:
                await bot.session.close()

        except Exception as e:
            logger.error(f"❌ Error getting webhook info for user {user_id}: {e}")
            return {"success": False, "error": str(e), "message": f"Error: {str(e)}"}

    def validate_webhook_secret(self, provided_secret: str, expected_secret: str) -> bool:
        """
        Validate webhook secret token using constant-time comparison
        
        Args:
            provided_secret: Secret from request header
            expected_secret: Expected secret from database
            
        Returns:
            True if secrets match, False otherwise
        """
        if not provided_secret or not expected_secret:
            return False

        # Use constant-time comparison to prevent timing attacks
        return secrets.compare_digest(provided_secret, expected_secret)


# Global instance (initialized by DI container)
_webhook_manager: Optional[WebhookManager] = None


def init_webhook_manager(base_url: str) -> WebhookManager:
    """
    Initialize global WebhookManager instance
    
    Args:
        base_url: Base URL for webhooks
        
    Returns:
        WebhookManager instance
    """
    global _webhook_manager
    _webhook_manager = WebhookManager(base_url)
    return _webhook_manager


def get_webhook_manager() -> WebhookManager:
    """
    Get global WebhookManager instance
    
    Returns:
        WebhookManager instance
        
    Raises:
        RuntimeError: If not initialized
    """
    if _webhook_manager is None:
        raise RuntimeError(
            "WebhookManager not initialized. Call init_webhook_manager() first or use DI container."
        )
    return _webhook_manager
