"""
Phase 2.3: Content Protection Service
Advanced watermarking and premium content features
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel


class WatermarkConfig(BaseModel):
    """Watermark configuration"""
    text: str
    position: Literal["top-left", "top-right", "bottom-left", "bottom-right", "center"] = "bottom-right"
    opacity: float = 0.7
    font_size: int = 24
    color: str = "white"
    shadow: bool = True


class ContentProtectionService:
    """Advanced content protection and premium features service"""
    
    def __init__(self):
        self.temp_dir = Path("/tmp/analyticbot_media")
        self.temp_dir.mkdir(exist_ok=True)
    
    async def add_image_watermark(
        self, 
        image_path: str | Path, 
        config: WatermarkConfig
    ) -> Path:
        """Add watermark to image using Pillow"""
        
        input_path = Path(image_path)
        output_filename = f"watermarked_{uuid4().hex[:8]}_{input_path.name}"
        output_path = self.temp_dir / output_filename
        
        try:
            # Open image
            with Image.open(input_path) as image:
                # Convert to RGBA for transparency support
                if image.mode != 'RGBA':
                    image = image.convert('RGBA')
                
                # Create watermark overlay
                overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(overlay)
                
                # Try to use custom font, fall back to default
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", config.font_size)
                except:
                    font = ImageFont.load_default()
                
                # Calculate text position
                bbox = draw.textbbox((0, 0), config.text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                positions = {
                    "top-left": (20, 20),
                    "top-right": (image.width - text_width - 20, 20),
                    "bottom-left": (20, image.height - text_height - 20),
                    "bottom-right": (image.width - text_width - 20, image.height - text_height - 20),
                    "center": ((image.width - text_width) // 2, (image.height - text_height) // 2)
                }
                
                x, y = positions[config.position]
                
                # Add shadow if enabled
                if config.shadow:
                    shadow_color = (0, 0, 0, int(255 * config.opacity * 0.8))
                    draw.text((x + 2, y + 2), config.text, font=font, fill=shadow_color)
                
                # Add main text
                text_color = self._hex_to_rgba(config.color, config.opacity)
                draw.text((x, y), config.text, font=font, fill=text_color)
                
                # Composite watermark onto image
                watermarked = Image.alpha_composite(image, overlay)
                
                # Convert back to RGB if needed and save
                if watermarked.mode == 'RGBA':
                    watermarked = watermarked.convert('RGB')
                
                watermarked.save(output_path, 'JPEG', quality=95)
                
                return output_path
                
        except Exception as e:
            raise RuntimeError(f"Failed to add watermark to image: {e}")
    
    async def add_video_watermark(
        self, 
        video_path: str | Path, 
        config: WatermarkConfig
    ) -> Path:
        """Add watermark to video using FFmpeg"""
        
        input_path = Path(video_path)
        output_filename = f"watermarked_{uuid4().hex[:8]}_{input_path.stem}.mp4"
        output_path = self.temp_dir / output_filename
        
        try:
            # Position mappings for FFmpeg
            positions = {
                "top-left": "x=20:y=20",
                "top-right": "x=w-tw-20:y=20", 
                "bottom-left": "x=20:y=h-th-20",
                "bottom-right": "x=w-tw-20:y=h-th-20",
                "center": "x=(w-tw)/2:y=(h-th)/2"
            }
            
            position = positions[config.position]
            
            # Convert opacity to FFmpeg alpha (0-1)
            alpha = config.opacity
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-vf', f"drawtext=text='{config.text}':fontcolor={config.color}@{alpha}:fontsize={config.font_size}:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:{position}",
                '-codec:a', 'copy',  # Copy audio without re-encoding
                '-y',  # Overwrite output file
                str(output_path)
            ]
            
            # Execute FFmpeg command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown FFmpeg error"
                raise RuntimeError(f"FFmpeg failed: {error_msg}")
            
            return output_path
            
        except FileNotFoundError:
            raise RuntimeError("FFmpeg not installed. Please install FFmpeg to use video watermarking.")
        except Exception as e:
            raise RuntimeError(f"Failed to add watermark to video: {e}")
    
    async def create_custom_emoji_message(
        self, 
        text: str, 
        emoji_ids: list[str]
    ) -> tuple[str, list[dict]]:
        """Create message with custom emoji entities for premium users"""
        
        entities = []
        processed_text = text
        
        # Find emoji placeholders and create entities
        for i, emoji_id in enumerate(emoji_ids):
            placeholder = f"{{emoji_{i}}}"
            if placeholder in processed_text:
                start_pos = processed_text.find(placeholder)
                entities.append({
                    "type": "custom_emoji",
                    "offset": start_pos,
                    "length": len(placeholder),
                    "custom_emoji_id": emoji_id
                })
                # Replace placeholder with actual emoji representation
                processed_text = processed_text.replace(placeholder, "😊", 1)
        
        return processed_text, entities
    
    async def detect_content_theft(self, content: str) -> dict:
        """Basic content anti-theft detection"""
        
        theft_indicators = {
            "suspicious_patterns": [],
            "risk_level": "low",
            "recommendations": []
        }
        
        # Check for common theft patterns
        suspicious_words = ["stolen", "copied", "repost", "found this", "not mine"]
        found_patterns = [word for word in suspicious_words if word in content.lower()]
        
        if found_patterns:
            theft_indicators["suspicious_patterns"] = found_patterns
            theft_indicators["risk_level"] = "medium"
            theft_indicators["recommendations"].append("Review content for potential theft")
        
        # Check for excessive external links (spam indicator)
        import re
        links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        
        if len(links) > 3:
            theft_indicators["risk_level"] = "high"
            theft_indicators["recommendations"].append("Content contains excessive links")
        
        return theft_indicators
    
    async def apply_premium_content_protection(
        self, 
        user_id: int, 
        content_type: str,
        file_path: Path | None = None,
        text_content: str | None = None
    ) -> dict:
        """Apply comprehensive content protection for premium users"""
        
        protection_result = {
            "protected": False,
            "watermarked_file": None,
            "protection_level": "basic",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check if user has premium subscription (implement based on your payment system)
        is_premium = await self._check_premium_status(user_id)
        
        if not is_premium:
            protection_result["protection_level"] = "basic"
            return protection_result
        
        try:
            # Apply watermarking for media content
            if file_path and content_type in ["image", "video"]:
                watermark_config = WatermarkConfig(
                    text=f"@AnalyticBot • User {user_id}",
                    position="bottom-right",
                    opacity=0.6
                )
                
                if content_type == "image":
                    watermarked_path = await self.add_image_watermark(file_path, watermark_config)
                    protection_result["watermarked_file"] = str(watermarked_path)
                elif content_type == "video":
                    watermarked_path = await self.add_video_watermark(file_path, watermark_config)
                    protection_result["watermarked_file"] = str(watermarked_path)
                
                protection_result["protected"] = True
                protection_result["protection_level"] = "premium"
            
            # Apply text content analysis
            if text_content:
                theft_analysis = await self.detect_content_theft(text_content)
                protection_result["theft_analysis"] = theft_analysis
            
            return protection_result
            
        except Exception as e:
            protection_result["error"] = str(e)
            return protection_result
    
    def _hex_to_rgba(self, hex_color: str, opacity: float) -> tuple:
        """Convert hex color to RGBA tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        a = int(255 * opacity)
        return (r, g, b, a)
    
    async def _check_premium_status(self, user_id: int) -> bool:
        """Check if user has active premium subscription"""
        # TODO: Integrate with your payment system (Phase 2.2)
        # This is a placeholder - implement based on your subscription model
        
        # For now, return True for demo purposes
        # In production, check subscription status from database
        return True  # Replace with actual subscription check
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary watermarked files"""
        import time
        
        current_time = time.time()
        for file_path in self.temp_dir.glob("watermarked_*"):
            if current_time - file_path.stat().st_mtime > max_age_hours * 3600:
                file_path.unlink()


# Premium emoji service for enhanced user experience
class PremiumEmojiService:
    """Premium custom emoji features"""
    
    @staticmethod
    async def get_premium_emoji_pack(user_tier: str) -> list[str]:
        """Get available custom emoji based on user tier"""
        
        emoji_packs = {
            "starter": [
                "5432109876543210987",  # Custom analytics emoji
                "6543210987654321098",  # Custom success emoji
            ],
            "pro": [
                "5432109876543210987",  # Analytics
                "6543210987654321098",  # Success  
                "7654321098765432109",  # Premium star
                "8765432109876543210",  # Growth arrow
                "9876543210987654321",  # Champion trophy
            ],
            "enterprise": [
                # All pro emojis plus enterprise exclusives
                "5432109876543210987", "6543210987654321098", 
                "7654321098765432109", "8765432109876543210", 
                "9876543210987654321",
                "1098765432109876543",  # Enterprise crown
                "2109876543210987654",  # VIP badge
                "3210987654321098765",  # Platinum shield
            ]
        }
        
        return emoji_packs.get(user_tier, [])
    
    @staticmethod
    async def format_premium_message(
        text: str, 
        user_tier: str, 
        include_signature: bool = True
    ) -> tuple[str, list[dict]]:
        """Format message with premium styling and custom emojis"""
        
        if user_tier in ["pro", "enterprise"]:
            # Add premium formatting
            if include_signature:
                signature = "\n\n✨ _Sent via AnalyticBot Premium_"
                text += signature
        
        # Get available custom emojis for tier
        await PremiumEmojiService.get_premium_emoji_pack(user_tier)
        
        # Create entities for custom emojis (if any in text)
        entities = []
        # Implementation would parse text for emoji placeholders
        
        return text, entities
