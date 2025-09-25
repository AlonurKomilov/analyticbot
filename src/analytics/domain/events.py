"""
Analytics Domain Events
"""

from datetime import datetime
from typing import Dict, Any

from ...shared_kernel.domain.domain_events import DomainEvent


class ChannelAdded(DomainEvent):
    """Event raised when a new channel is added for analytics"""
    
    def __init__(self, channel_id: str, user_id: str, channel_username: str, channel_title: str):
        super().__init__()
        self.channel_id = channel_id
        self.user_id = user_id  
        self.channel_username = channel_username
        self.channel_title = channel_title
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'channel_id': self.channel_id,
            'user_id': self.user_id,
            'channel_username': self.channel_username,
            'channel_title': self.channel_title
        }


class PostScheduled(DomainEvent):
    """Event raised when a post is scheduled"""
    
    def __init__(self, post_id: str, channel_id: str, user_id: str, scheduled_at: datetime):
        super().__init__()
        self.post_id = post_id
        self.channel_id = channel_id
        self.user_id = user_id
        self.scheduled_at = scheduled_at
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'post_id': self.post_id,
            'channel_id': self.channel_id,
            'user_id': self.user_id,
            'scheduled_at': self.scheduled_at.isoformat()
        }


class PostPublished(DomainEvent):
    """Event raised when a post is successfully published"""
    
    def __init__(self, post_id: str, channel_id: str, user_id: str, message_id: int, published_at: datetime):
        super().__init__()
        self.post_id = post_id
        self.channel_id = channel_id
        self.user_id = user_id
        self.message_id = message_id
        self.published_at = published_at
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'post_id': self.post_id,
            'channel_id': self.channel_id,
            'user_id': self.user_id,
            'message_id': self.message_id,
            'published_at': self.published_at.isoformat()
        }


class ViewsUpdated(DomainEvent):
    """Event raised when post view count is updated"""
    
    def __init__(self, post_id: str, channel_id: str, user_id: str, old_views: int, new_views: int, view_increase: int):
        super().__init__()
        self.post_id = post_id
        self.channel_id = channel_id
        self.user_id = user_id
        self.old_views = old_views
        self.new_views = new_views
        self.view_increase = view_increase
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'post_id': self.post_id,
            'channel_id': self.channel_id,
            'user_id': self.user_id,
            'old_views': self.old_views,
            'new_views': self.new_views,
            'view_increase': self.view_increase
        }


class ChannelStatsGenerated(DomainEvent):
    """Event raised when channel statistics are generated"""
    
    def __init__(self, channel_id: str, user_id: str, report_type: str, 
                 period_start: datetime, period_end: datetime, total_posts: int, total_views: int):
        super().__init__()
        self.channel_id = channel_id
        self.user_id = user_id
        self.report_type = report_type
        self.period_start = period_start
        self.period_end = period_end
        self.total_posts = total_posts
        self.total_views = total_views
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'channel_id': self.channel_id,
            'user_id': self.user_id,
            'report_type': self.report_type,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'total_posts': self.total_posts,
            'total_views': self.total_views
        }


class AnalyticsInsightGenerated(DomainEvent):
    """Event raised when an analytics insight is generated"""
    
    def __init__(self, user_id: str, channel_id: str, insight_type: str, insight_data: Dict[str, Any]):
        super().__init__()
        self.user_id = user_id
        self.channel_id = channel_id
        self.insight_type = insight_type
        self.insight_data = insight_data
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'channel_id': self.channel_id,
            'insight_type': self.insight_type,
            'insight_data': self.insight_data
        }