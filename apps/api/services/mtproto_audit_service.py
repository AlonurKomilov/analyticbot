"""
Service for logging MTProto-related audit events.

This service tracks all MTProto state changes including enable/disable toggles,
setup, verification, and removal actions for compliance and debugging purposes.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import Request

from core.domain.mtproto_models import MTProtoAuditLogDTO
from core.ports.mtproto_repository import IMTProtoAuditRepository


class MTProtoAuditService:
    """Service for logging MTProto audit events."""

    def __init__(self, audit_repo: IMTProtoAuditRepository):
        self.audit_repo = audit_repo

    async def log_event(
        self,
        user_id: int,
        action: str,
        channel_id: int | None = None,
        previous_state: bool | None = None,
        new_state: bool | None = None,
        request: Request | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Log an MTProto-related event.

        Args:
            user_id: ID of the user performing the action
            action: Type of action (enabled, disabled, setup, verified, disconnected, removed)
            channel_id: Optional channel ID (NULL for global settings)
            previous_state: Previous mtproto_enabled state
            new_state: New mtproto_enabled state
            request: FastAPI request object for IP/user agent extraction
            metadata: Optional JSON metadata (e.g., error details, additional context)
        """
        ip_address = None
        user_agent = None

        if request:
            # Extract IP address (check for proxy headers first)
            ip_address = (
                request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                or request.headers.get("X-Real-IP")
                or (request.client.host if request.client else None)
            )
            # Truncate to 45 chars (max IPv6 length)
            if ip_address:
                ip_address = ip_address[:45]

            # Extract user agent and truncate to 500 chars
            user_agent = request.headers.get("User-Agent")
            if user_agent:
                user_agent = user_agent[:500]

        details = metadata or {}
        if previous_state is not None:
            details["previous_state"] = previous_state
        if new_state is not None:
            details["new_state"] = new_state

        await self.audit_repo.log_action(
            user_id=user_id,
            action=action,
            channel_id=channel_id,
            details=details,
            timestamp=datetime.now(UTC),
        )

    async def log_toggle_event(
        self,
        user_id: int,
        enabled: bool,
        request: Request | None = None,
        channel_id: int | None = None,
        previous_state: bool | None = None,
    ) -> None:
        """
        Log a toggle enable/disable event.

        Args:
            user_id: ID of the user
            enabled: New enabled state
            request: FastAPI request for IP/user agent
            channel_id: Optional channel ID (for per-channel toggles)
            previous_state: Previous enabled state
        """
        action = "enabled" if enabled else "disabled"
        scope = f"channel_{channel_id}" if channel_id else "global"

        await self.log_event(
            user_id=user_id,
            action=action,
            channel_id=channel_id,
            previous_state=previous_state,
            new_state=enabled,
            request=request,
            metadata={"scope": scope},
        )

    async def log_setup_event(
        self,
        user_id: int,
        phone: str,
        request: Request | None = None,
    ) -> None:
        """Log MTProto setup initiation."""
        await self.log_event(
            user_id=user_id,
            action="setup",
            request=request,
            metadata={"phone": phone},
        )

    async def log_verification_event(
        self,
        user_id: int,
        success: bool,
        request: Request | None = None,
        error: str | None = None,
    ) -> None:
        """Log MTProto verification attempt."""
        metadata: dict[str, Any] = {"success": success}
        if error:
            metadata["error"] = error

        await self.log_event(
            user_id=user_id,
            action="verified" if success else "verification_failed",
            request=request,
            metadata=metadata,
        )

    async def log_disconnect_event(
        self,
        user_id: int,
        request: Request | None = None,
    ) -> None:
        """Log MTProto client disconnect."""
        await self.log_event(
            user_id=user_id,
            action="disconnected",
            request=request,
        )

    async def log_removal_event(
        self,
        user_id: int,
        request: Request | None = None,
    ) -> None:
        """Log MTProto configuration removal."""
        await self.log_event(
            user_id=user_id,
            action="removed",
            request=request,
        )

    async def get_user_audit_history(
        self,
        user_id: int,
        channel_id: int | None = None,
        limit: int = 50,
    ) -> list[MTProtoAuditLogDTO]:
        """
        Get audit history for a user.

        Args:
            user_id: ID of the user
            channel_id: Optional filter by channel ID (None = all)
            limit: Maximum number of records to return

        Returns:
            List of audit log entries, most recent first
        """
        if channel_id is not None:
            actions = await self.audit_repo.get_channel_actions(channel_id, limit=limit)
        else:
            actions = await self.audit_repo.get_user_actions(user_id, limit=limit)

        return [MTProtoAuditLogDTO.from_dict(action) for action in actions]
