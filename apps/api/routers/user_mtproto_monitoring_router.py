"""
User MTProto Collection Monitoring Router

Provides real-time monitoring endpoints for users to track their MTProto
data collection progress, session status, and worker activity.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from apps.api.middleware.auth import get_current_user_id
from apps.di import get_container, get_user_mtproto_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/user-mtproto/monitoring",
    tags=["MTProto Monitoring"],
)


# ============================================================================
# RESPONSE MODELS
# ============================================================================


class ChannelCollectionStats(BaseModel):
    """Statistics for a single channel"""

    channel_id: int
    channel_name: str
    total_posts: int
    latest_post_date: datetime | None
    oldest_post_date: datetime | None
    last_collected: datetime | None
    collection_enabled: bool


class CollectionProgress(BaseModel):
    """Overall collection progress for user"""

    total_channels: int
    active_channels: int
    total_posts_collected: int
    collection_active: bool
    last_collection_time: datetime | None
    next_collection_eta: datetime | None
    estimated_completion_percent: float = Field(
        description="Estimated percentage of data collected (0-100)"
    )


class WorkerStatus(BaseModel):
    """Status of automatic worker service"""

    worker_running: bool
    worker_interval_minutes: int
    last_run: datetime | None
    next_run: datetime | None
    runs_today: int
    errors_today: int

    # Real-time progress tracking
    currently_collecting: bool = False
    current_channel: str | None = None
    channels_processed: int = 0
    channels_total: int = 0
    messages_collected_current_run: int = 0
    errors_current_run: int = 0
    collection_start_time: datetime | None = None
    estimated_time_remaining: int | None = None  # seconds


class SessionHealth(BaseModel):
    """Health status of MTProto session"""

    session_valid: bool
    session_connected: bool
    session_last_used: datetime | None
    api_calls_today: int
    rate_limit_hits_today: int
    connection_errors_today: int
    health_score: float = Field(description="Overall health score (0-100)", ge=0, le=100)


class MTProtoMonitoringResponse(BaseModel):
    """Complete monitoring data for user's MTProto"""

    user_id: int
    mtproto_enabled: bool
    session_health: SessionHealth
    collection_progress: CollectionProgress
    worker_status: WorkerStatus
    channels: list[ChannelCollectionStats]
    timestamp: datetime


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get(
    "/overview",
    response_model=MTProtoMonitoringResponse,
    summary="Get comprehensive MTProto monitoring overview",
    description=(
        "Returns complete monitoring data including session health, "
        "collection progress, and worker status"
    ),
)
async def get_monitoring_overview(
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """
    Get comprehensive monitoring overview for user's MTProto collection

    Returns:
    - Session health and connection status
    - Collection progress and statistics
    - Worker status and scheduling
    - Per-channel collection statistics
    """
    try:
        container = get_container()
        pool = await container.database.asyncpg_pool()

        # Get user's MTProto credentials
        async with pool.acquire() as conn:
            creds = await conn.fetchrow(
                (
                    "SELECT mtproto_enabled, telegram_phone, session_string "
                    "FROM user_bot_credentials WHERE user_id = $1"
                ),
                user_id,
            )

            if not creds:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="MTProto not configured for this user",
                )

            mtproto_enabled = creds["mtproto_enabled"]
            has_session = creds["session_string"] is not None

            # Get session health
            session_health = await _get_session_health(conn, user_id, has_session)

            # Get collection progress
            collection_progress = await _get_collection_progress(conn, user_id)

            # Get worker status
            worker_status = await _get_worker_status(user_id)

            # Get per-channel statistics
            channels = await _get_channel_stats(conn, user_id)

        return MTProtoMonitoringResponse(
            user_id=user_id,
            mtproto_enabled=mtproto_enabled,
            session_health=session_health,
            collection_progress=collection_progress,
            worker_status=worker_status,
            channels=channels,
            timestamp=datetime.now(UTC),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitoring overview for user {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get monitoring data: {str(e)}",
        )


@router.get(
    "/session-health",
    response_model=SessionHealth,
    summary="Get MTProto session health status",
    description="Returns detailed health metrics for the user's MTProto session",
)
async def get_session_health(
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """Get detailed session health metrics"""
    try:
        container = get_container()
        pool = await container.database.asyncpg_pool()

        async with pool.acquire() as conn:
            creds = await conn.fetchrow(
                "SELECT session_string FROM user_bot_credentials WHERE user_id = $1",
                user_id,
            )

            if not creds:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="MTProto not configured",
                )

            has_session = creds["session_string"] is not None
            return await _get_session_health(conn, user_id, has_session)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session health for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session health: {str(e)}",
        )


