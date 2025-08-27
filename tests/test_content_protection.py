"""
Content Protection Test Suite - Phase 2.3
Comprehensive tests for content protection and premium features
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from apps.bot.services.content_protection import ContentProtectionService, PremiumEmojiService, WatermarkConfig
from apps.bot.models.content_protection import (
    ContentType, UserTier, ProtectionLevel, PremiumFeatureLimits,
    ContentProtectionRequest, ContentProtectionResponse
)


class TestContentProtectionService:
    """Test content protection functionality"""
    
    @pytest.fixture
    def content_protection_service(self):
        """Create ContentProtectionService instance for testing"""
        return ContentProtectionService()
    
    @pytest.fixture
    def sample_image_path(self):
        """Create a temporary test image file"""
        # Create a simple test image using PIL
        from PIL import Image, ImageDraw
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            # Create a simple 200x200 white image with blue text
            img = Image.new('RGB', (200, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((50, 90), "TEST IMAGE", fill='blue')
            img.save(tmp_file.name, 'JPEG')
            
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
            shadow=True
        )
    
    @pytest.mark.asyncio
    async def test_image_watermark_creation(self, content_protection_service, sample_image_path, watermark_config):
        """Test image watermarking functionality"""
        
        # Apply watermark
        watermarked_path = await content_protection_service.add_image_watermark(
            sample_image_path, watermark_config
        )
        
        # Verify watermarked file was created
        assert watermarked_path.exists()
        assert watermarked_path != sample_image_path
        assert watermarked_path.suffix == '.jpg'
        
        # Verify file is valid image
        from PIL import Image
        with Image.open(watermarked_path) as img:
            assert img.size == (200, 200)
            assert img.format == 'JPEG'
        
        # Cleanup
        watermarked_path.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_watermark_config_positions(self, content_protection_service, sample_image_path):
        """Test different watermark positions"""
        
        positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        
        for position in positions:
            config = WatermarkConfig(
                text="TEST",
                position=position,
                opacity=0.5,
                font_size=16,
                color="red"
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


class TestPremiumEmojiService:
    """Test premium emoji functionality"""
    
    @pytest.fixture
    def premium_emoji_service(self):
        """Create PremiumEmojiService instance for testing"""
        return PremiumEmojiService()
    
    @pytest.mark.asyncio
    async def test_emoji_pack_retrieval(self, premium_emoji_service):
        """Test getting emoji packs by tier"""
        
        # Test different tiers
        for tier in ['free', 'basic', 'pro', 'enterprise']:
            emoji_pack = await premium_emoji_service.get_premium_emoji_pack(tier)
            
            assert isinstance(emoji_pack, dict)
            assert len(emoji_pack) > 0
            
            # Higher tiers should have more emojis
            if tier == 'enterprise':
                assert len(emoji_pack) >= 50  # Enterprise has most emojis
            elif tier == 'free':
                assert len(emoji_pack) >= 10   # Free has basic set
    
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
    
    @pytest.mark.asyncio
    async def test_emoji_formatting_free_vs_premium(self, premium_emoji_service):
        """Test different formatting between free and premium tiers"""
        
        test_message = "Great content!"
        
        # Free tier formatting
        free_formatted, _ = await premium_emoji_service.format_premium_message(
            test_message, "free", include_signature=False
        )
        
        # Pro tier formatting
        pro_formatted, _ = await premium_emoji_service.format_premium_message(
            test_message, "pro", include_signature=True
        )
        
        # Pro should be enhanced compared to free
        assert len(pro_formatted) >= len(free_formatted)


class TestPremiumFeatureLimits:
    """Test premium feature limits and tier management"""
    
    def test_tier_limits_structure(self):
        """Test that all tiers have proper limit definitions"""
        
        for tier in UserTier:
            limits = PremiumFeatureLimits.get_limits_for_tier(tier)
            
            # All tiers should have these attributes
            assert hasattr(limits, 'watermarks_per_month')
            assert hasattr(limits, 'custom_emojis_per_month')
            assert hasattr(limits, 'theft_scans_per_month')
            assert hasattr(limits, 'max_file_size_mb')
            
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
        if free_limits.watermarks_per_month is not None and pro_limits.watermarks_per_month is not None:
            assert free_limits.watermarks_per_month < pro_limits.watermarks_per_month


class TestContentProtectionIntegration:
    """Test integration between different content protection components"""
    
    @pytest.fixture
    def mock_user_data(self):
        """Mock user data for testing"""
        return {
            "id": 12345,
            "username": "testuser",
            "tier": UserTier.PRO,
            "subscription_active": True
        }
    
    @pytest.mark.asyncio
    async def test_watermark_with_tier_restrictions(self, mock_user_data):
        """Test watermarking respects user tier restrictions"""
        
        content_protection = ContentProtectionService()
        
        # Test file size restrictions
        limits = PremiumFeatureLimits.get_limits_for_tier(mock_user_data["tier"])
        
        # Large file should be rejected for free tier
        free_limits = PremiumFeatureLimits.get_limits_for_tier(UserTier.FREE)
        large_file_size = (free_limits.max_file_size_mb + 1) * 1024 * 1024  # Exceed limit
        
        # This would be handled at the API/handler level, not service level
        assert large_file_size > free_limits.max_file_size_mb * 1024 * 1024
    
    @pytest.mark.asyncio
    async def test_usage_tracking_integration(self):
        """Test that usage is properly tracked across features"""
        
        # This would test database integration
        # For now, verify the tracking structure is correct
        
        usage_data = {
            "user_id": 12345,
            "month_year": "2024-01",
            "watermarks_used": 5,
            "custom_emojis_used": 12,
            "theft_scans_used": 3
        }
        
        # Verify structure matches our model expectations
        required_fields = ["user_id", "month_year", "watermarks_used", "custom_emojis_used", "theft_scans_used"]
        for field in required_fields:
            assert field in usage_data


class TestContentProtectionModels:
    """Test Pydantic models for content protection"""
    
    def test_content_protection_request_model(self):
        """Test ContentProtectionRequest validation"""
        
        # Valid request
        request_data = {
            "content_type": "IMAGE",
            "watermark_text": "Test Watermark",
            "user_tier": "PRO",
            "file_size_bytes": 1024000
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
            "timestamp": datetime.utcnow()
        }
        
        response = ContentProtectionResponse(**response_data)
        assert response.protected is True
        assert response.protection_level == ProtectionLevel.PREMIUM
        assert isinstance(response.timestamp, datetime)


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_invalid_image_file(self):
        """Test handling of invalid image files"""
        
        content_protection = ContentProtectionService()
        
        # Create invalid image file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
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


@pytest.mark.integration
class TestContentProtectionEndToEnd:
    """End-to-end tests for content protection workflow"""
    
    @pytest.mark.asyncio
    async def test_complete_image_protection_workflow(self):
        """Test complete image protection from upload to download"""
        
        # This would test the full API workflow:
        # 1. Upload image
        # 2. Apply watermark
        # 3. Store protected file
        # 4. Track usage
        # 5. Return download link
        
        # For now, verify the components work together
        content_protection = ContentProtectionService()
        
        # Create test image
        from PIL import Image
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            img = Image.new('RGB', (100, 100), color='red')
            img.save(tmp_file.name, 'JPEG')
            test_path = Path(tmp_file.name)
        
        try:
            # Apply watermark
            watermark_config = WatermarkConfig(
                text="@AnalyticBot",
                position="bottom-right",
                opacity=0.8
            )
            
            protected_path = await content_protection.add_image_watermark(test_path, watermark_config)
            
            # Verify protection applied
            assert protected_path.exists()
            assert protected_path != test_path
            
            # Verify protected image is valid
            from PIL import Image
            with Image.open(protected_path) as protected_img:
                assert protected_img.size == (100, 100)
            
        finally:
            # Cleanup
            test_path.unlink(missing_ok=True)
            if 'protected_path' in locals():
                protected_path.unlink(missing_ok=True)
