"""
PostgreSQL implementation of SharedReportsRepository
Handles shared report storage and management in PostgreSQL database
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

import asyncpg

from core.repositories.shared_reports_repository import SharedReportsRepository
from infra.db.connection import get_db_connection

logger = logging.getLogger(__name__)


class AsyncPgSharedReportsRepository(SharedReportsRepository):
    """AsyncPG implementation of shared reports repository"""

    async def create_shared_report(
        self,
        share_token: str,
        report_type: str,
        channel_id: str,
        period: int,
        format: str,
        expires_at: datetime,
    ) -> str:
        """Create a new shared report"""
        query = """
        INSERT INTO shared_reports (
            id, share_token, report_type, channel_id, 
            period, format, expires_at, created_at, access_count
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id;
        """

        shared_report_id = str(uuid4())
        created_at = datetime.utcnow()

        try:
            async with get_db_connection() as conn:
                result = await conn.fetchrow(
                    query,
                    shared_report_id,
                    share_token,
                    report_type,
                    channel_id,
                    period,
                    format,
                    expires_at,
                    created_at,
                    0,
                )

                if not result:
                    raise RuntimeError("Failed to create shared report")

                logger.info(f"Created shared report {shared_report_id} with token {share_token}")
                return shared_report_id

        except asyncpg.UniqueViolationError:
            logger.error(f"Share token collision: {share_token}")
            raise ValueError("Share token already exists")
        except Exception as e:
            logger.error(f"Failed to create shared report: {e}")
            raise

    async def get_shared_report(self, share_token: str) -> dict[str, Any] | None:
        """Get shared report by token"""
        query = """
        SELECT id, share_token, report_type, channel_id, period, 
               format, created_at, expires_at, access_count
        FROM shared_reports 
        WHERE share_token = $1;
        """

        try:
            async with get_db_connection() as conn:
                result = await conn.fetchrow(query, share_token)

                if not result:
                    return None

                return {
                    "id": result["id"],
                    "share_token": result["share_token"],
                    "report_type": result["report_type"],
                    "channel_id": result["channel_id"],
                    "period": result["period"],
                    "format": result["format"],
                    "created_at": result["created_at"],
                    "expires_at": result["expires_at"],
                    "access_count": result["access_count"],
                }

        except Exception as e:
            logger.error(f"Failed to get shared report {share_token}: {e}")
            raise

    async def increment_access_count(self, share_token: str) -> None:
        """Increment access count for a shared report"""
        query = """
        UPDATE shared_reports 
        SET access_count = access_count + 1,
            last_accessed_at = $1
        WHERE share_token = $2;
        """

        try:
            async with get_db_connection() as conn:
                await conn.execute(query, datetime.utcnow(), share_token)
                logger.debug(f"Incremented access count for share {share_token}")

        except Exception as e:
            logger.error(f"Failed to increment access count for {share_token}: {e}")
            raise

    async def delete_shared_report(self, share_token: str) -> None:
        """Delete a shared report"""
        query = "DELETE FROM shared_reports WHERE share_token = $1;"

        try:
            async with get_db_connection() as conn:
                result = await conn.execute(query, share_token)

                # Extract affected rows from result status
                if hasattr(result, "split") and "DELETE" in result:
                    rows_deleted = int(result.split()[-1])
                    if rows_deleted > 0:
                        logger.info(f"Deleted shared report {share_token}")
                    else:
                        logger.warning(f"No shared report found for token {share_token}")
                else:
                    logger.info(f"Deleted shared report {share_token}")

        except Exception as e:
            logger.error(f"Failed to delete shared report {share_token}: {e}")
            raise

    async def cleanup_expired(self) -> int:
        """Clean up expired shared reports"""
        query = """
        DELETE FROM shared_reports 
        WHERE expires_at < $1;
        """

        try:
            async with get_db_connection() as conn:
                result = await conn.execute(query, datetime.utcnow())

                # Extract deleted count from result status
                if hasattr(result, "split") and "DELETE" in result:
                    deleted_count = int(result.split()[-1])
                else:
                    deleted_count = 0

                logger.info(f"Cleaned up {deleted_count} expired shared reports")
                return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired shared reports: {e}")
            raise

    async def get_reports_by_channel(
        self, channel_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get shared reports for a specific channel"""
        query = """
        SELECT id, share_token, report_type, channel_id, period, 
               format, created_at, expires_at, access_count
        FROM shared_reports 
        WHERE channel_id = $1 
        AND expires_at > $2
        ORDER BY created_at DESC 
        LIMIT $3;
        """

        try:
            async with get_db_connection() as conn:
                results = await conn.fetch(query, channel_id, datetime.utcnow(), limit)

                reports = []
                for result in results:
                    reports.append(
                        {
                            "id": result["id"],
                            "share_token": result["share_token"],
                            "report_type": result["report_type"],
                            "channel_id": result["channel_id"],
                            "period": result["period"],
                            "format": result["format"],
                            "created_at": result["created_at"],
                            "expires_at": result["expires_at"],
                            "access_count": result["access_count"],
                        }
                    )

                logger.debug(f"Found {len(reports)} shared reports for channel {channel_id}")
                return reports

        except Exception as e:
            logger.error(f"Failed to get shared reports for channel {channel_id}: {e}")
            raise
