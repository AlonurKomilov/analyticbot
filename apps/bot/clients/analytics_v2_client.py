"""
Analytics V2 API Client for Bot Integration
Provides async HTTP client for accessing Analytics Fusion API v2
"""

import asyncio
import logging
from datetime import datetime
from typing import Any
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AnalyticsOverview(BaseModel):
    """Analytics overview response model"""

    subscribers: int
    subscriber_growth: int
    total_posts: int
    total_views: int
    average_views_per_post: float
    engagement_rate: float


class GrowthData(BaseModel):
    """Growth analytics response model"""

    subscriber_growth: int
    growth_rate: float
    daily_growth: list[dict[str, Any]]


class ReachData(BaseModel):
    """Reach analytics response model"""

    total_views: int
    unique_viewers: int
    view_reach_ratio: float
    peak_concurrent: int
    hourly_distribution: dict[str, int]


class TopPost(BaseModel):
    """Top post model"""

    post_id: int
    message: str
    views: int
    forwards: int
    reactions: int
    engagement_score: float
    published_at: datetime


class SourceData(BaseModel):
    """Traffic sources data model"""

    direct: dict[str, Any]
    forwards: dict[str, Any]
    links: dict[str, Any]
    search: dict[str, Any]
    referral_channels: list[dict[str, Any]]


class TrendingData(BaseModel):
    """Trending analysis response model"""

    is_trending: bool
    trend_score: float
    trend_direction: str
    z_score: float
    ewma_score: float
    confidence: str
    analysis: str


class AnalyticsV2Response(BaseModel):
    """Base analytics response with metadata"""

    channel_id: str
    period: int
    period_start: datetime
    period_end: datetime
    data_sources: list[str]
    cache_hit: bool = False
    last_updated: datetime


class OverviewResponse(AnalyticsV2Response):
    """Complete overview response"""

    overview: AnalyticsOverview


class GrowthResponse(AnalyticsV2Response):
    """Complete growth response"""

    growth: GrowthData


class ReachResponse(AnalyticsV2Response):
    """Complete reach response"""

    reach: ReachData


class TopPostsResponse(AnalyticsV2Response):
    """Complete top posts response"""

    top_posts: list[TopPost]


class SourcesResponse(AnalyticsV2Response):
    """Complete sources response"""

    sources: SourceData


class TrendingResponse(AnalyticsV2Response):
    """Complete trending response"""

    trending: TrendingData


class AnalyticsV2ClientError(Exception):
    """Analytics V2 client error"""


class AnalyticsV2Client:
    """
    Async HTTP client for Analytics Fusion API v2
    Provides bot-friendly interface to analytics endpoints
    """

    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries

        # Configure headers
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "AnalyticBot-V2Client/1.0",
        }

        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

        # Create HTTP client
        self._client = httpx.AsyncClient(
            headers=self.headers, timeout=timeout, follow_redirects=True
        )

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()

    def _build_url(self, endpoint: str) -> str:
        """Build complete API URL"""
        return urljoin(f"{self.base_url}/", endpoint.lstrip("/"))

    async def _make_request(
        self, method: str, endpoint: str, params: dict[str, Any] | None = None, **kwargs
    ) -> dict[str, Any]:
        """Make HTTP request with retry logic"""
        url = self._build_url(endpoint)

        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(
                    method=method, url=url, params=params, **kwargs
                )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    raise AnalyticsV2ClientError("Authentication required or token invalid")
                elif response.status_code == 403:
                    raise AnalyticsV2ClientError("Insufficient permissions for this channel")
                elif response.status_code == 404:
                    raise AnalyticsV2ClientError("Channel not found")
                elif response.status_code == 503:
                    data = response.json()
                    raise AnalyticsV2ClientError(
                        f"Service unavailable: {data.get('message', 'Unknown error')}"
                    )
                else:
                    response.raise_for_status()

            except httpx.RequestError as e:
                logger.warning(f"Request error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise AnalyticsV2ClientError(
                        f"Request failed after {self.max_retries} attempts: {e}"
                    )

                # Exponential backoff
                await asyncio.sleep(2**attempt)

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e}")
                raise AnalyticsV2ClientError(f"API returned error {e.response.status_code}")

    async def overview(self, channel_id: str, days: int = 30) -> OverviewResponse:
        """Get channel overview analytics"""
        endpoint = "/api/v2/analytics/overview"
        params = {"channel_id": channel_id, "days": days}

        try:
            data = await self._make_request("GET", endpoint, params=params)
            return OverviewResponse(**data)
        except Exception as e:
            logger.error(f"Failed to get overview for channel {channel_id}: {e}")
            raise AnalyticsV2ClientError(f"Overview request failed: {e}")

    async def growth(self, channel_id: str, days: int = 30) -> GrowthResponse:
        """Get channel growth analytics"""
        endpoint = "/api/v2/analytics/growth"
        params = {"channel_id": channel_id, "days": days}

        try:
            data = await self._make_request("GET", endpoint, params=params)
            return GrowthResponse(**data)
        except Exception as e:
            logger.error(f"Failed to get growth for channel {channel_id}: {e}")
            raise AnalyticsV2ClientError(f"Growth request failed: {e}")

    async def reach(self, channel_id: str, days: int = 30) -> ReachResponse:
        """Get channel reach analytics"""
        endpoint = "/api/v2/analytics/reach"
        params = {"channel_id": channel_id, "days": days}

        try:
            data = await self._make_request("GET", endpoint, params=params)
            return ReachResponse(**data)
        except Exception as e:
            logger.error(f"Failed to get reach for channel {channel_id}: {e}")
            raise AnalyticsV2ClientError(f"Reach request failed: {e}")

    async def top_posts(self, channel_id: str, days: int = 30, limit: int = 10) -> TopPostsResponse:
        """Get channel top posts"""
        endpoint = "/api/v2/analytics/top-posts"
        params = {"channel_id": channel_id, "days": days, "limit": limit}

        try:
            data = await self._make_request("GET", endpoint, params=params)
            return TopPostsResponse(**data)
        except Exception as e:
            logger.error(f"Failed to get top posts for channel {channel_id}: {e}")
            raise AnalyticsV2ClientError(f"Top posts request failed: {e}")

    async def sources(self, channel_id: str, days: int = 30) -> SourcesResponse:
        """Get channel traffic sources"""
        endpoint = "/api/v2/analytics/sources"
        params = {"channel_id": channel_id, "days": days}

        try:
            data = await self._make_request("GET", endpoint, params=params)
            return SourcesResponse(**data)
        except Exception as e:
            logger.error(f"Failed to get sources for channel {channel_id}: {e}")
            raise AnalyticsV2ClientError(f"Sources request failed: {e}")

    async def trending(self, channel_id: str, days: int = 30) -> TrendingResponse:
        """Get channel trending analysis"""
        endpoint = "/api/v2/analytics/trending"
        params = {"channel_id": channel_id, "days": days}

        try:
            data = await self._make_request("GET", endpoint, params=params)
            return TrendingResponse(**data)
        except Exception as e:
            logger.error(f"Failed to get trending for channel {channel_id}: {e}")
            raise AnalyticsV2ClientError(f"Trending request failed: {e}")

    async def health_check(self) -> dict[str, Any]:
        """Check API health"""
        try:
            data = await self._make_request("GET", "/health")
            return data
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise AnalyticsV2ClientError(f"Health check failed: {e}")
