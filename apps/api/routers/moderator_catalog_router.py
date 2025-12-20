"""
Moderator Catalog Router - Channel Catalog Management

Provides moderator-only endpoints for managing the public channel catalog.
Moderators can add, update, feature, and remove channels.

Domain: Public catalog management
Path: /moderator/catalog/*
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.middleware.auth import require_moderator_user
from apps.di import get_db_session
from config import settings
from core.services.system.cache.public_catalog_service import PublicCatalogService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/moderator/catalog",
    tags=["Moderator - Catalog Management"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# Request/Response Models
# ============================================================================


class AddChannelRequest(BaseModel):
    """Request to add a channel to the catalog."""

    telegram_id: int | None = None
    username: str | None = None
    category_id: int
    country_code: str | None = Field(default=None, max_length=2)
    language_code: str | None = Field(default=None, max_length=5)
    is_featured: bool = False


class UpdateChannelRequest(BaseModel):
    """Request to update a channel in the catalog."""

    category_id: int | None = None
    country_code: str | None = Field(default=None, max_length=2)
    language_code: str | None = Field(default=None, max_length=5)
    is_featured: bool | None = None
    is_verified: bool | None = None
    is_active: bool | None = None


class CatalogEntryResponse(BaseModel):
    """Catalog entry response."""

    id: int
    telegram_id: int
    username: str | None
    title: str
    description: str | None
    avatar_url: str | None
    category_id: int | None
    category_name: str | None = None
    country_code: str | None
    language_code: str | None
    is_featured: bool
    is_verified: bool
    is_active: bool
    added_by: int | None
    added_at: datetime
    last_synced_at: datetime | None
    subscriber_count: int | None = None


class CatalogListResponse(BaseModel):
    """Paginated list of catalog entries."""

    entries: list[CatalogEntryResponse]
    total: int
    page: int
    per_page: int


class CategoryRequest(BaseModel):
    """Request to create/update a category."""

    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=50)
    icon: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=20)
    parent_id: int | None = None
    sort_order: int = 0


# ============================================================================
# Helper Functions
# ============================================================================


def get_catalog_service(db: AsyncSession) -> PublicCatalogService:
    """Create a PublicCatalogService instance."""
    bot_token = getattr(settings, "BOT_TOKEN", None) or getattr(
        settings, "TELEGRAM_BOT_TOKEN", None
    )
    # Handle SecretStr by unwrapping it
    if bot_token is not None and hasattr(bot_token, "get_secret_value"):
        bot_token = bot_token.get_secret_value()
    return PublicCatalogService(db_session=db, bot_token=bot_token)


# ============================================================================
# Catalog Management Endpoints
# ============================================================================


@router.get("", response_model=CatalogListResponse)
async def list_catalog_entries(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    category_id: int | None = None,
    is_featured: bool | None = None,
    is_active: bool | None = True,
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    List all catalog entries with filters.

    Requires moderator role.
    """
    try:
        # Build WHERE clause
        where_clauses = []
        params: dict[str, Any] = {}

        if category_id is not None:
            where_clauses.append("pcc.category_id = :category_id")
            params["category_id"] = category_id
        if is_featured is not None:
            where_clauses.append("pcc.is_featured = :is_featured")
            params["is_featured"] = is_featured
        if is_active is not None:
            where_clauses.append("pcc.is_active = :is_active")
            params["is_active"] = is_active

        where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"

        # Get total count
        count_result = await db.execute(
            text(f"SELECT COUNT(*) FROM public_channel_catalog pcc WHERE {where_sql}"),
            params,
        )
        total = count_result.scalar() or 0

        # Get entries with pagination
        offset = (page - 1) * per_page
        params["limit"] = per_page
        params["offset"] = offset

        result = await db.execute(
            text(
                f"""
                SELECT 
                    pcc.id, pcc.telegram_id, pcc.username, pcc.title, pcc.description,
                    pcc.avatar_url, pcc.category_id, pcc.country_code, pcc.language_code,
                    pcc.is_featured, pcc.is_verified, pcc.is_active, pcc.added_by,
                    pcc.added_at, pcc.last_synced_at,
                    csc.subscriber_count,
                    cc.name as category_name
                FROM public_channel_catalog pcc
                LEFT JOIN channel_stats_cache csc ON pcc.telegram_id = csc.telegram_id
                LEFT JOIN channel_categories cc ON pcc.category_id = cc.id
                WHERE {where_sql}
                ORDER BY pcc.added_at DESC
                LIMIT :limit OFFSET :offset
            """
            ),
            params,
        )
        rows = result.fetchall()

        entries = [
            CatalogEntryResponse(
                id=row.id,
                telegram_id=row.telegram_id,
                username=row.username,
                title=row.title,
                description=row.description,
                avatar_url=row.avatar_url,
                category_id=row.category_id,
                category_name=row.category_name,
                country_code=row.country_code,
                language_code=row.language_code,
                is_featured=row.is_featured,
                is_verified=row.is_verified,
                is_active=row.is_active,
                added_by=row.added_by,
                added_at=row.added_at,
                last_synced_at=row.last_synced_at,
                subscriber_count=row.subscriber_count,
            )
            for row in rows
        ]

        return CatalogListResponse(
            entries=entries,
            total=total,
            page=page,
            per_page=per_page,
        )
    except Exception as e:
        logger.error(f"Error listing catalog entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to list catalog entries")


