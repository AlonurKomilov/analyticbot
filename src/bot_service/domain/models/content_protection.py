"""
Content Protection Models
Data models for Phase 2.3: Content Protection & Premium Features
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.shared_kernel.domain.models.base import BaseORMModel


class ContentType(str, Enum):
    """Content types for protection"""

    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    DOCUMENT = "document"


class ProtectionLevel(str, Enum):
    """Content protection levels"""

    NONE = "none"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class WatermarkPosition(str, Enum):
    """Watermark position options"""

    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    CENTER = "center"


class UserTier(str, Enum):
    """User subscription tiers"""

    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# Request/Response Models
class WatermarkRequest(BaseModel):
    """Request to add watermark to content"""

    content_type: ContentType
    watermark_text: str | None = None
    position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT
    opacity: float = 0.7
    font_size: int = 24
    color: str = "white"
    add_shadow: bool = True


class ContentProtectionRequest(BaseModel):
    """Request for comprehensive content protection"""

    user_id: int
    content_type: ContentType
    apply_watermark: bool = True
    detect_theft: bool = True
    watermark_config: WatermarkRequest | None = None


class ContentProtectionResponse(BaseModel):
    """Response for content protection operation"""

    protection_id: str
    protected: bool
    protection_level: ProtectionLevel
    watermarked_file_url: str | None = None
    theft_analysis: dict[str, Any] | None = None
    processing_time_ms: int
    timestamp: datetime

    class Config:
        use_enum_values = True


class CustomEmojiRequest(BaseModel):
    """Request to use custom emojis in message"""

    text: str
    emoji_ids: list[str]
    user_tier: UserTier


class CustomEmojiResponse(BaseModel):
    """Response with custom emoji formatted message"""

    formatted_text: str
    entities: list[dict[str, Any]]
    emojis_used: int


class TheftDetectionResult(BaseModel):
    """Content theft detection analysis result"""

    risk_level: str  # low, medium, high
    suspicious_patterns: list[str]
    confidence_score: float
    recommendations: list[str]
    analyzed_at: datetime


class PremiumFeatureUsage(BaseModel):
    """Track premium feature usage"""

    user_id: int
    feature_type: str
    usage_count: int
    last_used: datetime
    monthly_limit: int | None = None


# Database Models
class ContentProtection(BaseORMModel):
    """Content protection records"""

    __tablename__ = "content_protections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    content_type = Column(String(20), nullable=False)
    protection_level = Column(String(20), nullable=False)

    # File information
    original_file_path = Column(String(500))
    protected_file_path = Column(String(500))
    file_size_bytes = Column(Integer)

    # Watermark settings
    watermark_applied = Column(Boolean, default=False)
    watermark_text = Column(String(200))
    watermark_position = Column(String(20))
    watermark_opacity = Column(Float)

    # Theft detection
    theft_detected = Column(Boolean, default=False)
    theft_analysis = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    expires_at = Column(DateTime)  # For temporary files cleanup


class PremiumEmojiUsage(BaseORMModel):
    """Premium emoji usage tracking"""

    __tablename__ = "premium_emoji_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    emoji_id = Column(String(100), nullable=False)

    # Usage tracking
    usage_count = Column(Integer, default=1)
    first_used = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)

    # Context
    message_text = Column(Text)
    channel_id = Column(String(100))


class ContentTheftLog(BaseORMModel):
    """Content theft detection log"""

    __tablename__ = "content_theft_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    content_hash = Column(String(64), index=True)  # SHA256 hash of content

    # Detection results
    risk_level = Column(String(10), nullable=False)
    confidence_score = Column(Float)
    suspicious_patterns = Column(JSON)
    recommendations = Column(JSON)

    # Content info
    content_type = Column(String(20))
    content_preview = Column(Text)  # First 500 chars
    detected_at = Column(DateTime, default=datetime.utcnow)


class UserPremiumFeatures(BaseORMModel):
    """Track user's premium feature usage and limits"""

    __tablename__ = "user_premium_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, nullable=False, index=True)
    user_tier = Column(String(20), nullable=False)

    # Monthly usage tracking
    watermarks_used = Column(Integer, default=0)
    custom_emojis_used = Column(Integer, default=0)
    theft_scans_used = Column(Integer, default=0)

    # Limits based on tier
    watermarks_limit = Column(Integer)
    custom_emojis_limit = Column(Integer)
    theft_scans_limit = Column(Integer)

    # Reset tracking
    usage_month = Column(String(7))  # YYYY-MM format
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Analytics models for premium features
class ContentProtectionAnalytics(BaseModel):
    """Analytics for content protection usage"""

    total_protections: int
    protections_by_type: dict[str, int]
    watermarks_applied: int
    theft_detections: int
    average_processing_time_ms: float
    premium_feature_adoption: dict[str, float]


class PremiumFeatureLimits(BaseModel):
    """Premium feature limits by tier"""

    tier: UserTier
    watermarks_per_month: int | None = None  # None = unlimited
    custom_emojis_per_month: int | None = None
    theft_scans_per_month: int | None = None
    max_file_size_mb: int = 50
    supported_formats: list[str] = ["jpg", "jpeg", "png", "mp4", "mov"]

    @classmethod
    def get_limits_for_tier(cls, tier: UserTier) -> "PremiumFeatureLimits":
        """Get feature limits for specific tier"""
        limits_config = {
            UserTier.FREE: cls(
                tier=tier,
                watermarks_per_month=5,
                custom_emojis_per_month=10,
                theft_scans_per_month=3,
                max_file_size_mb=10,
                supported_formats=["jpg", "jpeg", "png"],
            ),
            UserTier.STARTER: cls(
                tier=tier,
                watermarks_per_month=50,
                custom_emojis_per_month=100,
                theft_scans_per_month=25,
                max_file_size_mb=25,
                supported_formats=["jpg", "jpeg", "png", "mp4"],
            ),
            UserTier.PRO: cls(
                tier=tier,
                watermarks_per_month=200,
                custom_emojis_per_month=500,
                theft_scans_per_month=100,
                max_file_size_mb=50,
                supported_formats=["jpg", "jpeg", "png", "mp4", "mov", "gif"],
            ),
            UserTier.ENTERPRISE: cls(
                tier=tier,
                watermarks_per_month=None,  # Unlimited
                custom_emojis_per_month=None,  # Unlimited
                theft_scans_per_month=None,  # Unlimited
                max_file_size_mb=100,
                supported_formats=["jpg", "jpeg", "png", "mp4", "mov", "gif", "webm"],
            ),
        }

        return limits_config.get(tier, limits_config[UserTier.FREE])
