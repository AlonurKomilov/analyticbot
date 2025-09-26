"""
ChannelService Interface - Public API for channels module
"""

from typing import Protocol, runtime_checkable, Optional, Dict, Any, List
from datetime import datetime


@runtime_checkable
class ChannelService(Protocol):
    """ChannelService public interface"""
    
    async def get_channel_info(self, channel_id: int) -> Optional[dict]:
        """get_channel_info operation"""
        ...

    async def add_channel(self, user_id: int, channel_data: dict) -> dict:
        """add_channel operation"""
        ...

    async def remove_channel(self, channel_id: int) -> bool:
        """remove_channel operation"""
        ...

    async def get_user_channels(self, user_id: int) -> List[dict]:
        """get_user_channels operation"""
        ...
