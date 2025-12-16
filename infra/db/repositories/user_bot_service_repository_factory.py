"""
User Bot Moderation Repository Factory - Creates repositories with fresh sessions
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.models.user_bot_service_domain import (
    BannedWord,
    ChatSettings,
    InviteRecord,
    InviteStats,
    MessageType,
    ModerationLogEntry,
    Warning,
    WelcomeMessage,
)

from .user_bot_service_repository import UserBotServiceRepository


class UserBotServiceRepositoryFactory:
    """
    Repository factory that creates fresh sessions for each operation

    This ensures proper session lifecycle management for moderation operations.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Initialize repository factory

        Args:
            session_factory: SQLAlchemy async session factory
        """
        self.session_factory = session_factory

    # ===========================================
    # Chat Settings
    # ===========================================

    async def get_chat_settings(
        self, user_id: int, chat_id: int
    ) -> ChatSettings | None:
        """Get settings for a specific chat."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            return await repo.get_chat_settings(user_id, chat_id)

    async def get_user_chat_settings(self, user_id: int) -> list[ChatSettings]:
        """Get all chat settings for a user."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            return await repo.get_user_chat_settings(user_id)

    async def create_chat_settings(self, settings: ChatSettings) -> ChatSettings:
        """Create settings for a chat."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.create_chat_settings(settings)
            await session.commit()
            return result

    async def update_chat_settings(self, settings: ChatSettings) -> ChatSettings:
        """Update settings for a chat."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.update_chat_settings(settings)
            await session.commit()
            return result

    async def delete_chat_settings(self, user_id: int, chat_id: int) -> bool:
        """Delete settings for a chat."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.delete_chat_settings(user_id, chat_id)
            await session.commit()
            return result

    # ===========================================
    # Banned Words
    # ===========================================

    async def get_banned_words(self, user_id: int, chat_id: int) -> list[BannedWord]:
        """Get banned words for a chat."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            return await repo.get_banned_words(user_id, chat_id)

    async def add_banned_word(self, banned_word: BannedWord) -> BannedWord:
        """Add a banned word."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.add_banned_word(banned_word)
            await session.commit()
            return result

    async def remove_banned_word(self, word_id: int, user_id: int) -> bool:
        """Remove a banned word."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.remove_banned_word(word_id, user_id)
            await session.commit()
            return result

    # ===========================================
    # Warnings
    # ===========================================

    async def get_user_warnings(
        self, user_id: int, chat_id: int, warned_user_id: int
    ) -> list[Warning]:
        """Get warnings for a user in a chat."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            return await repo.get_user_warnings(user_id, chat_id, warned_user_id)

    async def add_warning(self, warning: Warning) -> Warning:
        """Add a warning."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.add_warning(warning)
            await session.commit()
            return result

    async def get_warning_count(
        self, user_id: int, chat_id: int, warned_user_id: int
    ) -> int:
        """Get warning count for a user."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            return await repo.get_warning_count(user_id, chat_id, warned_user_id)

    async def clear_warnings(
        self, user_id: int, chat_id: int, warned_user_id: int
    ) -> bool:
        """Clear warnings for a user."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.clear_warnings(user_id, chat_id, warned_user_id)
            await session.commit()
            return result

    # ===========================================
    # Welcome Messages
    # ===========================================

    async def get_welcome_message(
        self, user_id: int, chat_id: int, message_type: MessageType = MessageType.WELCOME
    ) -> WelcomeMessage | None:
        """Get welcome message for a chat."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            return await repo.get_welcome_message(user_id, chat_id, message_type)

    async def set_welcome_message(
        self, welcome_message: WelcomeMessage
    ) -> WelcomeMessage:
        """Set welcome message for a chat."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.set_welcome_message(welcome_message)
            await session.commit()
            return result

    async def delete_welcome_message(self, user_id: int, chat_id: int) -> bool:
        """Delete welcome message for a chat."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.delete_welcome_message(user_id, chat_id)
            await session.commit()
            return result

    # ===========================================
    # Invite Tracking
    # ===========================================

    async def record_invite(self, invite: InviteRecord) -> InviteRecord:
        """Record an invite."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.record_invite(invite)
            await session.commit()
            return result

    async def get_invite_stats(
        self, user_id: int, chat_id: int
    ) -> list[InviteStats]:
        """Get invite statistics."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            return await repo.get_invite_stats(user_id, chat_id)

    # ===========================================
    # Moderation Log
    # ===========================================

    async def log_action(self, log_entry: ModerationLogEntry) -> ModerationLogEntry:
        """Log a moderation action."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            result = await repo.log_action(log_entry)
            await session.commit()
            return result

    async def get_moderation_log(
        self, user_id: int, chat_id: int, limit: int = 50, offset: int = 0
    ) -> list[ModerationLogEntry]:
        """Get moderation log for a chat."""
        async with self.session_factory() as session:
            repo = UserBotServiceRepository(session)
            return await repo.get_moderation_log(user_id, chat_id, limit, offset)
