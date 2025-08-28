"""
Isolated Content Protection Test Suite - Phase 2.3
Tests without importing the full application (to avoid settings dependencies)
"""

import os

# Isolated imports to avoid settings issues
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "apps", "bot"))

from models.content_protection import (
    ContentProtectionRequest,
    ContentProtectionResponse,
    ContentType,
    PremiumFeatureLimits,
    ProtectionLevel,
    UserTier,
)
from services.content_protection import (
    ContentProtectionService,
    PremiumEmojiService,
    WatermarkConfig,
)


class TestContentProtectionServiceIsolated:
    """Test content protection functionality in isolation"""

    @pytest.fixture
    def content_protection_service(self):
        """Create ContentProtectionService instance for testing"""
        return ContentProtectionService()

    @pytest.fixture
    def sample_image_path(self):
        """Create a temporary test image file"""
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            pytest.skip("Pillow not installed - run: pip install Pillow")

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            # Create a simple 200x200 white image with blue text
            img = Image.new("RGB", (200, 200), color="white")
            draw = ImageDraw.Draw(img)
            try:
                draw.text((50, 90), "TEST IMAGE", fill="blue")
            except OSError:
                # If no font available, skip text
                pass
            img.save(tmp_file.name, "JPEG")

            yield Path(tmp_file.name)

            # Cleanup
            Path(tmp_file.name).unlink(missing_ok=True)

    @pytest.fixture
    def watermark_config(self):
        """Standard watermark configuration for testing"""
        return WatermarkConfig(
            text="TEST WATERMARK",
            position="bottom-right",
            opacity=0.7,
            font_size=20,
            color="white",
            shadow=True,
        )

    @pytest.mark.asyncio
    async def test_image_watermark_creation(
        self, content_protection_service, sample_image_path, watermark_config
    ):
        """Test image watermarking functionality"""

        try:
            from PIL import Image
        except ImportError:
            pytest.skip("Pillow not installed")

        # Apply watermark
        watermarked_path = await content_protection_service.add_image_watermark(
            sample_image_path, watermark_config
        )

        # Verify watermarked file was created
        assert watermarked_path.exists()
        assert watermarked_path != sample_image_path
        assert watermarked_path.suffix == ".jpg"

        # Verify file is valid image
        with Image.open(watermarked_path) as img:
            assert img.size == (200, 200)
            assert img.format == "JPEG"

        # Cleanup
        watermarked_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_watermark_config_positions(self, content_protection_service, sample_image_path):
        """Test different watermark positions"""

        try:
            pass
        except ImportError:
            pytest.skip("Pillow not installed")

        positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]

        for position in positions:
            config = WatermarkConfig(
                text="TEST", position=position, opacity=0.5, font_size=16, color="red"
            )

            watermarked_path = await content_protection_service.add_image_watermark(
                sample_image_path, config
            )

            assert watermarked_path.exists()
            watermarked_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_content_theft_detection(self, content_protection_service):
        """Test content theft detection algorithm"""

        # Test high-risk content (suspicious patterns)
        high_risk_content = """
        🔥🔥🔥 EXCLUSIVE LEAKED CONTENT 🔥🔥🔥
        DM for more!!! Don't share this!!!
        Credit: @someone_else
        Repost if you want more 📢📢📢
        """

        analysis = await content_protection_service.detect_content_theft(high_risk_content)

        assert analysis["risk_score"] > 0.6
        assert analysis["risk_level"] in ["MEDIUM", "HIGH", "CRITICAL"]
        assert len(analysis["indicators"]) > 0
        assert "leaked" in str(analysis["indicators"]).lower()

        # Test low-risk content (original content)
        low_risk_content = """
        Just finished working on my latest project!
        Really excited to share my thoughts on this topic.
        What do you all think about this approach?
        """

        analysis_low = await content_protection_service.detect_content_theft(low_risk_content)

        assert analysis_low["risk_score"] < 0.4
        assert analysis_low["risk_level"] == "LOW"

    @pytest.mark.asyncio
    async def test_content_theft_empty_content(self, content_protection_service):
        """Test theft detection with edge cases"""

        # Empty content
        analysis = await content_protection_service.detect_content_theft("")
        assert analysis["risk_score"] == 0.0
        assert analysis["risk_level"] == "LOW"

        # Very short content
        analysis = await content_protection_service.detect_content_theft("Hi")
        assert analysis["risk_score"] < 0.2


class TestPremiumEmojiServiceIsolated:
    """Test premium emoji functionality in isolation"""

    @pytest.fixture
    def premium_emoji_service(self):
        """Create PremiumEmojiService instance for testing"""
        return PremiumEmojiService()

    @pytest.mark.asyncio
    async def test_emoji_pack_retrieval(self, premium_emoji_service):
        """Test getting emoji packs by tier"""

        # Test different tiers
        for tier in ["free", "basic", "pro", "enterprise"]:
            emoji_pack = await premium_emoji_service.get_premium_emoji_pack(tier)

            assert isinstance(emoji_pack, dict)
            assert len(emoji_pack) > 0

            # Higher tiers should have more emojis
            if tier == "enterprise":
                assert len(emoji_pack) >= 50  # Enterprise has most emojis
            elif tier == "free":
                assert len(emoji_pack) >= 10  # Free has basic set

    @pytest.mark.asyncio
    async def test_message_formatting(self, premium_emoji_service):
        """Test premium message formatting"""

        test_message = "Hello world! This is a test message."

        formatted_text, entities = await premium_emoji_service.format_premium_message(
            test_message, "pro", include_signature=True
        )

        # Should include original message
        assert test_message in formatted_text

        # Should add premium signature for pro tier
        assert "✨" in formatted_text or "Premium" in formatted_text

        # Entities should be provided for proper formatting
        assert isinstance(entities, list)


