"""
Analytics Export API v2 Endpoints
Provides CSV and PNG export functionality for analytics data
"""

import asyncio
import logging
import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
import aiohttp

from config.settings import Settings
from apps.api.exports.csv_v2 import CSVExporter
from infra.rendering.charts import ChartRenderer, ChartRenderingError, MATPLOTLIB_AVAILABLE
from apps.bot.clients.analytics_v2_client import AnalyticsV2Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/exports", tags=["exports"])

# Response models
class ExportStatus(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    size_bytes: Optional[int] = None


def get_analytics_client() -> AnalyticsV2Client:
    """Get analytics client instance"""
    settings = Settings()
    return AnalyticsV2Client(settings.ANALYTICS_API_URL)


def get_csv_exporter() -> CSVExporter:
    """Get CSV exporter instance"""
    return CSVExporter()


def get_chart_renderer() -> ChartRenderer:
    """Get chart renderer instance"""
    if not MATPLOTLIB_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="PNG chart rendering not available. Install matplotlib to enable."
        )
    return ChartRenderer()


def check_export_enabled():
    """Check if export functionality is enabled"""
    settings = Settings()
    if not settings.EXPORT_ENABLED:
        raise HTTPException(
            status_code=403,
            detail="Export functionality is disabled"
        )


@router.get("/csv/overview/{channel_id}")
async def export_overview_csv(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    csv_exporter: CSVExporter = Depends(get_csv_exporter),
    _: None = Depends(check_export_enabled)
):
    """Export channel overview as CSV"""
    try:
        # Fetch analytics data
        async with aiohttp.ClientSession() as session:
            analytics_client.session = session
            overview_data = await analytics_client.get_overview(channel_id, period)
        
        if not overview_data:
            raise HTTPException(status_code=404, detail="Analytics data not found")
        
        # Generate CSV
        csv_content = csv_exporter.overview_to_csv(overview_data)
        filename = csv_exporter.get_filename("overview", channel_id, period)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
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
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    csv_exporter: CSVExporter = Depends(get_csv_exporter),
    _: None = Depends(check_export_enabled)
):
    """Export growth data as CSV"""
    try:
        async with aiohttp.ClientSession() as session:
            analytics_client.session = session
            growth_data = await analytics_client.get_growth(channel_id, period)
        
        if not growth_data:
            raise HTTPException(status_code=404, detail="Growth data not found")
        
        csv_content = csv_exporter.growth_to_csv(growth_data)
        filename = csv_exporter.get_filename("growth", channel_id, period)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
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
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    csv_exporter: CSVExporter = Depends(get_csv_exporter),
    _: None = Depends(check_export_enabled)
):
    """Export reach data as CSV"""
    try:
        async with aiohttp.ClientSession() as session:
            analytics_client.session = session
            reach_data = await analytics_client.get_reach(channel_id, period)
        
        if not reach_data:
            raise HTTPException(status_code=404, detail="Reach data not found")
        
        csv_content = csv_exporter.reach_to_csv(reach_data)
        filename = csv_exporter.get_filename("reach", channel_id, period)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
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
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    csv_exporter: CSVExporter = Depends(get_csv_exporter),
    _: None = Depends(check_export_enabled)
):
    """Export traffic sources as CSV"""
    try:
        async with aiohttp.ClientSession() as session:
            analytics_client.session = session
            sources_data = await analytics_client.get_sources(channel_id, period)
        
        if not sources_data:
            raise HTTPException(status_code=404, detail="Sources data not found")
        
        csv_content = csv_exporter.sources_to_csv(sources_data)
        filename = csv_exporter.get_filename("sources", channel_id, period)
        
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch sources data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except Exception as e:
        logger.error(f"Sources export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/png/growth/{channel_id}")
async def export_growth_chart(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    chart_renderer: ChartRenderer = Depends(get_chart_renderer),
    _: None = Depends(check_export_enabled)
):
    """Export growth chart as PNG"""
    try:
        async with aiohttp.ClientSession() as session:
            analytics_client.session = session
            growth_data = await analytics_client.get_growth(channel_id, period)
        
        if not growth_data:
            raise HTTPException(status_code=404, detail="Growth data not found")
        
        # Render chart
        png_bytes = chart_renderer.render_growth_chart(growth_data)
        
        filename = f"growth_{channel_id}_{period}d_{datetime.now().strftime('%Y%m%d')}.png"
        
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch growth data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except ChartRenderingError as e:
        logger.error(f"Chart rendering failed: {e}")
        raise HTTPException(status_code=500, detail="Chart rendering failed")
    except Exception as e:
        logger.error(f"PNG export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/png/reach/{channel_id}")
async def export_reach_chart(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    chart_renderer: ChartRenderer = Depends(get_chart_renderer),
    _: None = Depends(check_export_enabled)
):
    """Export reach distribution chart as PNG"""
    try:
        async with aiohttp.ClientSession() as session:
            analytics_client.session = session
            reach_data = await analytics_client.get_reach(channel_id, period)
        
        if not reach_data:
            raise HTTPException(status_code=404, detail="Reach data not found")
        
        # Render chart
        png_bytes = chart_renderer.render_reach_chart(reach_data)
        
        filename = f"reach_{channel_id}_{period}d_{datetime.now().strftime('%Y%m%d')}.png"
        
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch reach data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except ChartRenderingError as e:
        logger.error(f"Chart rendering failed: {e}")
        raise HTTPException(status_code=500, detail="Chart rendering failed")
    except Exception as e:
        logger.error(f"PNG export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/png/sources/{channel_id}")
async def export_sources_chart(
    channel_id: str,
    period: int = Query(default=30, ge=1, le=365),
    analytics_client: AnalyticsV2Client = Depends(get_analytics_client),
    chart_renderer: ChartRenderer = Depends(get_chart_renderer),
    _: None = Depends(check_export_enabled)
):
    """Export traffic sources pie chart as PNG"""
    try:
        async with aiohttp.ClientSession() as session:
            analytics_client.session = session
            sources_data = await analytics_client.get_sources(channel_id, period)
        
        if not sources_data:
            raise HTTPException(status_code=404, detail="Sources data not found")
        
        # Render chart
        png_bytes = chart_renderer.render_sources_chart(sources_data)
        
        filename = f"sources_{channel_id}_{period}d_{datetime.now().strftime('%Y%m%d')}.png"
        
        return Response(
            content=png_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch sources data: {e}")
        raise HTTPException(status_code=502, detail="Analytics service unavailable")
    except ChartRenderingError as e:
        logger.error(f"Chart rendering failed: {e}")
        raise HTTPException(status_code=500, detail="Chart rendering failed")
    except Exception as e:
        logger.error(f"PNG export failed: {e}")
        raise HTTPException(status_code=500, detail="Export failed")


@router.get("/status")
async def export_status():
    """Get export system status"""
    settings = Settings()
    
    return {
        "exports_enabled": settings.EXPORT_ENABLED,
        "csv_available": True,
        "png_available": MATPLOTLIB_AVAILABLE,
        "max_export_size_mb": settings.MAX_EXPORT_SIZE_MB,
        "rate_limits": {
            "per_minute": settings.RATE_LIMIT_PER_MINUTE,
            "per_hour": settings.RATE_LIMIT_PER_HOUR
        }
    }
