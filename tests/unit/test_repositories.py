from unittest.mock import AsyncMock, MagicMock

import pytest

from infra.db.repositories.plan_repository import AsyncpgPlanRepository
from infra.db.repositories.user_repository import AsyncpgUserRepository


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
    repo = AsyncpgPlanRepository(pool=mock_pool)
    plan = await repo.get_plan_by_name("free")
    assert plan["name"] == "free"
    mock_conn.fetchrow.assert_called_once_with(
        "\n                SELECT\n                    id,\n                    name,\n                    /* backward compatibility for callers expecting 'plan_name' */\n                    name AS plan_name,\n                    max_channels,\n                    max_posts_per_month\n                FROM plans\n                WHERE name = $1\n                LIMIT 1\n                ",
        "free",
    )


@pytest.mark.asyncio
async def test_create_user():
    """
    Tests creating a user.
    """
    mock_pool = AsyncMock()
    repo = AsyncpgUserRepository(pool=mock_pool)
    await repo.create_user(123, "testuser")
    mock_pool.execute.assert_called_once_with(
        "\n            INSERT INTO users (id, username)\n            VALUES ($1, $2)\n            ON CONFLICT (id) DO NOTHING\n        ",
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
    repo = AsyncpgUserRepository(pool=mock_pool)
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
    repo = AsyncpgUserRepository(pool=mock_pool)
    plan_name = await repo.get_user_plan_name(123)
    assert plan_name == "pro"
    mock_pool.fetchval.assert_called_once_with(
        "\n            SELECT p.name\n            FROM users u\n            JOIN plans p ON u.plan_id = p.id\n            WHERE u.id = $1\n        ",
        123,
    )
