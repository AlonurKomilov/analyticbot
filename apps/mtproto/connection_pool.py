"""
MTProto Connection Pool Manager with Auto-Close and Per-User Limits

Optimizes MTProto worker performance by:
1. Auto-closing connections after each collection session
2. Limiting max concurrent connections per user
3. Tracking session duration and resource usage
4. Implementing connection timeouts
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class SessionMetrics:
    """Metrics for a single MTProto collection session"""

    user_id: int
    start_time: datetime
    end_time: datetime | None = None
    channels_processed: int = 0
    messages_collected: int = 0
    duration_seconds: float = 0.0
    connection_opened: bool = False
    connection_closed: bool = False
    errors: int = 0


class ConnectionPoolConfig:
    """Configuration for MTProto connection pool"""

    # Maximum concurrent connections per user
    MAX_CONNECTIONS_PER_USER = 1  # One connection at a time per user

    # Maximum total concurrent connections across all users
    # This should be configurable by admin for scaling
    MAX_TOTAL_CONNECTIONS = 10  # System-wide limit (configurable)

    # Connection timeout (seconds)
    CONNECTION_TIMEOUT = 300  # 5 minutes

    # Session timeout (seconds) - auto-close after this long
    SESSION_TIMEOUT = 600  # 10 minutes

    # Idle timeout (seconds) - disconnect if idle
    IDLE_TIMEOUT = 180  # 3 minutes

    # Database connection pool per MTProto worker
    DB_POOL_MIN_SIZE = 5
    DB_POOL_MAX_SIZE = 15

    # Cleanup interval (seconds)
    CLEANUP_INTERVAL = 300  # 5 minutes

    @classmethod
    def from_settings(cls, settings):
        """Create configuration from MTProtoSettings.

        Args:
            settings: MTProtoSettings instance

        Returns:
            ConnectionPoolConfig with values from settings
        """
        config = cls()
        config.MAX_CONNECTIONS_PER_USER = settings.MTPROTO_MAX_CONNECTIONS_PER_USER
        config.MAX_TOTAL_CONNECTIONS = settings.MTPROTO_MAX_CONNECTIONS
        config.CONNECTION_TIMEOUT = settings.MTPROTO_CONNECTION_TIMEOUT
        config.SESSION_TIMEOUT = settings.MTPROTO_SESSION_TIMEOUT
        config.IDLE_TIMEOUT = settings.MTPROTO_IDLE_TIMEOUT
        config.CLEANUP_INTERVAL = settings.MTPROTO_CLEANUP_INTERVAL
        config.DB_POOL_MIN_SIZE = settings.MTPROTO_DB_POOL_MIN_SIZE
        config.DB_POOL_MAX_SIZE = settings.MTPROTO_DB_POOL_MAX_SIZE
        return config

    @classmethod
    def from_settings(cls, settings):
        """Create config from MTProtoSettings"""
        config = cls()
        config.MAX_CONNECTIONS_PER_USER = settings.MTPROTO_MAX_CONNECTIONS_PER_USER
        config.MAX_TOTAL_CONNECTIONS = settings.MTPROTO_MAX_CONCURRENT_USERS
        config.CONNECTION_TIMEOUT = settings.MTPROTO_CONNECTION_TIMEOUT
        config.SESSION_TIMEOUT = settings.MTPROTO_SESSION_TIMEOUT
        config.IDLE_TIMEOUT = settings.MTPROTO_IDLE_TIMEOUT
        return config


class MTProtoConnectionPool:
    """
    Manages MTProto connections with auto-close and resource limits.

    Key features:
    - One connection per user at a time
    - Auto-close after collection completes
    - Track session metrics
    - Enforce timeouts
    - Cleanup idle connections
    """

    def __init__(self, config: ConnectionPoolConfig | None = None):
        self.config = config or ConnectionPoolConfig()
        self._active_sessions: dict[int, SessionMetrics] = {}
        self._session_locks: dict[int, asyncio.Lock] = {}
        self._total_connections_semaphore = asyncio.Semaphore(self.config.MAX_TOTAL_CONNECTIONS)
        self._cleanup_task: asyncio.Task | None = None
        self._metrics_history: list[SessionMetrics] = []

    async def acquire_session(self, user_id: int) -> bool:
        """
        Acquire a session for user. Returns False if user already has active session.

        Args:
            user_id: User ID requesting session

        Returns:
            True if session acquired, False if user already active
        """
        # Check if user already has active session
        if user_id in self._active_sessions:
            logger.warning(f"User {user_id} already has active MTProto session, skipping")
            return False

        # Acquire system-wide semaphore
        acquired = await asyncio.wait_for(
            self._total_connections_semaphore.acquire(),
            timeout=self.config.CONNECTION_TIMEOUT,
        )

        if not acquired:
            logger.error(f"Failed to acquire connection for user {user_id} (system limit)")
            return False

        # Create user lock if doesn't exist
        if user_id not in self._session_locks:
            self._session_locks[user_id] = asyncio.Lock()

        # Acquire user lock
        await self._session_locks[user_id].acquire()

        # Create session metrics
        session = SessionMetrics(user_id=user_id, start_time=datetime.utcnow())
        session.connection_opened = True
        self._active_sessions[user_id] = session

        logger.info(
            f"📡 Acquired MTProto session for user {user_id} "
            f"(active: {len(self._active_sessions)}/{self.config.MAX_TOTAL_CONNECTIONS})"
        )

        return True

    async def release_session(
        self,
        user_id: int,
        channels_processed: int = 0,
        messages_collected: int = 0,
        errors: int = 0,
    ):
        """
        Release session and record metrics.

        Args:
            user_id: User ID
            channels_processed: Number of channels processed
            messages_collected: Number of messages collected
            errors: Number of errors encountered
        """
        if user_id not in self._active_sessions:
            logger.warning(f"No active session found for user {user_id}")
            return

        # Update session metrics
        session = self._active_sessions[user_id]
        session.end_time = datetime.utcnow()
        session.duration_seconds = (session.end_time - session.start_time).total_seconds()
        session.channels_processed = channels_processed
        session.messages_collected = messages_collected
        session.errors = errors
        session.connection_closed = True

        # Move to history
        self._metrics_history.append(session)

        # Keep only last 1000 sessions in history
        if len(self._metrics_history) > 1000:
            self._metrics_history = self._metrics_history[-1000:]

        # Remove from active
        del self._active_sessions[user_id]

        # Release locks
        if user_id in self._session_locks:
            self._session_locks[user_id].release()

        self._total_connections_semaphore.release()

        logger.info(
            f"✅ Released MTProto session for user {user_id} "
            f"(duration: {session.duration_seconds:.1f}s, "
            f"channels: {channels_processed}, "
            f"messages: {messages_collected}, "
            f"errors: {errors})"
        )

    async def cleanup_stale_sessions(self):
        """Cleanup sessions that exceeded timeout"""
        now = datetime.utcnow()
        session_timeout = timedelta(seconds=self.config.SESSION_TIMEOUT)

        stale_users = []
        for user_id, session in self._active_sessions.items():
            if now - session.start_time > session_timeout:
                stale_users.append(user_id)
                logger.warning(
                    f"⚠️  Session for user {user_id} exceeded timeout "
                    f"({self.config.SESSION_TIMEOUT}s), force closing"
                )

        for user_id in stale_users:
            await self.release_session(user_id, errors=1)

    def get_active_sessions_count(self) -> int:
        """Get number of active sessions"""
        return len(self._active_sessions)

    def get_metrics_summary(self) -> dict:
        """Get summary of recent session metrics"""
        if not self._metrics_history:
            return {
                "total_sessions": 0,
                "avg_duration_seconds": 0,
                "avg_messages_per_session": 0,
                "avg_channels_per_session": 0,
                "total_errors": 0,
            }

        recent = self._metrics_history[-100:]  # Last 100 sessions

        return {
            "total_sessions": len(self._metrics_history),
            "recent_sessions": len(recent),
            "avg_duration_seconds": sum(s.duration_seconds for s in recent) / len(recent),
            "avg_messages_per_session": sum(s.messages_collected for s in recent) / len(recent),
            "avg_channels_per_session": sum(s.channels_processed for s in recent) / len(recent),
            "total_errors": sum(s.errors for s in recent),
            "active_sessions": len(self._active_sessions),
            "max_connections": self.config.MAX_TOTAL_CONNECTIONS,
        }

    async def start_cleanup_task(self):
        """Start background cleanup task"""

        async def cleanup_loop():
            while True:
                await asyncio.sleep(self.config.CLEANUP_INTERVAL)
                try:
                    await self.cleanup_stale_sessions()
                except Exception as e:
                    logger.error(f"Error in cleanup task: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_loop())
        logger.info("🧹 Started connection pool cleanup task")

    async def stop_cleanup_task(self):
        """Stop cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("🛑 Stopped connection pool cleanup task")


# Global connection pool instance
_connection_pool: MTProtoConnectionPool | None = None


def get_connection_pool() -> MTProtoConnectionPool:
    """Get global connection pool instance"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = MTProtoConnectionPool()
    return _connection_pool


async def init_connection_pool(config: ConnectionPoolConfig | None = None):
    """Initialize global connection pool"""
    global _connection_pool
    _connection_pool = MTProtoConnectionPool(config)
    await _connection_pool.start_cleanup_task()
    logger.info("✅ MTProto connection pool initialized")


async def shutdown_connection_pool():
    """Shutdown global connection pool"""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.stop_cleanup_task()
        _connection_pool = None
    logger.info("✅ MTProto connection pool shutdown")