class TestPremiumFeatureLimitsIsolated:
    """Test premium feature limits and tier management"""

    def test_tier_limits_structure(self):
        """Test that all tiers have proper limit definitions"""

        for tier in UserTier:
            limits = PremiumFeatureLimits.get_limits_for_tier(tier)

            # All tiers should have these attributes
            assert hasattr(limits, "watermarks_per_month")
            assert hasattr(limits, "custom_emojis_per_month")
            assert hasattr(limits, "theft_scans_per_month")
            assert hasattr(limits, "max_file_size_mb")

            # File size should increase with tier
            if tier == UserTier.FREE:
                assert limits.max_file_size_mb <= 10
            elif tier == UserTier.ENTERPRISE:
                assert limits.max_file_size_mb >= 100

    def test_tier_progression(self):
        """Test that higher tiers have better limits"""

        free_limits = PremiumFeatureLimits.get_limits_for_tier(UserTier.FREE)
        pro_limits = PremiumFeatureLimits.get_limits_for_tier(UserTier.PRO)
        enterprise_limits = PremiumFeatureLimits.get_limits_for_tier(UserTier.ENTERPRISE)

        # File size should increase
        assert free_limits.max_file_size_mb < pro_limits.max_file_size_mb
        assert pro_limits.max_file_size_mb <= enterprise_limits.max_file_size_mb

        # Watermark limits should increase (None = unlimited)
        if (
            free_limits.watermarks_per_month is not None
            and pro_limits.watermarks_per_month is not None
        ):
            assert free_limits.watermarks_per_month < pro_limits.watermarks_per_month


class TestContentProtectionModelsIsolated:
    """Test Pydantic models for content protection"""

    def test_content_protection_request_model(self):
        """Test ContentProtectionRequest validation"""

        # Valid request
        request_data = {
            "content_type": "IMAGE",
            "watermark_text": "Test Watermark",
            "user_tier": "PRO",
            "file_size_bytes": 1024000,
        }

        request = ContentProtectionRequest(**request_data)
        assert request.content_type == ContentType.IMAGE
        assert request.user_tier == UserTier.PRO
        assert request.file_size_bytes == 1024000

    def test_content_protection_response_model(self):
        """Test ContentProtectionResponse structure"""

        response_data = {
            "protection_id": "img_12345",
            "protected": True,
            "protection_level": "PREMIUM",
            "processing_time_ms": 1500,
            "timestamp": datetime.utcnow(),
        }

        response = ContentProtectionResponse(**response_data)
        assert response.protected is True
        assert response.protection_level == ProtectionLevel.PREMIUM
        assert isinstance(response.timestamp, datetime)


class TestErrorHandlingIsolated:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_invalid_image_file(self):
        """Test handling of invalid image files"""

        try:
            pass
        except ImportError:
            pytest.skip("Pillow not installed")

        content_protection = ContentProtectionService()

        # Create invalid image file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
            tmp_file.write(b"This is not an image file")
            invalid_path = Path(tmp_file.name)

        watermark_config = WatermarkConfig(text="Test", position="center")

        try:
            # Should raise exception for invalid image
            with pytest.raises(Exception):
                await content_protection.add_image_watermark(invalid_path, watermark_config)
        finally:
            invalid_path.unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_missing_file_handling(self):
        """Test handling of missing files"""

        content_protection = ContentProtectionService()
        non_existent_path = Path("/tmp/non_existent_file.jpg")
        watermark_config = WatermarkConfig(text="Test", position="center")

        with pytest.raises(FileNotFoundError):
            await content_protection.add_image_watermark(non_existent_path, watermark_config)


def test_pillow_availability():
    """Test that Pillow dependency is properly installed"""
    try:
        from PIL import Image

        # Try to create a simple image to verify functionality
        img = Image.new("RGB", (10, 10), color="red")
        assert img.size == (10, 10)
        print("✅ Pillow is properly installed and functional")
    except ImportError as e:
        pytest.fail(f"Pillow not properly installed: {e}")


def test_watermark_config_creation():
    """Test basic WatermarkConfig functionality"""
    config = WatermarkConfig(
        text="Test Watermark",
        position="center",
        opacity=0.5,
        font_size=18,
        color="blue",
        shadow=False,
    )

    assert config.text == "Test Watermark"
    assert config.position == "center"
    assert config.opacity == 0.5
    assert config.font_size == 18
    assert config.color == "blue"
    assert config.shadow is False


if __name__ == "__main__":
    # Run basic tests without pytest
    print("Running basic content protection tests...")
    test_pillow_availability()
    test_watermark_config_creation()
    print("✅ Basic tests passed!")
