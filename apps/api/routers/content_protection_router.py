"""
Content Protection API Endpoints
FastAPI routes for Phase 3.3: Content Protection with Clean Architecture
Uses Protocol-based services from Phase 3.3 refactoring
"""

import logging
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from apps.api.middleware.auth import get_current_user
from apps.bot.models.content_protection import (
    ContentProtectionResponse as APIContentProtectionResponse,
)
from apps.bot.models.content_protection import (
    CustomEmojiRequest,
    CustomEmojiResponse,
    PremiumFeatureLimits,
    ProtectionLevel,
    UserTier,
)
from apps.bot.services.premium_emoji_service import PremiumEmojiService

# ✅ Phase 3.3: Use DI container to get services
from apps.di import get_content_protection_service
from core.services.bot.content.content_protection_service import (
    ContentProtectionService,
)

logger = logging.getLogger(__name__)

# ✅ Phase 3.3: Use new domain models
from core.services.bot.content.models import (
    ContentProtectionRequest,
    WatermarkConfig,
    WatermarkPosition,
)

router = APIRouter(prefix="/content", tags=["Content Protection"])


@router.post("/watermark/image", response_model=APIContentProtectionResponse)
async def add_image_watermark(
    file: UploadFile = File(...),
    watermark_text: str = Form(...),
    position: str = Form("bottom-right"),
    opacity: float = Form(0.7),
    font_size: int = Form(24),
    color: str = Form("white"),
    add_shadow: bool = Form(True),
    current_user: dict = Depends(get_current_user),
    content_protection: ContentProtectionService = Depends(get_content_protection_service),
):
    """Add watermark to uploaded image (Phase 3.3 API)"""

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    # Validate filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Check user premium status and limits
    user_tier = await _get_user_tier(current_user["id"])
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)

    if file.size and file.size > limits.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds limit for {user_tier.value} tier: {limits.max_file_size_mb}MB",
        )

    # Check monthly usage limits
    await _check_feature_usage("watermarks", current_user["id"], user_tier)

    # Initialize tmp_path to None for cleanup safety
    tmp_path: Path | None = None

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(file.filename).suffix
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        # Map position string to enum
        try:
            watermark_position = WatermarkPosition(position)
        except ValueError:
            watermark_position = WatermarkPosition.BOTTOM_RIGHT

        # Create watermark config using Phase 3.3 domain model
        watermark_config = WatermarkConfig(
            text=watermark_text,
            position=watermark_position,
            opacity=opacity,
            font_size=font_size,
            color=color,
            shadow=add_shadow,
        )

        # Create protection request
        protection_request = ContentProtectionRequest(
            content_type="image",
            file_path=str(tmp_path),
            watermark_config=watermark_config,
            user_id=current_user["id"],
        )

        # Apply watermark using Phase 3.3 service
        protection_response = await content_protection.protect_content(protection_request)

        # Update usage tracking
        await _increment_feature_usage("watermarks", current_user["id"])

        # Convert domain response to API response
        if (
            protection_response.watermark_result
            and protection_response.watermark_result.output_path
        ):
            watermarked_path = Path(protection_response.watermark_result.output_path)
            return APIContentProtectionResponse(
                protection_id=f"img_{watermarked_path.stem}",
                protected=True,
                protection_level=(
                    ProtectionLevel.PREMIUM if user_tier != UserTier.FREE else ProtectionLevel.BASIC
                ),
                watermarked_file_url=f"/api/content-protection/files/{watermarked_path.name}",
                processing_time_ms=int(protection_response.total_processing_time_ms),
                timestamp=datetime.utcnow(),
            )
        else:
            error_msg = protection_response.error or "Watermarking failed"
            raise HTTPException(status_code=500, detail=error_msg)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Watermarking failed: {str(e)}")
    finally:
        # Cleanup temporary input file
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


