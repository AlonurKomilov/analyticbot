"""
Feature Gate Service

Controls access to marketplace services based on user subscriptions.
Used throughout the bot and MTProto workers to check if user has access to features.
"""

import logging
from typing import Any

from infra.db.repositories.marketplace_service_repository import (
    MarketplaceServiceRepository,
)

logger = logging.getLogger(__name__)


class FeatureGateService:
    """Service for checking feature access based on marketplace subscriptions"""

    def __init__(self, marketplace_repo: MarketplaceServiceRepository):
        self.marketplace_repo = marketplace_repo

    async def check_access(
        self, user_id: int, service_key: str, raise_on_deny: bool = False
    ) -> bool:
        """
        Check if user has access to a service.
        
        Args:
            user_id: User ID
            service_key: Service key to check
            raise_on_deny: If True, raises ValueError instead of returning False
            
        Returns:
            True if user has active subscription, False otherwise
            
        Raises:
            ValueError: If raise_on_deny=True and access denied
        """
        subscription = await self.marketplace_repo.check_user_has_service(
            user_id, service_key
        )

        has_access = subscription is not None

        if not has_access and raise_on_deny:
            raise ValueError(
                f"Access denied: User does not have active subscription to {service_key}"
            )

        return has_access

    async def get_user_features(self, user_id: int) -> list[str]:
        """
        Get list of all service keys user has access to.
        Useful for bulk feature checks.
        
        Returns:
            List of service_key strings
        """
        return await self.marketplace_repo.get_user_active_services(user_id)

    async def check_quota(
        self,
        user_id: int,
        service_key: str,
        check_type: str = "daily",
    ) -> dict:
        """
        Check if user is within usage quota for a service.
        
        Args:
            user_id: User ID
            service_key: Service key
            check_type: 'daily' or 'monthly'
            
        Returns:
            Dict with:
                - has_access: bool (has subscription)
                - within_quota: bool (not exceeded)
                - used: int (current usage)
                - limit: int | None (quota limit, None = unlimited)
                - remaining: int | None (remaining quota, None = unlimited)
        """
        # Check subscription
        subscription = await self.marketplace_repo.check_user_has_service(
            user_id, service_key
        )

        if not subscription:
            return {
                "has_access": False,
                "within_quota": False,
                "used": 0,
                "limit": None,
                "remaining": None,
                "message": "No active subscription",
            }

        # Get service details
        service = await self.marketplace_repo.get_service_by_id(
            subscription["service_id"]
        )

        # Determine quota and usage based on check type
        if check_type == "daily":
            limit = service.get("usage_quota_daily")
            used = subscription.get("usage_count_daily", 0)
        elif check_type == "monthly":
            limit = service.get("usage_quota_monthly")
            used = subscription.get("usage_count_monthly", 0)
        else:
            raise ValueError(f"Invalid check_type: {check_type}")

        # Check quota
        if limit is None:
            # Unlimited
            return {
                "has_access": True,
                "within_quota": True,
                "used": used,
                "limit": None,
                "remaining": None,
                "message": "Unlimited usage",
            }
        else:
            within_quota = used < limit
            return {
                "has_access": True,
                "within_quota": within_quota,
                "used": used,
                "limit": limit,
                "remaining": limit - used if within_quota else 0,
                "message": f"Used {used}/{limit}" if within_quota else "Quota exceeded",
            }

    async def require_service(
        self,
        user_id: int,
        service_key: str,
        check_quota: bool = True,
        quota_type: str = "daily",
    ) -> dict:
        """
        Combined check: requires both subscription and quota (if applicable).
        Use this as a single gate before executing service actions.
        
        Args:
            user_id: User ID
            service_key: Service key required
            check_quota: Also check usage quota
            quota_type: 'daily' or 'monthly'
            
        Returns:
            Dict with:
                - allowed: bool (access granted)
                - subscription: dict | None
                - quota_info: dict | None (if check_quota=True)
                - deny_reason: str | None (if denied)
                
        Raises:
            ValueError: If access denied
        """
        # Check subscription
        subscription = await self.marketplace_repo.check_user_has_service(
            user_id, service_key
        )

        if not subscription:
            raise ValueError(
                f"Service subscription required: {service_key}. "
                "Please purchase this service from the marketplace."
            )

        result = {
            "allowed": True,
            "subscription": subscription,
            "quota_info": None,
            "deny_reason": None,
        }

        # Check quota if requested
        if check_quota:
            quota_info = await self.check_quota(
                user_id=user_id,
                service_key=service_key,
                check_type=quota_type,
            )

            result["quota_info"] = quota_info

            if not quota_info["within_quota"]:
                result["allowed"] = False
                result["deny_reason"] = f"Usage quota exceeded ({quota_type})"
                raise ValueError(
                    f"Usage quota exceeded. "
                    f"Used {quota_info['used']}/{quota_info['limit']} "
                    f"({quota_type})."
                )

        return result

    # ============================================
    # CONVENIENCE METHODS FOR SPECIFIC SERVICES
    # ============================================

    async def can_use_anti_spam(self, user_id: int) -> bool:
        """Check if user can use anti-spam service"""
        return await self.check_access(user_id, "bot_anti_spam")

    async def can_auto_delete_joins(self, user_id: int) -> bool:
        """Check if user can use auto-delete joins service"""
        return await self.check_access(user_id, "bot_auto_delete_joins")

    async def can_use_banned_words(self, user_id: int) -> bool:
        """Check if user can use banned words service"""
        return await self.check_access(user_id, "bot_banned_words")

    async def can_use_welcome_messages(self, user_id: int) -> bool:
        """Check if user can use welcome messages service"""
        return await self.check_access(user_id, "bot_welcome_messages")

    async def can_track_invites(self, user_id: int) -> bool:
        """Check if user can use invite tracking service"""
        return await self.check_access(user_id, "bot_invite_tracking")

    async def can_use_warning_system(self, user_id: int) -> bool:
        """Check if user can use warning system service"""
        return await self.check_access(user_id, "bot_warning_system")

    async def can_access_mtproto_history(self, user_id: int) -> bool:
        """Check if user can access MTProto history"""
        return await self.check_access(user_id, "mtproto_history_access")

    async def can_use_bulk_export(self, user_id: int) -> bool:
        """Check if user can use bulk export"""
        return await self.check_access(user_id, "mtproto_bulk_export")

    async def can_use_auto_collect(self, user_id: int) -> bool:
        """Check if user can use auto-collection"""
        return await self.check_access(user_id, "mtproto_auto_collect")
