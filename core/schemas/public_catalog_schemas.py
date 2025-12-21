"""
Public Catalog Schemas

Pydantic models for the public analytics catalog API.
These models are used for public-facing endpoints that don't require authentication.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ============================================================================
# Category Schemas
# ============================================================================


class PublicCategory(BaseModel):
    """Public category information"""

    id: int
    name: str
    slug: str
    icon: str | None = None
    color: str | None = None
    channel_count: int = 0

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Response for category listing"""

    categories: list[PublicCategory]
    total: int


# ============================================================================
# Channel Schemas
# ============================================================================


class PublicChannelBasic(BaseModel):
    """Basic channel info for listings"""

    telegram_id: int
    username: str | None = None
    title: str
    description: str | None = None
    avatar_url: str | None = None
    category: PublicCategory | None = None
    subscriber_count: int | None = None
    is_verified: bool = False
    is_featured: bool = False

    class Config:
        from_attributes = True


class PublicChannelStats(BaseModel):
    """Channel statistics"""

    subscriber_count: int | None = None
    avg_views: int | None = None
    avg_reactions: int | None = None
    avg_comments: int | None = None
    posts_per_day: float | None = None
    growth_rate: float | None = None  # % change in last 30 days
    last_post_at: datetime | None = None

    class Config:
        from_attributes = True


class PublicChannelDetail(PublicChannelBasic):
    """Detailed channel info with stats"""

    country_code: str | None = None
    language_code: str | None = None
    stats: PublicChannelStats | None = None
    added_at: datetime | None = None
    last_synced_at: datetime | None = None


class ChannelListResponse(BaseModel):
    """Paginated channel list response"""

    channels: list[PublicChannelBasic]
    total: int
    page: int
    per_page: int
    total_pages: int


# ============================================================================
# Post Schemas
# ============================================================================


class PublicPost(BaseModel):
    """Public post information"""

    message_id: int
    text: str | None = None
    views: int | None = None
    forwards: int | None = None
    reactions: int | None = None
    comments: int | None = None
    posted_at: datetime | None = None
    has_media: bool = False
    media_type: str | None = None  # photo, video, document, etc.


class PostListResponse(BaseModel):
    """Response for recent posts"""

    posts: list[PublicPost]
    total: int
    channel_username: str | None = None


# ============================================================================
# Search Schemas
# ============================================================================


class SearchQuery(BaseModel):
    """Search query parameters"""

    q: str = Field(..., min_length=2, max_length=100)
    category_id: int | None = None
    country_code: str | None = None
    limit: int = Field(default=20, le=50)


class SearchResult(PublicChannelBasic):
    """Search result with relevance"""

    relevance_score: float | None = None


class SearchResponse(BaseModel):
    """Search results response"""

    results: list[SearchResult]
    total: int
    query: str


# ============================================================================
# Trending Schemas
# ============================================================================


class TrendingChannel(PublicChannelBasic):
    """Channel with trending metrics"""

    growth_rate: float | None = None  # % growth
    growth_subscribers: int | None = None  # Absolute growth
    rank: int | None = None


class TrendingResponse(BaseModel):
    """Trending channels response"""

    channels: list[TrendingChannel]
    period: str = "30d"  # 7d, 30d, 90d


# ============================================================================
# Moderator Schemas (for catalog management)
# ============================================================================


class AddChannelRequest(BaseModel):
    """Request to add channel to catalog"""

    telegram_id: int | None = None
    username: str | None = None  # Either telegram_id or username required
    category_id: int
    country_code: str | None = None
    language_code: str | None = None
    is_featured: bool = False


class UpdateChannelRequest(BaseModel):
    """Request to update channel in catalog"""

    category_id: int | None = None
    country_code: str | None = None
    language_code: str | None = None
    is_featured: bool | None = None
    is_verified: bool | None = None
    is_active: bool | None = None


class ChannelCatalogEntry(BaseModel):
    """Full catalog entry for moderators"""

    id: int
    telegram_id: int
    username: str | None
    title: str
    description: str | None
    avatar_url: str | None
    category_id: int | None
    category: PublicCategory | None
    country_code: str | None
    language_code: str | None
    is_featured: bool
    is_verified: bool
    is_active: bool
    added_by: int | None
    added_at: datetime
    last_synced_at: datetime | None
    metadata: dict[str, Any] = {}

    class Config:
        from_attributes = True
