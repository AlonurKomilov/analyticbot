"""
Table Partition Manager
=======================

For 100K+ users with millions of rows, table partitioning is essential:
- Faster queries (scan only relevant partitions)
- Easier data management (drop old partitions)
- Better vacuum performance
- Parallel query execution

Partition Strategies:
    1. Time-based: post_metrics, service_usage_log, credit_transactions
    2. Range-based: users (by ID range)
    3. List-based: channels (by user_id hash)
"""

import logging
from datetime import datetime, timedelta
from typing import Any

import asyncpg

logger = logging.getLogger(__name__)


class PartitionManager:
    """
    Manages table partitioning for high-scale deployments.

    Tables recommended for partitioning at 100K+ users:

    1. post_metrics (time-series data)
       - Partition by: month
       - Retention: 12 months
       - Expected: millions of rows/month

    2. service_usage_log (usage tracking)
       - Partition by: month
       - Retention: 6 months
       - Expected: 100K+ rows/day

    3. credit_transactions (financial)
       - Partition by: month
       - Retention: 24 months (compliance)
       - Expected: 50K+ rows/day

    4. mtproto_audit_log (security)
       - Partition by: month
       - Retention: 12 months
       - Expected: 100K+ rows/day
    """

    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def create_partitioned_table(
        self,
        table_name: str,
        partition_key: str,
        partition_type: str = "RANGE",
    ) -> bool:
        """
        Convert existing table to partitioned table.

        WARNING: This requires downtime. Use during maintenance window.
        """
        logger.info(f"Creating partitioned table: {table_name}")

        # This is a template - actual implementation depends on table structure
        # You would need to:
        # 1. Create new partitioned table
        # 2. Migrate data
        # 3. Swap tables
        # 4. Drop old table

        return True

    async def create_monthly_partitions(
        self,
        table_name: str,
        months_ahead: int = 3,
        months_behind: int = 12,
    ) -> list[str]:
        """
        Create monthly partitions for time-series tables.

        Args:
            table_name: Base table name
            months_ahead: Create partitions for future months
            months_behind: Keep partitions for past months

        Returns:
            List of created partition names
        """
        created = []
        today = datetime.now()

        async with self._pool.acquire() as conn:
            for offset in range(-months_behind, months_ahead + 1):
                # Calculate partition month
                partition_date = today.replace(day=1) + timedelta(days=32 * offset)
                partition_date = partition_date.replace(day=1)

                year = partition_date.year
                month = partition_date.month

                partition_name = f"{table_name}_y{year}m{month:02d}"

                # Calculate partition bounds
                start_date = partition_date
                if month == 12:
                    end_date = partition_date.replace(year=year + 1, month=1)
                else:
                    end_date = partition_date.replace(month=month + 1)

                # Create partition if not exists
                try:
                    await conn.execute(f"""
                        CREATE TABLE IF NOT EXISTS {partition_name}
                        PARTITION OF {table_name}
                        FOR VALUES FROM ('{start_date.date()}') TO ('{end_date.date()}')
                    """)
                    created.append(partition_name)
                    logger.info(f"Created partition: {partition_name}")
                except asyncpg.DuplicateTableError:
                    # Partition already exists
                    pass
                except Exception as e:
                    logger.error(f"Failed to create partition {partition_name}: {e}")

        return created

    async def drop_old_partitions(
        self,
        table_name: str,
        retention_months: int = 12,
    ) -> list[str]:
        """
        Drop partitions older than retention period.

        Args:
            table_name: Base table name
            retention_months: Keep data for this many months

        Returns:
            List of dropped partition names
        """
        dropped = []
        cutoff_date = datetime.now() - timedelta(days=retention_months * 30)

        async with self._pool.acquire() as conn:
            # Find old partitions
            partitions = await conn.fetch(
                """
                SELECT inhrelid::regclass::text as partition_name
                FROM pg_inherits
                WHERE inhparent = $1::regclass
            """,
                table_name,
            )

            for row in partitions:
                partition_name = row["partition_name"]

                # Extract date from partition name (e.g., table_y2024m01)
                try:
                    parts = partition_name.split("_y")
                    if len(parts) >= 2:
                        date_part = parts[-1]  # e.g., "2024m01"
                        year = int(date_part[:4])
                        month = int(date_part[5:7])
                        partition_date = datetime(year, month, 1)

                        if partition_date < cutoff_date:
                            await conn.execute(f"DROP TABLE IF EXISTS {partition_name}")
                            dropped.append(partition_name)
                            logger.info(f"Dropped old partition: {partition_name}")
                except (ValueError, IndexError):
                    continue

        return dropped

    async def get_partition_stats(self, table_name: str) -> list[dict[str, Any]]:
        """Get statistics for all partitions of a table"""
        async with self._pool.acquire() as conn:
            stats = await conn.fetch(
                """
                SELECT 
                    child.relname as partition_name,
                    pg_size_pretty(pg_relation_size(child.oid)) as size,
                    pg_stat_user_tables.n_live_tup as row_count
                FROM pg_inherits
                JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
                JOIN pg_class child ON pg_inherits.inhrelid = child.oid
                LEFT JOIN pg_stat_user_tables ON child.relname = pg_stat_user_tables.relname
                WHERE parent.relname = $1
                ORDER BY child.relname
            """,
                table_name,
            )

            return [dict(row) for row in stats]


# Migration scripts for converting tables to partitioned
PARTITION_MIGRATIONS = {
    "post_metrics": """
        -- Step 1: Create new partitioned table
        CREATE TABLE post_metrics_new (
            channel_id BIGINT NOT NULL,
            msg_id BIGINT NOT NULL,
            snapshot_time TIMESTAMPTZ NOT NULL,
            views BIGINT,
            forwards BIGINT,
            replies_count BIGINT,
            reactions JSONB,
            reactions_count BIGINT,
            PRIMARY KEY (channel_id, msg_id, snapshot_time)
        ) PARTITION BY RANGE (snapshot_time);
        
        -- Step 2: Create initial partitions (run create_monthly_partitions)
        
        -- Step 3: Migrate data (do in batches during maintenance)
        -- INSERT INTO post_metrics_new SELECT * FROM post_metrics;
        
        -- Step 4: Swap tables
        -- ALTER TABLE post_metrics RENAME TO post_metrics_old;
        -- ALTER TABLE post_metrics_new RENAME TO post_metrics;
        
        -- Step 5: Drop old table after verification
        -- DROP TABLE post_metrics_old;
    """,
    "service_usage_log": """
        CREATE TABLE service_usage_log_new (
            id BIGSERIAL,
            subscription_id INTEGER NOT NULL,
            user_id BIGINT NOT NULL,
            service_id INTEGER NOT NULL,
            action VARCHAR(100) NOT NULL,
            resource_id VARCHAR(255),
            usage_count INTEGER DEFAULT 1,
            success BOOLEAN NOT NULL,
            error_message TEXT,
            response_time_ms INTEGER,
            metadata JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY (id, created_at)
        ) PARTITION BY RANGE (created_at);
    """,
    "credit_transactions": """
        CREATE TABLE credit_transactions_new (
            id SERIAL,
            user_id BIGINT NOT NULL,
            amount NUMERIC(12,2) NOT NULL,
            balance_after NUMERIC(12,2) NOT NULL,
            type VARCHAR(50) NOT NULL,
            category VARCHAR(50),
            description VARCHAR(500),
            reference_id VARCHAR(100),
            metadata JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY (id, created_at)
        ) PARTITION BY RANGE (created_at);
    """,
}
