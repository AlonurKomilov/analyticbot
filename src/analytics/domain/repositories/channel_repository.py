"""
Channel Repository Interface - Analytics Domain
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ....shared_kernel.domain.value_objects import UserId
from ..value_objects.analytics_value_objects import ChannelId, ChannelUsername
from ..entities.channel import Channel, ChannelStatus, ChannelType


class IChannelRepository(ABC):
    """
    Repository interface for Channel aggregate
    
    Defines contract for persisting and retrieving Channel entities
    following Repository pattern and Clean Architecture principles.
    """
    
    @abstractmethod
    async def save(self, channel: Channel) -> None:
        """
        Save channel aggregate (create or update)
        
        Args:
            channel: Channel aggregate to persist
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, channel_id: ChannelId) -> Optional[Channel]:
        """
        Retrieve channel by ID
        
        Args:
            channel_id: Unique channel identifier
            
        Returns:
            Channel aggregate if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_username(self, username: ChannelUsername) -> Optional[Channel]:
        """
        Retrieve channel by username
        
        Args:
            username: Channel username (without @)
            
        Returns:
            Channel aggregate if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[Channel]:
        """
        Get all channels belonging to a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of Channel aggregates owned by the user
        """
        pass
    
    @abstractmethod
    async def get_active_channels(self, user_id: UserId) -> List[Channel]:
        """
        Get active channels for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of active Channel aggregates
        """
        pass
    
    @abstractmethod
    async def get_channels_by_status(
        self, 
        user_id: UserId, 
        status: ChannelStatus
    ) -> List[Channel]:
        """
        Get channels by status for a user
        
        Args:
            user_id: User identifier
            status: Channel status to filter by
            
        Returns:
            List of Channel aggregates with specified status
        """
        pass
    
    @abstractmethod
    async def search_channels(
        self,
        user_id: UserId,
        search_query: Optional[str] = None,
        channel_type: Optional[ChannelType] = None,
        status: Optional[ChannelStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Channel]:
        """
        Search channels with filters
        
        Args:
            user_id: User identifier
            search_query: Text search in title/username
            channel_type: Filter by channel type
            status: Filter by status
            limit: Maximum results to return
            offset: Results offset for pagination
            
        Returns:
            List of matching Channel aggregates
        """
        pass
    
    @abstractmethod
    async def get_top_performing_channels(
        self,
        user_id: UserId,
        metric: str = "total_views",
        limit: int = 10,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> List[Channel]:
        """
        Get top performing channels by metric
        
        Args:
            user_id: User identifier
            metric: Metric to rank by (total_views, average_views_per_post, etc.)
            limit: Number of top channels to return
            period_start: Optional start date for metric calculation
            period_end: Optional end date for metric calculation
            
        Returns:
            List of top performing Channel aggregates
        """
        pass
    
    @abstractmethod
    async def get_channel_statistics(
        self,
        channel_id: ChannelId,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """
        Get aggregated statistics for a channel in a period
        
        Args:
            channel_id: Channel identifier
            period_start: Start of statistics period
            period_end: End of statistics period
            
        Returns:
            Dictionary with aggregated statistics
        """
        pass
    
    @abstractmethod
    async def update_channel_metrics(
        self,
        channel_id: ChannelId,
        metrics: Dict[str, Any]
    ) -> None:
        """
        Bulk update channel metrics
        
        Args:
            channel_id: Channel identifier
            metrics: Dictionary of metrics to update
            
        Raises:
            RepositoryError: If update operation fails
        """
        pass
    
    @abstractmethod
    async def get_channels_needing_analytics_update(
        self,
        last_update_before: datetime,
        limit: int = 50
    ) -> List[Channel]:
        """
        Get channels that need analytics updates
        
        Args:
            last_update_before: Channels updated before this time
            limit: Maximum channels to return
            
        Returns:
            List of Channel aggregates needing updates
        """
        pass
    
    @abstractmethod
    async def delete(self, channel_id: ChannelId) -> bool:
        """
        Delete channel (hard delete)
        
        Args:
            channel_id: Channel identifier
            
        Returns:
            True if channel was deleted, False if not found
            
        Note:
            This is hard delete. For soft delete, use Channel.delete_channel()
        """
        pass
    
    @abstractmethod
    async def exists(self, channel_id: ChannelId) -> bool:
        """
        Check if channel exists
        
        Args:
            channel_id: Channel identifier
            
        Returns:
            True if channel exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def count_by_user(self, user_id: UserId) -> int:
        """
        Count total channels for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Total number of channels owned by user
        """
        pass
    
    @abstractmethod
    async def get_user_channel_summary(self, user_id: UserId) -> Dict[str, Any]:
        """
        Get summary statistics for all user's channels
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with aggregated statistics across all user channels
        """
        pass