@router.post("/watermark/video", response_model=APIContentProtectionResponse)
async def add_video_watermark(
    file: UploadFile = File(...),
    watermark_text: str = Form(...),
    position: str = Form("bottom-right"),
    opacity: float = Form(0.7),
    font_size: int = Form(24),
    current_user: dict = Depends(get_current_user),
    content_protection: ContentProtectionService = Depends(get_content_protection_service),
):
    """Add watermark to uploaded video (Phase 3.3 API, requires FFmpeg)"""

    # Validate file type
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video files are supported")

    # Check user premium status and limits
    user_tier = await _get_user_tier(current_user["id"])
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)

    if user_tier == UserTier.FREE:
        raise HTTPException(
            status_code=403, detail="Video watermarking requires premium subscription"
        )

    if file.size and file.size > limits.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds limit for {user_tier.value} tier: {limits.max_file_size_mb}MB",
        )

    # Check monthly usage limits
    await _check_feature_usage("watermarks", current_user["id"], user_tier)

    # Initialize tmp_path to None for cleanup safety
    tmp_path: Path | None = None

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        # Map position string to enum
        try:
            watermark_position = WatermarkPosition(position)
        except ValueError:
            watermark_position = WatermarkPosition.BOTTOM_RIGHT

        # Create watermark config using Phase 3.3 domain model
        watermark_config = WatermarkConfig(
            text=watermark_text,
            position=watermark_position,
            opacity=opacity,
            font_size=font_size,
        )

        # Create protection request
        protection_request = ContentProtectionRequest(
            content_type="video",
            file_path=str(tmp_path),
            watermark_config=watermark_config,
            user_id=current_user["id"],
        )

        # Apply watermark using Phase 3.3 service
        protection_response = await content_protection.protect_content(protection_request)

        # Update usage tracking
        await _increment_feature_usage("watermarks", current_user["id"])

        # Convert domain response to API response
        if (
            protection_response.watermark_result
            and protection_response.watermark_result.output_path
        ):
            watermarked_path = Path(protection_response.watermark_result.output_path)
            return APIContentProtectionResponse(
                protection_id=f"vid_{watermarked_path.stem}",
                protected=True,
                protection_level=ProtectionLevel.PREMIUM,
                watermarked_file_url=f"/api/v1/content-protection/files/{watermarked_path.name}",
                processing_time_ms=int(protection_response.total_processing_time_ms),
                timestamp=datetime.utcnow(),
            )
        else:
            error_msg = protection_response.error or "Video watermarking failed"
            raise HTTPException(status_code=500, detail=error_msg)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video watermarking failed: {str(e)}")
    finally:
        # Cleanup temporary input file
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


@router.post("/custom-emoji", response_model=CustomEmojiResponse)
async def format_custom_emoji_message(
    request: CustomEmojiRequest, current_user: dict = Depends(get_current_user)
):
    """Format message with custom emojis for premium users"""

    user_tier = await _get_user_tier(current_user["id"])

    if user_tier == UserTier.FREE:
        raise HTTPException(
            status_code=403, detail="Custom emoji features require premium subscription"
        )

    # Check monthly usage limits
    await _check_feature_usage("custom_emojis", current_user["id"], user_tier)

    try:
        # Get available emoji pack for user tier
        available_emojis = await PremiumEmojiService.get_premium_emoji_pack(user_tier.value)

        # Validate requested emojis are available for user's tier
        invalid_emojis = [eid for eid in request.emoji_ids if eid not in available_emojis]
        if invalid_emojis:
            raise HTTPException(
                status_code=400,
                detail=f"Emoji IDs not available for {user_tier.value} tier: {invalid_emojis}",
            )

        # Format message with custom emojis
        formatted_text, entities = await PremiumEmojiService.format_premium_message(
            request.text, user_tier.value, include_signature=True
        )

        # Update usage tracking
        await _increment_feature_usage("custom_emojis", current_user["id"], len(request.emoji_ids))

        return CustomEmojiResponse(
            formatted_text=formatted_text,
            entities=entities,
            emojis_used=len(request.emoji_ids),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom emoji formatting failed: {str(e)}")


@router.post("/theft-detection")
async def detect_content_theft(
    content: str = Form(...),
    current_user: dict = Depends(get_current_user),
    content_protection: ContentProtectionService = Depends(get_content_protection_service),
):
    """Analyze content for potential theft indicators (Phase 3.3 API)"""

    user_tier = await _get_user_tier(current_user["id"])

    # Check monthly usage limits
    await _check_feature_usage("theft_scans", current_user["id"], user_tier)

    try:
        # Create protection request for text content theft detection
        protection_request = ContentProtectionRequest(
            content_type="text",
            text_content=content,
            user_id=current_user["id"],
            check_theft=True,
        )

        # Analyze using Phase 3.3 service
        protection_response = await content_protection.protect_content(protection_request)

        # Update usage tracking
        await _increment_feature_usage("theft_scans", current_user["id"])

        return {
            "analysis": protection_response.theft_analysis,
            "scanned_at": datetime.utcnow(),
            "user_tier": user_tier.value,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Theft detection failed: {str(e)}")


@router.get("/files/{filename}")
async def download_protected_file(filename: str, current_user: dict = Depends(get_current_user)):
    """Download watermarked file (Phase 3.3 compatible)"""

    # Use default temp directory (consistent with adapters)
    temp_dir = Path("/tmp/analyticbot_media")
    file_path = temp_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found or expired")

    # Basic security: check if file was created for this user (implement proper authorization)
    return FileResponse(path=file_path, filename=filename, media_type="application/octet-stream")


@router.get("/premium-features/{tier}")
async def get_premium_features(tier: UserTier):
    """Get available premium features and limits for tier"""

    limits = PremiumFeatureLimits.get_limits_for_tier(tier)
    available_emojis = await PremiumEmojiService.get_premium_emoji_pack(tier.value)

    return {
        "tier": tier.value,
        "limits": limits.dict(),
        "features": {
            "image_watermarking": True,
            "video_watermarking": tier != UserTier.FREE,
            "custom_emojis": tier != UserTier.FREE,
            "theft_detection": True,
            "premium_signature": tier in [UserTier.PRO, UserTier.ENTERPRISE],
        },
        "available_custom_emojis": len(available_emojis),
        "emoji_preview": available_emojis[:3],  # Show first 3 for preview
    }


@router.get("/usage/{user_id}")
async def get_feature_usage(user_id: int, current_user: dict = Depends(get_current_user)):
    """Get current month's feature usage for user"""

    # Authorization check - users can only view their own usage
    if current_user["id"] != user_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    # Get current usage (implement database query)
    usage = await _get_current_usage(user_id)
    user_tier = await _get_user_tier(user_id)
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)

    return {
        "user_id": user_id,
        "tier": user_tier.value,
        "current_month": datetime.utcnow().strftime("%Y-%m"),
        "usage": usage,
        "limits": {
            "watermarks": limits.watermarks_per_month,
            "custom_emojis": limits.custom_emojis_per_month,
            "theft_scans": limits.theft_scans_per_month,
        },
        "remaining": {
            "watermarks": (
                (limits.watermarks_per_month - usage["watermarks"])
                if limits.watermarks_per_month
                else "unlimited"
            ),
            "custom_emojis": (
                (limits.custom_emojis_per_month - usage["custom_emojis"])
                if limits.custom_emojis_per_month
                else "unlimited"
            ),
            "theft_scans": (
                (limits.theft_scans_per_month - usage["theft_scans"])
                if limits.theft_scans_per_month
                else "unlimited"
            ),
        },
    }


# Helper functions (implement based on your existing systems)
async def _get_user_tier(user_id: int) -> UserTier:
    """
    Get user's current subscription tier.

    ✅ Issue #3 Phase 2 (Oct 21, 2025): Integrated with SubscriptionAdapter
    """
    try:
        from apps.di import get_container

        container = get_container()
        subscription_service = container.bot.subscription_service()

        if subscription_service:
            tier_name = await subscription_service.get_user_tier(user_id)
            # Map tier name to UserTier enum
            tier_map = {
                "free": UserTier.FREE,
                "starter": UserTier.STARTER,
                "pro": UserTier.PRO,
                "premium": UserTier.PRO,  # Map premium to PRO
                "enterprise": UserTier.ENTERPRISE,
            }
            return tier_map.get(tier_name.lower(), UserTier.FREE)
    except Exception as e:
        logger.error(f"Error getting user tier: {e}", exc_info=True)

    # Default to FREE on error
    return UserTier.FREE


async def _check_feature_usage(feature: str, user_id: int, user_tier: UserTier):
    """Check if user has reached monthly feature limit"""
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)
    usage = await _get_current_usage(user_id)

    feature_limit = getattr(limits, f"{feature}_per_month", None)
    if feature_limit is not None and usage.get(feature, 0) >= feature_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly {feature} limit reached for {user_tier.value} tier",
        )


