"""
Analytics Domain Entities

Domain entities for analytics bounded context following
Domain-Driven Design principles.
"""

from .channel import Channel, ChannelStatus, ChannelType
from .post import Post, PostStatus, PostType
from .analytics_report import (
    AnalyticsReport, 
    ReportId, 
    ReportType, 
    ReportStatus, 
    ReportInsight,
    MetricTrend
)

__all__ = [
    # Channel
    "Channel",
    "ChannelStatus",
    "ChannelType",
    
    # Post
    "Post",
    "PostStatus", 
    "PostType",
    
    # Analytics Report
    "AnalyticsReport",
    "ReportId",
    "ReportType",
    "ReportStatus",
    "ReportInsight",
    "MetricTrend"
]