"""
Schedule Repository Implementation
Concrete implementation using PostgreSQL/asyncpg
"""

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from core.models import (
    Delivery,
    DeliveryFilter,
    DeliveryStatus,
    PostStatus,
    ScheduledPost,
    ScheduleFilter,
)
from core.repositories.interfaces import DeliveryRepository, ScheduleRepository


class AsyncpgScheduleRepository(ScheduleRepository):
    """
    PostgreSQL implementation of ScheduleRepository
    Uses asyncpg connection for database operations
    """

    def __init__(self, pool):
        """Initialize with database connection pool"""
        self.db = pool

    async def create(self, post: ScheduledPost) -> ScheduledPost:
        """Create a new scheduled post in PostgreSQL"""
        query = """
        INSERT INTO scheduled_posts (
            user_id, channel_id, post_text, status, schedule_time
        ) VALUES (
            $1, $2, $3, $4, $5
        ) RETURNING *
        """

        # Map domain status to database status
        db_status = self._map_status_to_db(post.status)

        result = await self.db.fetchrow(
            query,
            int(post.user_id),  # bigint in database
            int(post.channel_id),  # bigint in database
            post.content,  # Map to post_text column
            db_status,
            post.scheduled_at,  # Map to schedule_time column
        )

        return self._row_to_scheduled_post(result)

    async def get_by_id(self, post_id: UUID) -> ScheduledPost | None:
        """Get scheduled post by ID"""
        query = "SELECT * FROM scheduled_posts WHERE id = $1"
        result = await self.db.fetchrow(query, post_id)

        if result:
            return self._row_to_scheduled_post(result)
        return None

    async def update(self, post: ScheduledPost) -> ScheduledPost:
        """Update an existing scheduled post"""
        post.updated_at = datetime.utcnow()

        query = """
        UPDATE scheduled_posts SET
            title = $2, content = $3, channel_id = $4, user_id = $5,
            scheduled_at = $6, updated_at = $7, status = $8,
            tags = $9, metadata = $10, media_urls = $11, media_types = $12
        WHERE id = $1
        RETURNING *
        """

        result = await self.db.fetchrow(
            query,
            post.id,
            post.title,
            post.content,
            post.channel_id,
            post.user_id,
            post.scheduled_at,
            post.updated_at,
            post.status.value,
            post.tags,
            json.dumps(post.metadata),
            post.media_urls,
            post.media_types,
        )

        return self._row_to_scheduled_post(result)

    async def delete(self, post_id: UUID) -> bool:
        """Delete a scheduled post"""
        query = "DELETE FROM scheduled_posts WHERE id = $1"
        result = await self.db.execute(query, post_id)
        return result.split()[-1] == "1"  # Returns "DELETE 1" if successful

    async def find(self, filter_criteria: ScheduleFilter) -> list[ScheduledPost]:
        """Find scheduled posts by filter criteria"""
        query = "SELECT * FROM scheduled_posts WHERE 1=1"
        params = []
        param_count = 0

        # Build dynamic WHERE clause
        if filter_criteria.user_id:
            param_count += 1
            query += f" AND user_id = ${param_count}"
            params.append(filter_criteria.user_id)

        if filter_criteria.channel_id:
            param_count += 1
            query += f" AND channel_id = ${param_count}"
            params.append(filter_criteria.channel_id)

        if filter_criteria.status:
            param_count += 1
            query += f" AND status = ${param_count}"
            params.append(filter_criteria.status.value)

        if filter_criteria.from_date:
            param_count += 1
            query += f" AND scheduled_at >= ${param_count}"
            params.append(filter_criteria.from_date)

        if filter_criteria.to_date:
            param_count += 1
            query += f" AND scheduled_at <= ${param_count}"
            params.append(filter_criteria.to_date)

        if filter_criteria.tags:
            param_count += 1
            query += f" AND tags && ${param_count}"
            params.append(filter_criteria.tags)

        # Add ordering and pagination
        query += " ORDER BY scheduled_at DESC"

        if filter_criteria.limit:
            param_count += 1
            query += f" LIMIT ${param_count}"
            params.append(filter_criteria.limit)

        if filter_criteria.offset:
            param_count += 1
            query += f" OFFSET ${param_count}"
            params.append(filter_criteria.offset)

        results = await self.db.fetch(query, *params)
        return [self._row_to_scheduled_post(row) for row in results]

    async def get_ready_for_delivery(self) -> list[ScheduledPost]:
        """Get all posts that are ready for delivery"""
        query = """
        SELECT * FROM scheduled_posts
        WHERE status = $1 AND scheduled_at <= $2
        ORDER BY scheduled_at ASC
        """

        results = await self.db.fetch(query, "scheduled", datetime.utcnow())

        return [self._row_to_scheduled_post(row) for row in results]

    async def count(self, filter_criteria: ScheduleFilter) -> int:
        """Count scheduled posts matching filter criteria"""
        query = "SELECT COUNT(*) FROM scheduled_posts WHERE 1=1"
        params = []
        param_count = 0

        if filter_criteria.user_id:
            param_count += 1
            query += f" AND user_id = ${param_count}"
            params.append(filter_criteria.user_id)

        if filter_criteria.channel_id:
            param_count += 1
            query += f" AND channel_id = ${param_count}"
            params.append(filter_criteria.channel_id)

        if filter_criteria.status:
            param_count += 1
            db_status = self._map_status_to_db(filter_criteria.status)
            query += f" AND status = ${param_count}"
            params.append(db_status)

        if filter_criteria.from_date:
            param_count += 1
            query += f" AND scheduled_at >= ${param_count}"
            params.append(filter_criteria.from_date)

        if filter_criteria.to_date:
            param_count += 1
            query += f" AND scheduled_at <= ${param_count}"
            params.append(filter_criteria.to_date)

        result = await self.db.fetchval(query, *params)
        return result or 0

    async def update_post_status(self, post_id: int, status: str) -> bool:
        """Update the status of a scheduled post"""
        query = """
        UPDATE scheduled_posts
        SET status = $2, updated_at = NOW()
        WHERE id = $1
        """
        try:
            result = await self.db.execute(query, post_id, status)
            return result == "UPDATE 1"
        except Exception:
            return False

    async def create_scheduled_post(
        self,
        user_id: int,
        channel_id: int,
        post_text: str,
        schedule_time: datetime,
        media_id: str | None = None,
        media_type: str | None = None,
        inline_buttons: dict | None = None,
    ) -> int:
        """Create a new scheduled post and return its ID"""
        query = """
        INSERT INTO scheduled_posts (
            user_id, channel_id, post_text, schedule_time,
            media_id, media_type, inline_buttons, status, created_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, 'pending', NOW()
        ) RETURNING id
        """

        inline_buttons_json = json.dumps(inline_buttons) if inline_buttons else None

        result = await self.db.fetchval(
            query,
            user_id,
            channel_id,
            post_text,
            schedule_time,
            media_id,
            media_type,
            inline_buttons_json,
        )
        return result

    async def get_pending_posts(self, limit: int = 50) -> list[dict]:
        """Get pending posts that are ready to be sent"""
        query = """
        SELECT id, user_id, channel_id, post_text, schedule_time,
               media_id, media_type, inline_buttons, status, created_at
        FROM scheduled_posts
        WHERE status = 'pending' AND schedule_time <= NOW()
        ORDER BY schedule_time ASC
        LIMIT $1
        """

        rows = await self.db.fetch(query, limit)
        posts = []
        for row in rows:
            post_dict = dict(row)
            # Parse inline_buttons JSON if present
            if post_dict.get("inline_buttons"):
                try:
                    post_dict["inline_buttons"] = json.loads(post_dict["inline_buttons"])
                except (json.JSONDecodeError, TypeError):
                    post_dict["inline_buttons"] = None
            posts.append(post_dict)

        return posts

    async def count_user_posts_this_month(self, user_id: int) -> int:
        """Count posts created by user in current month"""
        query = """
        SELECT COUNT(*) FROM scheduled_posts
        WHERE user_id = $1
        AND created_at >= date_trunc('month', CURRENT_DATE)
        AND created_at < date_trunc('month', CURRENT_DATE) + INTERVAL '1 month'
        """
        result = await self.db.fetchval(query, user_id)
        return result or 0

    async def delete_old_posts(self, days_old: int, statuses: list[str]) -> int:
        """
        Delete old posts in specified statuses

        ✅ Issue #3 Phase 3: Real implementation for cleanup_old_posts

        Args:
            days_old: Delete posts older than this many days
            statuses: List of statuses to delete (e.g., ['sent', 'cancelled', 'error'])

        Returns:
            Number of posts deleted
        """
        query = """
        DELETE FROM scheduled_posts
        WHERE status = ANY($1)
        AND created_at < NOW() - INTERVAL '1 day' * $2
        """
        try:
            result = await self.db.execute(query, statuses, days_old)
            # Parse "DELETE N" result
            deleted_count = int(result.split()[-1]) if result else 0
            return deleted_count
        except Exception:
            return 0

    async def get_stuck_sending_posts(self, timeout_minutes: int = 30) -> list[dict]:
        """
        Get posts stuck in 'sending' status for too long

        ✅ Issue #3 Phase 3: Real implementation for requeue_stuck_sending_posts

        Args:
            timeout_minutes: Consider posts stuck if in 'sending' status for this many minutes

        Returns:
            List of stuck post dictionaries
        """
        query = """
        SELECT id, user_id, channel_id, post_text, schedule_time,
               media_id, media_type, inline_buttons, status, created_at
        FROM scheduled_posts
        WHERE status = 'sending'
        AND updated_at < NOW() - INTERVAL '1 minute' * $1
        ORDER BY updated_at ASC
        """
        try:
            rows = await self.db.fetch(query, timeout_minutes)
            posts = []
            for row in rows:
                post_dict = dict(row)
                # Parse inline_buttons JSON if present
                if post_dict.get("inline_buttons"):
                    try:
                        post_dict["inline_buttons"] = json.loads(post_dict["inline_buttons"])
                    except (json.JSONDecodeError, TypeError):
                        post_dict["inline_buttons"] = None
                posts.append(post_dict)
            return posts
        except Exception:
            return []

    async def count_posts_by_status(
        self,
        status: str,
        user_id: int | None = None,
        channel_id: int | None = None,
    ) -> int:
        """
        Count posts by status with optional filters

        ✅ Issue #3 Phase 3: Supporting method for maintenance tasks

        Args:
            status: Post status to count
            user_id: Optional user ID filter
            channel_id: Optional channel ID filter

        Returns:
            Count of posts with given status
        """
        query = "SELECT COUNT(*) FROM scheduled_posts WHERE status = $1"
        params: list[Any] = [status]
        param_count = 1

        if user_id is not None:
            param_count += 1
            query += f" AND user_id = ${param_count}"
            params.append(user_id)

        if channel_id is not None:
            param_count += 1
            query += f" AND channel_id = ${param_count}"
            params.append(channel_id)

        try:
            result = await self.db.fetchval(query, *params)
            return result or 0
        except Exception:
            return 0

    async def get_expired_schedulers(self, days_old: int = 90) -> list[dict]:
        """
        Get schedulers that are very old and in terminal states

        ✅ Issue #3 Phase 3: Real implementation for remove_expired_schedulers

        Args:
            days_old: Consider schedulers expired if older than this many days

        Returns:
            List of expired scheduler dictionaries
        """
        query = """
        SELECT id, user_id, channel_id, status, created_at
        FROM scheduled_posts
        WHERE status IN ('sent', 'cancelled', 'error', 'failed')
        AND created_at < NOW() - INTERVAL '1 day' * $1
        ORDER BY created_at ASC
        LIMIT 1000
        """
        try:
            rows = await self.db.fetch(query, days_old)
            return [dict(row) for row in rows]
        except Exception:
            return []

    def _row_to_scheduled_post(self, row) -> ScheduledPost:
        """Convert database row to ScheduledPost domain model"""
        return ScheduledPost(
            id=row["id"],
            title="",  # Not stored in current schema
            content=row["post_text"],  # Map post_text to content
            channel_id=str(row["channel_id"]),  # Convert to string
            user_id=str(row["user_id"]),  # Convert to string
            scheduled_at=row["schedule_time"],  # Map schedule_time to scheduled_at
            created_at=row["created_at"],
            updated_at=None,  # Not available in current schema
            status=self._map_status_from_db(row["status"]),
            tags=[],  # Not stored in current schema
            metadata={},  # Not stored in current schema
            media_urls=[],  # Not stored in current schema
            media_types=[],  # Not stored in current schema
        )

    def _map_status_to_db(self, status: PostStatus) -> str:
        """Map domain status to database status

        Database constraint: status IN ('pending', 'sent', 'error')
        Domain model: SCHEDULED, PUBLISHED, FAILED, DRAFT, CANCELLED
        """
        mapping = {
            PostStatus.SCHEDULED: "pending",      # scheduled → pending
            PostStatus.DRAFT: "pending",          # draft → pending
            PostStatus.PUBLISHED: "sent",         # published → sent
            PostStatus.FAILED: "error",           # failed → error
            PostStatus.CANCELLED: "error",        # cancelled → error
        }
        return mapping.get(status, "pending")

    def _map_status_from_db(self, db_status: str) -> PostStatus:
        """Map database status to domain status"""
        mapping = {
            "pending": PostStatus.SCHEDULED,
            "sent": PostStatus.PUBLISHED,
            "error": PostStatus.FAILED,
        }
        return mapping.get(db_status, PostStatus.DRAFT)


