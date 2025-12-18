"""
Public Catalog Service

Business logic for managing the public channel catalog.
Handles fetching channel data from Telegram, caching, and database operations.
"""

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class PublicCatalogService:
    """
    Service for managing the public channel catalog.

    Responsibilities:
    - Fetch channel data from Telegram Bot API
    - Cache data in Redis (with DB fallback)
    - Sync channel stats periodically
    - Add/update/remove channels from catalog
    """

    def __init__(
        self,
        db_session: AsyncSession,
        bot_token: str | None = None,
        redis_client: Any = None,
    ):
        self.db = db_session
        self.bot_token = bot_token
        self.redis = redis_client
        self._bot = None

    async def _get_bot(self):
        """Get or create aiogram bot instance."""
        if self._bot is None and self.bot_token:
            try:
                from aiogram import Bot

                self._bot = Bot(token=self.bot_token)
            except ImportError:
                logger.error("aiogram not installed")
                return None
        return self._bot

    # =========================================================================
    # Telegram API Methods
    # =========================================================================

    async def fetch_channel_from_telegram(self, username: str) -> dict[str, Any] | None:
        """
        Fetch channel info directly from Telegram Bot API.

        Args:
            username: Channel username (without @)

        Returns:
            Channel info dict or None if not found
        """
        bot = await self._get_bot()
        if not bot:
            logger.warning("No bot available for Telegram API calls")
            return None

        try:
            # Clean username
            clean_username = username.lstrip("@")

            # Get chat info
            chat = await bot.get_chat(chat_id=f"@{clean_username}")

            # Get member count
            try:
                member_count = await bot.get_chat_member_count(chat_id=chat.id)
            except Exception:
                member_count = None

            # Get chat photo URL if available
            avatar_url = None
            if chat.photo:
                try:
                    # Get file info for the small photo
                    file = await bot.get_file(chat.photo.small_file_id)
                    avatar_url = (
                        f"https://api.telegram.org/file/bot{self.bot_token}/{file.file_path}"
                    )
                except Exception as e:
                    logger.debug(f"Could not get avatar URL: {e}")

            return {
                "telegram_id": chat.id,
                "username": chat.username,
                "title": chat.title or clean_username,
                "description": getattr(chat, "description", None),
                "avatar_url": avatar_url,
                "subscriber_count": member_count,
                "type": chat.type,
                "success": True,
            }
        except Exception as e:
            logger.error(f"Failed to fetch channel @{username} from Telegram: {e}")
            return None

    async def resolve_username(self, username: str) -> int | None:
        """
        Resolve a username to a Telegram ID.

        Args:
            username: Channel username

        Returns:
            Telegram ID or None if not found
        """
        info = await self.fetch_channel_from_telegram(username)
        return info["telegram_id"] if info else None

    # =========================================================================
    # Catalog Management Methods
    # =========================================================================

    async def add_channel_to_catalog(
        self,
        telegram_id: int | None = None,
        username: str | None = None,
        category_id: int | None = None,
        country_code: str | None = None,
        language_code: str | None = None,
        added_by: int | None = None,
        is_featured: bool = False,
    ) -> dict[str, Any]:
        """
        Add a channel to the public catalog.

        Either telegram_id or username must be provided.
        If only username is provided, it will be resolved via Telegram API.
        """
        # Resolve username to telegram_id if needed
        if not telegram_id and username:
            info = await self.fetch_channel_from_telegram(username)
            if not info:
                return {
                    "success": False,
                    "error": f"Channel @{username} not found on Telegram",
                }
            telegram_id = info["telegram_id"]
            username = info.get("username")
            title = info.get("title", username)
            description = info.get("description")
            avatar_url = info.get("avatar_url")
            subscriber_count = info.get("subscriber_count")
        elif telegram_id:
            # Fetch info by ID
            bot = await self._get_bot()
            if bot:
                try:
                    chat = await bot.get_chat(chat_id=telegram_id)
                    username = chat.username
                    title = chat.title or str(telegram_id)
                    description = getattr(chat, "description", None)
                    avatar_url = None
                    subscriber_count = await bot.get_chat_member_count(chat_id=telegram_id)
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Channel {telegram_id} not accessible: {e}",
                    }
            else:
                return {"success": False, "error": "Bot not configured"}
        else:
            return {
                "success": False,
                "error": "Either telegram_id or username is required",
            }

        try:
            # Check if already exists
            existing = await self.db.execute(
                text("SELECT id FROM public_channel_catalog WHERE telegram_id = :tid"),
                {"tid": telegram_id},
            )
            if existing.fetchone():
                return {"success": False, "error": "Channel already in catalog"}

            # Insert into catalog
            result = await self.db.execute(
                text(
                    """
                    INSERT INTO public_channel_catalog 
                    (telegram_id, username, title, description, avatar_url, category_id, 
                     country_code, language_code, is_featured, is_verified, is_active, 
                     added_by, last_synced_at, metadata)
                    VALUES (:telegram_id, :username, :title, :description, :avatar_url, 
                            :category_id, :country_code, :language_code, :is_featured, 
                            :is_verified, :is_active, :added_by, NOW(), :metadata)
                    RETURNING id
                """
                ),
                {
                    "telegram_id": telegram_id,
                    "username": username,
                    "title": title,
                    "description": description,
                    "avatar_url": avatar_url,
                    "category_id": category_id,
                    "country_code": country_code,
                    "language_code": language_code,
                    "is_featured": is_featured,
                    "is_verified": False,  # Not verified by default
                    "is_active": True,  # Active by default
                    "added_by": added_by,
                    "metadata": "{}",  # Empty JSON object
                },
            )
            row = result.fetchone()
            catalog_id = row[0] if row else None

            # Insert stats cache
            if subscriber_count:
                await self.db.execute(
                    text(
                        """
                        INSERT INTO channel_stats_cache (telegram_id, subscriber_count, cached_at)
                        VALUES (:tid, :count, NOW())
                        ON CONFLICT (telegram_id) DO UPDATE 
                        SET subscriber_count = :count, cached_at = NOW()
                    """
                    ),
                    {"tid": telegram_id, "count": subscriber_count},
                )

            # Update category channel count
            if category_id:
                await self.db.execute(
                    text(
                        """
                        UPDATE channel_categories 
                        SET channel_count = channel_count + 1 
                        WHERE id = :cid
                    """
                    ),
                    {"cid": category_id},
                )

            await self.db.commit()

            return {
                "success": True,
                "catalog_id": catalog_id,
                "telegram_id": telegram_id,
                "username": username,
                "title": title,
            }
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to add channel to catalog: {e}")
            return {"success": False, "error": str(e)}

    async def update_channel(
        self,
        catalog_id: int,
        category_id: int | None = None,
        country_code: str | None = None,
        language_code: str | None = None,
        is_featured: bool | None = None,
        is_verified: bool | None = None,
        is_active: bool | None = None,
    ) -> dict[str, Any]:
        """Update a channel in the catalog."""
        try:
            updates = []
            params = {"id": catalog_id}

            if category_id is not None:
                updates.append("category_id = :category_id")
                params["category_id"] = category_id
            if country_code is not None:
                updates.append("country_code = :country_code")
                params["country_code"] = country_code
            if language_code is not None:
                updates.append("language_code = :language_code")
                params["language_code"] = language_code
            if is_featured is not None:
                updates.append("is_featured = :is_featured")
                params["is_featured"] = is_featured
            if is_verified is not None:
                updates.append("is_verified = :is_verified")
                params["is_verified"] = is_verified
            if is_active is not None:
                updates.append("is_active = :is_active")
                params["is_active"] = is_active

            if not updates:
                return {"success": False, "error": "No updates provided"}

            await self.db.execute(
                text(f"UPDATE public_channel_catalog SET {', '.join(updates)} WHERE id = :id"),
                params,
            )
            await self.db.commit()

            return {"success": True, "catalog_id": catalog_id}
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update channel: {e}")
            return {"success": False, "error": str(e)}

    async def remove_channel(self, catalog_id: int) -> dict[str, Any]:
        """Remove a channel from the catalog (soft delete)."""
        try:
            # Get category_id before deactivating
            result = await self.db.execute(
                text("SELECT category_id FROM public_channel_catalog WHERE id = :id"),
                {"id": catalog_id},
            )
            row = result.fetchone()
            category_id = row[0] if row else None

            # Soft delete
            await self.db.execute(
                text("UPDATE public_channel_catalog SET is_active = FALSE WHERE id = :id"),
                {"id": catalog_id},
            )

            # Update category count
            if category_id:
                await self.db.execute(
                    text(
                        """
                        UPDATE channel_categories 
                        SET channel_count = GREATEST(0, channel_count - 1) 
                        WHERE id = :cid
                    """
                    ),
                    {"cid": category_id},
                )

            await self.db.commit()
            return {"success": True, "catalog_id": catalog_id}
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to remove channel: {e}")
            return {"success": False, "error": str(e)}

    async def sync_channel_stats(self, telegram_id: int) -> dict[str, Any]:
        """
        Sync channel stats from Telegram API.

        Updates the channel_stats_cache table with fresh data.
        """
        bot = await self._get_bot()
        if not bot:
            return {"success": False, "error": "Bot not configured"}

        try:
            # Get fresh member count
            member_count = await bot.get_chat_member_count(chat_id=telegram_id)

            # Update stats cache
            await self.db.execute(
                text(
                    """
                    INSERT INTO channel_stats_cache (telegram_id, subscriber_count, cached_at)
                    VALUES (:tid, :count, NOW())
                    ON CONFLICT (telegram_id) DO UPDATE 
                    SET subscriber_count = :count, cached_at = NOW()
                """
                ),
                {"tid": telegram_id, "count": member_count},
            )

            # Update last_synced_at in catalog
            await self.db.execute(
                text(
                    """
                    UPDATE public_channel_catalog 
                    SET last_synced_at = NOW() 
                    WHERE telegram_id = :tid
                """
                ),
                {"tid": telegram_id},
            )

            await self.db.commit()

            return {
                "success": True,
                "telegram_id": telegram_id,
                "subscriber_count": member_count,
            }
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to sync channel {telegram_id}: {e}")
            return {"success": False, "error": str(e)}

    async def get_catalog_entry(self, catalog_id: int) -> dict[str, Any] | None:
        """Get a catalog entry by ID."""
        try:
            result = await self.db.execute(
                text(
                    """
                    SELECT pcc.*, csc.subscriber_count, csc.avg_views, csc.growth_rate,
                           cc.name as category_name, cc.slug as category_slug
                    FROM public_channel_catalog pcc
                    LEFT JOIN channel_stats_cache csc ON pcc.telegram_id = csc.telegram_id
                    LEFT JOIN channel_categories cc ON pcc.category_id = cc.id
                    WHERE pcc.id = :id
                """
                ),
                {"id": catalog_id},
            )
            row = result.fetchone()
            if not row:
                return None
            return dict(row._mapping)
        except Exception as e:
            logger.error(f"Failed to get catalog entry: {e}")
            return None
