"""
Recommendation Models
====================

Data models for posting time recommendations and analytics.
Clean separation between data structures and business logic.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PostingTimeRecommendation:
    """Single posting time recommendation"""

    hour: int
    day: int  # 0-6 (Sunday-Saturday)
    confidence: float
    avg_engagement: float


@dataclass
class DailyPerformanceData:
    """Daily performance metrics for calendar heatmap"""

    date: int  # Day of month (1-31)
    day_of_week: int  # 0-6 (Sunday-Saturday)
    post_count: int
    avg_engagement: float


@dataclass
class HourlyEngagementTrend:
    """Hourly engagement trend data for visualization"""

    hour: int
    engagement: float
    post_count: int


@dataclass
class BestDayRecommendation:
    """Best day of week recommendation"""

    day: str  # Day name (Monday, Tuesday, etc.)
    day_number: int  # 0-6
    confidence: float
    avg_engagement: float


@dataclass
class DayHourCombination:
    """Best day-hour combination for targeted recommendations"""

    day: int  # 0-6 (Sunday-Saturday)
    hour: int  # 0-23
    confidence: float
    avg_engagement: float
    post_count: int


@dataclass
class ContentTypeRecommendation:
    """Best time for specific content type"""

    content_type: str  # 'video', 'image', 'link', 'text'
    hour: int  # 0-23
    confidence: float
    avg_engagement: float
    post_count: int


@dataclass
class PostingTimeAnalysisResult:
    """Complete result from posting time analysis"""

    channel_id: int
    best_times: list[PostingTimeRecommendation]
    best_days: list[BestDayRecommendation]
    hourly_engagement_trend: list[HourlyEngagementTrend]
    daily_performance: list[DailyPerformanceData]
    current_avg_engagement: float
    analysis_period: str
    total_posts_analyzed: int
    confidence: float
    generated_at: str
    data_source: str = "real_analytics"
    # NEW: Advanced recommendations
    best_day_hour_combinations: list[DayHourCombination] | None = None
    content_type_recommendations: list[ContentTypeRecommendation] | None = None


@dataclass
class RawMetricsData:
    """Raw metrics data from database queries"""

    best_hours: list[dict[str, Any]]
    best_days: list[dict[str, Any]]
    daily_performance: list[dict[str, Any]]
    total_posts_analyzed: int
    # NEW: Advanced analytics
    best_day_hour_combinations: list[dict[str, Any]] | None = None
    content_type_recommendations: list[dict[str, Any]] | None = None


@dataclass
class AnalysisParameters:
    """Parameters for posting time analysis"""

    channel_id: int
    days: int | None = 90  # None = all-time (limited to 10k posts)
    min_posts_per_hour: int = 1
    min_posts_per_day: int = 1
    min_total_posts: int = 3
