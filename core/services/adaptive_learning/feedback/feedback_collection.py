"""
Feedback Collection Service for Adaptive Learning
=================================================

Collects, validates, and processes user feedback for model improvement.
Implements quality scoring and feedback preparation for learning algorithms.
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from ..protocols.feedback_protocols import (
    ContentType,
    FeedbackBatch,
    FeedbackType,
    UserFeedback,
)
from .feedback_storage import FeedbackStorageService

logger = logging.getLogger(__name__)


@dataclass
class FeedbackValidationConfig:
    """Configuration for feedback validation"""

    min_rating: float = 1.0
    max_rating: float = 5.0
    min_text_length: int = 5
    max_text_length: int = 1000
    required_fields: list[str] = field(default_factory=list)
    allowed_content_types: list[ContentType] = field(default_factory=list)
    spam_detection_enabled: bool = True
    profanity_filter_enabled: bool = True

    def __post_init__(self):
        if self.required_fields is None:
            self.required_fields = ["user_id", "content_id", "feedback_type"]
        if self.allowed_content_types is None:
            self.allowed_content_types = list(ContentType)


@dataclass
class FeedbackCollectionConfig:
    """Configuration for feedback collection service"""

    batch_size: int = 50
    processing_interval: int = 30  # seconds
    quality_threshold: float = 0.5
    auto_processing: bool = True
    feedback_aggregation: bool = True
    sentiment_analysis: bool = True
    duplicate_detection: bool = True


class FeedbackCollectionService:
    """
    Microservice for collecting and processing user feedback.

    Handles feedback validation, quality assessment,
    and preparation for adaptive learning algorithms.
    """

    def __init__(
        self,
        storage: FeedbackStorageService,
        collection_config: FeedbackCollectionConfig | None = None,
        validation_config: FeedbackValidationConfig | None = None,
    ):
        self.storage = storage
        self.collection_config = collection_config or FeedbackCollectionConfig()
        self.validation_config = validation_config or FeedbackValidationConfig()

        # Service state
        self.is_running = False
        self.processing_tasks: list[asyncio.Task] = []

        # Feedback queues
        self.pending_feedback: list[UserFeedback] = []
        self.processing_queue: asyncio.Queue = asyncio.Queue()

        # Quality tracking
        self.quality_stats: dict[str, Any] = {}
        self.processed_count: dict[str, int] = {}

        # Spam/duplicate detection
        self.spam_patterns: list[str] = [
            r"(.)\1{10,}",  # Repeated characters
            r"[A-Z]{20,}",  # Excessive caps
            r"http[s]?://\S+",  # URLs
        ]
        self.recent_feedback_cache: set[str] = set()

        logger.info("👥 Feedback Collection Service initialized")

    async def start_collection(self) -> bool:
        """Start feedback collection processing"""
        try:
            if not self.storage.is_initialized:
                logger.error("❌ Storage service not initialized")
                return False

            # Start processing tasks
            if self.collection_config.auto_processing:
                processing_task = asyncio.create_task(self._processing_loop())
                self.processing_tasks.append(processing_task)

            # Start quality analysis task
            if self.collection_config.sentiment_analysis:
                analysis_task = asyncio.create_task(self._analysis_loop())
                self.processing_tasks.append(analysis_task)

            self.is_running = True
            logger.info("✅ Feedback collection started")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start feedback collection: {e}")
            return False

    async def stop_collection(self) -> bool:
        """Stop feedback collection processing"""
        try:
            # Cancel processing tasks
            for task in self.processing_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            self.processing_tasks.clear()
            self.is_running = False

            logger.info("⏹️ Feedback collection stopped")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to stop feedback collection: {e}")
            return False

    async def collect_feedback(self, feedback: UserFeedback) -> bool:
        """Collect a single piece of feedback"""
        try:
            # Validate feedback
            validation_result = await self._validate_feedback(feedback)
            if not validation_result["is_valid"]:
                logger.warning(f"⚠️ Invalid feedback: {validation_result['reason']}")
                return False

            # Check for duplicates
            if self.collection_config.duplicate_detection:
                if await self._is_duplicate(feedback):
                    logger.warning(f"⚠️ Duplicate feedback detected from user {feedback.user_id}")
                    return False

            # Calculate quality score
            quality_score = await self._calculate_quality_score(feedback)
            if quality_score < self.collection_config.quality_threshold:
                logger.warning(f"⚠️ Low quality feedback: {quality_score}")
                # Still collect but mark as low quality

            # Add to processing queue
            self.pending_feedback.append(feedback)
            await self.processing_queue.put(feedback)

            # Update cache for duplicate detection
            feedback_hash = self._generate_feedback_hash(feedback)
            self.recent_feedback_cache.add(feedback_hash)

            logger.debug(f"👥 Collected feedback from user {feedback.user_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to collect feedback: {e}")
            return False

    async def collect_feedback_batch(self, feedback_list: list[UserFeedback]) -> dict[str, Any]:
        """Collect a batch of feedback"""
        try:
            results = {
                "total": len(feedback_list),
                "collected": 0,
                "rejected": 0,
                "errors": [],
            }

            for feedback in feedback_list:
                success = await self.collect_feedback(feedback)
                if success:
                    results["collected"] += 1
                else:
                    results["rejected"] += 1

            # Create batch if enabled
            if self.collection_config.feedback_aggregation and results["collected"] > 0:
                batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                batch = FeedbackBatch(batch_id=batch_id, feedback_list=feedback_list)

                await self.storage.store_feedback_batch(batch)
                results["batch_id"] = batch_id

            logger.info(
                f"📦 Processed feedback batch: {results['collected']}/{results['total']} collected"
            )
            return results

        except Exception as e:
            logger.error(f"❌ Failed to collect feedback batch: {e}")
            return {"error": str(e)}

    async def get_feedback_analysis(
        self,
        content_id: str | None = None,
        time_range: tuple[datetime, datetime] | None = None,
    ) -> dict[str, Any]:
        """Get analysis of collected feedback"""
        try:
            # Get feedback from storage
            feedback_list = await self.storage.get_feedback(
                content_type=None, time_range=time_range
            )

            if content_id:
                feedback_list = [f for f in feedback_list if f.content_id == content_id]

            if not feedback_list:
                return {"status": "no_data", "total_feedback": 0}

            # Analyze feedback
            analysis = await self._analyze_feedback(feedback_list)

            return {
                "status": "success",
                "total_feedback": len(feedback_list),
                "analysis": analysis,
                "time_range": {
                    "start": time_range[0].isoformat() if time_range else None,
                    "end": time_range[1].isoformat() if time_range else None,
                },
            }

        except Exception as e:
            logger.error(f"❌ Failed to get feedback analysis: {e}")
            return {"error": str(e)}

    async def get_collection_status(self) -> dict[str, Any]:
        """Get status of feedback collection service"""
        try:
            storage_status = await self.storage.get_storage_status()

            return {
                "service": "feedback_collection",
                "is_running": self.is_running,
                "pending_feedback": len(self.pending_feedback),
                "queue_size": self.processing_queue.qsize(),
                "active_tasks": len([t for t in self.processing_tasks if not t.done()]),
                "quality_stats": self.quality_stats,
                "processed_count": self.processed_count,
                "storage_status": storage_status,
                "config": {
                    "batch_size": self.collection_config.batch_size,
                    "quality_threshold": self.collection_config.quality_threshold,
                    "auto_processing": self.collection_config.auto_processing,
                    "duplicate_detection": self.collection_config.duplicate_detection,
                },
            }

        except Exception as e:
            logger.error(f"❌ Failed to get collection status: {e}")
            return {"error": str(e)}

    async def _validate_feedback(self, feedback: UserFeedback) -> dict[str, Any]:
        """Validate feedback against configured rules"""
        try:
            # Check required fields
            for field in self.validation_config.required_fields:
                if not getattr(feedback, field, None):
                    return {
                        "is_valid": False,
                        "reason": f"Missing required field: {field}",
                    }

            # Check content type
            if feedback.content_type not in self.validation_config.allowed_content_types:
                return {
                    "is_valid": False,
                    "reason": f"Invalid content type: {feedback.content_type}",
                }

            # Validate rating if present
            if feedback.rating is not None:
                if not (
                    self.validation_config.min_rating
                    <= feedback.rating
                    <= self.validation_config.max_rating
                ):
                    return {
                        "is_valid": False,
                        "reason": f"Rating out of range: {feedback.rating}",
                    }

            # Validate feedback text length
            if feedback.feedback_text:
                text_length = len(feedback.feedback_text)
                if text_length < self.validation_config.min_text_length:
                    return {
                        "is_valid": False,
                        "reason": f"Text too short: {text_length} characters",
                    }
                if text_length > self.validation_config.max_text_length:
                    return {
                        "is_valid": False,
                        "reason": f"Text too long: {text_length} characters",
                    }

            # Spam detection
            if self.validation_config.spam_detection_enabled and feedback.feedback_text:
                if await self._detect_spam(feedback.feedback_text):
                    return {"is_valid": False, "reason": "Spam detected"}

            return {"is_valid": True, "reason": "Valid feedback"}

        except Exception as e:
            logger.error(f"❌ Failed to validate feedback: {e}")
            return {"is_valid": False, "reason": f"Validation error: {e}"}

    async def _calculate_quality_score(self, feedback: UserFeedback) -> float:
        """Calculate quality score for feedback"""
        try:
            score = 0.0
            weight_sum = 0.0

            # Rating presence and validity (30%)
            if feedback.rating is not None:
                rating_normalized = (feedback.rating - self.validation_config.min_rating) / (
                    self.validation_config.max_rating - self.validation_config.min_rating
                )
                score += rating_normalized * 0.3
                weight_sum += 0.3

            # Text quality (40%)
            if feedback.feedback_text:
                text_score = await self._assess_text_quality(feedback.feedback_text)
                score += text_score * 0.4
                weight_sum += 0.4

            # Feedback type appropriateness (15%)
            type_score = 0.8  # Default good score
            if feedback.feedback_type in [
                FeedbackType.EXPLICIT_RATING,
                FeedbackType.CORRECTION,
            ]:
                type_score = 1.0  # High value feedback types
            score += type_score * 0.15
            weight_sum += 0.15

            # User engagement level (15%)
            engagement_score = await self._assess_user_engagement(feedback.user_id)
            score += engagement_score * 0.15
            weight_sum += 0.15

            # Normalize by actual weights used
            final_score = score / weight_sum if weight_sum > 0 else 0.0

            return min(1.0, max(0.0, final_score))

        except Exception as e:
            logger.error(f"❌ Failed to calculate quality score: {e}")
            return 0.5  # Default middle score

    async def _assess_text_quality(self, text: str) -> float:
        """Assess quality of feedback text"""
        try:
            if not text:
                return 0.0

            score = 0.5  # Base score

            # Length score (moderate length is better)
            length = len(text)
            if 20 <= length <= 200:
                score += 0.2
            elif 10 <= length <= 500:
                score += 0.1

            # Word count
            words = text.split()
            if 5 <= len(words) <= 50:
                score += 0.1

            # Sentence structure (simple check)
            sentences = text.split(".")
            if len(sentences) > 1:
                score += 0.1

            # No excessive repetition
            if not any(re.search(pattern, text) for pattern in self.spam_patterns):
                score += 0.1

            return min(1.0, score)

        except Exception as e:
            logger.error(f"❌ Failed to assess text quality: {e}")
            return 0.5

    async def _assess_user_engagement(self, user_id: str) -> float:
        """Assess user engagement level"""
        try:
            # Get user's feedback history
            user_summary = await self.storage.get_user_feedback_summary(user_id)

            if "error" in user_summary:
                return 0.5  # Default for new users

            total_feedback = user_summary.get("total_feedback", 0)
            recent_activity = user_summary.get("recent_activity_30d", 0)

            # Score based on activity
            if total_feedback >= 10:
                engagement = 1.0
            elif total_feedback >= 5:
                engagement = 0.8
            elif total_feedback >= 2:
                engagement = 0.6
            else:
                engagement = 0.4  # New user

            # Boost for recent activity
            if recent_activity > 0:
                engagement = min(1.0, engagement + 0.1)

            return engagement

        except Exception as e:
            logger.error(f"❌ Failed to assess user engagement: {e}")
            return 0.5

    async def _detect_spam(self, text: str) -> bool:
        """Detect spam in feedback text"""
        try:
            # Check against spam patterns
            for pattern in self.spam_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return True

            # Additional spam checks
            words = text.split()

            # Too many repeated words
            if len(set(words)) < len(words) * 0.3:  # Less than 30% unique words
                return True

            # All caps (if more than 10 characters)
            if len(text) > 10 and text.isupper():
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Failed to detect spam: {e}")
            return False

    async def _is_duplicate(self, feedback: UserFeedback) -> bool:
        """Check if feedback is a duplicate"""
        try:
            feedback_hash = self._generate_feedback_hash(feedback)
            return feedback_hash in self.recent_feedback_cache

        except Exception as e:
            logger.error(f"❌ Failed to check for duplicates: {e}")
            return False

    def _generate_feedback_hash(self, feedback: UserFeedback) -> str:
        """Generate hash for duplicate detection"""
        try:
            # Create hash from key fields
            hash_content = (
                f"{feedback.user_id}_{feedback.content_id}_{feedback.feedback_type.value}"
            )
            if feedback.feedback_text:
                # Add first 50 characters of text for uniqueness
                hash_content += f"_{feedback.feedback_text[:50]}"

            return str(hash(hash_content))

        except Exception as e:
            logger.error(f"❌ Failed to generate feedback hash: {e}")
            return ""

    async def _analyze_feedback(self, feedback_list: list[UserFeedback]) -> dict[str, Any]:
        """Analyze a list of feedback"""
        try:
            analysis = {
                "total_count": len(feedback_list),
                "feedback_by_type": {},
                "content_by_type": {},
                "rating_statistics": {},
                "quality_distribution": {},
                "sentiment_analysis": {},
                "user_engagement": {},
            }

            # Count by feedback type
            for feedback in feedback_list:
                feedback_type = feedback.feedback_type.value
                analysis["feedback_by_type"][feedback_type] = (
                    analysis["feedback_by_type"].get(feedback_type, 0) + 1
                )

                content_type = feedback.content_type.value
                analysis["content_by_type"][content_type] = (
                    analysis["content_by_type"].get(content_type, 0) + 1
                )

            # Rating statistics
            ratings = [f.rating for f in feedback_list if f.rating is not None]
            if ratings:
                analysis["rating_statistics"] = {
                    "count": len(ratings),
                    "average": sum(ratings) / len(ratings),
                    "min": min(ratings),
                    "max": max(ratings),
                }

            # Quality assessment
            qualities = []
            for feedback in feedback_list[:100]:  # Sample first 100 for performance
                quality = await self._calculate_quality_score(feedback)
                qualities.append(quality)

            if qualities:
                analysis["quality_distribution"] = {
                    "average": sum(qualities) / len(qualities),
                    "high_quality_count": len([q for q in qualities if q >= 0.8]),
                    "low_quality_count": len([q for q in qualities if q < 0.5]),
                }

            # User engagement analysis
            unique_users = {f.user_id for f in feedback_list}
            analysis["user_engagement"] = {
                "unique_users": len(unique_users),
                "feedback_per_user": (
                    len(feedback_list) / len(unique_users) if unique_users else 0
                ),
            }

            return analysis

        except Exception as e:
            logger.error(f"❌ Failed to analyze feedback: {e}")
            return {"error": str(e)}

    async def _processing_loop(self) -> None:
        """Background task for processing feedback"""
        while self.is_running:
            try:
                # Process pending feedback in batches
                if len(self.pending_feedback) >= self.collection_config.batch_size:
                    await self._process_feedback_batch()

                await asyncio.sleep(self.collection_config.processing_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in processing loop: {e}")

    async def _analysis_loop(self) -> None:
        """Background task for feedback analysis"""
        while self.is_running:
            try:
                # Perform periodic analysis
                await asyncio.sleep(300)  # Every 5 minutes

                # Update quality statistics
                await self._update_quality_statistics()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in analysis loop: {e}")

    async def _process_feedback_batch(self) -> None:
        """Process a batch of pending feedback"""
        try:
            if not self.pending_feedback:
                return

            batch = self.pending_feedback[: self.collection_config.batch_size]
            self.pending_feedback = self.pending_feedback[self.collection_config.batch_size :]

            # Store feedback
            for feedback in batch:
                success = await self.storage.store_feedback(feedback)
                if success:
                    # Update processed count
                    user_id = feedback.user_id
                    self.processed_count[user_id] = self.processed_count.get(user_id, 0) + 1

            logger.info(f"📦 Processed feedback batch of {len(batch)} items")

        except Exception as e:
            logger.error(f"❌ Failed to process feedback batch: {e}")

    async def _update_quality_statistics(self) -> None:
        """Update quality statistics"""
        try:
            # Get recent feedback for analysis
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)

            recent_feedback = await self.storage.get_feedback(
                time_range=(start_time, end_time), limit=100
            )

            if not recent_feedback:
                return

            # Calculate quality stats
            qualities = []
            for feedback in recent_feedback:
                quality = await self._calculate_quality_score(feedback)
                qualities.append(quality)

            if qualities:
                avg_quality = sum(qualities) / len(qualities)
                self.quality_stats["recent_average"] = avg_quality
                self.quality_stats["sample_size"] = len(qualities)
                self.quality_stats["last_updated"] = datetime.utcnow().isoformat()

        except Exception as e:
            logger.error(f"❌ Failed to update quality statistics: {e}")

    async def shutdown(self) -> None:
        """Shutdown feedback collection service"""
        try:
            await self.stop_collection()

            # Process any remaining feedback
            if self.pending_feedback:
                await self._process_feedback_batch()

            logger.info("🛑 Feedback collection service shutdown complete")

        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

    def get_service_health(self) -> dict[str, Any]:
        """Get service health status"""
        return {
            "service": "feedback_collection",
            "status": "healthy" if self.is_running else "stopped",
            "is_running": self.is_running,
            "pending_feedback": len(self.pending_feedback),
            "queue_size": (
                self.processing_queue.qsize() if hasattr(self.processing_queue, "qsize") else 0
            ),
        }
