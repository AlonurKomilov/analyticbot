"""
Admin Plans Router - Subscription Plan Management

Handles administrative operations for subscription plans and MTProto configuration.

Domain: Admin plan management operations
Path: /admin/plans/*
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from apps.api.middleware.auth import require_admin_user
from apps.di.analytics_container import get_database_pool

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/plans",
    tags=["Admin - Plans"],
    responses={404: {"description": "Not found"}},
)

# === MODELS ===


class PlanResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    price: float
    duration_days: int
    is_active: bool
    features: dict[str, Any] = Field(default_factory=dict)
    mtproto_interval_minutes: int = 60
    min_mtproto_interval_minutes: int = 30
    credits_per_interval_boost: int = 5
    interval_boost_minutes: int = 10
    can_purchase_boost: bool = True


class UpdateMTProtoConfigRequest(BaseModel):
    mtproto_interval_minutes: int = Field(gt=0, le=1440)
    min_mtproto_interval_minutes: int = Field(gt=0, le=1440)
    credits_per_interval_boost: int = Field(gt=0)
    interval_boost_minutes: int = Field(gt=0)
    can_purchase_boost: bool = True


# === ENDPOINTS ===


@router.get("", response_model=list[PlanResponse])
async def get_all_plans(
    _: Any = Depends(require_admin_user),
    pool=Depends(get_database_pool),
):
    """Get all subscription plans with MTProto configuration."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT
                id, name, slug, description, price, duration_days,
                is_active, features,
                COALESCE(mtproto_interval_minutes, 60) as mtproto_interval_minutes,
                COALESCE(min_mtproto_interval_minutes, 30) as min_mtproto_interval_minutes,
                COALESCE(credits_per_interval_boost, 5) as credits_per_interval_boost,
                COALESCE(interval_boost_minutes, 10) as interval_boost_minutes,
                COALESCE(can_purchase_boost, true) as can_purchase_boost
            FROM plans
            ORDER BY price ASC
        """
        )

        plans = []
        for row in rows:
            plans.append(
                PlanResponse(
                    id=row["id"],
                    name=row["name"],
                    slug=row["slug"],
                    description=row["description"],
                    price=float(row["price"]),
                    duration_days=row["duration_days"],
                    is_active=row["is_active"],
                    features=row["features"] or {},
                    mtproto_interval_minutes=row["mtproto_interval_minutes"],
                    min_mtproto_interval_minutes=row["min_mtproto_interval_minutes"],
                    credits_per_interval_boost=row["credits_per_interval_boost"],
                    interval_boost_minutes=row["interval_boost_minutes"],
                    can_purchase_boost=row["can_purchase_boost"],
                )
            )

        return plans


@router.patch("/{plan_id}/mtproto-config", response_model=PlanResponse)
async def update_plan_mtproto_config(
    plan_id: int,
    request: UpdateMTProtoConfigRequest,
    _: Any = Depends(require_admin_user),
    pool=Depends(get_database_pool),
):
    """Update MTProto configuration for a subscription plan."""
    # Validate: min interval must be <= base interval
    if request.min_mtproto_interval_minutes > request.mtproto_interval_minutes:
        raise HTTPException(
            status_code=400,
            detail="Minimum interval cannot be greater than base interval",
        )

    # Validate: boost reduction makes sense
    if request.interval_boost_minutes > (
        request.mtproto_interval_minutes - request.min_mtproto_interval_minutes
    ):
        raise HTTPException(
            status_code=400,
            detail="Boost reduction is too large for the interval range",
        )

    async with pool.acquire() as conn:
        # Check plan exists
        plan_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM plans WHERE id = $1)", plan_id
        )
        if not plan_exists:
            raise HTTPException(status_code=404, detail="Plan not found")

        # Update plan
        row = await conn.fetchrow(
            """
            UPDATE plans
            SET
                mtproto_interval_minutes = $1,
                min_mtproto_interval_minutes = $2,
                credits_per_interval_boost = $3,
                interval_boost_minutes = $4,
                can_purchase_boost = $5
            WHERE id = $6
            RETURNING
                id, name, slug, description, price, duration_days,
                is_active, features,
                mtproto_interval_minutes,
                min_mtproto_interval_minutes,
                credits_per_interval_boost,
                interval_boost_minutes,
                can_purchase_boost
            """,
            request.mtproto_interval_minutes,
            request.min_mtproto_interval_minutes,
            request.credits_per_interval_boost,
            request.interval_boost_minutes,
            request.can_purchase_boost,
            plan_id,
        )

        if not row:
            raise HTTPException(status_code=500, detail="Failed to update plan")

        logger.info(
            f"Admin updated MTProto config for plan {plan_id}: "
            f"interval={request.mtproto_interval_minutes}min, "
            f"min={request.min_mtproto_interval_minutes}min, "
            f"boost_cost={request.credits_per_interval_boost}, "
            f"boost_reduction={request.interval_boost_minutes}min"
        )

        return PlanResponse(
            id=row["id"],
            name=row["name"],
            slug=row["slug"],
            description=row["description"],
            price=float(row["price"]),
            duration_days=row["duration_days"],
            is_active=row["is_active"],
            features=row["features"] or {},
            mtproto_interval_minutes=row["mtproto_interval_minutes"],
            min_mtproto_interval_minutes=row["min_mtproto_interval_minutes"],
            credits_per_interval_boost=row["credits_per_interval_boost"],
            interval_boost_minutes=row["interval_boost_minutes"],
            can_purchase_boost=row["can_purchase_boost"],
        )
