"""Pipeline — orchestrates: fetch → analyze → persist → generate report"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.analyzer.fetcher import FetchResult, fetch_channel, parse_channel_identifier
from src.analyzer.metrics import AnalysisMetrics, compute_metrics
from src.cache import get_cached_analysis, set_cached_analysis
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
    progress_callback=None,
    lang: str = "en",
) -> tuple[AnalysisMetrics, str]:
    """
    Full analysis pipeline.

    Args:
        channel_input: Channel link, @username, or plain username.
        session: Database session.
        requested_by: Telegram user ID of requestor (optional).
        source: "bot" or "web".
        max_posts: Override max posts to fetch.
        progress_callback: Optional async callable(stage: str) for progress updates.

    Returns:
        (metrics, pdf_path) tuple.
    """
    repo = AnalysisRepository(session)
    identifier = parse_channel_identifier(channel_input)

    # ── Check cache first ──────────────────────────────────────────────
    cached = await get_cached_analysis(identifier)
    if cached and os.path.exists(cached.get("pdf_path", "")) and cached.get("lang", "en") == lang:
        logger.info(f"Returning cached result for @{identifier}")
        # Still create a request record for tracking
        request = await repo.create_request(
            identifier, requested_by=requested_by, source=source
        )
        request.status = "done"
        request.channel_title = cached.get("channel_title")
        request.completed_at = datetime.now(UTC)
        await session.commit()

        # Reconstruct minimal metrics from cache for the summary
        from src.analyzer.metrics import (
            ContentMix,
            EngagementBreakdown,
            PostingPattern,
            ViewsTrend,
        )

        eng_data = cached.get("engagement", {})
        metrics = AnalysisMetrics(
            channel_title=cached.get("channel_title", ""),
            channel_username=cached.get("channel_username"),
            channel_type=cached.get("channel_type", "channel"),
            member_count=cached.get("member_count", 0),
            description=None,
            total_posts=cached.get("total_posts", 0),
            total_views=cached.get("total_views", 0),
            total_forwards=cached.get("total_forwards", 0),
            total_reactions=cached.get("total_reactions", 0),
            total_replies=cached.get("total_replies", 0),
            avg_views=cached.get("avg_views", 0.0),
            avg_engagement_rate=cached.get("avg_engagement_rate", 0.0),
            avg_forwards_per_post=cached.get("avg_forwards_per_post", 0.0),
            avg_reactions_per_post=cached.get("avg_reactions_per_post", 0.0),
            engagement=EngagementBreakdown(
                median_views=eng_data.get("median_views", 0.0),
                virality_rate=eng_data.get("virality_rate", 0.0),
                interaction_rate=eng_data.get("interaction_rate", 0.0),
                avg_replies_per_post=eng_data.get("avg_replies_per_post", 0.0),
                pct_posts_with_links=eng_data.get("pct_posts_with_links", 0.0),
                views_per_member=eng_data.get("views_per_member", 0.0),
            ),
            posting_pattern=PostingPattern(
                avg_posts_per_day=cached.get("avg_posts_per_day", 0.0),
                most_active_hour=cached.get("most_active_hour"),
                most_active_weekday=cached.get("most_active_weekday"),
            ),
            content_mix=ContentMix(
                pct_text_only=cached.get("pct_text_only", 0),
                pct_photo=cached.get("pct_photo", 0),
                pct_video=cached.get("pct_video", 0),
                pct_document=cached.get("pct_document", 0),
                pct_other=cached.get("pct_other", 0),
            ),
            views_trend=ViewsTrend(),
            top_posts_by_views=[],
            top_posts_by_engagement=[],
            date_from=None,
            date_to=None,
            analysis_period_days=cached.get("analysis_period_days", 0),
            days_since_last_post=cached.get("days_since_last_post", 0),
            activity_status=cached.get("activity_status", "active"),
            posting_frequency=cached.get("posting_frequency", "moderate"),
            data_note="Cached result.",
        )
        return metrics, cached["pdf_path"]

    # ── Full pipeline ──────────────────────────────────────────────────

    # 1. Create request record
    request = await repo.create_request(identifier, requested_by=requested_by, source=source)
    await session.commit()

    try:
        # 2. Fetch channel data
        if progress_callback:
            await progress_callback("Fetching channel data...")
        logger.info(f"[analysis:{request.id}] Fetching @{identifier}...")
        result: FetchResult = await fetch_channel(identifier, max_posts=max_posts)

        await repo.set_request_running(request.id, result.channel.channel_id, result.channel.title)
        await session.commit()

        # 3. Save channel snapshot
        if progress_callback:
            await progress_callback(f"Fetched {len(result.posts)} posts, saving...")
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
        if progress_callback:
            await progress_callback("Computing metrics...")
        logger.info(f"[analysis:{request.id}] Computing metrics for {len(result.posts)} posts...")
        metrics = compute_metrics(result)

        # 6. Generate PDF report
        if progress_callback:
            await progress_callback("Generating PDF report...")
        pdf_path = generate_pdf_report(metrics, analysis_id=request.id, lang=lang)

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

        # 8. Cache result
        await set_cached_analysis(
            identifier,
            analysis_id=request.id,
            pdf_path=pdf_path,
            summary={
                "channel_title": metrics.channel_title,
                "channel_username": metrics.channel_username,
                "channel_type": metrics.channel_type,
                "member_count": metrics.member_count,
                "total_posts": metrics.total_posts,
                "total_views": metrics.total_views,
                "total_forwards": metrics.total_forwards,
                "total_reactions": metrics.total_reactions,
                "total_replies": metrics.total_replies,
                "avg_views": metrics.avg_views,
                "avg_engagement_rate": metrics.avg_engagement_rate,
                "avg_forwards_per_post": metrics.avg_forwards_per_post,
                "avg_reactions_per_post": metrics.avg_reactions_per_post,
                "avg_posts_per_day": metrics.posting_pattern.avg_posts_per_day,
                "most_active_hour": metrics.posting_pattern.most_active_hour,
                "most_active_weekday": metrics.posting_pattern.most_active_weekday,
                "analysis_period_days": metrics.analysis_period_days,
                "days_since_last_post": metrics.days_since_last_post,
                "activity_status": metrics.activity_status,
                "posting_frequency": metrics.posting_frequency,
                "lang": lang,
                "pct_text_only": metrics.content_mix.pct_text_only,
                "pct_photo": metrics.content_mix.pct_photo,
                "pct_video": metrics.content_mix.pct_video,
                "pct_document": metrics.content_mix.pct_document,
                "pct_other": metrics.content_mix.pct_other,
                "engagement": {
                    "median_views": metrics.engagement.median_views,
                    "virality_rate": metrics.engagement.virality_rate,
                    "interaction_rate": metrics.engagement.interaction_rate,
                    "avg_replies_per_post": metrics.engagement.avg_replies_per_post,
                    "pct_posts_with_links": metrics.engagement.pct_posts_with_links,
                    "views_per_member": metrics.engagement.views_per_member,
                },
            },
        )

        logger.info(f"[analysis:{request.id}] Done → {pdf_path}")
        return metrics, pdf_path

    except Exception as e:
        logger.error(f"[analysis:{request.id}] Failed: {e}")
        await repo.set_request_failed(request.id, str(e))
        await session.commit()
        raise
