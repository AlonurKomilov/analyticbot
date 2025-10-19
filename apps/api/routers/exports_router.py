"""
Analytics Export API v2 Endpoints
Provides CSV and PNG export functionality for analytics data
"""

import io
import logging
from datetime import datetime

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from apps.shared.clients.analytics_client import AnalyticsClient

# ✅ PHASE 1 FIX: Import from apps.shared.exports (circular dependency fix)
from apps.shared.exports.csv_v2 import CSVExporter
from apps.shared.factory import get_repository_factory
from apps.shared.protocols import ChartServiceProtocol
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exports", tags=["Exports"])


# Response models
class ExportStatus(BaseModel):
    success: bool
    message: str
    filename: str | None = None
    size_bytes: int | None = None


def get_analytics_client() -> AnalyticsClient:
    """Get analytics client instance"""
    return AnalyticsClient(settings.ANALYTICS_V2_BASE_URL)


def get_csv_exporter() -> CSVExporter:
    """Get CSV exporter instance"""
    return CSVExporter()


def get_chart_service() -> ChartServiceProtocol:
    """Get chart service instance"""
    factory = get_repository_factory()
    return factory.get_chart_service()


def check_export_enabled():
    """Check if export functionality is enabled"""
    if not settings.EXPORT_ENABLED:
        raise HTTPException(status_code=403, detail="Export functionality is disabled")


# CSV Export Endpoints


@router.get("/csv/overview/{channel_id}")
async def export_overview_csv(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
    csv_exporter: CSVExporter = Depends(get_csv_exporter),
    _: None = Depends(check_export_enabled),
):
    """Export channel overview as CSV"""
    try:
        # Fetch analytics data
        overview_data = await analytics_client.overview(channel_id, period)

        if not overview_data:
            raise HTTPException(status_code=404, detail="Analytics data not found")

        # Generate CSV
        csv_content = csv_exporter.overview_to_csv(overview_data)
        filename = csv_exporter.generate_filename("overview", channel_id, period)

        # Create bytes stream for StreamingResponse
        csv_bytes = io.BytesIO(csv_content.getvalue().encode("utf-8"))

        return StreamingResponse(
            csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch analytics data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except Exception as e:
        logger.error(f"CSV export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/csv/growth/{channel_id}")
async def export_growth_csv(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
    csv_exporter: CSVExporter = Depends(get_csv_exporter),
    _: None = Depends(check_export_enabled),
):
    """Export growth data as CSV"""
    try:
        growth_data = await analytics_client.growth(channel_id, period)

        if not growth_data:
            raise HTTPException(status_code=404, detail="Growth data not found")

        csv_content = csv_exporter.growth_to_csv(growth_data)
        filename = csv_exporter.generate_filename("growth", channel_id, period)

        # Create bytes stream for StreamingResponse
        csv_bytes = io.BytesIO(csv_content.getvalue().encode("utf-8"))

        return StreamingResponse(
            csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch growth data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except Exception as e:
        logger.error(f"Growth export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/csv/reach/{channel_id}")
async def export_reach_csv(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
    csv_exporter: CSVExporter = Depends(get_csv_exporter),
    _: None = Depends(check_export_enabled),
):
    """Export reach data as CSV"""
    try:
        reach_data = await analytics_client.reach(channel_id, period)

        if not reach_data:
            raise HTTPException(status_code=404, detail="Reach data not found")

        csv_content = csv_exporter.reach_to_csv(reach_data)
        filename = csv_exporter.generate_filename("reach", channel_id, period)

        # Create bytes stream for StreamingResponse
        csv_bytes = io.BytesIO(csv_content.getvalue().encode("utf-8"))

        return StreamingResponse(
            csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch reach data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except Exception as e:
        logger.error(f"Reach export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/csv/sources/{channel_id}")
async def export_sources_csv(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
    csv_exporter: CSVExporter = Depends(get_csv_exporter),
    _: None = Depends(check_export_enabled),
):
    """Export traffic sources as CSV"""
    try:
        sources_data = await analytics_client.sources(channel_id, period)

        if not sources_data:
            raise HTTPException(status_code=404, detail="Sources data not found")

        csv_content = csv_exporter.sources_to_csv(sources_data)
        filename = csv_exporter.generate_filename("sources", channel_id, period)

        # Create bytes stream for StreamingResponse
        csv_bytes = io.BytesIO(csv_content.getvalue().encode("utf-8"))

        return StreamingResponse(
            csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch sources data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except Exception as e:
        logger.error(f"Sources export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


# PNG Chart Export Endpoints


@router.get("/png/growth/{channel_id}")
async def export_growth_chart(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
    chart_service: ChartServiceProtocol = Depends(get_chart_service),
    _: None = Depends(check_export_enabled),
):
    """Export growth chart as PNG"""
    try:
        growth_data = await analytics_client.growth(channel_id, period)

        if not growth_data:
            raise HTTPException(status_code=404, detail="Growth data not found")

        # Render chart - convert Pydantic model to dict
        chart_bytes = chart_service.render_growth_chart(growth_data.model_dump())

        filename = f"growth_{channel_id}_{period}d_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        return Response(
            content=chart_bytes,
            media_type="image/png",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch growth data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except Exception as e:
        logger.error(f"PNG export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/png/reach/{channel_id}")
async def export_reach_chart(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
    chart_service: ChartServiceProtocol = Depends(get_chart_service),
    _: None = Depends(check_export_enabled),
):
    """Export reach chart as PNG"""
    try:
        reach_data = await analytics_client.reach(channel_id, period)

        if not reach_data:
            raise HTTPException(status_code=404, detail="Reach data not found")

        # Render chart - convert Pydantic model to dict
        chart_bytes = chart_service.render_reach_chart(reach_data.model_dump())

        filename = f"reach_{channel_id}_{period}d_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        return Response(
            content=chart_bytes,
            media_type="image/png",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch reach data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except Exception as e:
        logger.error(f"PNG export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/png/sources/{channel_id}")
async def export_sources_chart(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
    chart_service: ChartServiceProtocol = Depends(get_chart_service),
    _: None = Depends(check_export_enabled),
):
    """Export sources chart as PNG"""
    try:
        sources_data = await analytics_client.sources(channel_id, period)

        if not sources_data:
            raise HTTPException(status_code=404, detail="Sources data not found")

        # Render chart - convert Pydantic model to dict
        chart_bytes = chart_service.render_sources_chart(sources_data.model_dump())

        filename = f"sources_{channel_id}_{period}d_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        return Response(
            content=chart_bytes,
            media_type="image/png",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch sources data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except Exception as e:
        logger.error(f"PNG export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


# System Status Endpoint


@router.get("/status")
async def export_status():
    """Get export system status"""

    # Check chart service availability
    factory = get_repository_factory()
    chart_service = factory.get_chart_service()

    return {
        "exports_enabled": settings.EXPORT_ENABLED,
        "csv_available": True,
        "png_available": chart_service.is_available(),
        "max_export_size_mb": settings.MAX_EXPORT_SIZE_MB,
        "rate_limits": {
            "per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "per_hour": settings.RATE_LIMIT_PER_HOUR,
        },
    }