@router.get(
    "/collection-progress",
    response_model=CollectionProgress,
    summary="Get collection progress statistics",
    description="Returns progress metrics for data collection across all channels",
)
async def get_collection_progress(
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """Get collection progress statistics"""
    try:
        container = get_container()
        pool = await container.database.asyncpg_pool()

        async with pool.acquire() as conn:
            return await _get_collection_progress(conn, user_id)

    except Exception as e:
        logger.error(f"Error getting collection progress for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get collection progress: {str(e)}",
        )


@router.get(
    "/channels",
    response_model=list[ChannelCollectionStats],
    summary="Get per-channel collection statistics",
    description="Returns detailed collection stats for each channel",
)
async def get_channel_statistics(
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    """Get detailed statistics for each channel"""
    try:
        container = get_container()
        pool = await container.database.asyncpg_pool()

        async with pool.acquire() as conn:
            return await _get_channel_stats(conn, user_id)

    except Exception as e:
        logger.error(f"Error getting channel stats for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get channel statistics: {str(e)}",
        )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


async def _get_session_health(conn, user_id: int, has_session: bool) -> SessionHealth:
    """Calculate session health metrics"""

    # Check if session is actively connected
    session_connected = False
    session_last_used = None

    if has_session:
        try:
            mtproto_service = await get_user_mtproto_service()
            session_connected = mtproto_service.is_user_connected(user_id)
            if session_connected:
                # Get client to access last_used
                client = await mtproto_service.get_user_client(user_id)
                if client:
                    session_last_used = client.last_used
        except Exception as e:
            logger.warning(f"Error checking session connection: {e}")

    # Get today's activity from audit log (if exists)
    api_calls_today = 0
    rate_limit_hits_today = 0
    connection_errors_today = 0

    try:
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

        audit_stats = await conn.fetchrow(
            """
            SELECT
                COUNT(*) FILTER (WHERE action = 'api_call') as api_calls,
                COUNT(*) FILTER (WHERE action LIKE '%rate_limit%') as rate_limits,
                COUNT(*) FILTER (WHERE action LIKE '%error%') as errors
            FROM mtproto_audit_log
            WHERE user_id = $1 AND timestamp >= $2
            """,
            user_id,
            today_start,
        )

        if audit_stats:
            api_calls_today = audit_stats["api_calls"] or 0
            rate_limit_hits_today = audit_stats["rate_limits"] or 0
            connection_errors_today = audit_stats["errors"] or 0

    except Exception as e:
        logger.debug(f"Could not get audit stats (table might not exist): {e}")

    # Calculate health score (0-100)
    health_score = 100.0

    if not has_session:
        health_score = 0.0
    else:
        # Deduct points for issues
        if not session_connected:
            health_score -= 20
        if rate_limit_hits_today > 0:
            health_score -= min(30, rate_limit_hits_today * 5)
        if connection_errors_today > 0:
            health_score -= min(20, connection_errors_today * 10)
        if session_last_used:
            # Make session_last_used timezone-aware if it isn't
            if session_last_used.tzinfo is None:
                session_last_used = session_last_used.replace(tzinfo=UTC)
            seconds_since = (datetime.now(UTC) - session_last_used).total_seconds()
            if seconds_since > 86400:
                health_score -= 10  # Not used in last 24 hours

    health_score = max(0.0, min(100.0, health_score))

    return SessionHealth(
        session_valid=has_session,
        session_connected=session_connected,
        session_last_used=session_last_used,
        api_calls_today=api_calls_today,
        rate_limit_hits_today=rate_limit_hits_today,
        connection_errors_today=connection_errors_today,
        health_score=health_score,
    )


async def _get_collection_progress(conn, user_id: int) -> CollectionProgress:
    """Calculate collection progress metrics"""

    # Get channel count
    channel_stats = await conn.fetchrow(
        """
        SELECT
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE EXISTS (
                SELECT 1 FROM channel_mtproto_settings
                WHERE channel_id = channels.id AND mtproto_enabled = true
            )) as active
        FROM channels
        WHERE user_id = $1
        """,
        user_id,
    )

    total_channels = channel_stats["total"] or 0
    active_channels = channel_stats["active"] or 0

    # Get total posts collected
    posts_stats = await conn.fetchrow(
        """
        SELECT
            COUNT(*) as total_posts
        FROM posts p
        JOIN channels c ON p.channel_id = c.id
        WHERE c.user_id = $1
        """,
        user_id,
    )

    total_posts = posts_stats["total_posts"] or 0

    # Get ACTUAL last collection time from audit log (not post date!)
    last_collection_row = await conn.fetchrow(
        """
        SELECT timestamp as last_collected
        FROM mtproto_audit_log
        WHERE user_id = $1 AND action = 'collection_end'
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        user_id,
    )

    last_collected = last_collection_row["last_collected"] if last_collection_row else None

    # Estimate completion percentage
    # This is a rough estimate based on post activity
    estimated_percent = 0.0
    if total_posts > 0:
        # If we have posts, estimate 50% minimum
        # Add more based on recent activity
        estimated_percent = 50.0
        if last_collected:
            # Make last_collected timezone-aware if it isn't
            if last_collected.tzinfo is None:
                last_collected = last_collected.replace(tzinfo=UTC)
            hours_since = (datetime.now(UTC) - last_collected).total_seconds() / 3600
            if hours_since < 1:
                estimated_percent = 95.0
            elif hours_since < 24:
                estimated_percent = 75.0
            else:
                estimated_percent = 60.0

    # Check if collection is currently active (posts in last hour)
    collection_active = False
    if last_collected:
        # Make last_collected timezone-aware if it isn't
        if last_collected.tzinfo is None:
            last_collected = last_collected.replace(tzinfo=UTC)
        minutes_since = (datetime.now(UTC) - last_collected).total_seconds() / 60
        collection_active = minutes_since < 60

    # Estimate next collection (every 10 minutes by default)
    next_collection_eta = None
    if last_collected:
        # Make last_collected timezone-aware if it isn't
        if last_collected.tzinfo is None:
            last_collected = last_collected.replace(tzinfo=UTC)
        next_collection_eta = last_collected + timedelta(minutes=10)
        if next_collection_eta < datetime.now(UTC):
            next_collection_eta = datetime.now(UTC) + timedelta(minutes=10)

    return CollectionProgress(
        total_channels=total_channels,
        active_channels=active_channels,
        total_posts_collected=total_posts,
        collection_active=collection_active,
        last_collection_time=last_collected,
        next_collection_eta=next_collection_eta,
        estimated_completion_percent=estimated_percent,
    )


async def _get_worker_status(user_id: int) -> WorkerStatus:
    """Get automatic worker status from audit logs"""

    # Check if workers are running
    import subprocess

    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
        worker_running = "mtproto.worker" in result.stdout
    except Exception:
        worker_running = False

    # Default worker interval is 10 minutes
    worker_interval = 10

    # Get status from audit logs
    container = get_container()
    pool = await container.database.asyncpg_pool()

    async with pool.acquire() as conn:
        # Get last collection_start event
        last_start = await conn.fetchrow(
            """
            SELECT timestamp, metadata
            FROM mtproto_audit_log
            WHERE user_id = $1 AND action = 'collection_start'
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            user_id,
        )

        # Get last collection_end event
        last_end = await conn.fetchrow(
            """
            SELECT timestamp, metadata
            FROM mtproto_audit_log
            WHERE user_id = $1 AND action = 'collection_end'
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            user_id,
        )

        # Get most recent progress event (new detailed format)
        last_progress = await conn.fetchrow(
            """
            SELECT timestamp, metadata, channel_id
            FROM mtproto_audit_log
            WHERE user_id = $1 AND action = 'collection_progress_detail'
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            user_id,
        )

        # Get errors count for today
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        errors_today = (
            await conn.fetchval(
                """
            SELECT COUNT(*)
            FROM mtproto_audit_log
            WHERE user_id = $1
            AND timestamp >= $2
            AND metadata->>'errors' IS NOT NULL
            AND (metadata->>'errors')::int > 0
            """,
                user_id,
                today_start,
            )
            or 0
        )

        # Get runs count for today
        runs_today = (
            await conn.fetchval(
                """
            SELECT COUNT(*)
            FROM mtproto_audit_log
            WHERE user_id = $1
            AND timestamp >= $2
            AND action = 'collection_start'
            """,
                user_id,
                today_start,
            )
            or 0
        )

    now = datetime.now(UTC)

    # Determine if currently collecting
    currently_collecting = False
    current_channel = None
    channels_processed = 0
    channels_total = 0
    messages_collected_current_run = 0
    errors_current_run = 0
    collection_start_time = None
    estimated_time_remaining = None

    if last_start and last_end:
        # Check if last_start is more recent than last_end
        currently_collecting = last_start["timestamp"] > last_end["timestamp"]
    elif last_start:
        # Have start but no end - must be collecting
        currently_collecting = True

    if currently_collecting and last_start:
        collection_start_time = last_start["timestamp"]
        start_metadata = last_start["metadata"] if last_start["metadata"] else {}
        channels_total = (
            start_metadata.get("total_channels", 0) if isinstance(start_metadata, dict) else 0
        )

        # Get progress from most recent detailed progress event
        if last_progress and last_progress["timestamp"] > last_start["timestamp"]:
            progress_metadata = last_progress["metadata"] if last_progress["metadata"] else {}

            if isinstance(progress_metadata, dict):
                # Use new detailed progress format
                current_channel = progress_metadata.get("channel_name")

                # If no channel name in metadata, get it from channel_id
                if not current_channel and last_progress.get("channel_id"):
                    channel_row = await conn.fetchrow(
                        "SELECT title FROM channels WHERE id = $1",
                        abs(last_progress["channel_id"]),
                    )
                    if channel_row:
                        current_channel = channel_row["title"]

                # Calculate channels processed from progress (we have 1 channel in this case)
                channels_processed = (
                    1
                    if progress_metadata.get("phase") in ["fetching", "processing", "complete"]
                    else 0
                )

                # Get messages from detailed progress
                messages_collected_current_run = progress_metadata.get("messages_current", 0)

                # Get errors if available
                errors_current_run = progress_metadata.get("errors", 0)

                # Calculate ETA from progress
                eta_seconds = progress_metadata.get("eta_seconds")
                if eta_seconds:
                    estimated_time_remaining = int(eta_seconds)
                elif channels_total > 0 and channels_processed > 0:
                    # Fallback to old calculation
                    elapsed_seconds = (now - collection_start_time).total_seconds()
                    avg_seconds_per_channel = elapsed_seconds / channels_processed
                    remaining_channels = channels_total - channels_processed
                    estimated_time_remaining = int(avg_seconds_per_channel * remaining_channels)

    # Calculate last_run and next_run
    if last_end:
        last_run = last_end["timestamp"]
        # Calculate next_run from now, not from last_run
        # If last_run was less than interval ago, next run is in the future
        time_since_last = (now - last_run).total_seconds() / 60  # minutes
        if time_since_last < worker_interval:
            # Next run is in the future
            next_run = last_run + timedelta(minutes=worker_interval)
        else:
            # We're overdue - next run should be imminent
            next_run = now + timedelta(seconds=30)  # Very soon
    elif last_start:
        # If collecting, last complete run would be before this start
        last_run = last_start["timestamp"] - timedelta(minutes=worker_interval)
        next_run = last_start["timestamp"] + timedelta(minutes=worker_interval)
    else:
        # No data - estimate based on system time
        last_run = now - timedelta(minutes=now.minute % worker_interval)
        next_run = last_run + timedelta(minutes=worker_interval)

    return WorkerStatus(
        worker_running=worker_running,
        worker_interval_minutes=worker_interval,
        last_run=last_run,
        next_run=next_run,
        runs_today=runs_today,
        errors_today=errors_today,
        currently_collecting=currently_collecting,
        current_channel=current_channel,
        channels_processed=channels_processed,
        channels_total=channels_total,
        messages_collected_current_run=messages_collected_current_run,
        errors_current_run=errors_current_run,
        collection_start_time=collection_start_time,
        estimated_time_remaining=estimated_time_remaining,
    )


async def _get_channel_stats(conn, user_id: int) -> list[ChannelCollectionStats]:
    """Get statistics for each channel"""

    rows = await conn.fetch(
        """
        SELECT
            c.id as channel_id,
            c.title as channel_name,
            COUNT(p.msg_id) as total_posts,
            MAX(p.date) as latest_post,
            MIN(p.date) as oldest_post,
            COALESCE(cms.mtproto_enabled, false) as collection_enabled
        FROM channels c
        LEFT JOIN posts p ON c.id = p.channel_id
        LEFT JOIN channel_mtproto_settings cms ON c.id = cms.channel_id
        WHERE c.user_id = $1
        GROUP BY c.id, c.title, cms.mtproto_enabled
        ORDER BY c.title
        """,
        user_id,
    )

    channels = []
    for row in rows:
        channels.append(
            ChannelCollectionStats(
                channel_id=row["channel_id"],
                channel_name=row["channel_name"],
                total_posts=row["total_posts"] or 0,
                latest_post_date=row["latest_post"],
                oldest_post_date=row["oldest_post"],
                last_collected=row["latest_post"],  # Use latest post as proxy
                collection_enabled=row["collection_enabled"],
            )
        )

    return channels
