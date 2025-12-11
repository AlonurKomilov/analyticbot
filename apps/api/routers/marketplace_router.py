"""
🏪 Marketplace API Router
Endpoints for browsing, purchasing, and managing marketplace items.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from apps.api.middleware.auth import get_current_user_id
from apps.di import get_container
from infra.db.repositories.marketplace_repository import MarketplaceRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


# ==================== Dependencies ====================


async def get_db_pool():
    """Get database pool from DI container."""
    container = get_container()
    try:
        pool = await container.database.asyncpg_pool()
        return pool
    except Exception as e:
        logger.error(f"Failed to get database pool: {e}")
        raise HTTPException(status_code=500, detail="Database pool not available")


async def get_marketplace_repository(pool=Depends(get_db_pool)) -> MarketplaceRepository:
    """Get marketplace repository instance."""
    return MarketplaceRepository(pool)


# ==================== Models ====================


class ItemResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    category: str
    subcategory: str | None
    price_credits: int
    is_premium: bool
    is_featured: bool
    preview_url: str | None
    icon_url: str | None
    metadata: dict | None
    download_count: int
    rating: float
    rating_count: int


class PurchaseRequest(BaseModel):
    item_id: int


class ReviewRequest(BaseModel):
    item_id: int
    rating: int = Field(..., ge=1, le=5)
    review_text: str | None = None


class GiftRequest(BaseModel):
    recipient_username: str
    amount: int = Field(..., ge=1)
    message: str | None = None


class BundlePurchaseRequest(BaseModel):
    bundle_id: int


# ==================== Items Endpoints ====================


@router.get("/items")
async def get_marketplace_items(
    category: str | None = None,
    subcategory: str | None = None,
    is_featured: bool | None = None,
    is_premium: bool | None = None,
    search: str | None = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    repo: MarketplaceRepository = Depends(get_marketplace_repository),
):
    """Get marketplace items with optional filters."""
    items = await repo.get_items(
        category=category,
        subcategory=subcategory,
        is_featured=is_featured,
        is_premium=is_premium,
        search=search,
        limit=limit,
        offset=offset,
    )
    return {"items": items, "count": len(items)}


@router.get("/items/{slug}")
async def get_item_by_slug(
    slug: str, repo: MarketplaceRepository = Depends(get_marketplace_repository)
):
    """Get a single marketplace item by slug."""
    item = await repo.get_item_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/categories")
async def get_categories(repo: MarketplaceRepository = Depends(get_marketplace_repository)):
    """Get all marketplace categories with item counts."""
    categories = await repo.get_categories()
    return {"categories": categories}


# ==================== Purchase Endpoints ====================


@router.post("/purchase")
async def purchase_item(
    request: PurchaseRequest,
    user_id: int = Depends(get_current_user_id),
    repo: MarketplaceRepository = Depends(get_marketplace_repository),
):
    """Purchase a marketplace item using credits."""
    # Get item to verify price
    item = await repo.get_item_by_id(request.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    result = await repo.purchase_item(
        user_id=user_id, item_id=request.item_id, price=item["price_credits"]
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "success": True,
        "message": f"Successfully purchased {item['name']}",
        "purchase_id": result["purchase_id"],
        "credits_spent": result["credits_spent"],
    }


@router.get("/purchases")
async def get_my_purchases(
    user_id: int = Depends(get_current_user_id),
    repo: MarketplaceRepository = Depends(get_marketplace_repository),
):
    """Get current user's purchases."""
    purchases = await repo.get_user_purchases(user_id)
    return {"purchases": purchases}


@router.get("/purchases/check/{item_id}")
async def check_purchase(
    item_id: int,
    user_id: int = Depends(get_current_user_id),
    repo: MarketplaceRepository = Depends(get_marketplace_repository),
):
    """Check if the current user has purchased an item."""
    has_purchased = await repo.has_purchased(user_id, item_id)
    return {"item_id": item_id, "purchased": has_purchased}


# ==================== Reviews Endpoints ====================


@router.post("/reviews")
async def add_review(
    request: ReviewRequest,
    user_id: int = Depends(get_current_user_id),
    repo: MarketplaceRepository = Depends(get_marketplace_repository),
):
    """Add or update a review for a marketplace item."""
    result = await repo.add_review(
        user_id=user_id,
        item_id=request.item_id,
        rating=request.rating,
        review_text=request.review_text,
    )
    return {
        "success": True,
        "message": "Review submitted",
        "is_verified_purchase": result["is_verified"],
    }


@router.get("/reviews/{item_id}")
async def get_item_reviews(
    item_id: int,
    limit: int = Query(20, le=50),
    offset: int = 0,
    repo: MarketplaceRepository = Depends(get_marketplace_repository),
):
    """Get reviews for a marketplace item."""
    reviews = await repo.get_item_reviews(item_id, limit, offset)
    return {"reviews": reviews}


# ==================== Gift Endpoints ====================


@router.post("/gift")
async def send_gift(
    request: GiftRequest,
    user_id: int = Depends(get_current_user_id),
    repo: MarketplaceRepository = Depends(get_marketplace_repository),
):
    """Send credits as a gift to another user."""
    result = await repo.send_gift(
        sender_id=user_id,
        recipient_username=request.recipient_username,
        amount=request.amount,
        message=request.message,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "success": True,
        "message": f"Successfully sent {result['amount']} credits to @{result['recipient']}",
        "gift_id": result["gift_id"],
    }


@router.get("/gifts")
async def get_gift_history(
    direction: str = Query("all", pattern="^(all|sent|received)$"),
    user_id: int = Depends(get_current_user_id),
    repo: MarketplaceRepository = Depends(get_marketplace_repository),
):
    """Get gift history for current user."""
    gifts = await repo.get_gift_history(user_id, direction)
    return {"gifts": gifts}


# ==================== Bundle Endpoints ====================


@router.get("/bundles")
async def get_bundles(
    featured_only: bool = False, repo: MarketplaceRepository = Depends(get_marketplace_repository)
):
    """Get available service bundles."""
    bundles = await repo.get_bundles(featured_only)
    return {"bundles": bundles}


@router.get("/bundles/{bundle_id}")
async def get_bundle_details(
    bundle_id: int, repo: MarketplaceRepository = Depends(get_marketplace_repository)
):
    """Get details of a specific bundle including its items."""
    bundles = await repo.get_bundles()
    bundle = next((b for b in bundles if b["id"] == bundle_id), None)

    if not bundle:
        raise HTTPException(status_code=404, detail="Bundle not found")

    items = await repo.get_bundle_items(bundle_id)
    return {**bundle, "items": items}


@router.post("/bundles/purchase")
async def purchase_bundle(
    request: BundlePurchaseRequest,
    user_id: int = Depends(get_current_user_id),
    repo: MarketplaceRepository = Depends(get_marketplace_repository),
):
    """Purchase a service bundle."""
    result = await repo.purchase_bundle(user_id, request.bundle_id)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return {
        "success": True,
        "message": f"Successfully purchased {result['bundle_name']}",
        "user_bundle_id": result["user_bundle_id"],
        "expires_at": result["expires_at"],
        "credits_spent": result["credits_spent"],
    }


@router.get("/bundles/my")
async def get_my_bundles(
    user_id: int = Depends(get_current_user_id),
    repo: MarketplaceRepository = Depends(get_marketplace_repository),
):
    """Get current user's purchased bundles."""
    bundles = await repo.get_user_bundles(user_id)
    return {"bundles": bundles}
