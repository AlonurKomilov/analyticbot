"""
Post Entity - Analytics Domain
"""

from datetime import datetime
from enum import Enum
from typing import Any

from ....shared_kernel.domain.base_entity import AggregateRoot
from ....shared_kernel.domain.exceptions import (
    BusinessRuleViolationError,
    ValidationError,
)
from ....shared_kernel.domain.value_objects import UserId
from ..events import PostPublished, PostScheduled, ViewsUpdated
from ..value_objects.analytics_value_objects import (
    ChannelId,
    MessageId,
    PostContent,
    PostId,
    ViewCount,
)


class PostStatus(str, Enum):
    """Post status enumeration"""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    DELETED = "deleted"


class PostType(str, Enum):
    """Post type enumeration"""

    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    POLL = "poll"
    ANIMATION = "animation"
    VOICE = "voice"
    VIDEO_NOTE = "video_note"


class Post(AggregateRoot[PostId]):
    """
    Post aggregate root - Represents a Telegram post in analytics

    Tracks individual posts within channels, their content, scheduling,
    publishing status, and view analytics.
    """

    def __init__(
        self,
        id: PostId,
        channel_id: ChannelId,
        user_id: UserId,
        content: PostContent,
        message_id: MessageId | None = None,
        post_type: PostType = PostType.TEXT,
        status: PostStatus = PostStatus.DRAFT,
        scheduled_at: datetime | None = None,
        published_at: datetime | None = None,
        views: ViewCount | None = None,
        last_view_update: datetime | None = None,
        view_history: list[dict[str, Any]] | None = None,
        peak_views_per_hour: int | None = None,
        view_velocity: float | None = None,
        shares: int | None = None,
        comments: int | None = None,
        reactions: dict[str, int] | None = None,
        media_file_id: str | None = None,
        media_file_size: int | None = None,
        media_duration: int | None = None,
        publish_attempt_count: int = 0,
        last_publish_error: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        super().__init__(
            id=id,
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow(),
        )

        # Core identity and relationships
        self.channel_id = channel_id
        self.user_id = user_id
        self.content = content
        self.message_id = message_id

        # Content and metadata
        self.post_type = post_type
        self.status = status

        # Scheduling
        self.scheduled_at = scheduled_at
        self.published_at = published_at

        # Analytics data
        self.views = views or ViewCount(0)
        self.last_view_update = last_view_update

        # Performance tracking
        self.view_history = view_history or []
        self.peak_views_per_hour = peak_views_per_hour
        self.view_velocity = view_velocity

        # Engagement metrics
        self.shares = shares
        self.comments = comments
        self.reactions = reactions

        # Media information
        self.media_file_id = media_file_id
        self.media_file_size = media_file_size
        self.media_duration = media_duration

        # Publishing details
        self.publish_attempt_count = publish_attempt_count
        self.last_publish_error = last_publish_error

        # Validate after initialization
        self._validate_post_data()

    def _validate_post_data(self) -> None:
        """Validate post data consistency"""
        # Status-based validations
        if self.status == PostStatus.PUBLISHED and not self.published_at:
            raise ValidationError("Published posts must have published_at timestamp")

        if self.status == PostStatus.SCHEDULED and not self.scheduled_at:
            raise ValidationError("Scheduled posts must have scheduled_at timestamp")

        if self.scheduled_at and self.scheduled_at <= datetime.utcnow():
            if self.status == PostStatus.SCHEDULED:
                raise ValidationError("Cannot schedule posts in the past")

        # View count validation
        if self.views.value < 0:
            raise ValidationError("Views cannot be negative")

        # Media validation
        if self.post_type != PostType.TEXT and not self.media_file_id:
            raise ValidationError(f"Posts of type {self.post_type} must have media_file_id")

    @classmethod
    def create_draft_post(
        cls,
        post_id: PostId,
        channel_id: ChannelId,
        user_id: UserId,
        content: PostContent,
        post_type: PostType = PostType.TEXT,
    ) -> "Post":
        """
        Factory method to create a new draft post
        """
        post = cls(
            id=post_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            post_type=post_type,
            status=PostStatus.DRAFT,
        )

        return post

    @classmethod
    def create_immediate_post(
        cls,
        post_id: PostId,
        channel_id: ChannelId,
        user_id: UserId,
        content: PostContent,
        post_type: PostType = PostType.TEXT,
    ) -> "Post":
        """
        Factory method to create a post for immediate publishing
        """
        post = cls(
            id=post_id,
            channel_id=channel_id,
            user_id=user_id,
            content=content,
            post_type=post_type,
            status=PostStatus.DRAFT,
        )

        # Immediately mark for publishing
        post.mark_for_immediate_publishing()

        return post

    def update_content(self, new_content: PostContent) -> None:
        """
        Update post content

        Business Rules:
        - Can only update draft or scheduled posts
        - Published posts cannot be modified
        """
        if self.status == PostStatus.PUBLISHED:
            raise BusinessRuleViolationError("Cannot modify published posts")

        self.content = new_content
        self.mark_as_updated()

    def schedule_post(self, scheduled_time: datetime) -> None:
        """
        Schedule post for future publishing

        Business Rules:
        - Can only schedule draft posts
        - Cannot schedule in the past
        - Must be at least 1 minute in the future
        """
        if self.status != PostStatus.DRAFT:
            raise BusinessRuleViolationError("Can only schedule draft posts")

        now = datetime.utcnow()
        if scheduled_time <= now:
            raise ValidationError("Cannot schedule posts in the past")

        # Business rule: minimum 1 minute scheduling window
        if (scheduled_time - now).total_seconds() < 60:
            raise BusinessRuleViolationError("Posts must be scheduled at least 1 minute in advance")

        self.scheduled_at = scheduled_time
        self.status = PostStatus.SCHEDULED
        self.mark_as_updated()

        # Emit domain event
        self.add_domain_event(
            PostScheduled(
                post_id=self.id.value,
                channel_id=self.channel_id.value,
                user_id=self.user_id.value,
                scheduled_at=scheduled_time,
            )
        )

    def mark_for_immediate_publishing(self) -> None:
        """
        Mark post for immediate publishing

        Business Rules:
        - Can only publish draft or scheduled posts
        - Clears scheduled time if previously scheduled
        """
        if self.status not in [PostStatus.DRAFT, PostStatus.SCHEDULED]:
            raise BusinessRuleViolationError("Can only publish draft or scheduled posts")

        self.scheduled_at = None
        self.status = PostStatus.SCHEDULED  # Will be published by background job
        self.mark_as_updated()

    def mark_as_published(self, message_id: MessageId) -> None:
        """
        Mark post as successfully published

        Called by the publishing service after successful Telegram API call
        """
        if self.status == PostStatus.PUBLISHED:
            raise BusinessRuleViolationError("Post is already published")

        self.message_id = message_id
        self.status = PostStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        self.publish_attempt_count += 1
        self.last_publish_error = None
        self.mark_as_updated()

        # Emit domain event
        self.add_domain_event(
            PostPublished(
                post_id=self.id.value,
                channel_id=self.channel_id.value,
                user_id=self.user_id.value,
                message_id=message_id.value,
                published_at=self.published_at,
            )
        )

    def mark_publish_failed(self, error_message: str) -> None:
        """
        Mark post publishing as failed

        Business Rules:
        - Increments attempt count
        - Stores error for debugging
        - Reverts to draft status for retry
        """
        self.status = PostStatus.FAILED
        self.publish_attempt_count += 1
        self.last_publish_error = error_message
        self.mark_as_updated()

    def retry_publishing(self) -> None:
        """
        Retry publishing a failed post

        Business Rules:
        - Maximum 3 retry attempts
        - Failed posts can be retried
        """
        if self.status != PostStatus.FAILED:
            raise BusinessRuleViolationError("Can only retry failed posts")

        if self.publish_attempt_count >= 3:
            raise BusinessRuleViolationError("Maximum publish attempts exceeded")

        self.status = PostStatus.SCHEDULED
        self.last_publish_error = None
        self.mark_as_updated()

    def update_views(self, new_view_count: ViewCount) -> None:
        """
        Update post view count

        Business Rules:
        - View count can only increase
        - Track view history for analytics
        - Calculate view velocity
        """
        if new_view_count.value < self.views.value:
            raise ValidationError("View count cannot decrease")

        old_views = self.views.value
        view_increase = new_view_count.value - old_views

        if view_increase > 0:
            # Update view count
            self.views = new_view_count
            self.last_view_update = datetime.utcnow()

            # Record view history for analytics
            self.view_history.append(
                {
                    "timestamp": self.last_view_update.isoformat(),
                    "total_views": new_view_count.value,
                    "view_increase": view_increase,
                }
            )

            # Keep only last 100 entries to avoid memory bloat
            if len(self.view_history) > 100:
                self.view_history = self.view_history[-100:]

            # Calculate view velocity (views per hour)
            if self.published_at:
                hours_since_publish = (
                    self.last_view_update - self.published_at
                ).total_seconds() / 3600
                if hours_since_publish > 0:
                    self.view_velocity = new_view_count.value / hours_since_publish

            self.mark_as_updated()

            # Emit domain event
            self.add_domain_event(
                ViewsUpdated(
                    post_id=self.id.value,
                    channel_id=self.channel_id.value,
                    user_id=self.user_id.value,
                    old_views=old_views,
                    new_views=new_view_count.value,
                    view_increase=view_increase,
                )
            )

    def add_media_info(
        self, file_id: str, file_size: int | None = None, duration: int | None = None
    ) -> None:
        """Add media file information to post"""
        self.media_file_id = file_id
        self.media_file_size = file_size
        self.media_duration = duration
        self.mark_as_updated()

    def update_engagement_metrics(
        self,
        shares: int | None = None,
        comments: int | None = None,
        reactions: dict[str, int] | None = None,
    ) -> None:
        """
        Update engagement metrics if available from Telegram API

        Business Rules:
        - Metrics cannot be negative
        - Only update provided metrics
        """
        if shares is not None:
            if shares < 0:
                raise ValidationError("Shares cannot be negative")
            self.shares = shares

        if comments is not None:
            if comments < 0:
                raise ValidationError("Comments cannot be negative")
            self.comments = comments

        if reactions is not None:
            # Validate reaction counts
            for reaction, count in reactions.items():
                if count < 0:
                    raise ValidationError(f"Reaction count for {reaction} cannot be negative")
            self.reactions = reactions

        self.mark_as_updated()

    def calculate_performance_score(self) -> float:
        """
        Calculate a performance score for this post

        Combines various metrics into a single score for ranking/comparison
        """
        if not self.is_published():
            return 0.0

        score = 0.0

        # Base score from views (normalized)
        if self.views.value > 0:
            score += min(self.views.value / 1000, 10.0)  # Max 10 points from views

        # Bonus for engagement
        if self.shares:
            score += min(self.shares * 0.5, 5.0)  # Max 5 points from shares

        if self.comments:
            score += min(self.comments * 0.3, 3.0)  # Max 3 points from comments

        if self.reactions:
            total_reactions = sum(self.reactions.values())
            score += min(total_reactions * 0.1, 2.0)  # Max 2 points from reactions

        # View velocity bonus (rapid initial growth)
        if self.view_velocity and self.view_velocity > 100:  # More than 100 views/hour
            score += min(self.view_velocity / 100, 5.0)  # Max 5 points from velocity

        return round(score, 2)

    def get_analytics_summary(self) -> dict[str, Any]:
        """Get comprehensive analytics summary for this post"""
        return {
            "post_id": self.id.value,
            "channel_id": self.channel_id.value,
            "message_id": self.message_id.value if self.message_id else None,
            "status": self.status.value,
            "post_type": self.post_type.value,
            "published_at": (self.published_at.isoformat() if self.published_at else None),
            "views": self.views.value,
            "view_velocity": self.view_velocity,
            "shares": self.shares,
            "comments": self.comments,
            "reactions": self.reactions,
            "performance_score": self.calculate_performance_score(),
            "hours_since_publish": (self._hours_since_publish() if self.published_at else None),
            "view_history_entries": len(self.view_history),
            "last_view_update": (
                self.last_view_update.isoformat() if self.last_view_update else None
            ),
        }

    def _hours_since_publish(self) -> float:
        """Calculate hours since post was published"""
        if not self.published_at:
            return 0.0
        return (datetime.utcnow() - self.published_at).total_seconds() / 3600

    def is_published(self) -> bool:
        """Check if post is published"""
        return self.status == PostStatus.PUBLISHED

    def is_scheduled(self) -> bool:
        """Check if post is scheduled"""
        return self.status == PostStatus.SCHEDULED

    def is_ready_to_publish(self) -> bool:
        """Check if scheduled post is ready to publish"""
        if not self.is_scheduled():
            return False

        if self.scheduled_at is None:
            return True  # Immediate publishing

        return datetime.utcnow() >= self.scheduled_at

    def can_be_modified(self) -> bool:
        """Check if post can still be modified"""
        return self.status in [PostStatus.DRAFT, PostStatus.SCHEDULED]

    def has_media(self) -> bool:
        """Check if post contains media"""
        return self.post_type != PostType.TEXT and self.media_file_id is not None

    def get_content_preview(self, max_length: int = 100) -> str:
        """Get a content preview for display"""
        content_str = str(self.content)
        if len(content_str) <= max_length:
            return content_str
        return content_str[: max_length - 3] + "..."

    def delete_post(self) -> None:
        """Mark post as deleted (soft delete)"""
        if self.status == PostStatus.PUBLISHED:
            raise BusinessRuleViolationError("Cannot delete published posts")

        self.status = PostStatus.DELETED
        self.mark_as_updated()
