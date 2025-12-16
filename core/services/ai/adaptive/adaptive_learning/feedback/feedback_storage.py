"""
Feedback Storage for Adaptive Learning
======================================

Provides infrastructure services for storing, retrieving,
and managing user feedback data.
"""

import asyncio
import json
import logging
import sqlite3
import threading
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..protocols.feedback_protocols import (
    ContentType,
    FeedbackBatch,
    FeedbackType,
    UserFeedback,
)

logger = logging.getLogger(__name__)


@dataclass
class FeedbackStorageConfig:
    """Configuration for feedback storage"""

    storage_path: str = "feedback_data/"
    db_file: str = "feedback.db"
    retention_days: int = 365
    batch_size: int = 50
    auto_cleanup_interval: int = 24 * 3600  # 24 hours in seconds
    enable_memory_cache: bool = True
    cache_size_limit: int = 1000
    enable_analytics: bool = True


class FeedbackStorageService:
    """
    Infrastructure service for feedback storage capabilities.

    Provides SQLite-based storage with in-memory caching
    for user feedback data management.
    """

    def __init__(self, config: FeedbackStorageConfig | None = None):
        self.config = config or FeedbackStorageConfig()
        self.storage_path = Path(self.config.storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Database connection
        self.db_path = self.storage_path / self.config.db_file
        self.db_lock = threading.Lock()

        # In-memory caches
        self.feedback_cache: dict[str, list[UserFeedback]] = defaultdict(list)
        self.batch_cache: dict[str, FeedbackBatch] = {}
        self.user_feedback_count: dict[str, int] = defaultdict(int)

        # Storage state
        self.is_initialized = False
        self.cleanup_tasks: list[asyncio.Task] = []

        logger.info("💾 Feedback Storage Service initialized")

    async def initialize_storage(self, config: dict[str, Any]) -> bool:
        """Initialize feedback storage infrastructure"""
        try:
            # Update configuration
            if "storage_path" in config:
                self.config.storage_path = config["storage_path"]
                self.storage_path = Path(self.config.storage_path)
                self.storage_path.mkdir(parents=True, exist_ok=True)
                self.db_path = self.storage_path / self.config.db_file

            if "retention_days" in config:
                self.config.retention_days = config["retention_days"]

            if "batch_size" in config:
                self.config.batch_size = config["batch_size"]

            # Initialize database
            await self._initialize_database()

            # Load cached data
            if self.config.enable_memory_cache:
                await self._load_recent_feedback()

            # Start background tasks
            if self.config.auto_cleanup_interval > 0:
                cleanup_task = asyncio.create_task(self._cleanup_loop())
                self.cleanup_tasks.append(cleanup_task)

            self.is_initialized = True
            logger.info("✅ Feedback storage initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize feedback storage: {e}")
            return False

    async def get_storage_status(self) -> dict[str, Any]:
        """Get status of feedback storage"""
        try:
            # Get database statistics
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Count total feedback
                cursor.execute("SELECT COUNT(*) FROM feedback")
                total_feedback = cursor.fetchone()[0]

                # Count by type
                cursor.execute("""
                    SELECT feedback_type, COUNT(*)
                    FROM feedback
                    GROUP BY feedback_type
                """)
                feedback_by_type = dict(cursor.fetchall())

                # Count recent feedback (last 24 hours)
                cursor.execute("""
                    SELECT COUNT(*) FROM feedback
                    WHERE timestamp > datetime('now', '-1 day')
                """)
                recent_feedback = cursor.fetchone()[0]

            return {
                "service": "feedback_storage",
                "status": "healthy" if self.is_initialized else "initializing",
                "is_initialized": self.is_initialized,
                "storage_path": str(self.storage_path),
                "database_path": str(self.db_path),
                "total_feedback": total_feedback,
                "recent_feedback_24h": recent_feedback,
                "feedback_by_type": feedback_by_type,
                "cached_users": len(self.feedback_cache),
                "cached_feedback": sum(
                    len(feedback_list) for feedback_list in self.feedback_cache.values()
                ),
                "cached_batches": len(self.batch_cache),
                "config": asdict(self.config),
            }

        except Exception as e:
            logger.error(f"❌ Failed to get storage status: {e}")
            return {"service": "feedback_storage", "status": "error", "error": str(e)}

    async def store_feedback(self, feedback: UserFeedback) -> bool:
        """Store user feedback"""
        try:
            # Validate feedback
            if not self._validate_feedback(feedback):
                logger.warning(f"⚠️ Invalid feedback data: {feedback}")
                return False

            # Store in database
            success = await self._store_feedback_db(feedback)
            if not success:
                return False

            # Update cache
            if self.config.enable_memory_cache:
                self.feedback_cache[feedback.user_id].append(feedback)
                self.user_feedback_count[feedback.user_id] += 1

                # Manage cache size
                await self._manage_cache_size()

            logger.debug(f"💾 Stored feedback from user {feedback.user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to store feedback: {e}")
            return False

    async def store_feedback_batch(self, batch: FeedbackBatch) -> bool:
        """Store a batch of feedback"""
        try:
            # Validate batch
            if not batch.feedback_list:
                logger.warning("⚠️ Empty feedback batch")
                return False

            # Store batch metadata
            self.batch_cache[batch.batch_id] = batch

            # Store individual feedback items
            success_count = 0
            for feedback in batch.feedback_list:
                if await self.store_feedback(feedback):
                    success_count += 1

            # Update batch with results
            batch.processed_count = success_count
            batch.status = "completed" if success_count == len(batch.feedback_list) else "partial"

            logger.info(
                f"📦 Stored feedback batch {batch.batch_id}: {success_count}/{len(batch.feedback_list)} items"
            )
            return success_count > 0

        except Exception as e:
            logger.error(f"❌ Failed to store feedback batch: {e}")
            return False

    async def get_feedback(
        self,
        user_id: str | None = None,
        content_type: ContentType | None = None,
        feedback_type: FeedbackType | None = None,
        time_range: tuple[datetime, datetime] | None = None,
        limit: int | None = None,
    ) -> list[UserFeedback]:
        """Retrieve feedback with optional filters"""
        try:
            # Build query
            where_conditions = []
            params = []

            if user_id:
                where_conditions.append("user_id = ?")
                params.append(user_id)

            if content_type:
                where_conditions.append("content_type = ?")
                params.append(content_type.value)

            if feedback_type:
                where_conditions.append("feedback_type = ?")
                params.append(feedback_type.value)

            if time_range:
                start_time, end_time = time_range
                where_conditions.append("timestamp BETWEEN ? AND ?")
                params.extend([start_time.isoformat(), end_time.isoformat()])

            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            limit_clause = f" LIMIT {limit}" if limit else ""

            query = f"""
                SELECT user_id, content_id, content_type, feedback_type,
                       rating, feedback_text, timestamp, metadata
                FROM feedback
                {where_clause}
                ORDER BY timestamp DESC
                {limit_clause}
            """

            # Execute query
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()

            # Convert to UserFeedback objects
            feedback_list = []
            for row in rows:
                feedback = UserFeedback(
                    user_id=row[0],
                    content_id=row[1],
                    content_type=ContentType(row[2]),
                    feedback_type=FeedbackType(row[3]),
                    rating=row[4],
                    feedback_text=row[5],
                    timestamp=datetime.fromisoformat(row[6]),
                    metadata=json.loads(row[7]) if row[7] else {},
                )
                feedback_list.append(feedback)

            logger.debug(f"📊 Retrieved {len(feedback_list)} feedback items")
            return feedback_list

        except Exception as e:
            logger.error(f"❌ Failed to get feedback: {e}")
            return []

    async def get_user_feedback_summary(self, user_id: str) -> dict[str, Any]:
        """Get summary of feedback for a specific user"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Total feedback count
                cursor.execute("SELECT COUNT(*) FROM feedback WHERE user_id = ?", (user_id,))
                total_count = cursor.fetchone()[0]

                # Feedback by type
                cursor.execute(
                    """
                    SELECT feedback_type, COUNT(*)
                    FROM feedback
                    WHERE user_id = ?
                    GROUP BY feedback_type
                """,
                    (user_id,),
                )
                feedback_by_type = dict(cursor.fetchall())

                # Average rating by content type
                cursor.execute(
                    """
                    SELECT content_type, AVG(rating), COUNT(*)
                    FROM feedback
                    WHERE user_id = ? AND rating IS NOT NULL
                    GROUP BY content_type
                """,
                    (user_id,),
                )
                rating_by_content = {
                    content_type: {"avg_rating": avg_rating, "count": count}
                    for content_type, avg_rating, count in cursor.fetchall()
                }

                # Recent activity (last 30 days)
                cursor.execute(
                    """
                    SELECT COUNT(*) FROM feedback
                    WHERE user_id = ? AND timestamp > datetime('now', '-30 days')
                """,
                    (user_id,),
                )
                recent_activity = cursor.fetchone()[0]

                # First and last feedback
                cursor.execute(
                    """
                    SELECT MIN(timestamp), MAX(timestamp)
                    FROM feedback
                    WHERE user_id = ?
                """,
                    (user_id,),
                )
                first_feedback, last_feedback = cursor.fetchone()

            return {
                "user_id": user_id,
                "total_feedback": total_count,
                "feedback_by_type": feedback_by_type,
                "rating_by_content": rating_by_content,
                "recent_activity_30d": recent_activity,
                "first_feedback": first_feedback,
                "last_feedback": last_feedback,
                "in_cache": user_id in self.feedback_cache,
            }

        except Exception as e:
            logger.error(f"❌ Failed to get user feedback summary: {e}")
            return {"user_id": user_id, "error": str(e)}

    async def cleanup_old_feedback(self, retention_days: int) -> int:
        """Clean up old feedback beyond retention period"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Count items to be deleted
                cursor.execute(
                    "SELECT COUNT(*) FROM feedback WHERE timestamp < ?", (cutoff_date.isoformat(),)
                )
                count_to_delete = cursor.fetchone()[0]

                # Delete old feedback
                cursor.execute(
                    "DELETE FROM feedback WHERE timestamp < ?", (cutoff_date.isoformat(),)
                )

                conn.commit()

            # Clean cache
            await self._clean_cache_old_feedback(cutoff_date)

            logger.info(f"🧹 Cleaned up {count_to_delete} old feedback items")
            return count_to_delete

        except Exception as e:
            logger.error(f"❌ Failed to cleanup old feedback: {e}")
            return 0

    async def get_feedback_analytics(
        self, time_range: tuple[datetime, datetime] | None = None
    ) -> dict[str, Any]:
        """Get analytics about feedback data"""
        try:
            if not self.config.enable_analytics:
                return {"analytics_disabled": True}

            time_filter = ""
            params = []

            if time_range:
                start_time, end_time = time_range
                time_filter = " WHERE timestamp BETWEEN ? AND ?"
                params = [start_time.isoformat(), end_time.isoformat()]

            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Total feedback count
                cursor.execute(f"SELECT COUNT(*) FROM feedback{time_filter}", params)
                total_feedback = cursor.fetchone()[0]

                # Feedback distribution by type
                cursor.execute(
                    f"""
                    SELECT feedback_type, COUNT(*)
                    FROM feedback{time_filter}
                    GROUP BY feedback_type
                """,
                    params,
                )
                feedback_distribution = dict(cursor.fetchall())

                # Content type distribution
                cursor.execute(
                    f"""
                    SELECT content_type, COUNT(*)
                    FROM feedback{time_filter}
                    GROUP BY content_type
                """,
                    params,
                )
                content_distribution = dict(cursor.fetchall())

                # Rating statistics
                cursor.execute(
                    f"""
                    SELECT AVG(rating), MIN(rating), MAX(rating), COUNT(*)
                    FROM feedback
                    {time_filter} AND rating IS NOT NULL
                """,
                    params,
                )
                rating_stats = cursor.fetchone()

                # Daily feedback volume (last 7 days)
                cursor.execute("""
                    SELECT DATE(timestamp) as day, COUNT(*)
                    FROM feedback
                    WHERE timestamp > datetime('now', '-7 days')
                    GROUP BY DATE(timestamp)
                    ORDER BY day
                """)
                daily_volume = dict(cursor.fetchall())

                # Top users by feedback count
                cursor.execute(
                    f"""
                    SELECT user_id, COUNT(*) as feedback_count
                    FROM feedback{time_filter}
                    GROUP BY user_id
                    ORDER BY feedback_count DESC
                    LIMIT 10
                """,
                    params,
                )
                top_users = dict(cursor.fetchall())

            return {
                "total_feedback": total_feedback,
                "feedback_distribution": feedback_distribution,
                "content_distribution": content_distribution,
                "rating_stats": {
                    "avg_rating": rating_stats[0] if rating_stats[0] else 0,
                    "min_rating": rating_stats[1] if rating_stats[1] else 0,
                    "max_rating": rating_stats[2] if rating_stats[2] else 0,
                    "total_ratings": rating_stats[3],
                },
                "daily_volume_7d": daily_volume,
                "top_users": top_users,
                "time_range": {
                    "start": time_range[0].isoformat() if time_range else None,
                    "end": time_range[1].isoformat() if time_range else None,
                },
            }

        except Exception as e:
            logger.error(f"❌ Failed to get feedback analytics: {e}")
            return {"error": str(e)}

    async def _initialize_database(self) -> None:
        """Initialize SQLite database"""
        try:
            with sqlite3.connect(str(self.db_path)) as conn:
                cursor = conn.cursor()

                # Create feedback table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        content_id TEXT NOT NULL,
                        content_type TEXT NOT NULL,
                        feedback_type TEXT NOT NULL,
                        rating REAL,
                        feedback_text TEXT,
                        timestamp TEXT NOT NULL,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON feedback(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_id ON feedback(content_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON feedback(timestamp)")
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_content_type ON feedback(content_type)"
                )

                conn.commit()

            logger.info("📚 Database initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise

    def _validate_feedback(self, feedback: UserFeedback) -> bool:
        """Validate feedback data"""
        try:
            # Required fields
            if not feedback.user_id or not feedback.content_id:
                return False

            # Rating validation
            if feedback.rating is not None:
                if not (0 <= feedback.rating <= 5):
                    return False

            # Enum validation
            if not isinstance(feedback.content_type, ContentType):
                return False

            if not isinstance(feedback.feedback_type, FeedbackType):
                return False

            return True

        except Exception:
            return False

    async def _store_feedback_db(self, feedback: UserFeedback) -> bool:
        """Store feedback in database"""
        try:
            with self.db_lock:
                with sqlite3.connect(str(self.db_path)) as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT INTO feedback (
                            user_id, content_id, content_type, feedback_type,
                            rating, feedback_text, timestamp, metadata
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            feedback.user_id,
                            feedback.content_id,
                            feedback.content_type.value,
                            feedback.feedback_type.value,
                            feedback.rating,
                            feedback.feedback_text,
                            feedback.timestamp.isoformat(),
                            json.dumps(feedback.metadata) if feedback.metadata else None,
                        ),
                    )

                    conn.commit()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to store feedback in database: {e}")
            return False

    async def _load_recent_feedback(self) -> None:
        """Load recent feedback into cache"""
        try:
            # Load feedback from last 7 days
            cutoff_date = datetime.utcnow() - timedelta(days=7)
            recent_feedback = await self.get_feedback(
                time_range=(cutoff_date, datetime.utcnow()), limit=self.config.cache_size_limit
            )

            # Organize by user
            for feedback in recent_feedback:
                self.feedback_cache[feedback.user_id].append(feedback)
                self.user_feedback_count[feedback.user_id] += 1

            logger.info(f"📂 Loaded {len(recent_feedback)} recent feedback items into cache")

        except Exception as e:
            logger.warning(f"⚠️ Failed to load recent feedback: {e}")

    async def _manage_cache_size(self) -> None:
        """Manage cache size to stay within limits"""
        try:
            total_cached = sum(len(feedback_list) for feedback_list in self.feedback_cache.values())

            if total_cached > self.config.cache_size_limit:
                # Remove oldest feedback from cache
                excess = total_cached - self.config.cache_size_limit
                removed = 0

                for user_id in list(self.feedback_cache.keys()):
                    if removed >= excess:
                        break

                    feedback_list = self.feedback_cache[user_id]
                    if feedback_list:
                        # Sort by timestamp and remove oldest
                        feedback_list.sort(key=lambda f: f.timestamp)
                        to_remove = min(len(feedback_list), excess - removed)

                        for _ in range(to_remove):
                            feedback_list.pop(0)
                            removed += 1

                        # Remove empty lists
                        if not feedback_list:
                            del self.feedback_cache[user_id]
                            if user_id in self.user_feedback_count:
                                del self.user_feedback_count[user_id]

                logger.debug(f"🧹 Removed {removed} items from cache to manage size")

        except Exception as e:
            logger.error(f"❌ Failed to manage cache size: {e}")

    async def _clean_cache_old_feedback(self, cutoff_date: datetime) -> None:
        """Clean old feedback from cache"""
        try:
            for user_id in list(self.feedback_cache.keys()):
                original_count = len(self.feedback_cache[user_id])
                self.feedback_cache[user_id] = [
                    feedback
                    for feedback in self.feedback_cache[user_id]
                    if feedback.timestamp > cutoff_date
                ]

                # Update count
                removed_count = original_count - len(self.feedback_cache[user_id])
                self.user_feedback_count[user_id] -= removed_count

                # Remove empty entries
                if not self.feedback_cache[user_id]:
                    del self.feedback_cache[user_id]
                    if user_id in self.user_feedback_count:
                        del self.user_feedback_count[user_id]

        except Exception as e:
            logger.error(f"❌ Failed to clean cache: {e}")

    async def _cleanup_loop(self) -> None:
        """Background task for periodic cleanup"""
        while True:
            try:
                await asyncio.sleep(self.config.auto_cleanup_interval)
                await self.cleanup_old_feedback(self.config.retention_days)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in cleanup loop: {e}")

    async def shutdown(self) -> None:
        """Shutdown feedback storage"""
        try:
            # Cancel cleanup tasks
            for task in self.cleanup_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            self.cleanup_tasks.clear()
            self.is_initialized = False

            logger.info("🛑 Feedback storage shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "feedback_storage",
            "status": "healthy" if self.is_initialized else "initializing",
            "is_initialized": self.is_initialized,
            "database_path": str(self.db_path),
            "cached_users": len(self.feedback_cache),
            "cached_feedback": sum(
                len(feedback_list) for feedback_list in self.feedback_cache.values()
            ),
        }
