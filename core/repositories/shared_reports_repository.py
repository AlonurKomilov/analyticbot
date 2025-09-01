"""
Shared Reports Repository Interface
Clean Architecture repository pattern for shared reports management
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class SharedReportsRepository(ABC):
    """Repository interface for shared reports management"""

    @abstractmethod
    async def create_shared_report(
        self,
        share_token: str,
        report_type: str,
        channel_id: str,
        period: int,
        format: str,
        expires_at: datetime,
    ) -> str:
        """
        Create a new shared report

        Args:
            share_token: Unique token for the share link
            report_type: Type of report (overview, growth, reach, etc.)
            channel_id: Channel identifier
            period: Time period in days
            format: Export format (csv, png)
            expires_at: Expiration timestamp

        Returns:
            Shared report ID
        """

    @abstractmethod
    async def get_shared_report(self, share_token: str) -> dict[str, Any] | None:
        """
        Get shared report by token

        Args:
            share_token: Share link token

        Returns:
            Shared report data or None if not found
        """

    @abstractmethod
    async def increment_access_count(self, share_token: str) -> None:
        """
        Increment access count for a shared report

        Args:
            share_token: Share link token
        """

    @abstractmethod
    async def delete_shared_report(self, share_token: str) -> None:
        """
        Delete a shared report

        Args:
            share_token: Share link token
        """

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """
        Clean up expired shared reports

        Returns:
            Number of reports deleted
        """

    @abstractmethod
    async def get_reports_by_channel(
        self, channel_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Get shared reports for a specific channel

        Args:
            channel_id: Channel identifier
            limit: Maximum number of reports to return

        Returns:
            List of shared report data
        """
