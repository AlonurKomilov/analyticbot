"""Pipeline — orchestrates: fetch → analyze → persist → generate report"""

from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.analyzer.fetcher import FetchResult, fetch_channel, parse_channel_identifier
from src.analyzer.metrics import AnalysisMetrics, compute_metrics
from src.db.models import AnalysisResult, ChannelSnapshot, PostRecord
from src.db.repository import AnalysisRepository
from src.reports.pdf import generate_pdf_report

logger = logging.getLogger(__name__)


async def run_analysis(
    channel_input: str,
    session: AsyncSession,
    requested_by: int | None = None,
    source: str = "bot",
    max_posts: int | None = None,
) -> tuple[AnalysisMetrics, str]:
    """
    Full analysis pipeline.

    Args:
        channel_input: Channel link, @username, or plain username.
        session: Database session.
        requested_by: Telegram user ID of requestor (optional).
        source: "bot" or "web".
        max_posts: Override max posts to fetch.

    Returns:
        (metrics, pdf_path) tuple.
    """
    repo = AnalysisRepository(session)

    # 1. Create request record
    identifier = parse_channel_identifier(channel_input)
    request = await repo.create_request(identifier, requested_by=requested_by, source=source)
    await session.commit()

    try:
        # 2. Fetch channel data
        logger.info(f"[analysis:{request.id}] Fetching @{identifier}...")
        result: FetchResult = await fetch_channel(identifier, max_posts=max_posts)

        await repo.set_request_running(request.id, result.channel.channel_id, result.channel.title)
        await session.commit()

        # 3. Save channel snapshot
        snapshot = ChannelSnapshot(
            analysis_id=request.id,
            channel_id=result.channel.channel_id,
            title=result.channel.title,
            username=result.channel.username,
            description=result.channel.description,
            member_count=result.channel.member_count,
            channel_type=result.channel.channel_type,
        )
        await repo.save_snapshot(snapshot)

        # 4. Save posts
        post_records = [
            PostRecord(
                analysis_id=request.id,
                channel_id=result.channel.channel_id,
                message_id=p.message_id,
                date=p.date,
                text=p.text,
                views=p.views,
                forwards=p.forwards,
                replies=p.replies,
                reactions_count=p.reactions_count,
                media_type=p.media_type,
                has_link=p.has_link,
            )
            for p in result.posts
        ]
        await repo.save_posts(post_records)
        await session.commit()

        # 5. Compute metrics
        logger.info(f"[analysis:{request.id}] Computing metrics for {len(result.posts)} posts...")
        metrics = compute_metrics(result)

        # 6. Generate PDF report
        pdf_path = generate_pdf_report(metrics, analysis_id=request.id)

        # 7. Save analysis result
        analysis_result = AnalysisResult(
            analysis_id=request.id,
            total_posts=metrics.total_posts,
            total_views=metrics.total_views,
            total_forwards=metrics.total_forwards,
            total_reactions=metrics.total_reactions,
            avg_views=metrics.avg_views,
            avg_engagement_rate=metrics.avg_engagement_rate,
            member_count=metrics.member_count,
            avg_posts_per_day=metrics.posting_pattern.avg_posts_per_day,
            most_active_hour=metrics.posting_pattern.most_active_hour,
            most_active_weekday=metrics.posting_pattern.most_active_weekday,
            pct_text_only=metrics.content_mix.pct_text_only,
            pct_photo=metrics.content_mix.pct_photo,
            pct_video=metrics.content_mix.pct_video,
            report_pdf_path=pdf_path,
        )
        await repo.save_result(analysis_result)

        await repo.set_request_done(request.id)
        await session.commit()

        logger.info(f"[analysis:{request.id}] Done → {pdf_path}")
        return metrics, pdf_path

    except Exception as e:
        logger.error(f"[analysis:{request.id}] Failed: {e}")
        await repo.set_request_failed(request.id, str(e))
        await session.commit()
        raise
