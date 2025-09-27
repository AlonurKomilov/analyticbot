"""
Content Protection API Endpoints
FastAPI routes for Phase 2.3: Content Protection & Premium Features
Moved from apps/api/ to apps/bot/api/ for better architecture cohesion
"""

import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

# from src.api_service.deps import get_current_user  # TODO: Use shared_kernel auth interface  # Updated import path for API-specific auth
from src.bot_service.models.content_protection import (
    ContentProtectionResponse,
    CustomEmojiRequest,
    CustomEmojiResponse,
    PremiumFeatureLimits,
    ProtectionLevel,
    UserTier,
)
from src.bot_service.services.content_protection import (
    ContentProtectionService,
    PremiumEmojiService,
)

router = APIRouter(prefix="/content", tags=["Content Protection"])


@router.post("/watermark/image", response_model=ContentProtectionResponse)
async def add_image_watermark(
    file: UploadFile = File(...),
    watermark_text: str = Form(...),
    position: str = Form("bottom-right"),
    opacity: float = Form(0.7),
    font_size: int = Form(24),
    color: str = Form("white"),
    add_shadow: bool = Form(True),
    current_user: dict = Depends(get_current_user),
):
    """Add watermark to uploaded image"""

    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")

    # Check user premium status and limits
    user_tier = await _get_user_tier(current_user["id"])
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)

    if file.size > limits.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds limit for {user_tier.value} tier: {limits.max_file_size_mb}MB",
        )

    # Check monthly usage limits
    await _check_feature_usage("watermarks", current_user["id"], user_tier)

    content_protection = ContentProtectionService()

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(file.filename).suffix
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        # Create watermark config
        from src.bot_service.services.content_protection import WatermarkConfig

        watermark_config = WatermarkConfig(
            text=watermark_text,
            position=position,
            opacity=opacity,
            font_size=font_size,
            color=color,
            shadow=add_shadow,
        )

        # Apply watermark
        import time

        start_time = time.time()

        watermarked_path = await content_protection.add_image_watermark(tmp_path, watermark_config)

        processing_time = int((time.time() - start_time) * 1000)

        # Update usage tracking
        await _increment_feature_usage("watermarks", current_user["id"])

        return ContentProtectionResponse(
            protection_id=f"img_{watermarked_path.stem}",
            protected=True,
            protection_level=(
                ProtectionLevel.PREMIUM if user_tier != UserTier.FREE else ProtectionLevel.BASIC
            ),
            watermarked_file_url=f"/api/v1/content-protection/files/{watermarked_path.name}",
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Watermarking failed: {str(e)}")
    finally:
        # Cleanup temporary input file
        if tmp_path.exists():
            tmp_path.unlink()


@router.post("/watermark/video", response_model=ContentProtectionResponse)
async def add_video_watermark(
    file: UploadFile = File(...),
    watermark_text: str = Form(...),
    position: str = Form("bottom-right"),
    opacity: float = Form(0.7),
    font_size: int = Form(24),
    current_user: dict = Depends(get_current_user),
):
    """Add watermark to uploaded video (requires FFmpeg)"""

    # Validate file type
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video files are supported")

    # Check user premium status and limits
    user_tier = await _get_user_tier(current_user["id"])
    limits = PremiumFeatureLimits.get_limits_for_tier(user_tier)

    if user_tier == UserTier.FREE:
        raise HTTPException(
            status_code=403, detail="Video watermarking requires premium subscription"
        )

    if file.size > limits.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds limit for {user_tier.value} tier: {limits.max_file_size_mb}MB",
        )

    # Check monthly usage limits
    await _check_feature_usage("watermarks", current_user["id"], user_tier)

    content_protection = ContentProtectionService()

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        # Create watermark config
        from src.bot_service.services.content_protection import WatermarkConfig

        watermark_config = WatermarkConfig(
            text=watermark_text, position=position, opacity=opacity, font_size=font_size
        )

        # Apply watermark (this may take longer for videos)
        import time

        start_time = time.time()

        watermarked_path = await content_protection.add_video_watermark(tmp_path, watermark_config)

        processing_time = int((time.time() - start_time) * 1000)

        # Update usage tracking
        await _increment_feature_usage("watermarks", current_user["id"])

        return ContentProtectionResponse(
            protection_id=f"vid_{watermarked_path.stem}",
            protected=True,
            protection_level=ProtectionLevel.PREMIUM,
            watermarked_file_url=f"/api/v1/content-protection/files/{watermarked_path.name}",
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video watermarking failed: {str(e)}")
    finally:
        # Cleanup temporary input file
        if tmp_path.exists():
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
    content: str = Form(...), current_user: dict = Depends(get_current_user)
):
    """Analyze content for potential theft indicators"""

    user_tier = await _get_user_tier(current_user["id"])

    # Check monthly usage limits
    await _check_feature_usage("theft_scans", current_user["id"], user_tier)

    content_protection = ContentProtectionService()

    try:
        theft_analysis = await content_protection.detect_content_theft(content)

        # Update usage tracking
        await _increment_feature_usage("theft_scans", current_user["id"])

        return {
            "analysis": theft_analysis,
            "scanned_at": datetime.utcnow(),
            "user_tier": user_tier.value,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Theft detection failed: {str(e)}")


@router.get("/files/{filename}")
async def download_protected_file(filename: str, current_user: dict = Depends(get_current_user)):
    """Download watermarked file"""

    content_protection = ContentProtectionService()
    file_path = content_protection.temp_dir / filename

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
    """Get user's current subscription tier"""
    # TODO: Integrate with your payment system (Phase 2.2) via infrastructure layer
    # For now, return PRO for demo purposes
    return UserTier.PRO  # Replace with actual subscription check using AsyncpgUserRepository


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
    """Increment feature usage counter"""
    # TODO: Implement database update via infrastructure layer
    # This should update the user_premium_features table using AsyncpgUserRepository


async def _get_current_usage(user_id: int) -> dict:
    """Get current month's feature usage"""
    # TODO: Implement database query via infrastructure layer
    # Return current usage from user_premium_features table using AsyncpgUserRepository
    return {"watermarks": 5, "custom_emojis": 12, "theft_scans": 2}  # Placeholder data
