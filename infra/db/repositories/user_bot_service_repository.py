"""
User Bot Moderation Repository Implementation

Repository for managing user bot moderation features:
- Chat settings
- Banned words
- Invite tracking
- Warnings
- Moderation logs
- Welcome messages
"""

from datetime import datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user_bot_service_domain import (
    BannedWord,
    ChatSettings,
    ChatType,
    InviteRecord,
    InviteStats,
    MessageType,
    ModerationAction,
    ModerationLogEntry,
    PerformedBy,
    Warning,
    WarningType,
    WelcomeMessage,
)
from infra.db.models.user_bot_service_orm import (
    UserBotBannedWordORM,
    UserBotInviteTrackingORM,
    UserBotServiceLogORM,
    UserBotSettingsORM,
    UserBotWarningORM,
    UserBotWelcomeMessageORM,
)


class UserBotServiceRepository:
    """Repository for user bot moderation features."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ===========================================
    # Chat Settings
    # ===========================================

    async def get_chat_settings(self, user_id: int, chat_id: int) -> ChatSettings | None:
        """Get settings for a specific chat."""
        result = await self.session.execute(
            select(UserBotSettingsORM).where(
                UserBotSettingsORM.user_id == user_id,
                UserBotSettingsORM.chat_id == chat_id,
            )
        )
        orm = result.scalar_one_or_none()
        return self._settings_to_domain(orm) if orm else None

    async def get_user_chat_settings(self, user_id: int) -> list[ChatSettings]:
        """Get all chat settings for a user."""
        result = await self.session.execute(
            select(UserBotSettingsORM).where(UserBotSettingsORM.user_id == user_id)
        )
        return [self._settings_to_domain(orm) for orm in result.scalars().all()]

    async def create_chat_settings(self, settings: ChatSettings) -> ChatSettings:
        """Create settings for a chat."""
        orm = UserBotSettingsORM(
            user_id=settings.user_id,
            chat_id=settings.chat_id,
            chat_type=settings.chat_type.value,
            chat_title=settings.chat_title,
            clean_join_messages=settings.clean_join_messages,
            clean_leave_messages=settings.clean_leave_messages,
            banned_words_enabled=settings.banned_words_enabled,
            anti_spam_enabled=settings.anti_spam_enabled,
            anti_link_enabled=settings.anti_link_enabled,
            anti_forward_enabled=settings.anti_forward_enabled,
            welcome_enabled=settings.welcome_enabled,
            invite_tracking_enabled=settings.invite_tracking_enabled,
            captcha_enabled=settings.captcha_enabled,
            slow_mode_enabled=settings.slow_mode_enabled,
            night_mode_enabled=settings.night_mode_enabled,
            spam_action=settings.spam_action.value,
            max_warnings=settings.max_warnings,
            warning_action=settings.warning_action.value,
            mute_duration_minutes=settings.mute_duration_minutes,
            flood_limit=settings.flood_limit,
            flood_interval_seconds=settings.flood_interval_seconds,
            night_mode_start_hour=settings.night_mode_start_hour,
            night_mode_end_hour=settings.night_mode_end_hour,
            night_mode_timezone=settings.night_mode_timezone,
            whitelisted_users=settings.whitelisted_users,
            admin_users=settings.admin_users,
        )
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._settings_to_domain(orm)

    async def update_chat_settings(self, settings: ChatSettings) -> ChatSettings:
        """Update settings for a chat."""
        result = await self.session.execute(
            select(UserBotSettingsORM).where(
                UserBotSettingsORM.user_id == settings.user_id,
                UserBotSettingsORM.chat_id == settings.chat_id,
            )
        )
        orm = result.scalar_one()

        # Update all fields
        orm.chat_type = settings.chat_type.value
        orm.chat_title = settings.chat_title
        orm.clean_join_messages = settings.clean_join_messages
        orm.clean_leave_messages = settings.clean_leave_messages
        orm.banned_words_enabled = settings.banned_words_enabled
        orm.anti_spam_enabled = settings.anti_spam_enabled
        orm.anti_link_enabled = settings.anti_link_enabled
        orm.anti_forward_enabled = settings.anti_forward_enabled
        orm.welcome_enabled = settings.welcome_enabled
        orm.invite_tracking_enabled = settings.invite_tracking_enabled
        orm.captcha_enabled = settings.captcha_enabled
        orm.slow_mode_enabled = settings.slow_mode_enabled
        orm.night_mode_enabled = settings.night_mode_enabled
        orm.spam_action = settings.spam_action.value
        orm.max_warnings = settings.max_warnings
        orm.warning_action = settings.warning_action.value
        orm.mute_duration_minutes = settings.mute_duration_minutes
        orm.flood_limit = settings.flood_limit
        orm.flood_interval_seconds = settings.flood_interval_seconds
        orm.night_mode_start_hour = settings.night_mode_start_hour
        orm.night_mode_end_hour = settings.night_mode_end_hour
        orm.night_mode_timezone = settings.night_mode_timezone
        orm.whitelisted_users = settings.whitelisted_users
        orm.admin_users = settings.admin_users
        orm.updated_at = datetime.now()

        await self.session.flush()
        await self.session.refresh(orm)
        return self._settings_to_domain(orm)

    async def upsert_chat_settings(self, settings: ChatSettings) -> ChatSettings:
        """Create or update chat settings."""
        existing = await self.get_chat_settings(settings.user_id, settings.chat_id)
        if existing:
            settings.id = existing.id
            return await self.update_chat_settings(settings)
        return await self.create_chat_settings(settings)

    async def delete_chat_settings(self, user_id: int, chat_id: int) -> bool:
        """Delete settings for a chat."""
        result = await self.session.execute(
            delete(UserBotSettingsORM).where(
                UserBotSettingsORM.user_id == user_id,
                UserBotSettingsORM.chat_id == chat_id,
            )
        )
        return result.rowcount > 0

    def _settings_to_domain(self, orm: UserBotSettingsORM) -> ChatSettings:
        """Convert ORM to domain model."""
        return ChatSettings(
            id=orm.id,
            user_id=orm.user_id,
            chat_id=orm.chat_id,
            chat_type=ChatType(orm.chat_type),
            chat_title=orm.chat_title,
            clean_join_messages=orm.clean_join_messages,
            clean_leave_messages=orm.clean_leave_messages,
            banned_words_enabled=orm.banned_words_enabled,
            anti_spam_enabled=orm.anti_spam_enabled,
            anti_link_enabled=orm.anti_link_enabled,
            anti_forward_enabled=orm.anti_forward_enabled,
            welcome_enabled=orm.welcome_enabled,
            invite_tracking_enabled=orm.invite_tracking_enabled,
            captcha_enabled=orm.captcha_enabled,
            slow_mode_enabled=orm.slow_mode_enabled,
            night_mode_enabled=orm.night_mode_enabled,
            spam_action=ModerationAction(orm.spam_action),
            max_warnings=orm.max_warnings,
            warning_action=ModerationAction(orm.warning_action),
            mute_duration_minutes=orm.mute_duration_minutes,
            flood_limit=orm.flood_limit,
            flood_interval_seconds=orm.flood_interval_seconds,
            night_mode_start_hour=orm.night_mode_start_hour,
            night_mode_end_hour=orm.night_mode_end_hour,
            night_mode_timezone=orm.night_mode_timezone or "UTC",
            whitelisted_users=orm.whitelisted_users or [],
            admin_users=orm.admin_users or [],
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    # ===========================================
    # Banned Words
    # ===========================================

    async def get_banned_words(self, user_id: int, chat_id: int | None = None) -> list[BannedWord]:
        """Get banned words for a user/chat."""
        query = select(UserBotBannedWordORM).where(
            UserBotBannedWordORM.user_id == user_id,
            UserBotBannedWordORM.is_active == True,
        )
        if chat_id is not None:
            # Get words for specific chat + global words (chat_id is NULL)
            query = query.where(
                (UserBotBannedWordORM.chat_id == chat_id) | (UserBotBannedWordORM.chat_id.is_(None))
            )

        result = await self.session.execute(query)
        return [self._banned_word_to_domain(orm) for orm in result.scalars().all()]

    async def add_banned_word(self, word: BannedWord) -> BannedWord:
        """Add a banned word."""
        orm = UserBotBannedWordORM(
            user_id=word.user_id,
            chat_id=word.chat_id,
            word=word.word,
            is_regex=word.is_regex,
            action=word.action.value,
            is_active=word.is_active,
        )
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._banned_word_to_domain(orm)

    async def remove_banned_word(self, word_id: int) -> bool:
        """Remove (deactivate) a banned word."""
        result = await self.session.execute(
            update(UserBotBannedWordORM)
            .where(UserBotBannedWordORM.id == word_id)
            .values(is_active=False)
        )
        return result.rowcount > 0

    async def delete_banned_word(self, word_id: int) -> bool:
        """Permanently delete a banned word."""
        result = await self.session.execute(
            delete(UserBotBannedWordORM).where(UserBotBannedWordORM.id == word_id)
        )
        return result.rowcount > 0

    def _banned_word_to_domain(self, orm: UserBotBannedWordORM) -> BannedWord:
        """Convert ORM to domain model."""
        return BannedWord(
            id=orm.id,
            user_id=orm.user_id,
            chat_id=orm.chat_id,
            word=orm.word,
            is_regex=orm.is_regex,
            action=ModerationAction(orm.action),
            is_active=orm.is_active,
            created_at=orm.created_at,
        )

    # ===========================================
    # Invite Tracking
    # ===========================================

    async def track_invite(self, record: InviteRecord) -> InviteRecord:
        """Record an invite."""
        orm = UserBotInviteTrackingORM(
            user_id=record.user_id,
            chat_id=record.chat_id,
            inviter_tg_id=record.inviter_tg_id,
            inviter_username=record.inviter_username,
            inviter_name=record.inviter_name,
            invited_tg_id=record.invited_tg_id,
            invited_username=record.invited_username,
            invited_name=record.invited_name,
            invite_link=record.invite_link,
            is_still_member=record.is_still_member,
        )
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._invite_to_domain(orm)

    async def mark_user_left(self, user_id: int, chat_id: int, invited_tg_id: int) -> bool:
        """Mark a user as having left the chat."""
        result = await self.session.execute(
            update(UserBotInviteTrackingORM)
            .where(
                UserBotInviteTrackingORM.user_id == user_id,
                UserBotInviteTrackingORM.chat_id == chat_id,
                UserBotInviteTrackingORM.invited_tg_id == invited_tg_id,
            )
            .values(left_at=datetime.now(), is_still_member=False)
        )
        return result.rowcount > 0

    async def get_invite_stats(self, user_id: int, chat_id: int) -> list[InviteStats]:
        """Get invite statistics per inviter."""
        query = (
            select(
                UserBotInviteTrackingORM.inviter_tg_id,
                UserBotInviteTrackingORM.inviter_username,
                UserBotInviteTrackingORM.inviter_name,
                func.count(UserBotInviteTrackingORM.id).label("total_invited"),
                func.count(func.nullif(UserBotInviteTrackingORM.is_still_member, False)).label(
                    "still_members"
                ),
            )
            .where(
                UserBotInviteTrackingORM.user_id == user_id,
                UserBotInviteTrackingORM.chat_id == chat_id,
            )
            .group_by(
                UserBotInviteTrackingORM.inviter_tg_id,
                UserBotInviteTrackingORM.inviter_username,
                UserBotInviteTrackingORM.inviter_name,
            )
            .order_by(func.count(UserBotInviteTrackingORM.id).desc())
        )

        result = await self.session.execute(query)
        stats = []
        for row in result.all():
            stats.append(
                InviteStats(
                    inviter_tg_id=row.inviter_tg_id,
                    inviter_username=row.inviter_username,
                    inviter_name=row.inviter_name,
                    total_invited=row.total_invited,
                    still_members=row.still_members,
                    left_count=row.total_invited - row.still_members,
                )
            )
        return stats

    async def get_invites_by_inviter(
        self, user_id: int, chat_id: int, inviter_tg_id: int
    ) -> list[InviteRecord]:
        """Get all invites by a specific inviter."""
        result = await self.session.execute(
            select(UserBotInviteTrackingORM)
            .where(
                UserBotInviteTrackingORM.user_id == user_id,
                UserBotInviteTrackingORM.chat_id == chat_id,
                UserBotInviteTrackingORM.inviter_tg_id == inviter_tg_id,
            )
            .order_by(UserBotInviteTrackingORM.joined_at.desc())
        )
        return [self._invite_to_domain(orm) for orm in result.scalars().all()]

    def _invite_to_domain(self, orm: UserBotInviteTrackingORM) -> InviteRecord:
        """Convert ORM to domain model."""
        return InviteRecord(
            id=orm.id,
            user_id=orm.user_id,
            chat_id=orm.chat_id,
            inviter_tg_id=orm.inviter_tg_id,
            inviter_username=orm.inviter_username,
            inviter_name=orm.inviter_name,
            invited_tg_id=orm.invited_tg_id,
            invited_username=orm.invited_username,
            invited_name=orm.invited_name,
            invite_link=orm.invite_link,
            joined_at=orm.joined_at,
            left_at=orm.left_at,
            is_still_member=orm.is_still_member,
        )

    # ===========================================
    # Warnings
    # ===========================================

    async def add_warning(self, warning: Warning) -> Warning:
        """Add a warning to a user."""
        orm = UserBotWarningORM(
            user_id=warning.user_id,
            chat_id=warning.chat_id,
            warned_tg_id=warning.warned_tg_id,
            warned_username=warning.warned_username,
            warned_name=warning.warned_name,
            reason=warning.reason,
            warning_type=warning.warning_type.value,
            message_id=warning.message_id,
            message_text=warning.message_text[:500] if warning.message_text else None,
            action_taken=warning.action_taken.value if warning.action_taken else None,
            is_active=warning.is_active,
            expires_at=warning.expires_at,
            created_by_tg_id=warning.created_by_tg_id,
        )
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._warning_to_domain(orm)

    async def get_active_warnings(
        self, user_id: int, chat_id: int, warned_tg_id: int
    ) -> list[Warning]:
        """Get active warnings for a user in a chat."""
        result = await self.session.execute(
            select(UserBotWarningORM)
            .where(
                UserBotWarningORM.user_id == user_id,
                UserBotWarningORM.chat_id == chat_id,
                UserBotWarningORM.warned_tg_id == warned_tg_id,
                UserBotWarningORM.is_active == True,
            )
            .order_by(UserBotWarningORM.created_at.desc())
        )
        return [self._warning_to_domain(orm) for orm in result.scalars().all()]

    async def get_warning_count(self, user_id: int, chat_id: int, warned_tg_id: int) -> int:
        """Get count of active warnings for a user."""
        result = await self.session.execute(
            select(func.count(UserBotWarningORM.id)).where(
                UserBotWarningORM.user_id == user_id,
                UserBotWarningORM.chat_id == chat_id,
                UserBotWarningORM.warned_tg_id == warned_tg_id,
                UserBotWarningORM.is_active == True,
            )
        )
        return result.scalar() or 0

    async def clear_warnings(self, user_id: int, chat_id: int, warned_tg_id: int) -> int:
        """Clear all warnings for a user."""
        result = await self.session.execute(
            update(UserBotWarningORM)
            .where(
                UserBotWarningORM.user_id == user_id,
                UserBotWarningORM.chat_id == chat_id,
                UserBotWarningORM.warned_tg_id == warned_tg_id,
            )
            .values(is_active=False)
        )
        return result.rowcount

    def _warning_to_domain(self, orm: UserBotWarningORM) -> Warning:
        """Convert ORM to domain model."""
        return Warning(
            id=orm.id,
            user_id=orm.user_id,
            chat_id=orm.chat_id,
            warned_tg_id=orm.warned_tg_id,
            warned_username=orm.warned_username,
            warned_name=orm.warned_name,
            reason=orm.reason,
            warning_type=WarningType(orm.warning_type),
            message_id=orm.message_id,
            message_text=orm.message_text,
            action_taken=(ModerationAction(orm.action_taken) if orm.action_taken else None),
            is_active=orm.is_active,
            expires_at=orm.expires_at,
            created_at=orm.created_at,
            created_by_tg_id=orm.created_by_tg_id,
        )

    # ===========================================
    # Moderation Log
    # ===========================================

    async def log_action(self, entry: ModerationLogEntry) -> ModerationLogEntry:
        """Log a moderation action."""
        orm = UserBotServiceLogORM(
            user_id=entry.user_id,
            chat_id=entry.chat_id,
            action=entry.action,
            target_tg_id=entry.target_tg_id,
            target_username=entry.target_username,
            performed_by=entry.performed_by.value,
            performed_by_tg_id=entry.performed_by_tg_id,
            reason=entry.reason,
            details=entry.details,
            message_id=entry.message_id,
        )
        self.session.add(orm)
        await self.session.flush()
        await self.session.refresh(orm)
        return self._log_to_domain(orm)

    async def get_moderation_log(
        self,
        user_id: int,
        chat_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ModerationLogEntry]:
        """Get moderation log entries."""
        result = await self.session.execute(
            select(UserBotServiceLogORM)
            .where(
                UserBotServiceLogORM.user_id == user_id,
                UserBotServiceLogORM.chat_id == chat_id,
            )
            .order_by(UserBotServiceLogORM.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [self._log_to_domain(orm) for orm in result.scalars().all()]

    def _log_to_domain(self, orm: UserBotServiceLogORM) -> ModerationLogEntry:
        """Convert ORM to domain model."""
        return ModerationLogEntry(
            id=orm.id,
            user_id=orm.user_id,
            chat_id=orm.chat_id,
            action=orm.action,
            target_tg_id=orm.target_tg_id,
            target_username=orm.target_username,
            performed_by=PerformedBy(orm.performed_by),
            performed_by_tg_id=orm.performed_by_tg_id,
            reason=orm.reason,
            details=orm.details or {},
            message_id=orm.message_id,
            created_at=orm.created_at,
        )

    # ===========================================
    # Welcome Messages
    # ===========================================

    async def get_welcome_message(
        self,
        user_id: int,
        chat_id: int,
        message_type: MessageType = MessageType.WELCOME,
    ) -> WelcomeMessage | None:
        """Get welcome message for a chat."""
        result = await self.session.execute(
            select(UserBotWelcomeMessageORM).where(
                UserBotWelcomeMessageORM.user_id == user_id,
                UserBotWelcomeMessageORM.chat_id == chat_id,
                UserBotWelcomeMessageORM.message_type == message_type.value,
                UserBotWelcomeMessageORM.is_active == True,
            )
        )
        orm = result.scalar_one_or_none()
        return self._welcome_to_domain(orm) if orm else None

    async def set_welcome_message(self, message: WelcomeMessage) -> WelcomeMessage:
        """Create or update welcome message."""
        existing = await self.get_welcome_message(
            message.user_id, message.chat_id, message.message_type
        )

        if existing:
            # Update existing
            result = await self.session.execute(
                select(UserBotWelcomeMessageORM).where(UserBotWelcomeMessageORM.id == existing.id)
            )
            orm = result.scalar_one()
            orm.message_text = message.message_text
            orm.parse_mode = message.parse_mode
            orm.buttons = message.buttons
            orm.media_type = message.media_type
            orm.media_file_id = message.media_file_id
            orm.delete_after_seconds = message.delete_after_seconds
            orm.is_active = message.is_active
            orm.updated_at = datetime.now()
        else:
            # Create new
            orm = UserBotWelcomeMessageORM(
                user_id=message.user_id,
                chat_id=message.chat_id,
                message_type=message.message_type.value,
                message_text=message.message_text,
                parse_mode=message.parse_mode,
                buttons=message.buttons,
                media_type=message.media_type,
                media_file_id=message.media_file_id,
                delete_after_seconds=message.delete_after_seconds,
                is_active=message.is_active,
            )
            self.session.add(orm)

        await self.session.flush()
        await self.session.refresh(orm)
        return self._welcome_to_domain(orm)

    async def delete_welcome_message(
        self,
        user_id: int,
        chat_id: int,
        message_type: MessageType = MessageType.WELCOME,
    ) -> bool:
        """Delete welcome message."""
        result = await self.session.execute(
            delete(UserBotWelcomeMessageORM).where(
                UserBotWelcomeMessageORM.user_id == user_id,
                UserBotWelcomeMessageORM.chat_id == chat_id,
                UserBotWelcomeMessageORM.message_type == message_type.value,
            )
        )
        return result.rowcount > 0

    def _welcome_to_domain(self, orm: UserBotWelcomeMessageORM) -> WelcomeMessage:
        """Convert ORM to domain model."""
        return WelcomeMessage(
            id=orm.id,
            user_id=orm.user_id,
            chat_id=orm.chat_id,
            message_type=MessageType(orm.message_type),
            message_text=orm.message_text,
            parse_mode=orm.parse_mode,
            buttons=orm.buttons,
            media_type=orm.media_type,
            media_file_id=orm.media_file_id,
            delete_after_seconds=orm.delete_after_seconds,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )
