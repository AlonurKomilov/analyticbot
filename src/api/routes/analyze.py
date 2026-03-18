"""API route: submit a channel for analysis"""

from __future__ import annotations

import logging
from dataclasses import asdict

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from src.analyzer.fetcher import parse_channel_identifier
from src.analyzer.pipeline import run_analysis
from src.db.repository import AnalysisRepository
from src.db.session import async_session

logger = logging.getLogger(__name__)
router = APIRouter()


class AnalyzeRequest(BaseModel):
    channel: str = Field(..., description="Channel link, @username, or plain username")
    max_posts: int = Field(default=500, ge=10, le=2000)


class AnalyzeResponse(BaseModel):
    analysis_id: int
    status: str
    message: str


class AnalysisResultResponse(BaseModel):
    analysis_id: int
    status: str
    channel_title: str | None = None
    member_count: int | None = None
    total_posts: int | None = None
    total_views: int | None = None
    avg_views: float | None = None
    avg_engagement_rate: float | None = None
    avg_posts_per_day: float | None = None
    report_pdf_path: str | None = None
    error_message: str | None = None


async def _run_in_background(channel: str, request_id: int, max_posts: int) -> None:
    """Background task that runs the full analysis pipeline."""
    try:
        async with async_session() as session:
            await run_analysis(channel, session=session, source="web", max_posts=max_posts)
    except Exception as e:
        logger.error(f"Background analysis {request_id} failed: {e}", exc_info=True)


@router.post("/analyze", response_model=AnalyzeResponse)
async def submit_analysis(body: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Submit a channel for analysis.

    Returns immediately with an analysis_id. Check status via GET /api/analysis/{id}.
    """
    try:
        username = parse_channel_identifier(body.channel)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid channel link or username")

    # Create a pending request
    async with async_session() as session:
        repo = AnalysisRepository(session)
        request = await repo.create_request(username, source="web")
        await session.commit()
        request_id = request.id

    # Run analysis in background
    background_tasks.add_task(_run_in_background, body.channel, request_id, body.max_posts)

    return AnalyzeResponse(
        analysis_id=request_id,
        status="pending",
        message=f"Analysis for @{username} has been queued. Poll GET /api/analysis/{request_id} for results.",
    )


@router.get("/analysis/{analysis_id}", response_model=AnalysisResultResponse)
async def get_analysis(analysis_id: int):
    """Get the status and results of an analysis."""
    async with async_session() as session:
        repo = AnalysisRepository(session)
        request = await repo.get_request(analysis_id)

        if not request:
            raise HTTPException(status_code=404, detail="Analysis not found")

        response = AnalysisResultResponse(
            analysis_id=request.id,
            status=request.status,
            channel_title=request.channel_title,
            error_message=request.error_message,
        )

        if request.status == "done":
            result = await repo.get_result(analysis_id)
            if result:
                response.member_count = result.member_count
                response.total_posts = result.total_posts
                response.total_views = result.total_views
                response.avg_views = result.avg_views
                response.avg_engagement_rate = result.avg_engagement_rate
                response.avg_posts_per_day = result.avg_posts_per_day
                response.report_pdf_path = result.report_pdf_path

        return response
