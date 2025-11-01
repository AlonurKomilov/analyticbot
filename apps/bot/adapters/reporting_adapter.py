"""
Bot Reporting Adapter - Thin layer adapting core reporting to bot interface
Follows Clean Architecture: Apps layer adapter wrapping Core business logic
"""

import logging
from typing import Any

import pandas as pd

from core.services.bot.reporting import AutomatedReportingSystem, ReportTemplate

logger = logging.getLogger(__name__)


class BotReportingAdapter:
    """
    Thin adapter for bot layer - translates bot requests to core reporting service
    This is how apps layer should work: thin translation, no business logic
    """

    def __init__(self, reporting_system: AutomatedReportingSystem):
        """
        Initialize bot reporting adapter

        Args:
            reporting_system: Core reporting system instance
        """
        self.reporting_system = reporting_system

    async def create_report(
        self,
        data: pd.DataFrame,
        template: ReportTemplate,
        output_format: str = "pdf",
        filename: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a report using core reporting system

        Args:
            data: Pandas DataFrame with report data
            template: Report template configuration
            output_format: Output format (pdf, excel, html, json)
            filename: Optional custom filename

        Returns:
            Result dictionary with file path and metadata
        """
        try:
            return await self.reporting_system.create_report(
                data, template, output_format, filename
            )
        except Exception as e:
            logger.error(f"Failed to create report: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None,
                "format": output_format,
            }

    async def schedule_report(
        self,
        schedule_name: str,
        data_generator: Any,
        template: ReportTemplate,
        schedule_time: str,
        output_format: str = "pdf",
        email_recipients: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Schedule a recurring report

        Args:
            schedule_name: Unique name for the scheduled report
            data_generator: Callable that generates report data
            template: Report template
            schedule_time: Schedule time string (e.g., "daily", "09:00")
            output_format: Output format
            email_recipients: Optional email recipients

        Returns:
            Scheduling result dictionary
        """
        try:
            return await self.reporting_system.schedule_report(
                schedule_name,
                data_generator,
                template,
                schedule_time,
                output_format,
                email_recipients,
            )
        except Exception as e:
            logger.error(f"Failed to schedule report: {e}")
            return {
                "success": False,
                "error": str(e),
                "report_id": None,
            }

    def configure_email(
        self, smtp_server: str, smtp_port: int, username: str, password: str
    ) -> None:
        """
        Configure email settings for report delivery

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port
            username: SMTP username
            password: SMTP password
        """
        self.reporting_system.configure_email(smtp_server, smtp_port, username, password)

    def get_report_history(self) -> dict[str, Any]:
        """
        Get report generation history

        Returns:
            Report history dictionary
        """
        return self.reporting_system.get_report_history()

    def get_scheduled_reports(self) -> dict[str, Any]:
        """
        Get list of scheduled reports

        Returns:
            Scheduled reports dictionary
        """
        return self.reporting_system.get_scheduled_reports()

    async def health_check(self) -> dict[str, Any]:
        """
        Check reporting system health

        Returns:
            Health check result dictionary
        """
        try:
            return await self.reporting_system.health_check()
        except Exception as e:
            logger.error(f"Reporting health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_reporting_system(self) -> AutomatedReportingSystem:
        """
        Get the underlying reporting system for advanced operations

        Returns:
            Core automated reporting system
        """
        return self.reporting_system
