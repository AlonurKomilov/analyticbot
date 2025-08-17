import pytest
from unittest.mock import AsyncMock, MagicMock

from bot.database.repositories.plan_repository import PlanRepository
from bot.database.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_get_plan_by_name():
    """
    Tests retrieving a plan by its name.
    """
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = {
        "id": 1,
        "name": "free",
        "plan_name": "free",
        "max_channels": 1,
        "max_posts_per_month": 30,
    }

    mock_pool = MagicMock()
    mock_pool.acquire.return_value = AsyncMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

    repo = PlanRepository(pool=mock_pool)
    plan = await repo.get_plan_by_name("free")

    assert plan["name"] == "free"
    mock_conn.fetchrow.assert_called_once_with(
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
        "free",
    )


@pytest.mark.asyncio
async def test_create_user():
    """
    Tests creating a user.
    """
    mock_pool = AsyncMock()
    repo = UserRepository(pool=mock_pool)
    await repo.create_user(123, "testuser")

    mock_pool.execute.assert_called_once_with(
        """
            INSERT INTO users (id, username)
            VALUES ($1, $2)
            ON CONFLICT (id) DO NOTHING
        """,
        123,
        "testuser",
    )


@pytest.mark.asyncio
async def test_user_exists():
    """
    Tests checking if a user exists.
    """
    mock_pool = AsyncMock()
    mock_pool.fetchval.return_value = True

    repo = UserRepository(pool=mock_pool)
    exists = await repo.user_exists(123)

    assert exists is True
    mock_pool.fetchval.assert_called_once_with(
        "SELECT EXISTS(SELECT 1 FROM users WHERE id = $1)", 123
    )


@pytest.mark.asyncio
async def test_get_user_plan_name():
    """
    Tests getting a user's plan name.
    """
    mock_pool = AsyncMock()
    mock_pool.fetchval.return_value = "pro"

    repo = UserRepository(pool=mock_pool)
    plan_name = await repo.get_user_plan_name(123)

    assert plan_name == "pro"
    mock_pool.fetchval.assert_called_once_with(
        """
            SELECT p.name
            FROM users u
            JOIN plans p ON u.plan_id = p.id
            WHERE u.id = $1
        """,
        123,
    )
