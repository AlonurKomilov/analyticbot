from typing import Any

import asyncpg


class PlanRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_plan_by_name(self, plan_name: str) -> dict[str, Any] | None:
        """Retrieves the limits for a specific plan by its name."""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(
                """
                SELECT
                    id,
                    name,
                    /* backward compatibility for callers expecting 'plan_name' */
                    name AS plan_name,
                    max_channels,
                    max_posts_per_month
                FROM plans
                WHERE name = $1
                LIMIT 1
                """,
                plan_name,
            )
