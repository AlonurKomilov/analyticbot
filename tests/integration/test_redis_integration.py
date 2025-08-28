"""
Module TQA.2.3.3: Redis Caching Integration Testing

This module provides comprehensive testing for Redis caching integration,
including cache operations, session management, rate limiting, and cache invalidation strategies.

Test Structure:
- TestRedisCacheOperations: Basic Redis cache operation testing
- TestRedisSessionManagement: User session storage and retrieval
- TestRedisRateLimiting: Rate limiting implementation validation
- TestRedisCacheInvalidation: Cache invalidation strategy testing
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List, Optional, Union
import json
import time
from datetime import datetime, timedelta
import pickle
import hashlib

# Test framework imports
import redis.asyncio as redis
from fakeredis import FakeRedis
from fakeredis.aioredis import FakeRedis as FakeAsyncRedis


@pytest.fixture
async def mock_redis_client():
    """Mock Redis client using fakeredis for testing"""
    client = FakeAsyncRedis(decode_responses=True)
    yield client
    await client.flushall()
    await client.close()


@pytest.fixture
async def mock_redis_binary_client():
    """Mock Redis client for binary data (pickled objects)"""
    client = FakeAsyncRedis(decode_responses=False)
    yield client
    await client.flushall()
    await client.close()


@pytest.fixture
def sample_cache_data():
    """Sample data for cache testing"""
    return {
        "user_data": {
            "user_id": 123456789,
            "username": "testuser",
            "preferences": {
                "language": "en",
                "timezone": "UTC"
            },
            "last_activity": "2023-01-01T12:00:00Z"
        },
        "analytics_data": {
            "channel_id": 987654321,
            "metrics": {
                "views": 1000,
                "subscribers": 50,
                "engagement_rate": 0.85
            },
            "updated_at": "2023-01-01T12:00:00Z"
        }
    }


@pytest.fixture
def rate_limit_config():
    """Rate limiting configuration for testing"""
    return {
        "api_calls": {
            "window_seconds": 60,
            "max_requests": 100
        },
        "message_sending": {
            "window_seconds": 3600,
            "max_requests": 50
        },
        "payment_attempts": {
            "window_seconds": 86400,
            "max_requests": 5
        }
    }


class TestRedisCacheOperations:
    """Test basic Redis cache operations"""
    
    @pytest.mark.asyncio
    async def test_set_and_get_string_data(self, mock_redis_client):
        """Test basic string data caching"""
        key = "test:string:key"
        value = "test_value_12345"
        
        # Set data in cache
        await mock_redis_client.set(key, value, ex=300)  # 5 minutes TTL
        
        # Retrieve data from cache
        cached_value = await mock_redis_client.get(key)
        
        # Validate retrieval
        assert cached_value == value
        
        # Check TTL
        ttl = await mock_redis_client.ttl(key)
        assert 290 <= ttl <= 300  # Should be close to 300 seconds
    
    @pytest.mark.asyncio
    async def test_set_and_get_json_data(self, mock_redis_client, sample_cache_data):
        """Test JSON data caching"""
        key = "test:json:user:123456789"
        json_data = json.dumps(sample_cache_data["user_data"])
        
        # Set JSON data
        await mock_redis_client.set(key, json_data, ex=600)
        
        # Retrieve and parse JSON data
        cached_json = await mock_redis_client.get(key)
        cached_data = json.loads(cached_json)
        
        # Validate data integrity
        assert cached_data["user_id"] == sample_cache_data["user_data"]["user_id"]
        assert cached_data["username"] == sample_cache_data["user_data"]["username"]
        assert cached_data["preferences"] == sample_cache_data["user_data"]["preferences"]
    
    @pytest.mark.asyncio
    async def test_hash_operations(self, mock_redis_client):
        """Test Redis hash operations for structured data"""
        hash_key = "test:hash:analytics:987654321"
        hash_data = {
            "views": "1000",
            "subscribers": "50",
            "engagement_rate": "0.85",
            "last_updated": "2023-01-01T12:00:00Z"
        }
        
        # Set hash fields
        await mock_redis_client.hset(hash_key, mapping=hash_data)
        
        # Get all hash data
        cached_hash = await mock_redis_client.hgetall(hash_key)
        
        # Validate hash data
        assert cached_hash["views"] == "1000"
        assert cached_hash["subscribers"] == "50"
        assert cached_hash["engagement_rate"] == "0.85"
        
        # Test individual field retrieval
        views = await mock_redis_client.hget(hash_key, "views")
        assert views == "1000"
        
        # Test field existence
        exists = await mock_redis_client.hexists(hash_key, "views")
        assert exists is True
        
        # Test field deletion
        await mock_redis_client.hdel(hash_key, "last_updated")
        updated_hash = await mock_redis_client.hgetall(hash_key)
        assert "last_updated" not in updated_hash
    
    @pytest.mark.asyncio
    async def test_list_operations(self, mock_redis_client):
        """Test Redis list operations"""
        list_key = "test:list:recent_activities"
        activities = [
            "User 123 logged in",
            "User 456 sent message",
            "User 789 made payment",
            "User 123 requested analytics"
        ]
        
        # Push activities to list
        for activity in activities:
            await mock_redis_client.lpush(list_key, activity)
        
        # Get list length
        list_length = await mock_redis_client.llen(list_key)
        assert list_length == len(activities)
        
        # Get recent activities (first 3)
        recent_activities = await mock_redis_client.lrange(list_key, 0, 2)
        assert len(recent_activities) == 3
        
        # Activities should be in reverse order due to lpush
        assert recent_activities[0] == activities[-1]  # Most recent first
    
    @pytest.mark.asyncio
    async def test_set_operations(self, mock_redis_client):
        """Test Redis set operations"""
        set_key = "test:set:active_users"
        users = ["user:123", "user:456", "user:789", "user:123"]  # Duplicate
        
        # Add users to set
        for user in users:
            await mock_redis_client.sadd(set_key, user)
        
        # Get set size (should deduplicate)
        set_size = await mock_redis_client.scard(set_key)
        assert set_size == 3  # Duplicates removed
        
        # Check membership
        is_member = await mock_redis_client.sismember(set_key, "user:123")
        assert is_member is True
        
        # Get all members
        members = await mock_redis_client.smembers(set_key)
        assert "user:123" in members
        assert "user:456" in members
        assert "user:789" in members


class TestRedisSessionManagement:
    """Test Redis-based session management"""
    
    @pytest.mark.asyncio
    async def test_user_session_creation(self, mock_redis_client):
        """Test user session creation and storage"""
        user_id = 123456789
        session_id = f"session:{user_id}:{int(time.time())}"
        session_data = {
            "user_id": str(user_id),
            "created_at": datetime.now().isoformat(),
            "state": "active",
            "context": {
                "current_action": "viewing_analytics",
                "channel_id": "987654321"
            }
        }
        
        # Store session data
        await mock_redis_client.hset(
            session_id,
            mapping={k: json.dumps(v) if isinstance(v, dict) else str(v) for k, v in session_data.items()}
        )
        
        # Set session expiration (24 hours)
        await mock_redis_client.expire(session_id, 86400)
        
        # Retrieve session data
        cached_session = await mock_redis_client.hgetall(session_id)
        
        # Validate session data
        assert cached_session["user_id"] == str(user_id)
        assert cached_session["state"] == "active"
        
        context_data = json.loads(cached_session["context"])
        assert context_data["current_action"] == "viewing_analytics"
        assert context_data["channel_id"] == "987654321"
    
    @pytest.mark.asyncio
    async def test_session_state_transitions(self, mock_redis_client):
        """Test session state management and transitions"""
        session_key = "session:123456789"
        states = ["idle", "processing", "waiting_input", "completed"]
        
        # Initial state
        await mock_redis_client.hset(session_key, "state", states[0])
        initial_state = await mock_redis_client.hget(session_key, "state")
        assert initial_state == "idle"
        
        # State transitions
        for i, next_state in enumerate(states[1:], 1):
            await mock_redis_client.hset(session_key, "state", next_state)
            current_state = await mock_redis_client.hget(session_key, "state")
            assert current_state == next_state
            
            # Update state timestamp
            await mock_redis_client.hset(
                session_key,
                f"state_changed_{i}",
                datetime.now().isoformat()
            )
    
    @pytest.mark.asyncio
    async def test_multiple_user_sessions(self, mock_redis_client):
        """Test multiple concurrent user sessions"""
        users = [111111111, 222222222, 333333333]
        
        # Create sessions for multiple users
        for user_id in users:
            session_key = f"session:{user_id}"
            session_data = {
                "user_id": str(user_id),
                "preferences": json.dumps({
                    "language": "en" if user_id % 2 == 0 else "ru",
                    "notifications": True
                }),
                "last_activity": datetime.now().isoformat()
            }
            
            await mock_redis_client.hset(session_key, mapping=session_data)
        
        # Validate session isolation
        for user_id in users:
            session_key = f"session:{user_id}"
            session = await mock_redis_client.hgetall(session_key)
            
            assert session["user_id"] == str(user_id)
            preferences = json.loads(session["preferences"])
            expected_language = "en" if user_id % 2 == 0 else "ru"
            assert preferences["language"] == expected_language
    
    @pytest.mark.asyncio
    async def test_session_cleanup(self, mock_redis_client):
        """Test session cleanup and expiration"""
        session_key = "session:expired:123"
        
        # Create session with short TTL
        await mock_redis_client.hset(session_key, "data", "test_data")
        await mock_redis_client.expire(session_key, 1)  # 1 second
        
        # Verify session exists
        exists_before = await mock_redis_client.exists(session_key)
        assert exists_before == 1
        
        # Wait for expiration
        await asyncio.sleep(1.5)
        
        # Verify session expired
        exists_after = await mock_redis_client.exists(session_key)
        assert exists_after == 0


class TestRedisRateLimiting:
    """Test Redis-based rate limiting implementation"""
    
    @pytest.mark.asyncio
    async def test_sliding_window_rate_limiting(self, mock_redis_client, rate_limit_config):
        """Test sliding window rate limiting"""
        user_id = 123456789
        limit_config = rate_limit_config["api_calls"]
        
        async def check_rate_limit(user_id: int, action: str, config: Dict[str, int]) -> bool:
            """Simple sliding window rate limiter"""
            key = f"rate_limit:{action}:{user_id}"
            current_time = int(time.time())
            window_start = current_time - config["window_seconds"]
            
            # Remove expired entries
            await mock_redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            current_count = await mock_redis_client.zcard(key)
            
            if current_count >= config["max_requests"]:
                return False
            
            # Add current request
            await mock_redis_client.zadd(key, {str(current_time): current_time})
            await mock_redis_client.expire(key, config["window_seconds"])
            
            return True
        
        # Test rate limiting
        allowed_requests = 0
        for i in range(limit_config["max_requests"] + 5):
            is_allowed = await check_rate_limit(user_id, "api_calls", limit_config)
            if is_allowed:
                allowed_requests += 1
        
        # Should allow exactly max_requests
        assert allowed_requests == limit_config["max_requests"]
    
    @pytest.mark.asyncio
    async def test_different_rate_limits_per_action(self, mock_redis_client, rate_limit_config):
        """Test different rate limits for different actions"""
        user_id = 123456789
        
        # Test API calls rate limit
        api_key = f"rate_limit:api_calls:{user_id}"
        await mock_redis_client.zadd(api_key, {str(time.time()): time.time()})
        api_count = await mock_redis_client.zcard(api_key)
        assert api_count == 1
        
        # Test message sending rate limit
        message_key = f"rate_limit:message_sending:{user_id}"
        await mock_redis_client.zadd(message_key, {str(time.time()): time.time()})
        message_count = await mock_redis_client.zcard(message_key)
        assert message_count == 1
        
        # Test payment attempts rate limit
        payment_key = f"rate_limit:payment_attempts:{user_id}"
        await mock_redis_client.zadd(payment_key, {str(time.time()): time.time()})
        payment_count = await mock_redis_client.zcard(payment_key)
        assert payment_count == 1
        
        # Validate keys are independent
        assert api_key != message_key != payment_key
    
    @pytest.mark.asyncio
    async def test_rate_limit_reset(self, mock_redis_client):
        """Test rate limit window reset"""
        user_id = 123456789
        rate_limit_key = f"rate_limit:test:{user_id}"
        
        # Add requests to rate limit
        current_time = time.time()
        for i in range(5):
            await mock_redis_client.zadd(
                rate_limit_key, 
                {f"req_{i}": current_time + i}
            )
        
        # Verify requests counted
        count_before = await mock_redis_client.zcard(rate_limit_key)
        assert count_before == 5
        
        # Remove old requests (simulate window slide)
        window_start = current_time + 10
        await mock_redis_client.zremrangebyscore(rate_limit_key, 0, window_start)
        
        # Verify old requests removed
        count_after = await mock_redis_client.zcard(rate_limit_key)
        assert count_after == 0


class TestRedisCacheInvalidation:
    """Test cache invalidation strategies"""
    
    @pytest.mark.asyncio
    async def test_tag_based_cache_invalidation(self, mock_redis_client):
        """Test tag-based cache invalidation"""
        # Create cache entries with tags
        cache_entries = [
            {"key": "analytics:channel:123", "data": {"views": 1000}, "tags": ["analytics", "channel:123"]},
            {"key": "analytics:channel:456", "data": {"views": 2000}, "tags": ["analytics", "channel:456"]},
            {"key": "user:profile:789", "data": {"name": "Test"}, "tags": ["user", "profile:789"]}
        ]
        
        # Store cache entries and tag mappings
        for entry in cache_entries:
            # Store actual data
            await mock_redis_client.set(
                entry["key"],
                json.dumps(entry["data"]),
                ex=3600
            )
            
            # Store tag mappings
            for tag in entry["tags"]:
                await mock_redis_client.sadd(f"cache_tag:{tag}", entry["key"])
        
        # Verify all entries cached
        for entry in cache_entries:
            exists = await mock_redis_client.exists(entry["key"])
            assert exists == 1
        
        # Invalidate by tag
        tag_to_invalidate = "analytics"
        tagged_keys = await mock_redis_client.smembers(f"cache_tag:{tag_to_invalidate}")
        
        if tagged_keys:
            await mock_redis_client.delete(*tagged_keys)
            await mock_redis_client.delete(f"cache_tag:{tag_to_invalidate}")
        
        # Verify analytics entries invalidated
        analytics_exists_1 = await mock_redis_client.exists("analytics:channel:123")
        analytics_exists_2 = await mock_redis_client.exists("analytics:channel:456")
        user_exists = await mock_redis_client.exists("user:profile:789")
        
        assert analytics_exists_1 == 0
        assert analytics_exists_2 == 0
        assert user_exists == 1  # User data should still exist
    
    @pytest.mark.asyncio
    async def test_pattern_based_cache_invalidation(self, mock_redis_client):
        """Test pattern-based cache invalidation"""
        # Create cache entries with patterns
        cache_patterns = [
            "user:123:profile",
            "user:123:preferences", 
            "user:123:sessions",
            "user:456:profile",
            "analytics:daily:2023-01-01",
            "analytics:daily:2023-01-02"
        ]
        
        # Store cache entries
        for pattern in cache_patterns:
            await mock_redis_client.set(pattern, f"data_for_{pattern}", ex=3600)
        
        # Verify all entries exist
        for pattern in cache_patterns:
            exists = await mock_redis_client.exists(pattern)
            assert exists == 1
        
        # Get keys matching pattern (user:123:*)
        # Note: fakeredis supports scan but pattern matching varies
        all_keys = []
        cursor = "0"
        while True:
            cursor, keys = await mock_redis_client.scan(cursor=cursor, match="user:123:*")
            all_keys.extend(keys)
            if cursor == 0:
                break
        
        # Verify pattern matching found correct keys
        user_123_keys = [k for k in all_keys if k.startswith("user:123:")]
        assert len(user_123_keys) >= 3  # Should find at least our 3 user:123 entries
    
    @pytest.mark.asyncio
    async def test_dependency_based_invalidation(self, mock_redis_client):
        """Test dependency-based cache invalidation"""
        # Create dependency mappings
        dependencies = {
            "user:123:analytics": ["user:123:profile", "analytics:daily:latest"],
            "channel:456:summary": ["analytics:channel:456", "user:123:profile"]
        }
        
        # Store cache entries and dependencies
        for cache_key, deps in dependencies.items():
            # Store main cache entry
            await mock_redis_client.set(cache_key, f"data_for_{cache_key}", ex=3600)
            
            # Store dependency mappings
            for dep in deps:
                await mock_redis_client.sadd(f"cache_deps:{dep}", cache_key)
        
        # Verify cache entries exist
        for cache_key in dependencies.keys():
            exists = await mock_redis_client.exists(cache_key)
            assert exists == 1
        
        # Invalidate a dependency
        dependency_to_invalidate = "user:123:profile"
        dependent_keys = await mock_redis_client.smembers(f"cache_deps:{dependency_to_invalidate}")
        
        # Remove dependent cache entries
        if dependent_keys:
            await mock_redis_client.delete(*dependent_keys)
        
        # Verify dependent entries were invalidated
        user_analytics_exists = await mock_redis_client.exists("user:123:analytics")
        channel_summary_exists = await mock_redis_client.exists("channel:456:summary")
        
        assert user_analytics_exists == 0
        assert channel_summary_exists == 0
    
    @pytest.mark.asyncio
    async def test_time_based_cache_invalidation(self, mock_redis_client):
        """Test time-based cache invalidation with TTL"""
        # Create cache entries with different TTL values
        ttl_entries = [
            {"key": "short_lived", "ttl": 1},     # 1 second
            {"key": "medium_lived", "ttl": 5},    # 5 seconds  
            {"key": "long_lived", "ttl": 3600}    # 1 hour
        ]
        
        # Store entries with TTL
        for entry in ttl_entries:
            await mock_redis_client.set(
                entry["key"],
                f"data_for_{entry['key']}",
                ex=entry["ttl"]
            )
        
        # Verify all entries exist initially
        for entry in ttl_entries:
            exists = await mock_redis_client.exists(entry["key"])
            assert exists == 1
        
        # Wait for short-lived entry to expire
        await asyncio.sleep(1.5)
        
        # Check expiration
        short_exists = await mock_redis_client.exists("short_lived")
        medium_exists = await mock_redis_client.exists("medium_lived")
        long_exists = await mock_redis_client.exists("long_lived")
        
        assert short_exists == 0    # Should be expired
        assert medium_exists == 1   # Should still exist
        assert long_exists == 1     # Should still exist


# Integration test configuration  
pytestmark = pytest.mark.integration

if __name__ == "__main__":
    # Run tests with coverage reporting
    pytest.main([
        __file__,
        "-v",
        "--tb=short", 
        "-x"  # Stop on first failure
    ])
