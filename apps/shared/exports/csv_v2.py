import csv
import io
import logging
from datetime import datetime

from apps.shared.clients.analytics_client import (
    GrowthResponse,
    OverviewResponse,
    ReachResponse,
    SourcesResponse,
    TopPostsResponse,
    TrendingResponse,
)

logger = logging.getLogger(__name__)


class CSVExporter:
    """Service for exporting analytics data to CSV format"""

    def __init__(self, max_rows: int = 10000):
        self.max_rows = max_rows

    def overview_to_csv(self, data: OverviewResponse) -> io.StringIO:
        """Export overview data to CSV"""
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # Header
        writer.writerow(
            [
                "metric",
                "value",
                "period_days",
                "channel_id",
                "data_sources",
                "last_updated",
            ]
        )

        # Data rows
        overview = data.overview
        base_data = [
            data.period,
            data.channel_id,
            "|".join(data.data_sources),
            data.last_updated.isoformat(),
        ]

        metrics = [
            ("subscribers", overview.subscribers),
            ("subscriber_growth", overview.subscriber_growth),
            ("total_posts", overview.total_posts),
            ("total_views", overview.total_views),
            ("average_views_per_post", overview.average_views_per_post),
            ("engagement_rate", overview.engagement_rate),
        ]

        for metric_name, value in metrics:
            writer.writerow([metric_name, value] + base_data)

        buffer.seek(0)
        return buffer

    def growth_to_csv(self, data: GrowthResponse) -> io.StringIO:
        """Export growth data to CSV"""
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # Header
        writer.writerow(
            [
                "date",
                "subscribers",
                "change",
                "growth_rate",
                "period_days",
                "channel_id",
                "data_sources",
                "last_updated",
            ]
        )

        # Limit rows to prevent excessive data
        daily_growth = data.growth.daily_growth[: self.max_rows]

        base_data = [
            data.period,
            data.channel_id,
            "|".join(data.data_sources),
            data.last_updated.isoformat(),
        ]

        for day_data in daily_growth:
            writer.writerow(
                [
                    day_data.get("date", ""),
                    day_data.get("subscribers", 0),
                    day_data.get("change", 0),
                    data.growth.growth_rate,
                ]
                + base_data
            )

        buffer.seek(0)
        return buffer

    def reach_to_csv(self, data: ReachResponse) -> io.StringIO:
        """Export reach data to CSV"""
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # Header for hourly distribution
        writer.writerow(
            [
                "hour",
                "views",
                "total_views",
                "unique_viewers",
                "view_reach_ratio",
                "peak_concurrent",
                "period_days",
                "channel_id",
                "data_sources",
                "last_updated",
            ]
        )

        reach = data.reach
        base_data = [
            reach.total_views,
            reach.unique_viewers,
            reach.view_reach_ratio,
            reach.peak_concurrent,
            data.period,
            data.channel_id,
            "|".join(data.data_sources),
            data.last_updated.isoformat(),
        ]

        # Hourly distribution data
        for hour, views in reach.hourly_distribution.items():
            writer.writerow([hour, views] + base_data)

        buffer.seek(0)
        return buffer

    def top_posts_to_csv(self, data: TopPostsResponse) -> io.StringIO:
        """Export top posts data to CSV"""
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # Header
        writer.writerow(
            [
                "rank",
                "post_id",
                "message_preview",
                "views",
                "forwards",
                "reactions",
                "engagement_score",
                "published_at",
                "period_days",
                "channel_id",
                "data_sources",
                "last_updated",
            ]
        )

        # Limit posts to prevent excessive data
        top_posts = data.top_posts[: self.max_rows]

        base_data = [
            data.period,
            data.channel_id,
            "|".join(data.data_sources),
            data.last_updated.isoformat(),
        ]

        for rank, post in enumerate(top_posts, 1):
            # Clean message for CSV (remove newlines, limit length)
            message_preview = post.message.replace("\n", " ").replace("\r", " ")[:200]

            writer.writerow(
                [
                    rank,
                    post.post_id,
                    message_preview,
                    post.views,
                    post.forwards,
                    post.reactions,
                    post.engagement_score,
                    post.published_at.isoformat(),
                ]
                + base_data
            )

        buffer.seek(0)
        return buffer

    def sources_to_csv(self, data: SourcesResponse) -> io.StringIO:
        """Export sources data to CSV"""
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # Header
        writer.writerow(
            [
                "source_type",
                "views",
                "percentage",
                "channel_id",
                "period_days",
                "data_sources",
                "last_updated",
            ]
        )

        sources = data.sources
        base_data = [
            data.channel_id,
            data.period,
            "|".join(data.data_sources),
            data.last_updated.isoformat(),
        ]

        # Main source types
        source_types = [
            ("direct", sources.direct),
            ("forwards", sources.forwards),
            ("links", sources.links),
            ("search", sources.search),
        ]

        for source_type, source_data in source_types:
            writer.writerow(
                [
                    source_type,
                    source_data.get("views", 0),
                    source_data.get("percentage", 0.0),
                ]
                + base_data
            )

        # Referral channels (limited to prevent excessive rows)
        referral_channels = sources.referral_channels[:100]  # Limit referrals
        for referrer in referral_channels:
            writer.writerow(
                [
                    f"referral:{referrer.get('channel', 'unknown')}",
                    referrer.get("views", 0),
                    referrer.get("conversion_rate", 0.0),
                ]
                + base_data
            )

        buffer.seek(0)
        return buffer

    def trending_to_csv(self, data: TrendingResponse) -> io.StringIO:
        """Export trending data to CSV"""
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        # Header
        writer.writerow(
            [
                "metric",
                "value",
                "is_trending",
                "trend_direction",
                "confidence",
                "period_days",
                "channel_id",
                "data_sources",
                "last_updated",
            ]
        )

        trending = data.trending
        base_data = [
            trending.is_trending,
            trending.trend_direction,
            trending.confidence,
            data.period,
            data.channel_id,
            "|".join(data.data_sources),
            data.last_updated.isoformat(),
        ]

        # Trending metrics
        metrics = [
            ("trend_score", trending.trend_score),
            ("z_score", trending.z_score),
            ("ewma_score", trending.ewma_score),
        ]

        for metric_name, value in metrics:
            writer.writerow([metric_name, value] + base_data)

        # Add analysis as a text row
        writer.writerow(["analysis", trending.analysis] + base_data)

        buffer.seek(0)
        return buffer

    def generate_filename(self, data_type: str, channel_id: str, period: int) -> str:
        """Generate standardized filename for CSV exports"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"analytics_{data_type}_{channel_id}_{period}d_{timestamp}.csv"

    def get_content_disposition_header(self, filename: str) -> str:
        """Get Content-Disposition header for file download"""
        return f'attachment; filename="{filename}"'
