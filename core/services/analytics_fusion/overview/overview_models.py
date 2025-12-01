"""
Analytics Overview Models
=========================

Data models for the Analytics Overview dashboard.
Mirrors TGStat-style metrics structure.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SubscriberStats:
    """Subscriber statistics"""
    total: int = 0
    today_change: int = 0
    week_change: int = 0
    month_change: int = 0
    growth_rate: float = 0.0  # Percentage
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "today_change": self.today_change,
            "week_change": self.week_change,
            "month_change": self.month_change,
            "growth_rate": round(self.growth_rate, 2),
        }


@dataclass
class PostsStats:
    """Posts statistics"""
    total: int = 0
    today: int = 0
    week: int = 0
    month: int = 0
    avg_per_day: float = 0.0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "today": self.today,
            "week": self.week,
            "month": self.month,
            "avg_per_day": round(self.avg_per_day, 2),
        }


@dataclass
class EngagementStats:
    """Engagement statistics"""
    total_views: int = 0
    total_reactions: int = 0
    total_forwards: int = 0
    total_comments: int = 0
    avg_views_per_post: float = 0.0
    avg_reactions_per_post: float = 0.0
    engagement_rate: float = 0.0  # (reactions + forwards + comments) / views * 100
    err: float = 0.0  # Engagement Rate Ratio
    err_24h: float = 0.0  # ERR for last 24 hours
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "total_views": self.total_views,
            "total_reactions": self.total_reactions,
            "total_forwards": self.total_forwards,
            "total_comments": self.total_comments,
            "avg_views_per_post": round(self.avg_views_per_post, 1),
            "avg_reactions_per_post": round(self.avg_reactions_per_post, 1),
            "engagement_rate": round(self.engagement_rate, 2),
            "err": round(self.err, 2),
            "err_24h": round(self.err_24h, 2),
        }


@dataclass
class ReachStats:
    """Reach and advertising statistics"""
    avg_post_reach: int = 0
    avg_ad_reach: int = 0  # Average advertising reach
    reach_12h: int = 0
    reach_24h: int = 0
    reach_48h: int = 0
    citation_index: float = 0.0  # Based on forwards/mentions
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "avg_post_reach": self.avg_post_reach,
            "avg_ad_reach": self.avg_ad_reach,
            "reach_12h": self.reach_12h,
            "reach_24h": self.reach_24h,
            "reach_48h": self.reach_48h,
            "citation_index": round(self.citation_index, 1),
        }


@dataclass
class ChannelInfo:
    """Basic channel information"""
    id: int = 0
    title: str = ""
    username: str | None = None
    description: str | None = None
    created_at: datetime | None = None
    age_days: int = 0
    age_formatted: str = ""  # e.g., "2 years 3 months"
    is_active: bool = True
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "username": self.username,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "age_days": self.age_days,
            "age_formatted": self.age_formatted,
            "is_active": self.is_active,
        }


@dataclass
class GrowthDataPoint:
    """Single data point for growth charts"""
    date: str  # ISO date string
    value: int = 0
    change: int = 0


@dataclass
class GrowthTimeSeries:
    """Time series data for growth charts"""
    metric: str  # subscribers, views, posts, etc.
    data: list[GrowthDataPoint] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "data": [{"date": p.date, "value": p.value, "change": p.change} for p in self.data],
        }


@dataclass
class ChannelOverviewMetrics:
    """Complete channel overview metrics - TGStat style"""
    channel_info: ChannelInfo = field(default_factory=ChannelInfo)
    subscribers: SubscriberStats = field(default_factory=SubscriberStats)
    posts: PostsStats = field(default_factory=PostsStats)
    engagement: EngagementStats = field(default_factory=EngagementStats)
    reach: ReachStats = field(default_factory=ReachStats)
    
    # Time series data for charts
    subscribers_history: list[dict] = field(default_factory=list)
    views_history: list[dict] = field(default_factory=list)
    posts_history: list[dict] = field(default_factory=list)
    
    # Metadata
    generated_at: datetime = field(default_factory=datetime.utcnow)
    data_freshness: str = "real-time"  # real-time, cached, historical
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_info": self.channel_info.to_dict(),
            "subscribers": self.subscribers.to_dict(),
            "posts": self.posts.to_dict(),
            "engagement": self.engagement.to_dict(),
            "reach": self.reach.to_dict(),
            "subscribers_history": self.subscribers_history,
            "views_history": self.views_history,
            "posts_history": self.posts_history,
            "generated_at": self.generated_at.isoformat(),
            "data_freshness": self.data_freshness,
        }
