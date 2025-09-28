"""
SQLite Database Engine
SQLite engine for development environment
"""

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SQLiteEngine:
    """SQLite database engine for local storage and development"""

    def __init__(self, db_path: str = "data/analyticbot.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[sqlite3.Connection] = None

    def get_connection(self) -> sqlite3.Connection:
        """Get SQLite connection with optimizations"""
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            # Enable WAL mode for better concurrency
            self._connection.execute("PRAGMA journal_mode=WAL")
            # Optimize for performance
            self._connection.execute("PRAGMA synchronous=NORMAL")
            self._connection.execute("PRAGMA cache_size=10000")
            self._connection.execute("PRAGMA temp_store=MEMORY")
            logger.info(f"SQLite connection established: {self.db_path}")
        
        return self._connection

    def close(self):
        """Close SQLite connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
            logger.info("SQLite connection closed")

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQLite query"""
        conn = self.get_connection()
        return conn.execute(query, params)

    def executemany(self, query: str, params_list: list) -> sqlite3.Cursor:
        """Execute SQLite query with multiple parameter sets"""
        conn = self.get_connection()
        return conn.executemany(query, params_list)

    def commit(self):
        """Commit current transaction"""
        if self._connection:
            self._connection.commit()

    def rollback(self):
        """Rollback current transaction"""
        if self._connection:
            self._connection.rollback()


# Global SQLite engine instance
sqlite_engine = SQLiteEngine()


def init_db() -> None:
    """Initialize SQLite database with required tables"""
    try:
        conn = sqlite_engine.get_connection()
        
        # Create tables if they don't exist
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                plan_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                username TEXT,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                subscriber_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL,
                message_id BIGINT,
                view_count INTEGER DEFAULT 0,
                forward_count INTEGER DEFAULT 0,
                reaction_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                share_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (channel_id) REFERENCES channels (id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                max_channels INTEGER DEFAULT 1,
                max_posts_per_month INTEGER DEFAULT 30,
                price DECIMAL(10, 2) DEFAULT 0.00,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS scheduled_posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                media_type TEXT,
                media_path TEXT,
                scheduled_time TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (channel_id) REFERENCES channels (id)
            )
            """
        ]
        
        for table_sql in tables:
            conn.execute(table_sql)
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)",
            "CREATE INDEX IF NOT EXISTS idx_channels_user_id ON channels(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_channels_telegram_id ON channels(telegram_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_channel_id ON analytics(channel_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_scheduled_posts_user_id ON scheduled_posts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_scheduled_posts_channel_id ON scheduled_posts(channel_id)",
            "CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON scheduled_posts(status)",
            "CREATE INDEX IF NOT EXISTS idx_scheduled_posts_scheduled_time ON scheduled_posts(scheduled_time)"
        ]
        
        for index_sql in indexes:
            try:
                conn.execute(index_sql)
            except sqlite3.OperationalError as e:
                # Index might already exist
                logger.debug(f"Index creation skipped: {e}")
        
        # Insert default plans if not exist
        default_plans = [
            ("Free", 1, 30, 0.00),
            ("Basic", 5, 100, 9.99),
            ("Pro", 20, 500, 29.99),
            ("Premium", 100, 2000, 99.99)
        ]
        
        for plan_name, max_channels, max_posts, price in default_plans:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO plans (name, max_channels, max_posts_per_month, price) VALUES (?, ?, ?, ?)",
                    (plan_name, max_channels, max_posts, price)
                )
            except sqlite3.Error as e:
                logger.debug(f"Plan insertion skipped: {e}")
        
        conn.commit()
        logger.info("SQLite database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize SQLite database: {e}")
        raise


def close_db():
    """Close SQLite database connection"""
    sqlite_engine.close()


# Convenience functions for backward compatibility
def get_sqlite_connection() -> sqlite3.Connection:
    """Get SQLite connection (backward compatibility)"""
    return sqlite_engine.get_connection()


def execute_sqlite_query(query: str, params: tuple = ()) -> sqlite3.Cursor:
    """Execute SQLite query (backward compatibility)"""
    return sqlite_engine.execute(query, params)