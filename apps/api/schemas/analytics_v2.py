"""
Analytics V2 API Schemas
Pydantic models for stable Analytics Fusion API v2
"""

from datetime import datetime
from typing import Optional, Literal, Union, Any
from pydantic import BaseModel, Field


class TimeRangeQuery(BaseModel):
    """Query parameters for time-based analytics"""
    from_dt: datetime = Field(..., alias="from", description="Start datetime (inclusive)")
    to_dt: datetime = Field(..., alias="to", description="End datetime (inclusive)")


class OverviewDTO(BaseModel):
    """Overview analytics data transfer object"""
    posts: int = Field(..., description="Number of posts in the period")
    views: int = Field(..., description="Total views across all posts")
    avg_reach: float = Field(..., description="Average reach (views per post)")
    err: Optional[float] = Field(None, description="Engagement rate ratio (avg_reach/followers * 100)")
    followers: Optional[int] = Field(None, description="Current follower/subscriber count")
    period: dict = Field(..., description="Time period with from/to dates")


class PointDTO(BaseModel):
    """Single data point for time series"""
    t: Union[str, datetime] = Field(..., description="Timestamp (ISO string or datetime)")
    y: Union[float, int] = Field(..., description="Value at this time point")


class SeriesDTO(BaseModel):
    """Time series data transfer object"""
    label: str = Field(..., description="Series label/name")
    points: list[PointDTO] = Field(default_factory=list, description="Data points in chronological order")


class PostDTO(BaseModel):
    """Post data transfer object"""
    msg_id: int = Field(..., description="Message ID")
    date: str = Field(..., description="Post date (ISO string)")
    views: int = Field(default=0, description="Number of views")
    forwards: int = Field(default=0, description="Number of forwards")
    replies: int = Field(default=0, description="Number of replies")
    reactions: Optional[dict] = Field(default_factory=dict, description="Reactions data")
    title: Optional[str] = Field(None, description="Post title or excerpt")
    permalink: Optional[str] = Field(None, description="Direct link to the post")


class EdgeDTO(BaseModel):
    """Edge data transfer object for mentions/forwards"""
    src: int = Field(..., description="Source channel ID")
    dst: int = Field(..., description="Destination channel ID")
    count: int = Field(..., description="Number of edges (mentions/forwards)")


class AnalyticsResponseMeta(BaseModel):
    """Response metadata"""
    source: list[str] = Field(default_factory=lambda: ["mtproto", "db", "legacy"], 
                             description="Data sources used")
    generated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, 
                                           description="When response was generated")
    cache_hit: Optional[bool] = Field(None, description="Whether response came from cache")


class OverviewResponse(BaseModel):
    """Wrapped overview response"""
    data: OverviewDTO
    meta: AnalyticsResponseMeta = Field(default_factory=AnalyticsResponseMeta)


class SeriesResponse(BaseModel):
    """Wrapped series response"""
    data: SeriesDTO
    meta: AnalyticsResponseMeta = Field(default_factory=AnalyticsResponseMeta)


class PostListResponse(BaseModel):
    """Wrapped post list response"""
    data: list[PostDTO]
    meta: AnalyticsResponseMeta = Field(default_factory=AnalyticsResponseMeta)


class EdgeListResponse(BaseModel):
    """Wrapped edge list response"""
    data: list[EdgeDTO]
    meta: AnalyticsResponseMeta = Field(default_factory=AnalyticsResponseMeta)


class TrendingQuery(BaseModel):
    """Query parameters for trending posts"""
    window_hours: int = Field(default=48, ge=1, le=168, description="Analysis window in hours")
    method: Literal["zscore", "ewma"] = Field(default="zscore", description="Trending detection method")


class SourcesQuery(BaseModel):
    """Query parameters for sources analysis"""
    kind: Literal["mention", "forward"] = Field(..., description="Type of edges to analyze")


class GrowthQuery(BaseModel):
    """Query parameters for growth analysis"""
    window: Literal["D", "H", "W"] = Field(default="D", description="Time window aggregation")


# Error response schemas

class ErrorDetail(BaseModel):
    """Error detail"""
    type: str
    message: str
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    details: Optional[list[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health check response

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    service: str = Field(default="analytics-fusion")
    version: str = Field(default="2.0.0")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
