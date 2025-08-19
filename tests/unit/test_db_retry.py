from unittest.mock import AsyncMock, patch

import pytest

from bot.database.db import create_pool


@pytest.mark.asyncio
@patch("bot.database.db.asyncpg.create_pool", new_callable=AsyncMock)
async def test_create_pool_success(mock_create_pool):
    """
    Tests that create_pool returns a pool on the first successful connection.
    """
    mock_create_pool.return_value = "fake_pool"
    pool = await create_pool(max_retries=3, backoff_factor=0.01)
    assert pool == "fake_pool"
    mock_create_pool.assert_called_once()


@pytest.mark.asyncio
@patch("bot.database.db.asyncpg.create_pool", new_callable=AsyncMock)
async def test_create_pool_failure(mock_create_pool):
    """
    Tests that create_pool raises an exception after all retries fail.
    """
    mock_create_pool.side_effect = OSError("Connection failed")

    with pytest.raises(OSError, match="Connection failed"):
        await create_pool(max_retries=3, backoff_factor=0.01)

    assert mock_create_pool.call_count == 3


@pytest.mark.asyncio
@patch("bot.database.db.asyncpg.create_pool", new_callable=AsyncMock)
async def test_create_pool_retry_once(mock_create_pool):
    """
    Tests that create_pool retries once and then succeeds.
    """
    mock_create_pool.side_effect = [
        OSError("Connection failed"),
        "fake_pool",
    ]
    pool = await create_pool(max_retries=3, backoff_factor=0.01)
    assert pool == "fake_pool"
    assert mock_create_pool.call_count == 2


@pytest.mark.asyncio
@patch("bot.database.db.asyncio.sleep", new_callable=AsyncMock)
@patch("bot.database.db.asyncpg.create_pool", new_callable=AsyncMock)
async def test_create_pool_backoff_timing(mock_create_pool, mock_sleep):
    """
    Tests that the backoff timing is calculated correctly.
    """
    mock_create_pool.side_effect = OSError("Connection failed")
    backoff_factor = 0.05

    with pytest.raises(OSError):
        await create_pool(max_retries=4, backoff_factor=backoff_factor)

    assert mock_sleep.call_count == 4
    mock_sleep.assert_any_call(backoff_factor * (2**0))  # 0.05
    mock_sleep.assert_any_call(backoff_factor * (2**1))  # 0.10
    mock_sleep.assert_any_call(backoff_factor * (2**2))  # 0.20
    mock_sleep.assert_any_call(backoff_factor * (2**3))  # 0.40
