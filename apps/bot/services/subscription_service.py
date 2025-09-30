from fastapi import HTTPException

from apps.bot.domain.models import SubscriptionStatus
from typing import Any

# TODO: Define proper repository protocols for all methods used
# For now using Any to maintain compatibility while removing direct infra imports


class SubscriptionService:
    """
    Subscription limits & usage checks.
    Constructor MUST match container wiring:
        subscription_service = Singleton(SubscriptionService,
                                       channel_repo=channel_repository,
                                       user_repo=user_repository,
                                       plan_repo=plan_repository,
                                       schedule_repo=schedule_repository)
    """

    def __init__(
        self,
        channel_repository: Any,
        user_repository: Any,
        plan_repository: Any,
        scheduler_repository: Any,
    ):
        self.channel_repo = channel_repository
        self.user_repo = user_repository
        self.plan_repo = plan_repository
        self.schedule_repo = scheduler_repository

    async def _get_plan_row(self, user_id: int) -> dict | None:
        """Return the plan row for the user, or None if not set."""
        plan_name = await self.user_repo.get_user_plan_name(user_id)
        if not plan_name:
            return None
        return await self.plan_repo.get_plan_by_name(plan_name)

    async def check_channel_limit(self, user_id: int) -> None:
        """
        Ensure the user has not exceeded max channels allowed by their plan.
        Raise HTTPException(403) on limit breach.
        """
        plan_row = await self._get_plan_row(user_id)
        if not plan_row:
            return
        max_channels = plan_row.get("max_channels")
        if max_channels is None:
            return
        current_channels = await self.channel_repo.count_user_channels(user_id)
        if current_channels >= max_channels:
            raise HTTPException(status_code=403, detail="Channel limit reached")

    async def check_post_limit(self, user_id: int) -> None:
        """
        Ensure the user has not exceeded max monthly posts allowed by their plan.
        Raise HTTPException(403) on limit breach.
        """
        plan_row = await self._get_plan_row(user_id)
        if not plan_row:
            return
        max_posts = plan_row.get("max_posts_per_month")
        if max_posts is None:
            return
        current_posts = await self.schedule_repo.count_user_posts_this_month(user_id)
        if current_posts >= max_posts:
            raise HTTPException(status_code=403, detail="Monthly post limit reached")

    async def get_usage_status(self, user_id: int) -> SubscriptionStatus | None:
        """
        Optional helper used by dashboards: summarize usage & limits.
        Not required by API right now but kept for completeness.
        """
        plan_row = await self._get_plan_row(user_id)
        if not plan_row:
            return None
        current_posts = await self.schedule_repo.count_user_posts_this_month(user_id)
        current_channels = await self.channel_repo.count_user_channels(user_id)
        plan_name = plan_row.get("plan_name") or plan_row.get("name") or "Unknown"
        return SubscriptionStatus(
            plan_name=plan_name,
            max_channels=plan_row.get("max_channels", 0),
            current_channels=current_channels,
            max_posts_per_month=plan_row.get("max_posts_per_month", 0),
            current_posts_this_month=current_posts,
        )
