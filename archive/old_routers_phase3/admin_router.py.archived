"""
Admin Microrouter - Administrative Operations

This microrouter handles ONLY administrative operations and system management.
Domain: Admin channel management, user management, system statistics, and administrative controls.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from apps.bot.container import container
from apps.bot.services.channel_management_service import ChannelManagementService
from apps.bot.services.analytics_service import AnalyticsService
from apps.api.middleware.auth import (
    get_current_user, 
    require_admin_role,
    get_current_user_id,
)
from apps.bot.database.performance import performance_timer

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/admin", tags=["Administration"], responses={404: {"description": "Not found"}}
)

# === ADMIN MODELS ===

class AdminChannelInfo(BaseModel):
    id: int
    name: str
    username: str | None = None
    owner_id: int
    owner_username: str | None = None
    subscriber_count: int = 0
    is_active: bool = True
    created_at: datetime
    last_activity: datetime | None = None
    total_posts: int = 0
    total_views: int = 0

class SystemStats(BaseModel):
    total_users: int
    total_channels: int
    total_posts: int
    total_views: int
    active_channels: int
    system_health: str
    uptime: str
    memory_usage: float
    cpu_usage: float
    disk_usage: float

class UserChannelInfo(BaseModel):
    user_id: int
    username: str | None = None
    channels: list[dict]
    total_channels: int
    active_channels: int
    last_activity: datetime | None = None

# === ADMIN ENDPOINTS ===

@router.get("/channels", response_model=list[AdminChannelInfo])
async def get_all_channels(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    status: str | None = Query(None, regex="^(active|inactive|all)$"),
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: container.channel_service()),
    analytics_service: AnalyticsService = Depends(lambda: container.analytics_service())
):
    """
    ## 👑 Get All Channels (Admin)
    
    Retrieve all channels in the system with administrative details.
    
    **Admin Only** - Requires admin role.
    
    **Parameters:**
    - page: Page number for pagination
    - limit: Number of channels per page (1-500)
    - status: Filter by channel status (active, inactive, all)
    
    **Returns:**
    - List of all channels with owner and statistics information
    """
    try:
        # Verify admin access
        await require_admin_role(current_user["id"])
        
        with performance_timer("admin_all_channels_fetch"):
            # Calculate offset for pagination
            offset = (page - 1) * limit
            
            channels = await channel_service.get_all_channels_admin(
                offset=offset,
                limit=limit,
                status_filter=status
            )
            
            # Enrich with analytics data
            enriched_channels = []
            for channel in channels:
                # Get additional analytics stats
                stats = await analytics_service.get_channel_summary_stats(channel["id"])
                
                enriched_channels.append(AdminChannelInfo(
                    id=channel["id"],
                    name=channel["name"],
                    username=channel.get("username"),
                    owner_id=channel["owner_id"],
                    owner_username=channel.get("owner_username"),
                    subscriber_count=channel.get("subscriber_count", 0),
                    is_active=channel.get("is_active", True),
                    created_at=channel.get("created_at", datetime.now()),
                    last_activity=channel.get("last_activity"),
                    total_posts=stats.get("total_posts", 0),
                    total_views=stats.get("total_views", 0)
                ))
            
            return enriched_channels
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin channels fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin channels")

@router.get("/users/{user_id}/channels", response_model=UserChannelInfo)
async def get_user_channels_admin(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: container.channel_service())
):
    """
    ## 👤 Get User Channels (Admin)
    
    Retrieve all channels owned by a specific user.
    
    **Admin Only** - Requires admin role.
    
    **Parameters:**
    - user_id: Target user ID
    
    **Returns:**
    - User's channel information and statistics
    """
    try:
        # Verify admin access
        await require_admin_role(current_user["id"])
        
        with performance_timer("admin_user_channels_fetch"):
            user_channels = await channel_service.get_user_channels_admin(user_id)
            
            if not user_channels:
                raise HTTPException(status_code=404, detail="User not found or has no channels")
            
            channels = user_channels.get("channels", [])
            active_channels = [ch for ch in channels if ch.get("is_active", True)]
            
            return UserChannelInfo(
                user_id=user_id,
                username=user_channels.get("username"),
                channels=channels,
                total_channels=len(channels),
                active_channels=len(active_channels),
                last_activity=user_channels.get("last_activity")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin user channels fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user channels")

@router.delete("/channels/{channel_id}")
async def delete_channel_admin(
    channel_id: int,
    reason: str = Query(..., min_length=10, max_length=500),
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: container.channel_service())
):
    """
    ## 🗑️ Delete Channel (Admin)
    
    Administratively delete a channel with reason logging.
    
    **Admin Only** - Requires admin role.
    
    **Parameters:**
    - channel_id: Target channel ID
    - reason: Reason for deletion (required, 10-500 characters)
    
    **Returns:**
    - Deletion confirmation with audit trail
    """
    try:
        # Verify admin access
        await require_admin_role(current_user["id"])
        
        with performance_timer("admin_channel_deletion"):
            # Get channel info before deletion for audit
            channel_info = await channel_service.get_channel_admin(channel_id)
            
            if not channel_info:
                raise HTTPException(status_code=404, detail="Channel not found")
            
            # Perform admin deletion with audit logging
            result = await channel_service.delete_channel_admin(
                channel_id=channel_id,
                admin_user_id=current_user["id"],
                reason=reason
            )
            
            if not result:
                raise HTTPException(status_code=500, detail="Failed to delete channel")
            
            # Log admin action
            logger.warning(
                f"ADMIN ACTION: Channel {channel_id} ({channel_info['name']}) "
                f"deleted by admin {current_user['id']} - Reason: {reason}"
            )
            
            return {
                "message": "Channel deleted successfully",
                "channel_id": channel_id,
                "channel_name": channel_info["name"],
                "owner_id": channel_info["owner_id"],
                "deleted_by": current_user["id"],
                "reason": reason,
                "deleted_at": datetime.now().isoformat(),
                "audit_logged": True
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin channel deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete channel")

@router.get("/stats/system", response_model=SystemStats)
async def get_system_stats(
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: container.channel_service()),
    analytics_service: AnalyticsService = Depends(lambda: container.analytics_service())
):
    """
    ## 📊 Get System Statistics (Admin)
    
    Retrieve comprehensive system statistics and health information.
    
    **Admin Only** - Requires admin role.
    
    **Returns:**
    - System-wide statistics, performance metrics, and health status
    """
    try:
        # Verify admin access
        await require_admin_role(current_user["id"])
        
        with performance_timer("admin_system_stats"):
            # Get system statistics
            system_stats = await analytics_service.get_system_statistics()
            
            # Get performance metrics
            performance_stats = await analytics_service.get_performance_metrics()
            
            return SystemStats(
                total_users=system_stats.get("total_users", 0),
                total_channels=system_stats.get("total_channels", 0),
                total_posts=system_stats.get("total_posts", 0),
                total_views=system_stats.get("total_views", 0),
                active_channels=system_stats.get("active_channels", 0),
                system_health=performance_stats.get("health_status", "unknown"),
                uptime=performance_stats.get("uptime", "unknown"),
                memory_usage=performance_stats.get("memory_usage_percent", 0.0),
                cpu_usage=performance_stats.get("cpu_usage_percent", 0.0),
                disk_usage=performance_stats.get("disk_usage_percent", 0.0)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin system stats failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system statistics")

@router.post("/channels/{channel_id}/suspend")
async def suspend_channel(
    channel_id: int,
    reason: str = Query(..., min_length=10, max_length=500),
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: container.channel_service())
):
    """
    ## ⏸️ Suspend Channel (Admin)
    
    Administratively suspend a channel with reason logging.
    
    **Admin Only** - Requires admin role.
    
    **Parameters:**
    - channel_id: Target channel ID
    - reason: Reason for suspension (required, 10-500 characters)
    
    **Returns:**
    - Suspension confirmation with audit trail
    """
    try:
        # Verify admin access
        await require_admin_role(current_user["id"])
        
        with performance_timer("admin_channel_suspension"):
            result = await channel_service.suspend_channel_admin(
                channel_id=channel_id,
                admin_user_id=current_user["id"],
                reason=reason
            )
            
            if not result:
                raise HTTPException(status_code=404, detail="Channel not found")
            
            # Log admin action
            logger.warning(
                f"ADMIN ACTION: Channel {channel_id} suspended by admin {current_user['id']} - Reason: {reason}"
            )
            
            return {
                "message": "Channel suspended successfully",
                "channel_id": channel_id,
                "suspended_by": current_user["id"],
                "reason": reason,
                "suspended_at": datetime.now().isoformat(),
                "status": "suspended",
                "audit_logged": True
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin channel suspension failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to suspend channel")

@router.post("/channels/{channel_id}/unsuspend")
async def unsuspend_channel(
    channel_id: int,
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: container.channel_service())
):
    """
    ## ▶️ Unsuspend Channel (Admin)
    
    Administratively unsuspend a previously suspended channel.
    
    **Admin Only** - Requires admin role.
    
    **Parameters:**
    - channel_id: Target channel ID
    
    **Returns:**
    - Unsuspension confirmation with audit trail
    """
    try:
        # Verify admin access
        await require_admin_role(current_user["id"])
        
        with performance_timer("admin_channel_unsuspension"):
            result = await channel_service.unsuspend_channel_admin(
                channel_id=channel_id,
                admin_user_id=current_user["id"]
            )
            
            if not result:
                raise HTTPException(status_code=404, detail="Channel not found or not suspended")
            
            # Log admin action
            logger.info(
                f"ADMIN ACTION: Channel {channel_id} unsuspended by admin {current_user['id']}"
            )
            
            return {
                "message": "Channel unsuspended successfully",
                "channel_id": channel_id,
                "unsuspended_by": current_user["id"],
                "unsuspended_at": datetime.now().isoformat(),
                "status": "active",
                "audit_logged": True
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin channel unsuspension failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to unsuspend channel")

@router.get("/audit/recent")
async def get_recent_admin_actions(
    limit: int = Query(50, ge=1, le=200),
    action_type: str | None = Query(None, regex="^(delete|suspend|unsuspend|create|update)$"),
    current_user: dict = Depends(get_current_user),
    channel_service: ChannelManagementService = Depends(lambda: container.channel_service())
):
    """
    ## 📋 Get Recent Admin Actions
    
    Retrieve recent administrative actions for audit purposes.
    
    **Admin Only** - Requires admin role.
    
    **Parameters:**
    - limit: Number of actions to retrieve (1-200)
    - action_type: Filter by action type (optional)
    
    **Returns:**
    - List of recent admin actions with details
    """
    try:
        # Verify admin access
        await require_admin_role(current_user["id"])
        
        with performance_timer("admin_audit_fetch"):
            audit_logs = await channel_service.get_admin_audit_logs(
                limit=limit,
                action_filter=action_type
            )
            
            return {
                "total_actions": len(audit_logs),
                "limit": limit,
                "filter": action_type,
                "actions": audit_logs,
                "fetched_at": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin audit fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch admin audit logs")