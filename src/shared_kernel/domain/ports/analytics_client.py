"""
Analytics Client Protocol
Defines the interface for analytics data clients
"""

from datetime import datetime
from typing import Any, Protocol, runtime_checkable


class AnalyticsDataProtocol(Protocol):
    """Protocol for analytics data structures"""
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation"""
        ...


class GrowthDataProtocol(Protocol):
    """Protocol for growth analytics data"""
    
    growth: Any
    channel_id: str
    period: int


class ReachDataProtocol(Protocol):
    """Protocol for reach analytics data"""
    
    reach: Any
    channel_id: str
    period: int


class SourcesDataProtocol(Protocol):
    """Protocol for sources analytics data"""
    
    sources: Any
    channel_id: str
    period: int


@runtime_checkable
class AnalyticsClientProtocol(Protocol):
    """Protocol for analytics client implementations"""
    
    async def get_growth_data(self, channel_id: str, period: int) -> GrowthDataProtocol:
        """Get growth analytics data"""
        ...
    
    async def get_reach_data(self, channel_id: str, period: int) -> ReachDataProtocol:
        """Get reach analytics data"""
        ...
    
    async def get_sources_data(self, channel_id: str, period: int) -> SourcesDataProtocol:
        """Get sources analytics data"""
        ...
