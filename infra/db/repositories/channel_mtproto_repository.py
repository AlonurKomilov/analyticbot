"""
Channel MTProto Settings Repository
Manages per-channel MTProto enable/disable settings
"""

from datetime import UTC, datetime

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.models.user_bot_orm import ChannelMTProtoSettings


class ChannelMTProtoRepository:
    """Repository for managing per-channel MTProto settings"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_setting(self, user_id: int, channel_id: int) -> ChannelMTProtoSettings | None:
        """
        Get MTProto setting for a specific user+channel combination.

        Args:
            user_id: User ID
            channel_id: Channel ID

        Returns:
            ChannelMTProtoSettings if exists, None otherwise
        """
        query = select(ChannelMTProtoSettings).where(
            and_(
                ChannelMTProtoSettings.user_id == user_id,
                ChannelMTProtoSettings.channel_id == channel_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_settings(self, user_id: int) -> list[ChannelMTProtoSettings]:
        """
        Get all channel MTProto settings for a user.

        Args:
            user_id: User ID

        Returns:
            List of all channel settings for the user
        """
        query = (
            select(ChannelMTProtoSettings)
            .where(ChannelMTProtoSettings.user_id == user_id)
            .order_by(ChannelMTProtoSettings.channel_id)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_or_update(
        self, user_id: int, channel_id: int, mtproto_enabled: bool
    ) -> ChannelMTProtoSettings:
        """
        Create or update per-channel MTProto setting.

        Args:
            user_id: User ID
            channel_id: Channel ID
            mtproto_enabled: Whether MTProto is enabled for this channel

        Returns:
            Created or updated ChannelMTProtoSettings
        """
        existing = await self.get_setting(user_id, channel_id)

        if existing:
            # Update existing
            existing.mtproto_enabled = mtproto_enabled
            existing.updated_at = datetime.now(UTC)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        else:
            # Create new
            setting = ChannelMTProtoSettings(
                user_id=user_id,
                channel_id=channel_id,
                mtproto_enabled=mtproto_enabled,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
            self.session.add(setting)
            await self.session.commit()
            await self.session.refresh(setting)
            return setting

    async def delete_setting(self, user_id: int, channel_id: int) -> bool:
        """
        Delete per-channel MTProto setting (reverts to default/global setting).

        Args:
            user_id: User ID
            channel_id: Channel ID

        Returns:
            True if deleted, False if not found
        """
        query = delete(ChannelMTProtoSettings).where(
            and_(
                ChannelMTProtoSettings.user_id == user_id,
                ChannelMTProtoSettings.channel_id == channel_id,
            )
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def delete_user_settings(self, user_id: int) -> int:
        """
        Delete all per-channel settings for a user.

        Args:
            user_id: User ID

        Returns:
            Number of settings deleted
        """
        query = delete(ChannelMTProtoSettings).where(ChannelMTProtoSettings.user_id == user_id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount

    async def is_channel_enabled(
        self, user_id: int, channel_id: int, global_enabled: bool = True
    ) -> bool:
        """
        Check if MTProto is enabled for a specific channel.

        Logic: global_enabled AND (channel_setting if exists else True)

        Args:
            user_id: User ID
            channel_id: Channel ID
            global_enabled: Global MTProto enabled flag from user_bot_credentials

        Returns:
            True if MTProto is enabled for this channel, False otherwise
        """
        if not global_enabled:
            # Global disabled overrides everything
            return False

        setting = await self.get_setting(user_id, channel_id)
        if setting is None:
            # No per-channel setting means default to enabled (if global is enabled)
            return True

        return setting.mtproto_enabled
