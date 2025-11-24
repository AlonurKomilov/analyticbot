"""
Bot Health Metrics ORM Model

Stores historical health metrics for user bots to enable:
- Trend analysis over time
- Recovery tracking after incidents
- Performance baseline establishment
- Admin reporting and analytics
"""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import BigInteger, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from infra.db.models.base import Base


class BotHealthMetricOrm(Base):
    """
    Persistent storage for bot health metrics snapshots.

    Captures point-in-time health data for each user bot to enable:
    - Historical trend analysis
    - Performance degradation detection
    - Recovery time tracking
    - SLA reporting
    """

    __tablename__ = "bot_health_metrics"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # User identification
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Health status
    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # healthy, degraded, unhealthy, suspended

    # Success/failure metrics
    total_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    successful_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Error rate (0.0 to 1.0)
    error_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Response time metrics (milliseconds)
    avg_response_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Timestamps
    last_success: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_failure: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    last_check: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Status flags
    is_rate_limited: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    last_error_type: Mapped[str] = mapped_column(String(255), nullable=True)

    # Circuit breaker state
    circuit_breaker_state: Mapped[str] = mapped_column(
        String(20), nullable=True
    )  # closed, open, half_open

    def __repr__(self) -> str:
        return (
            f"<BotHealthMetric(id={self.id}, user_id={self.user_id}, "
            f"status={self.status}, error_rate={self.error_rate:.2%}, "
            f"timestamp={self.timestamp})>"
        )


# Composite indexes for efficient queries
Index(
    "idx_bot_health_user_timestamp",
    BotHealthMetricOrm.user_id,
    BotHealthMetricOrm.timestamp.desc(),
)

Index(
    "idx_bot_health_status_timestamp",
    BotHealthMetricOrm.status,
    BotHealthMetricOrm.timestamp.desc(),
)
