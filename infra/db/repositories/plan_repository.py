"""
Plan Repository Implementation
Concrete implementation for subscription plan data operations
"""

from typing import Any, Optional
import asyncpg


class AsyncpgPlanRepository:
    """Plan repository implementation using asyncpg"""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_plan_by_name(self, plan_name: str) -> Optional[dict[str, Any]]:
        """Retrieves the limits for a specific plan by its name."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
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
            return dict(row) if row else None
