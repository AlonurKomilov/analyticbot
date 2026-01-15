"""
History Access Service - Full channel history access via MTProto

Marketplace service: mtproto_history_access
Price: 100 credits/month

Features:
- Full history access (no 100-message limit)
- Message search
- Date range filters
- Export to JSON/CSV
- API access
- 1000 messages/day quota
- 20000 messages/month quota
"""

import logging
from typing import Any

from core.services.mtproto.features.base_mtproto_service import BaseMTProtoService

logger = logging.getLogger(__name__)


class HistoryAccessService(BaseMTProtoService):
    """
    Full history access service for MTProto users.

    Removes the 100-message limit and allows users to fetch
    complete channel history for analysis.
    """

    def __init__(
        self,
        user_id: int,
        feature_gate_service: Any,
        marketplace_repo: Any,
        mtproto_client: Any | None = None,
    ):
        """
        Initialize history access service.

        Args:
            user_id: User's ID
            feature_gate_service: Service for access control
            marketplace_repo: Repository for usage logging
            mtproto_client: MTProto client for fetching messages
        """
        super().__init__(user_id, feature_gate_service, marketplace_repo)
        self.mtproto_client = mtproto_client

    @property
    def service_key(self) -> str:
        return "mtproto_history_access"

    async def execute(self, **kwargs) -> dict[str, Any]:
        """
        Fetch full channel history without limits.

        Args:
            channel_id: Channel/chat ID to fetch from
            limit: Maximum number of messages (default: 1000, max: 5000)
            offset_id: Start from this message ID (for pagination)
            min_date: Minimum message date (optional)
            max_date: Maximum message date (optional)
            search: Search query (optional)

        Returns:
            dict with messages and metadata
        """
        channel_id = kwargs.get("channel_id")
        limit = min(kwargs.get("limit", 1000), 5000)  # Cap at 5000 per request
        offset_id = kwargs.get("offset_id", 0)
        min_date = kwargs.get("min_date")
        max_date = kwargs.get("max_date")
        search_query = kwargs.get("search")

        if not channel_id:
            return {
                "error": "Missing required parameter: channel_id",
                "messages": [],
            }

        if not self.mtproto_client:
            return {
                "error": "MTProto client not available",
                "messages": [],
            }

        try:
            messages = []
            fetched_count = 0

            # Fetch messages with pagination
            logger.info(
                f"[HistoryAccess] User {self.user_id} - Fetching history from channel {channel_id}: "
                f"limit={limit}, offset_id={offset_id}"
            )

            # Use iter_history from the MTProto client
            async for message in self.mtproto_client.iter_history(
                peer=channel_id,
                offset_id=offset_id,
                limit=limit,
            ):
                # Apply date filters if specified
                if min_date and message.date < min_date:
                    continue
                if max_date and message.date > max_date:
                    continue

                # Apply search filter if specified
                if search_query and message.text:
                    if search_query.lower() not in message.text.lower():
                        continue

                # Convert message to dict (simplified)
                message_data = {
                    "id": message.id,
                    "date": message.date.isoformat() if message.date else None,
                    "text": message.text or "",
                    "from_id": (
                        getattr(message.from_id, "user_id", None) if message.from_id else None
                    ),
                    "views": message.views,
                    "forwards": message.forwards,
                    "replies": (getattr(message.replies, "replies", 0) if message.replies else 0),
                    "edit_date": (message.edit_date.isoformat() if message.edit_date else None),
                    "has_media": bool(message.media),
                }

                messages.append(message_data)
                fetched_count += 1

                if fetched_count >= limit:
                    break

            logger.info(
                f"[HistoryAccess] User {self.user_id} - Fetched {len(messages)} messages "
                f"from channel {channel_id}"
            )

            return {
                "messages": messages,
                "fetched_count": len(messages),
                "channel_id": channel_id,
                "has_more": len(messages) == limit,
                "last_message_id": messages[-1]["id"] if messages else None,
            }

        except Exception as e:
            logger.error(
                f"[HistoryAccess] Failed to fetch history for user {self.user_id}: {e}",
                exc_info=True,
            )
            return {
                "error": str(e),
                "messages": [],
                "fetched_count": 0,
            }

    async def is_available(self) -> bool:
        """Check if history access service is available for this user."""
        has_access, _ = await self.feature_gate.check_access(
            user_id=self.user_id,
            service_key=self.service_key,
        )
        return has_access

    async def get_usage_stats(self, days: int = 30) -> dict:
        """
        Get usage statistics for history access service.

        Args:
            days: Number of days to look back

        Returns:
            dict with usage statistics
        """
        try:
            # Get usage from the past N days
            stats = await self.marketplace_repo.get_usage_stats(
                user_id=self.user_id,
                service_key=self.service_key,
                days=days,
            )

            return {
                "service_key": self.service_key,
                "days": days,
                "total_requests": stats.get("total_count", 0),
                "successful_requests": stats.get("success_count", 0),
                "failed_requests": stats.get("error_count", 0),
                "total_messages_fetched": stats.get("total_messages", 0),
                "avg_response_time_ms": stats.get("avg_response_time", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get usage stats: {e}")
            return {}
