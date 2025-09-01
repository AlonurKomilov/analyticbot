"""
Unit tests for GuardService - Service Layer Testing with Mocks
Testing business logic while mocking external dependencies (Redis)
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from apps.bot.services.guard_service import GuardService


class TestGuardService:
    """Test GuardService - should achieve 100% coverage with mocked Redis"""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection for testing"""
        mock = AsyncMock()
        return mock

    @pytest.fixture
    def guard_service_with_redis(self, mock_redis):
        """GuardService instance with mocked Redis"""
        return GuardService(redis_conn=mock_redis)

    @pytest.fixture
    def guard_service_no_redis(self):
        """GuardService instance without Redis (None)"""
        return GuardService(redis_conn=None)

    def test_guard_service_init_with_redis(self, mock_redis):
        """Test GuardService initialization with Redis connection"""
        service = GuardService(redis_conn=mock_redis)
        assert service.redis == mock_redis

    def test_guard_service_init_without_redis(self):
        """Test GuardService initialization without Redis connection"""
        service = GuardService(redis_conn=None)
        assert service.redis is None

    def test_key_generation(self, guard_service_with_redis):
        """Test Redis key generation for channel"""
        channel_id = 12345
        expected_key = "blacklist:12345"
        
        key = guard_service_with_redis._key(channel_id)
        
        assert key == expected_key

    @pytest.mark.asyncio
    async def test_add_word_with_redis(self, guard_service_with_redis, mock_redis):
        """Test adding word to blacklist with Redis"""
        channel_id = 12345
        word = "BadWord"
        
        await guard_service_with_redis.add_word(channel_id, word)
        
        mock_redis.sadd.assert_called_once_with("blacklist:12345", "badword")

    @pytest.mark.asyncio
    async def test_add_word_without_redis(self, guard_service_no_redis):
        """Test adding word to blacklist without Redis (should do nothing)"""
        channel_id = 12345
        word = "BadWord"
        
        # Should not raise any exception
        result = await guard_service_no_redis.add_word(channel_id, word)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_remove_word_with_redis(self, guard_service_with_redis, mock_redis):
        """Test removing word from blacklist with Redis"""
        channel_id = 12345
        word = "BadWord"
        
        await guard_service_with_redis.remove_word(channel_id, word)
        
        mock_redis.srem.assert_called_once_with("blacklist:12345", "badword")

    @pytest.mark.asyncio
    async def test_remove_word_without_redis(self, guard_service_no_redis):
        """Test removing word from blacklist without Redis (should do nothing)"""
        channel_id = 12345
        word = "BadWord"
        
        # Should not raise any exception
        result = await guard_service_no_redis.remove_word(channel_id, word)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_list_words_with_redis(self, guard_service_with_redis, mock_redis):
        """Test listing blacklisted words with Redis"""
        channel_id = 12345
        mock_redis.smembers.return_value = [b"badword1", b"badword2", b"spam"]
        
        words = await guard_service_with_redis.list_words(channel_id)
        
        mock_redis.smembers.assert_called_once_with("blacklist:12345")
        assert words == {"badword1", "badword2", "spam"}

    @pytest.mark.asyncio
    async def test_list_words_without_redis(self, guard_service_no_redis):
        """Test listing blacklisted words without Redis (should return empty set)"""
        channel_id = 12345
        
        words = await guard_service_no_redis.list_words(channel_id)
        
        assert words == set()

    @pytest.mark.asyncio
    async def test_list_words_empty_result(self, guard_service_with_redis, mock_redis):
        """Test listing words when Redis returns empty set"""
        channel_id = 12345
        mock_redis.smembers.return_value = []
        
        words = await guard_service_with_redis.list_words(channel_id)
        
        assert words == set()

    @pytest.mark.asyncio
    async def test_is_blocked_no_blocked_words(self, guard_service_with_redis, mock_redis):
        """Test is_blocked when no words are blocked"""
        channel_id = 12345
        text = "This is a clean message"
        mock_redis.smembers.return_value = []
        
        result = await guard_service_with_redis.is_blocked(channel_id, text)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_is_blocked_with_blocked_word(self, guard_service_with_redis, mock_redis):
        """Test is_blocked when text contains blocked word"""
        channel_id = 12345
        text = "This contains spam content"
        mock_redis.smembers.return_value = [b"spam", b"badword"]
        
        result = await guard_service_with_redis.is_blocked(channel_id, text)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_is_blocked_case_insensitive(self, guard_service_with_redis, mock_redis):
        """Test is_blocked is case insensitive"""
        channel_id = 12345
        text = "This contains SPAM content"
        mock_redis.smembers.return_value = [b"spam"]
        
        result = await guard_service_with_redis.is_blocked(channel_id, text)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_is_blocked_word_boundary_detection(self, guard_service_with_redis, mock_redis):
        """Test is_blocked correctly detects word boundaries"""
        channel_id = 12345
        text = "This message is legitimate"  # "git" is in "legitimate"
        mock_redis.smembers.return_value = [b"git"]
        
        result = await guard_service_with_redis.is_blocked(channel_id, text)
        
        # Should be False because "git" should only match whole words
        assert result is False

    @pytest.mark.asyncio
    async def test_is_blocked_alphanumeric_extraction(self, guard_service_with_redis, mock_redis):
        """Test is_blocked correctly extracts alphanumeric tokens"""
        channel_id = 12345
        text = "Check this: spam@email.com and other-stuff!"
        mock_redis.smembers.return_value = [b"spam", b"other"]
        
        result = await guard_service_with_redis.is_blocked(channel_id, text)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_is_blocked_no_match(self, guard_service_with_redis, mock_redis):
        """Test is_blocked when no blocked words match"""
        channel_id = 12345
        text = "This is a completely clean message"
        mock_redis.smembers.return_value = [b"spam", b"badword", b"inappropriate"]
        
        result = await guard_service_with_redis.is_blocked(channel_id, text)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_is_blocked_without_redis(self, guard_service_no_redis):
        """Test is_blocked without Redis connection"""
        channel_id = 12345
        text = "Any message"
        
        result = await guard_service_no_redis.is_blocked(channel_id, text)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_check_bot_is_admin(self, guard_service_with_redis):
        """Test check_bot_is_admin placeholder method"""
        channel_username = "test_channel"
        user_id = 123456
        
        result = await guard_service_with_redis.check_bot_is_admin(channel_username, user_id)
        
        expected = {
            "id": 0,
            "channel_id": 0,
            "title": "",
            "username": "test_channel"
        }
        assert result == expected

    @pytest.mark.asyncio
    async def test_is_blocked_with_apostrophes(self, guard_service_with_redis, mock_redis):
        """Test is_blocked handles words with apostrophes correctly"""
        channel_id = 12345
        text = "Don't use that word here"
        mock_redis.smembers.return_value = [b"don't"]
        
        result = await guard_service_with_redis.is_blocked(channel_id, text)
        
        assert result is True

    @pytest.mark.asyncio
    async def test_word_normalization_in_add_word(self, guard_service_with_redis, mock_redis):
        """Test that words are normalized to lowercase when added"""
        channel_id = 12345
        word = "MiXeDCaSe"
        
        await guard_service_with_redis.add_word(channel_id, word)
        
        mock_redis.sadd.assert_called_once_with("blacklist:12345", "mixedcase")

    @pytest.mark.asyncio
    async def test_word_normalization_in_remove_word(self, guard_service_with_redis, mock_redis):
        """Test that words are normalized to lowercase when removed"""
        channel_id = 12345
        word = "MiXeDCaSe"
        
        await guard_service_with_redis.remove_word(channel_id, word)
        
        mock_redis.srem.assert_called_once_with("blacklist:12345", "mixedcase")
