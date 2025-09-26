"""
Mock Telegram Service
Implements TelegramAPIServiceProtocol for demo mode
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random
import uuid

from core.protocols import TelegramAPIServiceProtocol
# Demo constants (moved from old apps.api.__mocks__.constants)
DEMO_API_DELAY_MS = 100
DEMO_SUCCESS_RATE = 0.95
DEFAULT_DEMO_CHANNEL_ID = "demo_channel_123"
DEMO_POSTS_COUNT = 50
DEMO_METRICS_DAYS = 30

logger = logging.getLogger(__name__)


class MockTelegramService(TelegramAPIServiceProtocol):
    """Mock Telegram API service for demo mode"""
    
    def __init__(self):
        self.service_name = "MockTelegramService"
        self.mock_channels = self._generate_mock_channels()
        self.mock_posts = self._generate_mock_posts()
        logger.info(f"Initialized {self.service_name}")
    
    def get_service_name(self) -> str:
        return self.service_name
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock service health check"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        return {
            "status": "healthy",
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "mock": True,
            "channels_cached": len(self.mock_channels),
            "posts_cached": len(self.mock_posts)
        }
    
    async def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Get mock channel information"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        # Return specific channel or generate one
        channel = self.mock_channels.get(channel_id, self._generate_channel_info(channel_id))
        
        return channel
    
    async def get_channel_posts(self, channel_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get mock channel posts"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        # Filter posts for this channel and limit
        channel_posts = [
            post for post in self.mock_posts 
            if post["channel_id"] == channel_id
        ][:limit]
        
        if not channel_posts:
            # Generate posts if none exist
            channel_posts = self._generate_posts_for_channel(channel_id, min(limit, DEMO_POSTS_COUNT))
        
        return channel_posts
    
    async def send_message(self, chat_id: str, message: str) -> Dict[str, Any]:
        """Mock send message to chat"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        message_id = random.randint(1000, 9999)
        
        logger.info(f"📱 Mock message sent to {chat_id}: {message[:50]}...")
        
        return {
            "message_id": message_id,
            "chat_id": chat_id,
            "text": message,
            "date": int(datetime.utcnow().timestamp()),
            "sent_at": datetime.utcnow().isoformat(),
            "mock": True
        }
    
    async def get_chat_members_count(self, chat_id: str) -> int:
        """Get mock chat members count"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        # Return realistic member count
        return random.randint(100, 10000)
    
    def _generate_mock_channels(self) -> Dict[str, Dict[str, Any]]:
        """Generate mock channel data"""
        channels = {}
        
        # Default demo channel
        channels[DEFAULT_DEMO_CHANNEL_ID] = self._generate_channel_info(DEFAULT_DEMO_CHANNEL_ID)
        
        # Additional demo channels
        for i in range(3):
            channel_id = f"demo_channel_{i+1}"
            channels[channel_id] = self._generate_channel_info(channel_id)
        
        return channels
    
    def _generate_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Generate channel information"""
        return {
            "id": channel_id,
            "title": f"Demo Channel {channel_id.split('_')[-1] if '_' in channel_id else ''}",
            "username": f"@{channel_id}",
            "description": f"Mock description for {channel_id}",
            "member_count": random.randint(500, 50000),
            "photo": {
                "small_file_id": f"mock_photo_small_{channel_id}",
                "big_file_id": f"mock_photo_big_{channel_id}"
            },
            "invite_link": f"https://t.me/{channel_id}",
            "type": "channel",
            "is_verified": random.choice([True, False]),
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(30, 365))).isoformat(),
            "mock": True
        }
    
    def _generate_mock_posts(self) -> List[Dict[str, Any]]:
        """Generate mock posts for all channels"""
        posts = []
        
        for channel_id in self.mock_channels.keys():
            posts.extend(self._generate_posts_for_channel(channel_id, DEMO_POSTS_COUNT))
        
        return posts
    
    def _generate_posts_for_channel(self, channel_id: str, count: int) -> List[Dict[str, Any]]:
        """Generate mock posts for a specific channel"""
        posts = []
        content_types = ["text", "photo", "video", "document", "poll"]
        
        for i in range(count):
            post_id = f"{channel_id}_post_{i+1}"
            content_type = random.choice(content_types)
            
            post = {
                "message_id": random.randint(1000, 9999),
                "post_id": post_id,
                "channel_id": channel_id,
                "content_type": content_type,
                "text": self._generate_post_text(content_type),
                "date": int((datetime.utcnow() - timedelta(hours=random.randint(1, 720))).timestamp()),
                "views": random.randint(100, 10000),
                "forwards": random.randint(5, 200),
                "replies": random.randint(0, 50),
                "reactions": {
                    "👍": random.randint(0, 100),
                    "❤️": random.randint(0, 80),
                    "😂": random.randint(0, 50),
                    "😢": random.randint(0, 20),
                    "😡": random.randint(0, 10)
                },
                "hashtags": self._generate_hashtags(),
                "links": self._generate_links(),
                "media": self._generate_media_info(content_type),
                "mock": True
            }
            
            posts.append(post)
        
        return posts
    
    def _generate_post_text(self, content_type: str) -> str:
        """Generate mock post text"""
        templates = {
            "text": [
                "📊 Analytics insights for today show great engagement trends! #analytics #telegram",
                "🚀 New features coming soon to our platform! Stay tuned for updates.",
                "💡 Pro tip: Best posting times are between 6-9 PM for maximum reach.",
                "📈 Your channel growth this week: +15% subscribers, +23% engagement!",
                "🎯 Content strategy update: Focus on interactive posts for better results."
            ],
            "photo": [
                "📸 Check out this amazing analytics dashboard screenshot!",
                "🎨 New design preview - what do you think?",
                "📊 Visual representation of your channel's growth this month.",
                "🖼️ Behind the scenes of our analytics platform development."
            ],
            "video": [
                "🎥 Watch our latest tutorial on channel optimization!",
                "📹 Live demo of new analytics features coming next week.",
                "🎬 Customer success story - how they grew 200% in 30 days!",
                "🎞️ Quick tip video: How to interpret your engagement metrics."
            ],
            "poll": [
                "📊 What analytics feature would you like to see next?",
                "🗳️ Poll: What's your preferred posting time?",
                "❓ Quick survey: How often do you check your analytics?",
                "📋 Vote: Which content type performs best for you?"
            ],
            "document": [
                "📄 Download our free channel growth guide (PDF)",
                "📋 Analytics report template - customize for your needs",
                "📊 Comprehensive market research document available",
                "📝 Documentation for our new API endpoints"
            ]
        }
        
        return random.choice(templates.get(content_type, templates["text"]))
    
    def _generate_hashtags(self) -> List[str]:
        """Generate mock hashtags"""
        all_hashtags = [
            "#analytics", "#telegram", "#growth", "#engagement", "#marketing",
            "#socialmedia", "#data", "#insights", "#tips", "#tutorial",
            "#business", "#strategy", "#content", "#metrics", "#roi"
        ]
        return random.sample(all_hashtags, random.randint(1, 4))
    
    def _generate_links(self) -> List[str]:
        """Generate mock links"""
        if random.random() < 0.3:  # 30% chance of having links
            return [f"https://demo-link-{random.randint(1, 100)}.com"]
        return []
    
    def _generate_media_info(self, content_type: str) -> Dict[str, Any]:
        """Generate mock media information"""
        if content_type == "text":
            return {}
        
        media_info = {
            "file_id": f"mock_file_{uuid.uuid4().hex[:8]}",
            "file_size": random.randint(1024, 10485760),  # 1KB to 10MB
        }
        
        if content_type == "photo":
            media_info.update({
                "width": random.choice([1280, 1920, 2048]),
                "height": random.choice([720, 1080, 1536]),
                "thumbnail": f"mock_thumb_{uuid.uuid4().hex[:8]}"
            })
        elif content_type == "video":
            media_info.update({
                "duration": random.randint(30, 600),
                "width": random.choice([1280, 1920]),
                "height": random.choice([720, 1080]),
                "thumbnail": f"mock_thumb_{uuid.uuid4().hex[:8]}"
            })
        
        return media_info