@router.get("/stats")
async def get_catalog_stats(
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    Get catalog statistics for moderator dashboard.

    Requires moderator role.
    """
    try:
        result = await db.execute(
            text(
                """
                SELECT 
                    COUNT(*) as total_channels,
                    COUNT(*) FILTER (WHERE is_featured = true) as featured_channels,
                    COUNT(*) FILTER (WHERE is_verified = true) as verified_channels,
                    COUNT(*) FILTER (WHERE is_active = true) as active_channels,
                    COUNT(*) FILTER (WHERE is_active = false) as inactive_channels
                FROM public_channel_catalog
            """
            )
        )
        row = result.fetchone()

        cat_result = await db.execute(text("SELECT COUNT(*) FROM channel_categories"))
        total_categories = cat_result.scalar() or 0

        return {
            "total_channels": row.total_channels if row else 0,
            "featured_channels": row.featured_channels if row else 0,
            "verified_channels": row.verified_channels if row else 0,
            "active_channels": row.active_channels if row else 0,
            "inactive_channels": row.inactive_channels if row else 0,
            "total_categories": total_categories,
        }
    except Exception as e:
        logger.error(f"Error getting catalog stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get catalog stats")


@router.post("/add")
async def add_channel_to_catalog(
    request: AddChannelRequest,
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    Add a channel to the public catalog.

    Provide either telegram_id or username. If username is provided,
    it will be resolved via Telegram API.

    Requires moderator role.
    """
    if not request.telegram_id and not request.username:
        raise HTTPException(status_code=400, detail="Either telegram_id or username is required")

    service = get_catalog_service(db)
    result = await service.add_channel_to_catalog(
        telegram_id=request.telegram_id,
        username=request.username,
        category_id=request.category_id,
        country_code=request.country_code,
        language_code=request.language_code,
        added_by=user.get("id"),
        is_featured=request.is_featured,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to add channel"))

    return result


@router.put("/{catalog_id}")
async def update_catalog_entry(
    catalog_id: int,
    request: UpdateChannelRequest,
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    Update a channel in the catalog.

    Requires moderator role.
    """
    service = get_catalog_service(db)
    result = await service.update_channel(
        catalog_id=catalog_id,
        category_id=request.category_id,
        country_code=request.country_code,
        language_code=request.language_code,
        is_featured=request.is_featured,
        is_verified=request.is_verified,
        is_active=request.is_active,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to update channel"))

    return result


@router.delete("/{catalog_id}")
async def remove_catalog_entry(
    catalog_id: int,
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    Remove a channel from the catalog (soft delete).

    Requires moderator role.
    """
    service = get_catalog_service(db)
    result = await service.remove_channel(catalog_id)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to remove channel"))

    return result


@router.post("/{catalog_id}/feature")
async def toggle_featured(
    catalog_id: int,
    featured: bool = True,
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    Toggle featured status for a channel.

    Requires moderator role.
    """
    service = get_catalog_service(db)
    result = await service.update_channel(catalog_id=catalog_id, is_featured=featured)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to update"))

    return {"success": True, "catalog_id": catalog_id, "is_featured": featured}


@router.post("/{catalog_id}/verify")
async def toggle_verified(
    catalog_id: int,
    verified: bool = True,
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    Toggle verified status for a channel.

    Requires moderator role.
    """
    service = get_catalog_service(db)
    result = await service.update_channel(catalog_id=catalog_id, is_verified=verified)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to update"))

    return {"success": True, "catalog_id": catalog_id, "is_verified": verified}


@router.post("/{catalog_id}/sync")
async def sync_channel_stats(
    catalog_id: int,
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    Sync channel stats from Telegram API.

    Requires moderator role.
    """
    # Get telegram_id from catalog
    result = await db.execute(
        text("SELECT telegram_id FROM public_channel_catalog WHERE id = :id"),
        {"id": catalog_id},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Channel not found in catalog")

    service = get_catalog_service(db)
    sync_result = await service.sync_channel_stats(row.telegram_id)

    if not sync_result.get("success"):
        raise HTTPException(status_code=400, detail=sync_result.get("error", "Failed to sync"))

    return sync_result


# ============================================================================
# Category Management Endpoints
# ============================================================================


@router.get("/categories")
async def list_categories(
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    List all categories for management.

    Requires moderator role.
    """
    try:
        result = await db.execute(
            text(
                """
                SELECT id, name, slug, icon, color, parent_id, sort_order, channel_count,
                       created_at, updated_at
                FROM channel_categories
                ORDER BY sort_order, name
            """
            )
        )
        rows = result.fetchall()

        return {
            "categories": [
                {
                    "id": row.id,
                    "name": row.name,
                    "slug": row.slug,
                    "icon": row.icon,
                    "color": row.color,
                    "parent_id": row.parent_id,
                    "sort_order": row.sort_order,
                    "channel_count": row.channel_count,
                    "created_at": (row.created_at.isoformat() if row.created_at else None),
                    "updated_at": (row.updated_at.isoformat() if row.updated_at else None),
                }
                for row in rows
            ]
        }
    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to list categories")


@router.post("/categories")
async def create_category(
    request: CategoryRequest,
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    Create a new category.

    Requires moderator role.
    """
    try:
        result = await db.execute(
            text(
                """
                INSERT INTO channel_categories (name, slug, icon, color, parent_id, sort_order)
                VALUES (:name, :slug, :icon, :color, :parent_id, :sort_order)
                RETURNING id
            """
            ),
            {
                "name": request.name,
                "slug": request.slug,
                "icon": request.icon,
                "color": request.color,
                "parent_id": request.parent_id,
                "sort_order": request.sort_order,
            },
        )
        row = result.fetchone()
        await db.commit()

        return {"success": True, "category_id": row[0] if row else None}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating category: {e}")
        if "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="Category slug already exists")
        raise HTTPException(status_code=500, detail="Failed to create category")


@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    request: CategoryRequest,
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    Update a category.

    Requires moderator role.
    """
    try:
        await db.execute(
            text(
                """
                UPDATE channel_categories
                SET name = :name, slug = :slug, icon = :icon, color = :color,
                    parent_id = :parent_id, sort_order = :sort_order, updated_at = NOW()
                WHERE id = :id
            """
            ),
            {
                "id": category_id,
                "name": request.name,
                "slug": request.slug,
                "icon": request.icon,
                "color": request.color,
                "parent_id": request.parent_id,
                "sort_order": request.sort_order,
            },
        )
        await db.commit()

        return {"success": True, "category_id": category_id}
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating category: {e}")
        raise HTTPException(status_code=500, detail="Failed to update category")


# ============================================================================
# Lookup/Search Endpoints
# ============================================================================


@router.get("/lookup")
async def lookup_channel(
    username: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db_session),
    user: dict = Depends(require_moderator_user),
):
    """
    Look up a channel from Telegram API before adding to catalog.

    This allows moderators to preview channel info before adding.

    Requires moderator role.
    """
    service = get_catalog_service(db)
    result = await service.fetch_channel_from_telegram(username)

    if not result:
        raise HTTPException(status_code=404, detail=f"Channel @{username} not found on Telegram")

    # Check if already in catalog
    existing = await db.execute(
        text("SELECT id, is_active FROM public_channel_catalog WHERE telegram_id = :tid"),
        {"tid": result["telegram_id"]},
    )
    row = existing.fetchone()
    result["in_catalog"] = row is not None
    result["catalog_id"] = row.id if row else None
    result["catalog_active"] = row.is_active if row else None

    return result
