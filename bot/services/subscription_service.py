# bot/services/subscription_service.py

from fastapi import HTTPException

# Lazily resolve other repos via container to keep current DI untouched
from bot.container import container
from bot.database.models import SubscriptionStatus
from bot.database.repositories import (
    ChannelRepository,
    PlanRepository,
    SchedulerRepository,
    UserRepository,
)


class SubscriptionService:
    """
    Subscription limits & usage checks.
    Constructor MUST match container wiring:
        subscription_service = Singleton(SubscriptionService, repository=channel_repository)
    """

    def __init__(self, repository: ChannelRepository):
        # Keep the param name 'repository' to match Container; expose as channel_repo
        self.channel_repo = repository

    async def _get_plan_row(self, user_id: int) -> dict | None:
        """Return the plan row for the user, or None if not set."""
        user_repo = container.resolve(UserRepository)
        plan_repo = container.resolve(PlanRepository)

        plan_name = await user_repo.get_user_plan_name(user_id)
        if not plan_name:
            return None
        # plan table has columns like: name/plan_name, max_channels, max_posts_per_month
        return await plan_repo.get_plan_by_name(plan_name)

    async def check_channel_limit(self, user_id: int) -> None:
        """
        Ensure the user has not exceeded max channels allowed by their plan.
        Raise HTTPException(403) on limit breach.
        """
        plan_row = await self._get_plan_row(user_id)
        if not plan_row:
            # No plan associated -> no limit enforced (or treat as Free with defaults).
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

        scheduler_repo = container.resolve(SchedulerRepository)
        current_posts = await scheduler_repo.count_user_posts_this_month(user_id)
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

        scheduler_repo = container.resolve(SchedulerRepository)
        current_posts = await scheduler_repo.count_user_posts_this_month(user_id)
        current_channels = await self.channel_repo.count_user_channels(user_id)

        # plan name can be 'name' or 'plan_name' depending on the SELECT
        plan_name = plan_row.get("plan_name") or plan_row.get("name") or "Unknown"

        return SubscriptionStatus(
            plan_name=plan_name,
            max_channels=plan_row.get("max_channels", 0),
            current_channels=current_channels,
            max_posts_per_month=plan_row.get("max_posts_per_month", 0),
            current_posts_this_month=current_posts,
        )