class AsyncpgDeliveryRepository(DeliveryRepository):
    """
    PostgreSQL implementation of DeliveryRepository
    Uses asyncpg connection for database operations
    """

    def __init__(self, db_connection):
        """Initialize with database connection"""
        self.db = db_connection

    async def create(self, delivery: Delivery) -> Delivery:
        """Create a new delivery record"""
        query = """
        INSERT INTO deliveries (
            id, post_id, status, attempted_at, delivered_at, created_at,
            delivery_channel_id, message_id, error_message, retry_count,
            max_retries, delivery_metadata
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
        ) RETURNING *
        """

        result = await self.db.fetchrow(
            query,
            delivery.id,
            delivery.post_id,
            delivery.status.value,
            delivery.attempted_at,
            delivery.delivered_at,
            delivery.created_at,
            delivery.delivery_channel_id,
            delivery.message_id,
            delivery.error_message,
            delivery.retry_count,
            delivery.max_retries,
            json.dumps(delivery.delivery_metadata),
        )

        return self._row_to_delivery(result)

    async def get_by_id(self, delivery_id: UUID) -> Delivery | None:
        """Get delivery by ID"""
        query = "SELECT * FROM deliveries WHERE id = $1"
        result = await self.db.fetchrow(query, delivery_id)

        if result:
            return self._row_to_delivery(result)
        return None

    async def get_by_post_id(self, post_id: UUID) -> list[Delivery]:
        """Get all deliveries for a specific post"""
        query = "SELECT * FROM deliveries WHERE post_id = $1 ORDER BY created_at DESC"
        results = await self.db.fetch(query, post_id)

        return [self._row_to_delivery(row) for row in results]

    async def update(self, delivery: Delivery) -> Delivery:
        """Update an existing delivery"""
        query = """
        UPDATE deliveries SET
            status = $2, attempted_at = $3, delivered_at = $4,
            delivery_channel_id = $5, message_id = $6, error_message = $7,
            retry_count = $8, max_retries = $9, delivery_metadata = $10
        WHERE id = $1
        RETURNING *
        """

        result = await self.db.fetchrow(
            query,
            delivery.id,
            delivery.status.value,
            delivery.attempted_at,
            delivery.delivered_at,
            delivery.delivery_channel_id,
            delivery.message_id,
            delivery.error_message,
            delivery.retry_count,
            delivery.max_retries,
            json.dumps(delivery.delivery_metadata),
        )

        return self._row_to_delivery(result)

    async def find(self, filter_criteria: DeliveryFilter) -> list[Delivery]:
        """Find deliveries by filter criteria"""
        query = "SELECT * FROM deliveries WHERE 1=1"
        params = []
        param_count = 0

        # Build dynamic WHERE clause similar to PgScheduleRepository
        if filter_criteria.post_id:
            param_count += 1
            query += f" AND post_id = ${param_count}"
            params.append(filter_criteria.post_id)

        if filter_criteria.status:
            param_count += 1
            query += f" AND status = ${param_count}"
            params.append(filter_criteria.status.value)

        # ... (other filter conditions)

        query += " ORDER BY created_at DESC"

        if filter_criteria.limit:
            param_count += 1
            query += f" LIMIT ${param_count}"
            params.append(filter_criteria.limit)

        if filter_criteria.offset:
            param_count += 1
            query += f" OFFSET ${param_count}"
            params.append(filter_criteria.offset)

        results = await self.db.fetch(query, *params)
        return [self._row_to_delivery(row) for row in results]

    async def get_failed_retryable(self) -> list[Delivery]:
        """Get failed deliveries that can be retried"""
        query = """
        SELECT * FROM deliveries
        WHERE status IN ($1, $2) AND retry_count < max_retries
        ORDER BY attempted_at ASC
        """

        results = await self.db.fetch(
            query, DeliveryStatus.FAILED.value, DeliveryStatus.RETRYING.value
        )

        return [self._row_to_delivery(row) for row in results]

    async def count(self, filter_criteria: DeliveryFilter) -> int:
        """Count deliveries matching filter criteria"""
        query = "SELECT COUNT(*) FROM deliveries WHERE 1=1"
        params = []
        param_count = 0

        # Build same WHERE conditions as find()
        if filter_criteria.post_id:
            param_count += 1
            query += f" AND post_id = ${param_count}"
            params.append(filter_criteria.post_id)

        # ... (other conditions)

        result = await self.db.fetchval(query, *params)
        return result or 0

    def _row_to_delivery(self, row) -> Delivery:
        """Convert database row to Delivery domain model"""
        metadata = json.loads(row["delivery_metadata"]) if row["delivery_metadata"] else {}

        return Delivery(
            id=row["id"],
            post_id=row["post_id"],
            status=DeliveryStatus(row["status"]),
            attempted_at=row["attempted_at"],
            delivered_at=row["delivered_at"],
            created_at=row["created_at"],
            delivery_channel_id=row["delivery_channel_id"],
            message_id=row["message_id"],
            error_message=row["error_message"],
            retry_count=row["retry_count"],
            max_retries=row["max_retries"],
            delivery_metadata=metadata,
        )
