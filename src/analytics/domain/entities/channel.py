"""
Channel Entity - Analytics Domain
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from ....shared_kernel.domain.base_entity import AggregateRoot
from ....shared_kernel.domain.value_objects import UserId
from ....shared_kernel.domain.exceptions import ValidationError, BusinessRuleViolationError
from ..value_objects.analytics_value_objects import (
    ChannelId, ChannelTitle, ChannelUsername, ViewCount, AnalyticsMetric
)
from ..events import ChannelAdded, ChannelStatsGenerated


class ChannelStatus(str, Enum):
    """Channel status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class ChannelType(str, Enum):
    """Channel type enumeration"""
    PUBLIC = "public"
    PRIVATE = "private"
    GROUP = "group"


class Channel(AggregateRoot[ChannelId]):
    """
    Channel aggregate root - Core analytics entity
    
    Represents a Telegram channel being tracked for analytics.
    Contains business rules for channel management and analytics tracking.
    """
    
    def __init__(
        self,
        id: ChannelId,
        user_id: UserId,
        title: ChannelTitle,
        username: Optional[ChannelUsername] = None,
        channel_type: ChannelType = ChannelType.PUBLIC,
        status: ChannelStatus = ChannelStatus.ACTIVE,
        subscriber_count: Optional[int] = None,
        description: Optional[str] = None,
        total_posts: int = 0,
        total_views: Optional[ViewCount] = None,
        last_post_date: Optional[datetime] = None,
        last_analytics_update: Optional[datetime] = None,
        average_views_per_post: Optional[float] = None,
        engagement_rate: Optional[float] = None,
        growth_rate: Optional[float] = None,
        analytics_enabled: bool = True,
        auto_post_enabled: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        super().__init__(
            id=id,
            created_at=created_at or datetime.utcnow(),
            updated_at=updated_at or datetime.utcnow()
        )
        
        # Core identity
        self.user_id = user_id
        self.title = title
        self.username = username
        
        # Channel metadata
        self.channel_type = channel_type
        self.status = status
        self.subscriber_count = subscriber_count
        self.description = description
        
        # Analytics tracking
        self.total_posts = total_posts
        self.total_views = total_views or ViewCount(0)
        self.last_post_date = last_post_date
        self.last_analytics_update = last_analytics_update
        
        # Performance metrics
        self.average_views_per_post = average_views_per_post
        self.engagement_rate = engagement_rate
        self.growth_rate = growth_rate
        
        # Settings
        self.analytics_enabled = analytics_enabled
        self.auto_post_enabled = auto_post_enabled
        
        # Validate after initialization
        self._validate_channel_data()
    
    def _validate_channel_data(self) -> None:
        """Validate channel data consistency"""
        if self.subscriber_count is not None and self.subscriber_count < 0:
            raise ValidationError("Subscriber count cannot be negative")
        
        if self.total_posts < 0:
            raise ValidationError("Total posts cannot be negative")
    
    @classmethod
    def create_new_channel(
        cls,
        channel_id: ChannelId,
        user_id: UserId,
        title: ChannelTitle,
        username: Optional[ChannelUsername] = None,
        channel_type: ChannelType = ChannelType.PUBLIC
    ) -> "Channel":
        """
        Factory method to create a new channel for analytics tracking
        """
        channel = cls(
            id=channel_id,
            user_id=user_id,
            title=title,
            username=username,
            channel_type=channel_type,
            status=ChannelStatus.ACTIVE
        )
        
        # Emit domain event
        channel.add_domain_event(ChannelAdded(
            channel_id=channel_id.value,
            user_id=user_id.value,
            channel_username=str(username) if username else "",
            channel_title=str(title)
        ))
        
        return channel
    
    def update_basic_info(
        self, 
        title: Optional[ChannelTitle] = None,
        username: Optional[ChannelUsername] = None,
        description: Optional[str] = None
    ) -> None:
        """Update basic channel information"""
        if title is not None:
            self.title = title
        
        if username is not None:
            self.username = username
        
        if description is not None:
            self.description = description
        
        self.mark_as_updated()
    
    def update_subscriber_count(self, new_count: int) -> None:
        """
        Update subscriber count with validation
        
        Business Rules:
        - Subscriber count cannot be negative
        - Large decreases should be flagged for review
        """
        if new_count < 0:
            raise ValidationError("Subscriber count cannot be negative")
        
        old_count = self.subscriber_count or 0
        
        # Business rule: Flag suspicious subscriber losses
        if old_count > 0 and new_count < old_count * 0.5:
            # More than 50% subscriber loss - might be an error
            raise BusinessRuleViolationError(
                f"Suspicious subscriber loss: {old_count} -> {new_count}. Please verify."
            )
        
        self.subscriber_count = new_count
        
        # Calculate growth rate if we have previous data
        if old_count > 0:
            self.growth_rate = ((new_count - old_count) / old_count) * 100
        
        self.mark_as_updated()
    
    def add_post(self, views: ViewCount = None) -> None:
        """
        Record a new post for this channel
        
        Business Rules:
        - Updates total post count
        - Updates view statistics
        - Recalculates averages
        """
        self.total_posts += 1
        self.last_post_date = datetime.utcnow()
        
        if views:
            self.total_views = ViewCount(self.total_views.value + views.value)
            self._recalculate_averages()
        
        self.mark_as_updated()
    
    def update_post_views(self, view_increase: ViewCount) -> None:
        """
        Update total views when individual post views change
        
        Business Rules:
        - Only positive increases allowed
        - Triggers average recalculation
        """
        if view_increase.value < 0:
            raise ValidationError("View increase cannot be negative")
        
        self.total_views = ViewCount(self.total_views.value + view_increase.value)
        self._recalculate_averages()
        self.last_analytics_update = datetime.utcnow()
        self.mark_as_updated()
    
    def _recalculate_averages(self) -> None:
        """Recalculate average statistics"""
        if self.total_posts > 0:
            self.average_views_per_post = self.total_views.value / self.total_posts
        else:
            self.average_views_per_post = 0.0
    
    def generate_analytics_report(
        self, 
        period_start: datetime, 
        period_end: datetime,
        report_type: str = "standard"
    ) -> Dict[str, Any]:
        """
        Generate analytics report for the channel
        
        Business Rules:
        - Period must be valid (start < end)
        - Channel must be active for reporting
        """
        if period_start >= period_end:
            raise ValidationError("Period start must be before period end")
        
        if self.status != ChannelStatus.ACTIVE:
            raise BusinessRuleViolationError("Cannot generate reports for inactive channels")
        
        # Basic report data
        report = {
            "channel_id": self.id.value,
            "channel_title": str(self.title),
            "channel_username": str(self.username) if self.username else None,
            "report_type": report_type,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "total_posts": self.total_posts,
            "total_views": self.total_views.value,
            "average_views_per_post": self.average_views_per_post,
            "subscriber_count": self.subscriber_count,
            "engagement_rate": self.engagement_rate,
            "growth_rate": self.growth_rate,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Emit domain event
        self.add_domain_event(ChannelStatsGenerated(
            channel_id=self.id.value,
            user_id=self.user_id.value,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            total_posts=self.total_posts,
            total_views=self.total_views.value
        ))
        
        return report
    
    def calculate_engagement_metrics(self) -> List[AnalyticsMetric]:
        """
        Calculate various engagement metrics
        
        Returns list of analytics metrics for this channel
        """
        metrics = []
        
        # Average views per post
        if self.total_posts > 0:
            avg_views = AnalyticsMetric(
                name="average_views_per_post",
                value=self.total_views.value / self.total_posts,
                unit="views"
            )
            metrics.append(avg_views)
        
        # Engagement rate (if we have subscriber data)
        if self.subscriber_count and self.subscriber_count > 0 and self.average_views_per_post:
            engagement = AnalyticsMetric(
                name="engagement_rate",
                value=(self.average_views_per_post / self.subscriber_count),
                unit=""
            )
            metrics.append(engagement.as_percentage())
        
        # Growth rate
        if self.growth_rate is not None:
            growth = AnalyticsMetric(
                name="growth_rate",
                value=self.growth_rate,
                unit="%"
            )
            metrics.append(growth)
        
        # Posts per day (rough estimate)
        if self.last_post_date and self.created_at:
            days_active = (datetime.utcnow() - self.created_at).days or 1
            posts_per_day = AnalyticsMetric(
                name="posts_per_day",
                value=self.total_posts / days_active,
                unit="posts/day"
            )
            metrics.append(posts_per_day)
        
        return metrics
    
    def enable_analytics(self) -> None:
        """Enable analytics tracking for this channel"""
        if not self.analytics_enabled:
            self.analytics_enabled = True
            self.mark_as_updated()
    
    def disable_analytics(self) -> None:
        """Disable analytics tracking for this channel"""
        if self.analytics_enabled:
            self.analytics_enabled = False
            self.mark_as_updated()
    
    def activate_channel(self) -> None:
        """Activate channel for analytics tracking"""
        if self.status != ChannelStatus.ACTIVE:
            self.status = ChannelStatus.ACTIVE
            self.mark_as_updated()
    
    def suspend_channel(self) -> None:
        """Suspend channel (temporarily disable analytics)"""
        if self.status == ChannelStatus.ACTIVE:
            self.status = ChannelStatus.SUSPENDED
            self.mark_as_updated()
    
    def delete_channel(self) -> None:
        """Mark channel as deleted (soft delete)"""
        self.status = ChannelStatus.DELETED
        self.analytics_enabled = False
        self.mark_as_updated()
    
    def is_active(self) -> bool:
        """Check if channel is active"""
        return self.status == ChannelStatus.ACTIVE
    
    def can_generate_reports(self) -> bool:
        """Check if channel can generate analytics reports"""
        return self.is_active() and self.analytics_enabled
    
    def has_sufficient_data(self) -> bool:
        """Check if channel has sufficient data for meaningful analytics"""
        return self.total_posts >= 5  # Business rule: need at least 5 posts
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of channel performance"""
        return {
            "channel_id": self.id.value,
            "title": str(self.title),
            "total_posts": self.total_posts,
            "total_views": self.total_views.value,
            "average_views": self.average_views_per_post,
            "subscriber_count": self.subscriber_count,
            "is_active": self.is_active(),
            "analytics_enabled": self.analytics_enabled,
            "has_sufficient_data": self.has_sufficient_data(),
            "last_post_date": self.last_post_date.isoformat() if self.last_post_date else None,
            "last_updated": self.updated_at.isoformat()
        }