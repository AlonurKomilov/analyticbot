"""
Admin Rate Limits Router - Rate Limit Monitoring & Configuration

Handles administrative operations for rate limit management:
- View current rate limit configurations
- Monitor usage statistics across all services
- Update rate limit configurations dynamically
- View historical usage data
- Reset rate limits for specific users/IPs

Domain: Admin rate limit management
Path: /admin/rate-limits/*
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel

from apps.api.middleware.auth import (
    get_current_user,
    require_admin_user,
)
from apps.api.middleware.rate_limiter import (
    RateLimitConfig as RateLimitConfigMiddleware,
)
from apps.api.middleware.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/rate-limits",
    tags=["Admin - Rate Limit Management"],
    responses={404: {"description": "Not found"}},
)


# === MODELS ===


class RateLimitConfigModel(BaseModel):
    """Rate limit configuration model"""

    service: str
    limit: int
    period: str  # "minute", "hour", "day"
    enabled: bool = True
    description: str | None = None


class RateLimitConfigResponse(BaseModel):
    """Response containing all rate limit configurations"""

    configs: list[RateLimitConfigModel]
    total: int


class RateLimitUsageModel(BaseModel):
    """Current usage statistics for a service"""

    service: str
    current_usage: int
    limit: int
    period: str
    remaining: int
    reset_at: str | None
    utilization_percent: float
    is_at_limit: bool


class RateLimitUsageResponse(BaseModel):
    """Response containing all usage statistics"""

    stats: list[RateLimitUsageModel]
    total: int
    timestamp: str


class RateLimitUpdateRequest(BaseModel):
    """Request to update a rate limit configuration"""

    limit: int | None = None
    period: str | None = None
    enabled: bool | None = None
    description: str | None = None


class RateLimitHistoryModel(BaseModel):
    """Historical usage data point"""

    timestamp: str
    usage: int


class RateLimitHistoryResponse(BaseModel):
    """Response containing historical usage data"""

    service: str
    history: list[RateLimitHistoryModel]
    total_points: int


class TopUserModel(BaseModel):
    """Top user by rate limit usage"""

    user_id: int
    usage: int


class TopUsersResponse(BaseModel):
    """Response containing top users"""

    service: str
    users: list[TopUserModel]
    total: int


class ResetResponse(BaseModel):
    """Response for reset operations"""

    success: bool
    message: str


class RateLimitDashboardResponse(BaseModel):
    """Combined dashboard response with configs and stats"""

    configs: list[RateLimitConfigModel]
    stats: list[RateLimitUsageModel]
    summary: dict[str, Any]
    timestamp: str


# === HELPER FUNCTIONS ===


def get_rate_limit_service():
    """Get the rate limit monitoring service"""
    from core.services.system import get_rate_limit_service as get_service

    return get_service()


# === ENDPOINTS ===


@router.get("/dashboard", response_model=RateLimitDashboardResponse)
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def get_rate_limit_dashboard(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📊 Rate Limit Dashboard (Admin)

    Get a comprehensive dashboard view of all rate limits including:
    - All rate limit configurations
    - Current usage statistics for each service
    - Summary metrics (total services, at-limit count, etc.)

    **Admin Only**: Requires admin role

    **Returns:**
    - Combined view of configs and stats
    - Summary metrics for quick overview
    """
    try:
        await require_admin_user(current_user)

        service = get_rate_limit_service()

        # Get configs and stats in parallel (conceptually)
        configs = await service.get_all_configs()
        stats = await service.get_all_usage_stats()

        # Calculate summary metrics
        at_limit_count = sum(1 for s in stats if s.get("is_at_limit", False))
        high_usage_count = sum(1 for s in stats if s.get("utilization_percent", 0) > 80)
        total_requests = sum(s.get("current_usage", 0) for s in stats)

        summary = {
            "total_services": len(configs),
            "services_at_limit": at_limit_count,
            "high_usage_services": high_usage_count,
            "total_requests_this_period": total_requests,
            "enabled_services": sum(1 for c in configs if c.get("enabled", True)),
        }

        return RateLimitDashboardResponse(
            configs=[RateLimitConfigModel(**c) for c in configs],
            stats=[RateLimitUsageModel(**s) for s in stats],
            summary=summary,
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Error getting rate limit dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configs", response_model=RateLimitConfigResponse)
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def get_all_rate_limit_configs(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ⚙️ Get All Rate Limit Configurations (Admin)

    Retrieve all rate limit configurations for all services.

    **Admin Only**: Requires admin role

    **Returns:**
    - List of all rate limit configurations
    - Service name, limit, period, and status
    """
    try:
        await require_admin_user(current_user)

        service = get_rate_limit_service()
        configs = await service.get_all_configs()

        return RateLimitConfigResponse(
            configs=[RateLimitConfigModel(**c) for c in configs],
            total=len(configs),
        )

    except Exception as e:
        logger.error(f"Error getting rate limit configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configs/{service_name}", response_model=RateLimitConfigModel)
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def get_rate_limit_config(
    request: Request,
    response: Response,
    service_name: str,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ⚙️ Get Rate Limit Configuration (Admin)

    Retrieve rate limit configuration for a specific service.

    **Admin Only**: Requires admin role

    **Path Parameters:**
    - `service_name`: Name of the service (e.g., "bot_operations", "admin_operations")

    **Returns:**
    - Rate limit configuration for the service
    """
    try:
        await require_admin_user(current_user)

        service = get_rate_limit_service()
        config = await service.get_config(service_name)

        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Rate limit config not found for service: {service_name}",
            )

        return RateLimitConfigModel(**config)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rate limit config for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/configs/{service_name}", response_model=RateLimitConfigModel)
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def update_rate_limit_config(
    request: Request,
    response: Response,
    service_name: str,
    update: RateLimitUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    ## ✏️ Update Rate Limit Configuration (Admin)

    Update rate limit configuration for a specific service.

    **Admin Only**: Requires admin role

    **Path Parameters:**
    - `service_name`: Name of the service to update

    **Body Parameters:**
    - `limit`: New request limit (optional)
    - `period`: New time period - "minute", "hour", "day" (optional)
    - `enabled`: Enable/disable the rate limit (optional)
    - `description`: Description of the rate limit (optional)

    **Returns:**
    - Updated rate limit configuration

    **Example:**
    ```json
    {
        "limit": 200,
        "period": "minute",
        "enabled": true
    }
    ```
    """
    try:
        await require_admin_user(current_user)

        # Validate period if provided
        if update.period and update.period not in ["minute", "hour", "day"]:
            raise HTTPException(status_code=400, detail="Period must be 'minute', 'hour', or 'day'")

        # Validate limit if provided
        if update.limit is not None and update.limit < 1:
            raise HTTPException(status_code=400, detail="Limit must be at least 1")

        service = get_rate_limit_service()
        updated_config = await service.update_config(
            service=service_name,
            limit=update.limit,
            period=update.period,
            enabled=update.enabled,
            description=update.description,
        )

        logger.info(
            f"Admin {current_user.get('username')} updated rate limit for {service_name}: {update}"
        )

        return RateLimitConfigModel(**updated_config)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rate limit config for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=RateLimitUsageResponse)
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def get_rate_limit_stats(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📈 Get Rate Limit Usage Statistics (Admin)

    Retrieve current usage statistics for all rate-limited services.

    **Admin Only**: Requires admin role

    **Returns:**
    - Current usage for each service
    - Limit and remaining requests
    - Utilization percentage
    - Reset time
    """
    try:
        await require_admin_user(current_user)

        service = get_rate_limit_service()
        stats = await service.get_all_usage_stats()

        return RateLimitUsageResponse(
            stats=[RateLimitUsageModel(**s) for s in stats],
            total=len(stats),
            timestamp=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Error getting rate limit stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{service_name}", response_model=RateLimitUsageModel)
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def get_service_rate_limit_stats(
    request: Request,
    response: Response,
    service_name: str,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📈 Get Service Rate Limit Stats (Admin)

    Retrieve current usage statistics for a specific service.

    **Admin Only**: Requires admin role

    **Path Parameters:**
    - `service_name`: Name of the service

    **Returns:**
    - Current usage, limit, remaining, utilization
    """
    try:
        await require_admin_user(current_user)

        service = get_rate_limit_service()
        usage = await service.get_current_usage(service_name)

        return RateLimitUsageModel(
            service=usage.service,
            current_usage=usage.current_usage,
            limit=usage.limit,
            period=usage.period,
            remaining=usage.remaining,
            reset_at=usage.reset_at.isoformat() if usage.reset_at else None,
            utilization_percent=usage.utilization_percent,
            is_at_limit=usage.is_at_limit,
        )

    except Exception as e:
        logger.error(f"Error getting rate limit stats for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{service_name}", response_model=RateLimitHistoryResponse)
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def get_rate_limit_history(
    request: Request,
    response: Response,
    service_name: str,
    hours: int = Query(
        default=24,
        ge=1,
        le=168,
        description="Number of hours of history (max 168 = 7 days)",
    ),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📊 Get Rate Limit Usage History (Admin)

    Retrieve historical usage data for a specific service.

    **Admin Only**: Requires admin role

    **Path Parameters:**
    - `service_name`: Name of the service

    **Query Parameters:**
    - `hours`: Number of hours of history (default: 24, max: 168)

    **Returns:**
    - Historical usage data points with timestamps
    """
    try:
        await require_admin_user(current_user)

        service = get_rate_limit_service()
        history = await service.get_usage_history(service_name, hours=hours)

        return RateLimitHistoryResponse(
            service=service_name,
            history=[RateLimitHistoryModel(**h) for h in history],
            total_points=len(history),
        )

    except Exception as e:
        logger.error(f"Error getting rate limit history for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-users/{service_name}", response_model=TopUsersResponse)
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def get_top_users_by_rate_limit(
    request: Request,
    response: Response,
    service_name: str,
    limit: int = Query(default=10, ge=1, le=100, description="Number of top users to return"),
    current_user: dict = Depends(get_current_user),
):
    """
    ## 👥 Get Top Users by Rate Limit Usage (Admin)

    Retrieve the top users consuming rate limits for a specific service.

    **Admin Only**: Requires admin role

    **Path Parameters:**
    - `service_name`: Name of the service

    **Query Parameters:**
    - `limit`: Number of top users to return (default: 10, max: 100)

    **Returns:**
    - List of top users with their usage counts
    """
    try:
        await require_admin_user(current_user)

        service = get_rate_limit_service()
        users = await service.get_top_users(service_name, limit=limit)

        return TopUsersResponse(
            service=service_name,
            users=[TopUserModel(**u) for u in users],
            total=len(users),
        )

    except Exception as e:
        logger.error(f"Error getting top users for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/user/{user_id}", response_model=ResetResponse)
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def reset_rate_limits_for_user(
    request: Request,
    response: Response,
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔄 Reset Rate Limits for User (Admin)

    Reset all rate limits for a specific user, allowing them to make requests again.

    **Admin Only**: Requires admin role

    **Path Parameters:**
    - `user_id`: ID of the user to reset

    **Returns:**
    - Success/failure status
    """
    try:
        await require_admin_user(current_user)

        service = get_rate_limit_service()
        success = await service.reset_limits_for_user(user_id)

        if success:
            logger.info(
                f"Admin {current_user.get('username')} reset rate limits for user {user_id}"
            )
            return ResetResponse(success=True, message=f"Rate limits reset for user {user_id}")
        else:
            return ResetResponse(
                success=False,
                message="Failed to reset rate limits (Redis may be unavailable)",
            )

    except Exception as e:
        logger.error(f"Error resetting rate limits for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/ip/{ip_address:path}", response_model=ResetResponse)
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def reset_rate_limits_for_ip(
    request: Request,
    response: Response,
    ip_address: str,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 🔄 Reset Rate Limits for IP (Admin)

    Reset all rate limits for a specific IP address.

    **Admin Only**: Requires admin role

    **Path Parameters:**
    - `ip_address`: IP address to reset (can include dots)

    **Returns:**
    - Success/failure status
    """
    try:
        await require_admin_user(current_user)

        service = get_rate_limit_service()
        success = await service.reset_limits_for_ip(ip_address)

        if success:
            logger.info(
                f"Admin {current_user.get('username')} reset rate limits for IP {ip_address}"
            )
            return ResetResponse(success=True, message=f"Rate limits reset for IP {ip_address}")
        else:
            return ResetResponse(
                success=False,
                message="Failed to reset rate limits (Redis may be unavailable)",
            )

    except Exception as e:
        logger.error(f"Error resetting rate limits for IP {ip_address}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services", response_model=list[str])
@limiter.limit(RateLimitConfigMiddleware.ADMIN_OPERATIONS)
async def list_rate_limited_services(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
):
    """
    ## 📋 List Rate Limited Services (Admin)

    Get a list of all service names that have rate limits configured.

    **Admin Only**: Requires admin role

    **Returns:**
    - List of service names
    """
    try:
        await require_admin_user(current_user)

        from core.services.system import RateLimitService

        return [s.value for s in RateLimitService]

    except Exception as e:
        logger.error(f"Error listing rate limited services: {e}")
        raise HTTPException(status_code=500, detail=str(e))
