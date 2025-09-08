"""
Shared Reports API v2 Endpoints
Provides shareable links for analytics reports with TTL and access control
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel

from apps.api.exports.csv_v2 import CSVExporter
from apps.api.middleware.rate_limit import (
    check_access_rate_limit,
    check_creation_rate_limit,
)
from apps.bot.clients.analytics_v2_client import AnalyticsV2Client
from config import settings
from core.repositories.shared_reports_repository import SharedReportsRepository
from infra.db.repositories.shared_reports_repository import (
    AsyncPgSharedReportsRepository,
)
from infra.rendering.charts import (
    MATPLOTLIB_AVAILABLE,
    ChartRenderer,
    ChartRenderingError,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/share", tags=["sharing"])


# Response models
class ShareLinkResponse(BaseModel):
    share_token: str
    share_url: str
    expires_at: datetime
    access_count: int = 0


class SharedReportResponse(BaseModel):
    report_type: str
    channel_id: str
    period: int
    created_at: datetime
    expires_at: datetime
    access_count: int
    format: str  # 'csv' or 'png'
    data: dict[str, Any] | None = None


def get_analytics_client() -> AnalyticsV2Client:
    """Get analytics client instance"""
    return AnalyticsV2Client(settings.ANALYTICS_V2_BASE_URL)


def get_shared_reports_repository() -> SharedReportsRepository:
    """Get shared reports repository"""
    # TODO: Inject via DI container
    return AsyncPgSharedReportsRepository()


def get_csv_exporter() -> CSVExporter:
    """Get CSV exporter instance"""
    return CSVExporter()


def get_chart_renderer() -> ChartRenderer:
    """Get chart renderer instance"""
    if not MATPLOTLIB_AVAILABLE:
        raise HTTPException(status_code=503, detail="PNG chart rendering not available")
    return ChartRenderer()


def check_share_enabled():
    """Check if share functionality is enabled"""
    if not settings.SHARE_LINKS_ENABLED:
        raise HTTPException(status_code=403, detail="Share functionality is disabled")


def generate_share_token() -> str:
    """Generate secure share token"""
    return secrets.token_urlsafe(32)


@router.post("/create/{report_type}/{channel_id}")
async def create_share_link(
    report_type: str,
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    format: str = Query(default="csv", regex="^(csv|png)$"),
    ttl_hours: int = Query(default=24, ge=1, le=168),  # Max 1 week
    repository: SharedReportsRepository = Depends(get_shared_reports_repository),
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    request: Request = None,
    _: None = Depends(check_share_enabled),
    __: None = Depends(check_creation_rate_limit),
) -> ShareLinkResponse:
    """Create shareable link for analytics report"""

    # Validate report type
    valid_types = ["overview", "growth", "reach", "top_posts", "sources", "trending"]
    if report_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid report type. Must be one of: {valid_types}",
        )

    try:
        # Verify data exists
        timeout = aiohttp.ClientTimeout(total=30, connect=10)  # 30s total, 10s connect
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Note: AnalyticsV2Client manages session internally

            if report_type == "overview":
                data = await analytics_client.overview(channel_id, period)
            elif report_type == "growth":
                data = await analytics_client.growth(channel_id, period)
            elif report_type == "reach":
                data = await analytics_client.reach(channel_id, period)
            elif report_type == "top_posts":
                data = await analytics_client.top_posts(channel_id, period)
            elif report_type == "sources":
                data = await analytics_client.sources(channel_id, period)
            elif report_type == "trending":
                data = await analytics_client.trending(channel_id, period)

        if not data:
            raise HTTPException(status_code=404, detail="No analytics data available for sharing")

        # Generate share token and expiry
        share_token = generate_share_token()
        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        # Store shared report
        shared_report_id = await repository.create_shared_report(
            share_token=share_token,
            report_type=report_type,
            channel_id=channel_id,
            period=period,
            format=format,
            expires_at=expires_at,
        )

        # Build share URL
        base_url = str(request.base_url).rstrip("/")
        share_url = f"{base_url}/api/v2/share/report/{share_token}"

        logger.info(f"Created share link {share_token} for {report_type}/{channel_id}")

        return ShareLinkResponse(
            share_token=share_token,
            share_url=share_url,
            expires_at=expires_at,
            access_count=0,
        )

    except aiohttp.ClientError as e:
        logger.error(f"Failed to verify analytics data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except Exception as e:
        logger.error(f"Failed to create share link: {e}")
        raise HTTPException(status_code=500, detail="Share creation failed")


@router.get("/report/{share_token}")
async def access_shared_report(
    share_token: str,
    repository: SharedReportsRepository = Depends(get_shared_reports_repository),
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    csv_exporter: CSVExporter = Depends(get_csv_exporter),
    chart_renderer: ChartRenderer | None = Depends(get_chart_renderer),
    request: Request = None,
    _: None = Depends(check_share_enabled),
    __: None = Depends(check_access_rate_limit),
):
    """Access shared report by token"""
    try:
        # Get shared report
        shared_report = await repository.get_shared_report(share_token)

        if not shared_report:
            raise HTTPException(status_code=404, detail="Share link not found")

        # Check if expired
        if datetime.utcnow() > shared_report["expires_at"]:
            await repository.delete_shared_report(share_token)
            raise HTTPException(status_code=410, detail="Share link has expired")

        # Increment access count
        await repository.increment_access_count(share_token)

        # Fetch fresh analytics data
        channel_id = shared_report["channel_id"]
        period = shared_report["period"]
        report_type = shared_report["report_type"]
        format = shared_report["format"]

        timeout = aiohttp.ClientTimeout(total=30, connect=10)  # 30s total, 10s connect
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Note: AnalyticsV2Client manages session internally

            if report_type == "overview":
                data = await analytics_client.overview(channel_id, period)
            elif report_type == "growth":
                data = await analytics_client.growth(channel_id, period)
            elif report_type == "reach":
                data = await analytics_client.reach(channel_id, period)
            elif report_type == "top_posts":
                data = await analytics_client.top_posts(channel_id, period)
            elif report_type == "sources":
                data = await analytics_client.sources(channel_id, period)
            elif report_type == "trending":
                data = await analytics_client.trending(channel_id, period)

        if not data:
            raise HTTPException(status_code=404, detail="Analytics data no longer available")

        # Return data in requested format
        if format == "csv":
            if report_type == "overview":
                csv_content = csv_exporter.overview_to_csv(data)
            elif report_type == "growth":
                csv_content = csv_exporter.growth_to_csv(data)
            elif report_type == "reach":
                csv_content = csv_exporter.reach_to_csv(data)
            elif report_type == "top_posts":
                csv_content = csv_exporter.top_posts_to_csv(data)
            elif report_type == "sources":
                csv_content = csv_exporter.sources_to_csv(data)
            elif report_type == "trending":
                csv_content = csv_exporter.trending_to_csv(data)

            filename = csv_exporter.generate_filename(report_type, channel_id, period)

            import io

            from fastapi.responses import StreamingResponse

            return StreamingResponse(
                io.BytesIO(csv_content.getvalue().encode("utf-8")),
                media_type="text/csv",
                headers={"Content-Disposition": f'attachment; filename="{filename}"'},
            )

        elif format == "png":
            if not chart_renderer:
                raise HTTPException(status_code=503, detail="PNG rendering not available")

            try:
                if report_type == "growth":
                    png_bytes = chart_renderer.render_growth_chart(data)
                elif report_type == "reach":
                    png_bytes = chart_renderer.render_reach_chart(data)
                elif report_type == "sources":
                    png_bytes = chart_renderer.render_sources_chart(data)
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"PNG format not supported for {report_type}",
                    )

                filename = f"{report_type}_{channel_id}_{period}d_shared.png"

                from fastapi.responses import Response

                return Response(
                    content=png_bytes,
                    media_type="image/png",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'},
                )

            except ChartRenderingError as e:
                logger.error(f"Chart rendering failed: {e}")
                raise HTTPException(status_code=500, detail="Chart rendering failed")

        raise HTTPException(status_code=400, detail="Invalid format")

    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch analytics data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except Exception as e:
        logger.error(f"Failed to access shared report: {e}")
        raise HTTPException(status_code=500, detail="Access failed")


@router.get("/info/{share_token}")
async def get_share_info(
    share_token: str,
    repository: SharedReportsRepository = Depends(get_shared_reports_repository),
    _: None = Depends(check_share_enabled),
) -> SharedReportResponse:
    """Get share link information without accessing the report"""
    try:
        shared_report = await repository.get_shared_report(share_token)

        if not shared_report:
            raise HTTPException(status_code=404, detail="Share link not found")

        # Check if expired
        if datetime.utcnow() > shared_report["expires_at"]:
            await repository.delete_shared_report(share_token)
            raise HTTPException(status_code=410, detail="Share link has expired")

        return SharedReportResponse(
            report_type=shared_report["report_type"],
            channel_id=shared_report["channel_id"],
            period=shared_report["period"],
            created_at=shared_report["created_at"],
            expires_at=shared_report["expires_at"],
            access_count=shared_report["access_count"],
            format=shared_report["format"],
        )

    except Exception as e:
        logger.error(f"Failed to get share info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get share info")


@router.delete("/revoke/{share_token}")
async def revoke_share_link(
    share_token: str,
    repository: SharedReportsRepository = Depends(get_shared_reports_repository),
    _: None = Depends(check_share_enabled),
):
    """Revoke (delete) a share link"""
    try:
        shared_report = await repository.get_shared_report(share_token)

        if not shared_report:
            raise HTTPException(status_code=404, detail="Share link not found")

        await repository.delete_shared_report(share_token)

        logger.info(f"Revoked share link {share_token}")

        return {"message": "Share link revoked successfully"}

    except Exception as e:
        logger.error(f"Failed to revoke share link: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke share link")


@router.get("/cleanup")
async def cleanup_expired_shares(
    repository: SharedReportsRepository = Depends(get_shared_reports_repository),
    _: None = Depends(check_share_enabled),
):
    """Clean up expired share links (admin endpoint)"""
    try:
        deleted_count = await repository.cleanup_expired()

        logger.info(f"Cleaned up {deleted_count} expired share links")

        return {"deleted_count": deleted_count}

    except Exception as e:
        logger.error(f"Failed to cleanup expired shares: {e}")
        raise HTTPException(status_code=500, detail="Cleanup failed")