async def _increment_feature_usage(feature: str, user_id: int, count: int = 1):
    """
    Increment feature usage counter.

    ✅ Issue #3 Phase 2 (Oct 21, 2025): Implemented real database update
    """
    try:
        # Get database pool from connection manager
        from infra.db.connection_manager import db_manager

        pool = db_manager._pool._pool if db_manager._pool else None
        if not pool:
            logger.warning("Database pool not available, skipping usage tracking")
            return

        # Use user repository to increment usage
        from infra.db.repositories.user_repository import AsyncpgUserRepository

        user_repo = AsyncpgUserRepository(pool)
        new_count = await user_repo.increment_feature_usage(user_id, feature, count)
        logger.debug(f"Incremented {feature} usage for user {user_id}: new count = {new_count}")

    except Exception as e:
        logger.error(f"Error incrementing feature usage: {e}", exc_info=True)
        # Don't fail the request if usage tracking fails


async def _get_current_usage(user_id: int) -> dict:
    """
    Get current month's feature usage.

    ✅ Issue #3 Phase 2 (Oct 21, 2025): Implemented real database query
    """
    try:
        # Get database pool from connection manager
        from infra.db.connection_manager import db_manager

        pool = db_manager._pool._pool if db_manager._pool else None
        if not pool:
            logger.warning("Database pool not available, returning empty usage")
            return {}

        # Use user repository to get usage
        from infra.db.repositories.user_repository import AsyncpgUserRepository

        user_repo = AsyncpgUserRepository(pool)
        usage = await user_repo.get_current_month_usage(user_id)
        logger.debug(f"Current usage for user {user_id}: {usage}")
        return usage

    except Exception as e:
        logger.error(f"Error getting current usage: {e}", exc_info=True)
        # Return empty dict on error (safe default - allows features to work)
        return {}
