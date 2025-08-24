"""
Framework-agnostic business services
Contains core business logic without external dependencies
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import logging

from core.models import (
    ScheduledPost, Delivery, ScheduleFilter, DeliveryFilter,
    PostStatus, DeliveryStatus
)
from core.repositories import ScheduleRepository, DeliveryRepository


logger = logging.getLogger(__name__)


class ScheduleService:
    """
    Business service for managing scheduled posts
    Framework-agnostic, depends only on repository interfaces
    """
    
    def __init__(self, schedule_repo: ScheduleRepository):
        """Initialize with repository dependency injection"""
        self.schedule_repo = schedule_repo
    
    async def create_scheduled_post(
        self,
        title: str,
        content: str,
        channel_id: str,
        user_id: str,
        scheduled_at: datetime,
        tags: Optional[List[str]] = None,
        media_urls: Optional[List[str]] = None,
        media_types: Optional[List[str]] = None
    ) -> ScheduledPost:
        """
        Create a new scheduled post with business validation
        """
        # Business rule: cannot schedule posts in the past
        if scheduled_at <= datetime.utcnow():
            raise ValueError("Cannot schedule posts in the past")
        
        # Business rule: validate content requirements
        if not content and not media_urls:
            raise ValueError("Post must have either content or media")
        
        # Create domain model
        post = ScheduledPost(
            title=title,
            content=content,
            channel_id=channel_id,
            user_id=user_id,
            scheduled_at=scheduled_at,
            status=PostStatus.SCHEDULED,
            tags=tags or [],
            media_urls=media_urls or [],
            media_types=media_types or []
        )
        
        # Persist using repository
        created_post = await self.schedule_repo.create(post)
        
        logger.info(f"Created scheduled post {created_post.id} for user {user_id}")
        return created_post
    
    async def get_post(self, post_id: UUID) -> Optional[ScheduledPost]:
        """Get a scheduled post by ID"""
        return await self.schedule_repo.get_by_id(post_id)
    
    async def update_post(self, post: ScheduledPost) -> ScheduledPost:
        """Update a scheduled post with business validation"""
        # Business rule: cannot modify published posts
        if post.status == PostStatus.PUBLISHED:
            raise ValueError("Cannot modify published posts")
        
        # Business rule: validate rescheduling
        if post.scheduled_at <= datetime.utcnow() and post.status == PostStatus.SCHEDULED:
            raise ValueError("Cannot reschedule to past time")
        
        updated_post = await self.schedule_repo.update(post)
        
        logger.info(f"Updated scheduled post {post.id}")
        return updated_post
    
    async def cancel_post(self, post_id: UUID) -> bool:
        """Cancel a scheduled post"""
        post = await self.schedule_repo.get_by_id(post_id)
        if not post:
            return False
        
        # Business rule: can only cancel draft or scheduled posts
        if post.status not in [PostStatus.DRAFT, PostStatus.SCHEDULED]:
            raise ValueError(f"Cannot cancel post with status: {post.status}")
        
        post.status = PostStatus.CANCELLED
        await self.schedule_repo.update(post)
        
        logger.info(f"Cancelled scheduled post {post_id}")
        return True
    
    async def delete_post(self, post_id: UUID) -> bool:
        """Delete a scheduled post"""
        post = await self.schedule_repo.get_by_id(post_id)
        if not post:
            return False
        
        # Business rule: can only delete draft or cancelled posts
        if post.status not in [PostStatus.DRAFT, PostStatus.CANCELLED]:
            raise ValueError(f"Cannot delete post with status: {post.status}")
        
        deleted = await self.schedule_repo.delete(post_id)
        
        if deleted:
            logger.info(f"Deleted scheduled post {post_id}")
        
        return deleted
    
    async def get_user_posts(
        self,
        user_id: str,
        status: Optional[PostStatus] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[ScheduledPost]:
        """Get all posts for a specific user"""
        filter_criteria = ScheduleFilter(
            user_id=user_id,
            status=status,
            limit=limit,
            offset=offset
        )
        
        return await self.schedule_repo.find(filter_criteria)
    
    async def get_channel_posts(
        self,
        channel_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[ScheduledPost]:
        """Get all posts for a specific channel"""
        filter_criteria = ScheduleFilter(
            channel_id=channel_id,
            from_date=from_date,
            to_date=to_date,
            limit=limit
        )
        
        return await self.schedule_repo.find(filter_criteria)
    
    async def get_posts_ready_for_delivery(self) -> List[ScheduledPost]:
        """Get all posts that are ready to be delivered"""
        return await self.schedule_repo.get_ready_for_delivery()


class DeliveryService:
    """
    Business service for managing post deliveries
    Framework-agnostic, handles delivery logic and retry policies
    """
    
    def __init__(
        self, 
        delivery_repo: DeliveryRepository,
        schedule_repo: ScheduleRepository
    ):
        """Initialize with repository dependency injection"""
        self.delivery_repo = delivery_repo
        self.schedule_repo = schedule_repo
    
    async def initiate_delivery(self, post: ScheduledPost) -> Delivery:
        """
        Initiate delivery for a scheduled post
        Creates delivery record and validates business rules
        """
        # Business rule: post must be ready for delivery
        if not post.is_ready_for_delivery():
            raise ValueError(f"Post {post.id} is not ready for delivery")
        
        # Create delivery record
        delivery = Delivery(
            post_id=post.id,
            delivery_channel_id=post.channel_id,
            status=DeliveryStatus.PENDING
        )
        
        created_delivery = await self.delivery_repo.create(delivery)
        
        logger.info(f"Initiated delivery {created_delivery.id} for post {post.id}")
        return created_delivery
    
    async def mark_delivery_in_progress(self, delivery_id: UUID) -> Optional[Delivery]:
        """Mark delivery as being processed"""
        delivery = await self.delivery_repo.get_by_id(delivery_id)
        if not delivery:
            return None
        
        delivery.status = DeliveryStatus.PROCESSING
        delivery.attempted_at = datetime.utcnow()
        
        updated_delivery = await self.delivery_repo.update(delivery)
        
        logger.info(f"Delivery {delivery_id} marked as processing")
        return updated_delivery
    
    async def complete_delivery(
        self, 
        delivery_id: UUID, 
        message_id: str
    ) -> Optional[ScheduledPost]:
        """
        Complete a successful delivery
        Updates both delivery and post status
        """
        delivery = await self.delivery_repo.get_by_id(delivery_id)
        if not delivery:
            return None
        
        # Update delivery status
        delivery.mark_as_delivered(message_id)
        await self.delivery_repo.update(delivery)
        
        # Update post status
        post = await self.schedule_repo.get_by_id(delivery.post_id)
        if post:
            post.mark_as_published()
            await self.schedule_repo.update(post)
        
        logger.info(f"Completed delivery {delivery_id} for post {delivery.post_id}")
        return post
    
    async def fail_delivery(
        self, 
        delivery_id: UUID, 
        error_message: str
    ) -> Optional[Delivery]:
        """
        Mark delivery as failed and handle retry logic
        """
        delivery = await self.delivery_repo.get_by_id(delivery_id)
        if not delivery:
            return None
        
        delivery.mark_as_failed(error_message)
        
        # Business rule: check if retry is possible
        if delivery.can_retry():
            delivery.increment_retry()
            logger.info(
                f"Delivery {delivery_id} failed, scheduled for retry "
                f"({delivery.retry_count}/{delivery.max_retries}): {error_message}"
            )
        else:
            # No more retries, mark post as failed too
            post = await self.schedule_repo.get_by_id(delivery.post_id)
            if post:
                post.mark_as_failed()
                await self.schedule_repo.update(post)
            
            logger.error(
                f"Delivery {delivery_id} permanently failed after "
                f"{delivery.retry_count} attempts: {error_message}"
            )
        
        updated_delivery = await self.delivery_repo.update(delivery)
        return updated_delivery
    
    async def get_delivery(self, delivery_id: UUID) -> Optional[Delivery]:
        """Get delivery by ID"""
        return await self.delivery_repo.get_by_id(delivery_id)
    
    async def get_post_deliveries(self, post_id: UUID) -> List[Delivery]:
        """Get all delivery attempts for a post"""
        return await self.delivery_repo.get_by_post_id(post_id)
    
    async def get_failed_retryable_deliveries(self) -> List[Delivery]:
        """Get deliveries that failed but can be retried"""
        return await self.delivery_repo.get_failed_retryable()
    
    async def get_delivery_stats(
        self, 
        channel_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> dict:
        """
        Get delivery statistics for analytics
        """
        filter_criteria = DeliveryFilter(
            channel_id=channel_id,
            from_date=from_date,
            to_date=to_date
        )
        
        # Get counts by status
        stats = {}
        for status in DeliveryStatus:
            status_filter = DeliveryFilter(
                channel_id=channel_id,
                from_date=from_date,
                to_date=to_date,
                status=status
            )
            stats[status.value] = await self.delivery_repo.count(status_filter)
        
        # Calculate success rate
        total_attempts = sum(stats.values())
        successful = stats.get(DeliveryStatus.DELIVERED.value, 0)
        
        stats['total_attempts'] = total_attempts
        stats['success_rate'] = (successful / total_attempts * 100) if total_attempts > 0 else 0
        
        return stats
