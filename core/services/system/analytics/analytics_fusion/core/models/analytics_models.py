"""
Analytics Models
===============

Data models for analytics core service.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ChannelMetrics:
    """Channel metrics data model"""

    channel_id: int
    timestamp: datetime
    subscriber_count: int
    view_count: int
    engagement_count: int
    reach_count: int
    metadata: dict[str, Any] | None = None


@dataclass
class EngagementData:
    """Engagement data model"""

    channel_id: int
    post_id: str | None
    engagement_rate: float
    engagement_type: str
    timestamp: datetime
    content_type: str
    metadata: dict[str, Any] | None = None


@dataclass
class PerformanceScore:
    """Performance score data model"""

    channel_id: int
    overall_score: float
    engagement_score: float
    growth_score: float
    content_score: float
    calculated_at: datetime
    confidence: float = 0.8
