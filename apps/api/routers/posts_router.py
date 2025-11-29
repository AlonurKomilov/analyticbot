"""
Posts Router - API endpoints for managing and viewing posts
Integrates MTProto collected posts with the frontend
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from apps.api.middleware.auth import get_current_user
from apps.di import get_container

logger = logging.getLogger(__name__)

router = APIRouter(tags=["posts"])


@router.get("/posts/debug/current-user")
async def debug_current_user(current_user: dict = Depends(get_current_user)):
    """Debug endpoint to see who is currently logged in"""
    return {
        "user_id": current_user.get("id"),
        "username": current_user.get("username"),
        "email": current_user.get("email"),
        "message": "This is your current authenticated user",
    }


class PostMetrics(BaseModel):
    """Post metrics data"""

    views: int = 0
    forwards: int = 0
    comments_count: int = 0  # Discussion group comments
    replies_count: int = 0  # Direct threaded replies
    reactions_count: int = 0
    snapshot_time: datetime | None = None


class PostMediaFlags(BaseModel):
    """Media type flags for content type icons"""

    has_photo: bool = False
    has_video: bool = False
    has_audio: bool = False
    has_voice: bool = False
    has_document: bool = False
    has_gif: bool = False
    has_sticker: bool = False
    has_poll: bool = False
    has_link: bool = False
    has_web_preview: bool = False
    text_length: int = 0


class PostResponse(BaseModel):
    """Post response model"""

    id: int = Field(..., description="Message ID")
    channel_id: int = Field(..., description="Channel ID")
    msg_id: int = Field(..., description="Message ID (same as id)")
    date: datetime = Field(..., description="Post date")
    text: str = Field(default="", description="Post text content")
    created_at: datetime = Field(..., description="When post was first collected")
    updated_at: datetime = Field(..., description="Last update time")
    metrics: PostMetrics | None = Field(None, description="Latest metrics")
    channel_name: str | None = Field(None, description="Channel name")
    channel_username: str | None = Field(None, description="Channel username")
    media_flags: PostMediaFlags | None = Field(None, description="Media type flags")


class PostsListResponse(BaseModel):
    """Response for posts list"""

    posts: list[PostResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


async def get_db_pool():
    """Get database pool from container"""
    container = get_container()
    try:
        pool = await container.database.asyncpg_pool()
        return pool
    except Exception as e:
        logger.error(f"Failed to get database pool: {e}")
        raise HTTPException(status_code=500, detail="Database pool not available")


@router.get("/posts", response_model=PostsListResponse)
async def get_all_posts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of posts per page"),
    channel_id: int | None = Query(None, description="Filter by channel ID"),
    search: str | None = Query(None, description="Search by message ID or text content"),
    current_user: dict = Depends(get_current_user),
    db_pool=Depends(get_db_pool),
):
    """
    Get all collected posts with pagination.
    Returns posts from MTProto data collection with latest metrics.
    Supports search by message ID or text content.
    """
    try:
        offset = (page - 1) * page_size

        print(f"\n{'=' * 80}")
        print("POSTS API REQUEST")
        print(f"{'=' * 80}")
        print(f"Page: {page}")
        print(f"Page Size: {page_size}")
        print(f"Offset: {offset}")
        print(f"Channel ID: {channel_id}")
        print(f"Search Query: {search}")
        print(f"Current User: {current_user}")
        print(f"Current User ID: {current_user['id']}")
        print(f"{'=' * 80}\n")

        logger.info(
            f"=== Posts Request === page={page}, page_size={page_size}, offset={offset}, channel_id={channel_id}, search={search}"
        )
        logger.info(f"Current user: {current_user}")
        logger.info(f"Current user ID: {current_user['id']}")

        # Build query based on filters
        # Exclude deleted messages by default
        where_clause = "WHERE p.channel_id IN (SELECT id FROM channels WHERE user_id = $1) AND p.is_deleted = FALSE"
        params: list[Any] = [current_user["id"]]

        if channel_id:
            where_clause += f" AND p.channel_id = ${len(params) + 1}"
            params.append(channel_id)

        if search:
            # Search by message ID (exact match) or text content (case-insensitive partial match)
            search_value = search.strip()
            # Try to parse as integer for msg_id search
            try:
                msg_id_search = int(search_value)
                where_clause += (
                    f" AND (p.msg_id = ${len(params) + 1} OR p.text ILIKE ${len(params) + 2})"
                )
                params.append(msg_id_search)
                params.append(f"%{search_value}%")
            except ValueError:
                # Not a number, search only in text
                where_clause += f" AND p.text ILIKE ${len(params) + 1}"
                params.append(f"%{search_value}%")

        # Get total count
        count_query = f"SELECT COUNT(*) FROM posts p {where_clause}"
        async with db_pool.acquire() as conn:
            total = await conn.fetchval(count_query, *params)

            # Get posts with latest metrics
            # Build LIMIT and OFFSET with proper PostgreSQL parameter syntax
            limit_param_idx = len(params) + 1
            offset_param_idx = len(params) + 2

            query = (
                f"""
                SELECT
                    p.channel_id,
                    p.msg_id,
                    p.date,
                    p.text,
                    p.created_at,
                    p.updated_at,
                    c.title as channel_name,
                    c.username as channel_username,
                    -- Media type flags
                    p.has_photo,
                    p.has_video,
                    p.has_audio,
                    p.has_voice,
                    p.has_document,
                    p.has_gif,
                    p.has_sticker,
                    p.has_poll,
                    p.has_link,
                    p.has_web_preview,
                    p.text_length,
                    -- Metrics
                    pm.views,
                    pm.forwards,
                    pm.comments_count,
                    pm.replies_count,
                    pm.reactions_count,
                    pm.snapshot_time
                FROM posts p
                LEFT JOIN channels c ON p.channel_id = c.id
                LEFT JOIN LATERAL (
                    SELECT views, forwards, comments_count, replies_count, reactions_count, snapshot_time
                    FROM post_metrics
                    WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                    ORDER BY snapshot_time DESC
                    LIMIT 1
                ) pm ON true
                {where_clause}
                ORDER BY p.date DESC
                LIMIT $"""
                + str(limit_param_idx)
                + """ OFFSET $"""
                + str(offset_param_idx)
            )
            params.extend([page_size, offset])

            # Debug logging
            logger.info("=== PAGINATION DEBUG ===")
            logger.info(f"Page: {page}, PageSize: {page_size}, Offset: {offset}")
            logger.info(f"limit_param_idx: {limit_param_idx}, offset_param_idx: {offset_param_idx}")
            logger.info(f"Full params list: {params}")
            logger.info(
                f"Query tail: ...ORDER BY p.date DESC LIMIT ${limit_param_idx} OFFSET ${offset_param_idx}"
            )
            logger.info(f"Full Query: {query}")

            records = await conn.fetch(query, *params)
            logger.info(f"Records fetched: {len(records)}")

            posts = []
            for record in records:
                metrics = None
                if record["views"] is not None:
                    metrics = PostMetrics(
                        views=record["views"] or 0,
                        forwards=record["forwards"] or 0,
                        comments_count=record["comments_count"] or 0,
                        replies_count=record.get("replies_count") or 0,
                        reactions_count=record["reactions_count"] or 0,
                        snapshot_time=record["snapshot_time"],
                    )

                # Build media flags
                media_flags = PostMediaFlags(
                    has_photo=record.get("has_photo") or False,
                    has_video=record.get("has_video") or False,
                    has_audio=record.get("has_audio") or False,
                    has_voice=record.get("has_voice") or False,
                    has_document=record.get("has_document") or False,
                    has_gif=record.get("has_gif") or False,
                    has_sticker=record.get("has_sticker") or False,
                    has_poll=record.get("has_poll") or False,
                    has_link=record.get("has_link") or False,
                    has_web_preview=record.get("has_web_preview") or False,
                    text_length=record.get("text_length") or len(record["text"] or ""),
                )

                posts.append(
                    PostResponse(
                        id=record["msg_id"],
                        channel_id=record["channel_id"],
                        msg_id=record["msg_id"],
                        date=record["date"],
                        text=record["text"] or "",
                        created_at=record["created_at"],
                        updated_at=record["updated_at"],
                        metrics=metrics,
                        channel_name=record["channel_name"],
                        channel_username=record["channel_username"],
                        media_flags=media_flags,
                    )
                )

            return PostsListResponse(
                posts=posts,
                total=total,
                page=page,
                page_size=page_size,
                has_more=(offset + len(posts)) < total,
            )

    except Exception as e:
        logger.error(f"Error fetching posts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts: {str(e)}")


@router.get("/posts/{channel_id}/{msg_id}", response_model=PostResponse)
async def get_post(
    channel_id: int,
    msg_id: int,
    current_user: dict = Depends(get_current_user),
    db_pool=Depends(get_db_pool),
):
    """Get a specific post by channel ID and message ID"""
    try:
        async with db_pool.acquire() as conn:
            # Verify user owns this channel
            channel_check = await conn.fetchval(
                "SELECT 1 FROM channels WHERE id = $1 AND user_id = $2",
                channel_id,
                current_user["id"],
            )
            if not channel_check:
                raise HTTPException(status_code=404, detail="Channel not found")

            # Get post with latest metrics
            record = await conn.fetchrow(
                """
                SELECT
                    p.channel_id,
                    p.msg_id,
                    p.date,
                    p.text,
                    p.created_at,
                    p.updated_at,
                    c.title as channel_name,
                    pm.views,
                    pm.forwards,
                    pm.comments_count,
                    pm.replies_count,
                    pm.reactions_count,
                    pm.snapshot_time
                FROM posts p
                LEFT JOIN channels c ON p.channel_id = c.id
                LEFT JOIN LATERAL (
                    SELECT views, forwards, comments_count, replies_count, reactions_count, snapshot_time
                    FROM post_metrics
                    WHERE channel_id = p.channel_id AND msg_id = p.msg_id
                    ORDER BY snapshot_time DESC
                    LIMIT 1
                ) pm ON true
                WHERE p.channel_id = $1 AND p.msg_id = $2
                """,
                channel_id,
                msg_id,
            )

            if not record:
                raise HTTPException(status_code=404, detail="Post not found")

            metrics = None
            if record["views"] is not None:
                metrics = PostMetrics(
                    views=record["views"] or 0,
                    forwards=record["forwards"] or 0,
                    comments_count=record["comments_count"] or 0,
                    replies_count=record.get("replies_count") or 0,
                    reactions_count=record["reactions_count"] or 0,
                    snapshot_time=record["snapshot_time"],
                )

            return PostResponse(
                id=record["msg_id"],
                channel_id=record["channel_id"],
                msg_id=record["msg_id"],
                date=record["date"],
                text=record["text"] or "",
                created_at=record["created_at"],
                updated_at=record["updated_at"],
                metrics=metrics,
                channel_name=record["channel_name"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching post: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch post: {str(e)}")


@router.get("/channels/{channel_id}/posts", response_model=PostsListResponse)
async def get_channel_posts(
    channel_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db_pool=Depends(get_db_pool),
):
    """Get all posts for a specific channel"""
    return await get_all_posts(page, page_size, channel_id, current_user, db_pool)
