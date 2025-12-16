"""
Base MTProto Service - Abstract base class for all MTProto marketplace services

Provides:
- Feature gate integration
- Usage tracking
- Quota enforcement
- Error handling
- Logging
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from core.services.feature_gate_service import FeatureGateService
from infra.db.repositories.marketplace_service_repository import (
    MarketplaceServiceRepository,
)


logger = logging.getLogger(__name__)


class BaseMTProtoService(ABC):
    """
    Abstract base class for all MTProto marketplace services.
    
    Subclasses must implement:
    - service_key: Unique identifier matching marketplace_services table
    - execute(): Core service logic
    
    Provides automatic:
    - Feature gate checks
    - Usage logging
    - Quota enforcement
    - Error tracking
    """

    def __init__(
        self,
        user_id: int,
        feature_gate_service: FeatureGateService,
        marketplace_repo: MarketplaceServiceRepository,
    ):
        """
        Initialize MTProto service.
        
        Args:
            user_id: User's ID
            feature_gate_service: Service for access control
            marketplace_repo: Repository for usage logging
        """
        self.user_id = user_id
        self.feature_gate = feature_gate_service
        self.marketplace_repo = marketplace_repo
        
        # Service metadata (set by subclass)
        self._service_key: str | None = None
        self._service_name: str | None = None

    @property
    @abstractmethod
    def service_key(self) -> str:
        """Unique service identifier (e.g., 'mtproto_history_access')"""
        pass

    @property
    def service_name(self) -> str:
        """Human-readable service name"""
        return self._service_name or self.service_key

    @abstractmethod
    async def execute(self, **kwargs) -> dict[str, Any]:
        """
        Execute the service logic.
        
        This method should contain the core functionality of the service.
        It will only be called if the user has access.
        
        Args:
            **kwargs: Service-specific parameters
            
        Returns:
            dict with result details (success, message, data, etc.)
        """
        pass

    async def run(self, **kwargs) -> dict[str, Any]:
        """
        Run the service with automatic feature gating and logging.
        
        This is the main entry point - always call this instead of execute().
        
        Args:
            **kwargs: Service-specific parameters
            
        Returns:
            dict with execution results
        """
        start_time = datetime.now()
        
        try:
            # Check feature access
            has_access, denial_reason = await self.feature_gate.check_access(
                user_id=self.user_id,
                service_key=self.service_key,
            )
            
            if not has_access:
                logger.info(
                    f"MTProto service access denied for user {self.user_id}: "
                    f"{self.service_key} - {denial_reason}"
                )
                return {
                    "success": False,
                    "error": "access_denied",
                    "message": denial_reason or "Service not available",
                }
            
            # Check quota
            within_quota, quota_message = await self.feature_gate.check_quota(
                user_id=self.user_id,
                service_key=self.service_key,
            )
            
            if not within_quota:
                logger.info(
                    f"Quota exceeded for user {self.user_id}: "
                    f"{self.service_key} - {quota_message}"
                )
                return {
                    "success": False,
                    "error": "quota_exceeded",
                    "message": quota_message or "Usage limit reached",
                }
            
            # Execute service logic
            result = await self.execute(**kwargs)
            
            # Track execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log successful usage
            await self._log_usage(
                success=True,
                execution_time_ms=int(execution_time),
                metadata={
                    "result_summary": self._summarize_result(result),
                    "kwargs": self._sanitize_kwargs(kwargs),
                },
            )
            
            return {**result, "success": True}
            
        except Exception as e:
            # Log failed usage
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            await self._log_usage(
                success=False,
                execution_time_ms=int(execution_time),
                error_message=str(e),
                metadata={"kwargs": self._sanitize_kwargs(kwargs)},
            )
            
            logger.error(
                f"MTProto service execution failed for user {self.user_id}: "
                f"{self.service_key} - {e}",
                exc_info=True,
            )
            
            return {
                "success": False,
                "error": "execution_failed",
                "message": f"Service error: {str(e)}",
            }

    async def _log_usage(
        self,
        success: bool,
        execution_time_ms: int,
        metadata: dict | None = None,
        error_message: str | None = None,
    ) -> None:
        """Log service usage to database."""
        try:
            # Get subscription ID
            subscription = await self.marketplace_repo.get_user_subscription(
                user_id=self.user_id,
                service_key=self.service_key,
                active_only=True,
            )
            
            subscription_id = subscription["id"] if subscription else None
            
            # Get channel_id from metadata if available
            chat_id = None
            if metadata and "kwargs" in metadata:
                chat_id = metadata["kwargs"].get("channel_id") or metadata["kwargs"].get("chat_id")
            
            # Log usage
            await self.marketplace_repo.log_service_usage(
                user_id=self.user_id,
                service_key=self.service_key,
                subscription_id=subscription_id,
                action=f"{self.service_key}_executed",
                chat_id=chat_id,
                metadata=metadata,
                execution_time_ms=execution_time_ms,
                success=success,
                error_message=error_message,
            )
            
        except Exception as e:
            # Don't fail the request if logging fails
            logger.error(f"Failed to log MTProto service usage: {e}")

    def _sanitize_kwargs(self, kwargs: dict) -> dict:
        """Remove sensitive data from kwargs before logging."""
        # Create a copy to avoid modifying original
        sanitized = kwargs.copy()
        
        # Remove sensitive fields
        sensitive_fields = ["token", "password", "api_key", "secret", "session_string", "api_hash"]
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "***REDACTED***"
        
        # Truncate long strings
        for key, value in sanitized.items():
            if isinstance(value, str) and len(value) > 200:
                sanitized[key] = value[:200] + "..."
        
        return sanitized

    def _summarize_result(self, result: dict) -> dict:
        """Create a summary of the result for logging (avoid storing large data)."""
        summary = {}
        
        # Include counts but not full data
        if "messages" in result:
            summary["message_count"] = len(result["messages"]) if isinstance(result["messages"], list) else 0
        
        if "media" in result:
            summary["media_count"] = len(result["media"]) if isinstance(result["media"], list) else 0
        
        if "participants" in result:
            summary["participant_count"] = len(result["participants"]) if isinstance(result["participants"], list) else 0
        
        # Include simple fields
        for key, value in result.items():
            if key not in ["messages", "media", "participants", "data"]:
                if isinstance(value, (str, int, float, bool)) or value is None:
                    summary[key] = value
        
        return summary
