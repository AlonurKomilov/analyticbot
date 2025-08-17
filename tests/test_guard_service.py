import fakeredis.aioredis
import pytest

from bot.services.guard_service import GuardService


@pytest.fixture
async def redis_conn():
    # Haqiqiy Redis o'rniga fake (soxta) Redis ishlatamiz
    return fakeredis.aioredis.FakeRedis()


@pytest.fixture
async def guard_service(redis_conn):
    return GuardService(redis_conn)


@pytest.mark.asyncio
async def test_add_and_list_words(guard_service: GuardService):
    channel_id = 12345
    await guard_service.add_word(channel_id, "test1")
    await guard_service.add_word(channel_id, "TEST2")  # kichik harflarga o'tishi kerak

    words = await guard_service.list_words(channel_id)
    assert "test1" in words
    assert "test2" in words
    assert len(words) == 2


@pytest.mark.asyncio
async def test_remove_word(guard_service: GuardService):
    channel_id = 12345
    await guard_service.add_word(channel_id, "word_to_remove")

    # Olib tashlash
    await guard_service.remove_word(channel_id, "word_to_remove")
    words = await guard_service.list_words(channel_id)
    assert "word_to_remove" not in words


@pytest.mark.asyncio
async def test_is_blocked(guard_service: GuardService):
    channel_id = 54321
    await guard_service.add_word(channel_id, "spam")
    await guard_service.add_word(channel_id, "reklama")

    assert not await guard_service.is_blocked(channel_id, "Bu oddiy xabar")
    assert await guard_service.is_blocked(channel_id, "Bu yerda SPAM bor")
    assert await guard_service.is_blocked(channel_id, "Eng yaxshi reklama bizda")
    assert not await guard_service.is_blocked(channel_id, "Boshqa kanaldagi xabar")


@pytest.mark.asyncio
async def test_is_blocked_no_words(guard_service: GuardService):
    """Test is_blocked when no words are blacklisted."""
    channel_id = 1111
    assert not await guard_service.is_blocked(channel_id, "Any message")


@pytest.mark.asyncio
async def test_check_bot_is_admin(guard_service: GuardService):
    """Test the placeholder admin check."""
    result = await guard_service.check_bot_is_admin("test_channel", 123)
    assert result["username"] == "test_channel"
