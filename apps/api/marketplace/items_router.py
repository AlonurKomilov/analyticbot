"""
Marketplace Items Router
========================

API endpoints for marketplace items (one-time purchases):
- Browse items (themes, widgets, AI models)
- Purchase items
- Reviews and ratings
- Bundles
- Gift credits
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from apps.api.dependencies import CurrentUser
from apps.api.marketplace.schemas import (
    MarketplaceItemResponse,
    ItemPurchaseRequest,
    ItemPurchaseResponse,
    ItemReviewRequest,
    ItemReviewResponse,
    GiftCreditsRequest,
    GiftResponse,
    BundleResponse,
    BundlePurchaseRequest,
    BundlePurchaseResponse,
)
from apps.api.marketplace.dependencies import MarketplaceItemRepoDep

router = APIRouter(tags=["marketplace-items"])


# =============================================================================
# BROWSE ITEMS
# =============================================================================

@router.get("/items", response_model=list[MarketplaceItemResponse])
async def get_items(
    repo: MarketplaceItemRepoDep,
    current_user: CurrentUser,
    category: Optional[str] = Query(None, description="Filter by category"),
    subcategory: Optional[str] = Query(None, description="Filter by subcategory"),
    is_featured: Optional[bool] = Query(None, description="Filter featured items"),
    search: Optional[str] = Query(None, description="Search term"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
):
    """Get marketplace items with optional filtering."""
    items = await repo.get_items(
        category=category,
        subcategory=subcategory,
        is_featured=is_featured,
        search=search,
        limit=limit,
        offset=offset,
    )
    
    # Mark user-owned items
    if current_user:
        user_purchases = await repo.get_user_purchases(current_user.id)
        owned_ids = {p["item_id"] for p in user_purchases}
        for item in items:
            item["user_owned"] = item["id"] in owned_ids
    
    return items


@router.get("/items/{slug}", response_model=MarketplaceItemResponse)
async def get_item_by_slug(
    slug: str,
    repo: MarketplaceItemRepoDep,
    current_user: CurrentUser,
):
    """Get a single marketplace item by slug."""
    item = await repo.get_item_by_slug(slug)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check if user owns this item
    if current_user:
        item["user_owned"] = await repo.has_purchased(current_user.id, item["id"])
    
    return item


@router.get("/categories")
async def get_categories(repo: MarketplaceItemRepoDep):
    """Get all item categories with counts."""
    return await repo.get_categories()


# =============================================================================
# PURCHASES
# =============================================================================

@router.post("/items/purchase", response_model=ItemPurchaseResponse)
async def purchase_item(
    request: ItemPurchaseRequest,
    repo: MarketplaceItemRepoDep,
    current_user: CurrentUser,
):
    """Purchase a marketplace item."""
    # Get item details
    item = await repo.get_item_by_id(request.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Attempt purchase
    result = await repo.purchase_item(
        user_id=current_user.id,
        item_id=request.item_id,
        price=item["price_credits"],
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/purchases")
async def get_user_purchases(
    repo: MarketplaceItemRepoDep,
    current_user: CurrentUser,
):
    """Get user's purchased items."""
    return await repo.get_user_purchases(current_user.id)


# =============================================================================
# REVIEWS
# =============================================================================

@router.post("/items/review")
async def add_review(
    request: ItemReviewRequest,
    repo: MarketplaceItemRepoDep,
    current_user: CurrentUser,
):
    """Add or update a review for an item."""
    result = await repo.add_review(
        user_id=current_user.id,
        item_id=request.item_id,
        rating=request.rating,
        review_text=request.review_text,
    )
    return result


@router.get("/items/{item_id}/reviews", response_model=list[ItemReviewResponse])
async def get_item_reviews(
    item_id: int,
    repo: MarketplaceItemRepoDep,
    limit: int = Query(20, le=50),
    offset: int = Query(0, ge=0),
):
    """Get reviews for an item."""
    return await repo.get_item_reviews(item_id, limit=limit, offset=offset)


# =============================================================================
# BUNDLES
# =============================================================================

@router.get("/bundles", response_model=list[BundleResponse])
async def get_bundles(
    repo: MarketplaceItemRepoDep,
    featured_only: bool = Query(False),
):
    """Get available bundles."""
    bundles = await repo.get_bundles(featured_only=featured_only)
    
    # Add bundle items
    for bundle in bundles:
        bundle["items"] = await repo.get_bundle_items(bundle["id"])
    
    return bundles


@router.post("/bundles/purchase", response_model=BundlePurchaseResponse)
async def purchase_bundle(
    request: BundlePurchaseRequest,
    repo: MarketplaceItemRepoDep,
    current_user: CurrentUser,
):
    """Purchase a service bundle."""
    result = await repo.purchase_bundle(
        user_id=current_user.id,
        bundle_id=request.bundle_id,
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/bundles/my")
async def get_user_bundles(
    repo: MarketplaceItemRepoDep,
    current_user: CurrentUser,
):
    """Get user's purchased bundles."""
    return await repo.get_user_bundles(current_user.id)


# =============================================================================
# GIFTING
# =============================================================================

@router.post("/gift", response_model=GiftResponse)
async def send_gift(
    request: GiftCreditsRequest,
    repo: MarketplaceItemRepoDep,
    current_user: CurrentUser,
):
    """Send credits as a gift to another user."""
    result = await repo.send_gift(
        sender_id=current_user.id,
        recipient_username=request.recipient_username,
        amount=request.amount,
        message=request.message,
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/gifts")
async def get_gift_history(
    repo: MarketplaceItemRepoDep,
    current_user: CurrentUser,
    direction: str = Query("all", pattern="^(all|sent|received)$"),
):
    """Get gift history."""
    return await repo.get_gift_history(current_user.id, direction=direction)
