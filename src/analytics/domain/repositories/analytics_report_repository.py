"""
Analytics Report Repository Interface - Analytics Domain
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ....shared_kernel.domain.value_objects import UserId
from ..value_objects.analytics_value_objects import ChannelId
from ..entities.analytics_report import AnalyticsReport, ReportId, ReportType, ReportStatus


class IAnalyticsReportRepository(ABC):
    """
    Repository interface for AnalyticsReport aggregate
    
    Defines contract for persisting and retrieving AnalyticsReport entities
    following Repository pattern and Clean Architecture principles.
    """
    
    @abstractmethod
    async def save(self, report: AnalyticsReport) -> None:
        """
        Save analytics report aggregate (create or update)
        
        Args:
            report: AnalyticsReport aggregate to persist
            
        Raises:
            RepositoryError: If save operation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, report_id: ReportId) -> Optional[AnalyticsReport]:
        """
        Retrieve analytics report by ID
        
        Args:
            report_id: Unique report identifier
            
        Returns:
            AnalyticsReport aggregate if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: UserId,
        limit: int = 50,
        offset: int = 0
    ) -> List[AnalyticsReport]:
        """
        Get analytics reports by user ID with pagination
        
        Args:
            user_id: User identifier
            limit: Maximum reports to return
            offset: Results offset for pagination
            
        Returns:
            List of AnalyticsReport aggregates owned by the user
        """
        pass
    
    @abstractmethod
    async def get_by_status(
        self,
        status: ReportStatus,
        user_id: Optional[UserId] = None,
        limit: int = 100
    ) -> List[AnalyticsReport]:
        """
        Get reports by status with optional user filtering
        
        Args:
            status: Report status to filter by
            user_id: Optional user filter
            limit: Maximum reports to return
            
        Returns:
            List of AnalyticsReport aggregates with specified status
        """
        pass
    
    @abstractmethod
    async def get_by_type_and_period(
        self,
        user_id: UserId,
        report_type: ReportType,
        period_start: datetime,
        period_end: datetime
    ) -> List[AnalyticsReport]:
        """
        Get reports by type and period
        
        Args:
            user_id: User identifier
            report_type: Type of report
            period_start: Start of report period
            period_end: End of report period
            
        Returns:
            List of matching AnalyticsReport aggregates
        """
        pass
    
    @abstractmethod
    async def search_reports(
        self,
        user_id: UserId,
        search_query: Optional[str] = None,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AnalyticsReport]:
        """
        Search reports with multiple filters
        
        Args:
            user_id: User identifier
            search_query: Text search in title/description
            report_type: Filter by report type
            status: Filter by status
            date_from: Filter reports from this date
            date_to: Filter reports until this date
            limit: Maximum results to return
            offset: Results offset for pagination
            
        Returns:
            List of matching AnalyticsReport aggregates
        """
        pass
    
    @abstractmethod
    async def get_latest_report(
        self,
        user_id: UserId,
        report_type: Optional[ReportType] = None,
        status: ReportStatus = ReportStatus.COMPLETED
    ) -> Optional[AnalyticsReport]:
        """
        Get the latest report for a user
        
        Args:
            user_id: User identifier
            report_type: Optional report type filter
            status: Report status filter (default: completed)
            
        Returns:
            Latest AnalyticsReport aggregate if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_pending_reports(self, limit: int = 50) -> List[AnalyticsReport]:
        """
        Get reports that are pending generation
        
        Args:
            limit: Maximum reports to return
            
        Returns:
            List of pending AnalyticsReport aggregates
        """
        pass
    
    @abstractmethod
    async def get_expired_reports(self, limit: int = 100) -> List[AnalyticsReport]:
        """
        Get reports that have expired
        
        Args:
            limit: Maximum reports to return
            
        Returns:
            List of expired AnalyticsReport aggregates
        """
        pass
    
    @abstractmethod
    async def get_reports_by_channel(
        self,
        channel_id: ChannelId,
        user_id: UserId,
        limit: int = 20
    ) -> List[AnalyticsReport]:
        """
        Get reports that include a specific channel
        
        Args:
            channel_id: Channel identifier
            user_id: User identifier
            limit: Maximum reports to return
            
        Returns:
            List of AnalyticsReport aggregates including the channel
        """
        pass
    
    @abstractmethod
    async def get_report_by_share_token(self, share_token: str) -> Optional[AnalyticsReport]:
        """
        Get report by share token
        
        Args:
            share_token: Report share token
            
        Returns:
            AnalyticsReport aggregate if found and shareable, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_user_report_summary(self, user_id: UserId) -> Dict[str, Any]:
        """
        Get summary statistics for all user's reports
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with aggregated statistics across all user reports
        """
        pass
    
    @abstractmethod
    async def count_reports(
        self,
        user_id: Optional[UserId] = None,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> int:
        """
        Count reports with optional filters
        
        Args:
            user_id: Optional user filter
            report_type: Optional report type filter
            status: Optional status filter
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            Total number of matching reports
        """
        pass
    
    @abstractmethod
    async def delete(self, report_id: ReportId) -> bool:
        """
        Delete analytics report (hard delete)
        
        Args:
            report_id: Report identifier
            
        Returns:
            True if report was deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def exists(self, report_id: ReportId) -> bool:
        """
        Check if analytics report exists
        
        Args:
            report_id: Report identifier
            
        Returns:
            True if report exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def cleanup_old_reports(
        self,
        older_than: datetime,
        status: Optional[ReportStatus] = None
    ) -> int:
        """
        Clean up old reports (hard delete)
        
        Args:
            older_than: Delete reports older than this date
            status: Only delete reports with this status (optional)
            
        Returns:
            Number of reports deleted
        """
        pass
    
    @abstractmethod
    async def update_report_status(
        self,
        report_id: ReportId,
        status: ReportStatus,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Update report status (for background processing)
        
        Args:
            report_id: Report identifier
            status: New status
            error_message: Optional error message for failed status
            
        Returns:
            True if status was updated, False if report not found
        """
        pass
    
    @abstractmethod
    async def get_reports_for_regeneration(
        self,
        report_type: ReportType,
        user_id: Optional[UserId] = None,
        limit: int = 10
    ) -> List[AnalyticsReport]:
        """
        Get reports that might need regeneration (e.g., daily reports from yesterday)
        
        Args:
            report_type: Type of reports to check
            user_id: Optional user filter
            limit: Maximum reports to return
            
        Returns:
            List of AnalyticsReport aggregates that might need regeneration
        """
        pass