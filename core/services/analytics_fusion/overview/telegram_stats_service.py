"""
Telegram Statistics API Service
================================

Service for fetching channel statistics from Telegram's official Statistics API.
This provides demographics, traffic sources, and detailed engagement metrics
that are only available through the Statistics API (not regular MTProto calls).

Requirements:
- Channel must have 500+ subscribers
- User must be an admin of the channel
- MTProto client must be connected
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LanguageStats:
    """Language distribution statistics."""
    language_code: str
    language_name: str
    percentage: float
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "language_code": self.language_code,
            "language_name": self.language_name,
            "percentage": self.percentage,
        }


@dataclass
class CountryStats:
    """Country/region distribution statistics."""
    country_code: str
    country_name: str
    percentage: float
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "country_code": self.country_code,
            "country_name": self.country_name,
            "percentage": self.percentage,
        }


@dataclass  
class DeviceStats:
    """Device type distribution statistics."""
    device_type: str  # 'android', 'ios', 'desktop', 'web'
    percentage: float
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "device_type": self.device_type,
            "percentage": self.percentage,
        }


@dataclass
class TrafficSource:
    """Traffic source statistics."""
    source_type: str  # 'search', 'mentions', 'links', 'other_channels', 'direct'
    source_name: str
    subscribers_count: int
    percentage: float
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "source_type": self.source_type,
            "source_name": self.source_name,
            "subscribers_count": self.subscribers_count,
            "percentage": self.percentage,
        }


@dataclass
class GrowthPoint:
    """Single point in growth chart."""
    date: str
    subscribers: int
    joined: int = 0
    left: int = 0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "subscribers": self.subscribers,
            "joined": self.joined,
            "left": self.left,
        }


@dataclass
class InteractionStats:
    """Interaction statistics by source."""
    views_per_post: float
    shares_per_post: float
    reactions_per_post: float
    comments_per_post: float
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "views_per_post": self.views_per_post,
            "shares_per_post": self.shares_per_post,
            "reactions_per_post": self.reactions_per_post,
            "comments_per_post": self.comments_per_post,
        }


@dataclass
class TelegramChannelStats:
    """Complete Telegram Statistics API response."""
    channel_id: int
    is_available: bool = False
    error_message: str | None = None
    
    # Basic stats
    subscriber_count: int = 0
    mean_view_count: int = 0  # Average views per post
    mean_share_count: int = 0  # Average shares per post
    mean_reaction_count: int = 0  # Average reactions per post
    
    # Demographics
    languages: list[LanguageStats] = field(default_factory=list)
    countries: list[CountryStats] = field(default_factory=list)
    devices: list[DeviceStats] = field(default_factory=list)
    
    # Traffic sources
    traffic_sources: list[TrafficSource] = field(default_factory=list)
    
    # Growth data
    growth_history: list[GrowthPoint] = field(default_factory=list)
    followers_growth_rate: float = 0.0  # Percentage change
    
    # Interaction breakdown
    interactions: InteractionStats | None = None
    
    # Timestamps
    fetched_at: datetime = field(default_factory=datetime.utcnow)
    period_start: datetime | None = None
    period_end: datetime | None = None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "channel_id": self.channel_id,
            "is_available": self.is_available,
            "error_message": self.error_message,
            "subscriber_count": self.subscriber_count,
            "mean_view_count": self.mean_view_count,
            "mean_share_count": self.mean_share_count,
            "mean_reaction_count": self.mean_reaction_count,
            "languages": [l.to_dict() for l in self.languages],
            "countries": [c.to_dict() for c in self.countries],
            "devices": [d.to_dict() for d in self.devices],
            "traffic_sources": [t.to_dict() for t in self.traffic_sources],
            "growth_history": [g.to_dict() for g in self.growth_history],
            "followers_growth_rate": self.followers_growth_rate,
            "interactions": self.interactions.to_dict() if self.interactions else None,
            "fetched_at": self.fetched_at.isoformat(),
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
        }


# Language code to name mapping
LANGUAGE_NAMES = {
    "en": "English",
    "ru": "Russian",
    "uk": "Ukrainian",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "pt": "Portuguese",
    "it": "Italian",
    "ar": "Arabic",
    "fa": "Persian",
    "tr": "Turkish",
    "id": "Indonesian",
    "hi": "Hindi",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "pl": "Polish",
    "uz": "Uzbek",
    "kk": "Kazakh",
    "az": "Azerbaijani",
}

# Country code to name mapping
COUNTRY_NAMES = {
    "US": "United States",
    "RU": "Russia",
    "UA": "Ukraine",
    "DE": "Germany",
    "GB": "United Kingdom",
    "FR": "France",
    "ES": "Spain",
    "IT": "Italy",
    "BR": "Brazil",
    "IN": "India",
    "ID": "Indonesia",
    "TR": "Turkey",
    "IR": "Iran",
    "UZ": "Uzbekistan",
    "KZ": "Kazakhstan",
    "AZ": "Azerbaijan",
    "PL": "Poland",
    "NL": "Netherlands",
    "CA": "Canada",
    "AU": "Australia",
}


class TelegramStatsService:
    """
    Service for fetching channel statistics from Telegram Statistics API.
    
    This uses the MTProto GetBroadcastStats/GetMegagroupStats methods
    which require admin access to the channel.
    """
    
    def __init__(self, user_mtproto_service: Any):
        """
        Initialize the service.
        
        Args:
            user_mtproto_service: UserMTProtoService instance for getting client
        """
        self.user_mtproto_service = user_mtproto_service
        logger.info("📊 TelegramStatsService initialized")
    
    async def get_channel_stats(
        self, 
        user_id: int, 
        channel_id: int,
        dark: bool = False
    ) -> TelegramChannelStats:
        """
        Get statistics for a channel from Telegram Statistics API.
        
        Args:
            user_id: User ID who owns the channel
            channel_id: Channel ID to get stats for
            dark: Whether to use dark theme for graphs
            
        Returns:
            TelegramChannelStats with all available statistics
        """
        result = TelegramChannelStats(channel_id=channel_id)
        
        try:
            # Get MTProto client for this user
            user_client = await self.user_mtproto_service.get_user_client(user_id, channel_id)
            if not user_client:
                result.error_message = "MTProto client not available. Please configure MTProto in settings."
                logger.warning(f"No MTProto client for user {user_id}")
                return result
            
            # Get the underlying Telethon client
            client = user_client.client
            
            # Get the channel entity
            try:
                from telethon.tl.types import PeerChannel, InputPeerChannel
                
                # Convert channel_id to proper Telegram format
                # Database stores channel IDs in various formats:
                # - 1002678877654 (positive with 100 prefix embedded)
                # - -1002678877654 (negative Telegram format)
                # Telegram PeerChannel expects the raw channel ID without -100 prefix
                
                raw_id = abs(channel_id)  # Ensure positive
                
                # If ID starts with 100 (like 1002678877654), extract the actual channel ID
                # 1002678877654 -> 2678877654
                id_str = str(raw_id)
                if len(id_str) > 10 and id_str.startswith("100"):
                    # Remove the 100 prefix
                    actual_channel_id = int(id_str[3:])
                else:
                    actual_channel_id = raw_id
                
                logger.info(f"🔍 Attempting to get channel entity: raw={channel_id}, actual_channel_id={actual_channel_id}")
                
                entity = None
                errors = []
                
                # Method 1: Try PeerChannel with the actual channel ID
                try:
                    entity = await client.get_entity(PeerChannel(actual_channel_id))
                    logger.info(f"✅ Got entity using PeerChannel({actual_channel_id})")
                except Exception as e1:
                    errors.append(f"PeerChannel({actual_channel_id}): {e1}")
                    
                    # Method 2: Try with -100 prefixed ID (Telegram's internal format)
                    try:
                        telegram_format_id = int(f"-100{actual_channel_id}")
                        entity = await client.get_entity(telegram_format_id)
                        logger.info(f"✅ Got entity using -100 format: {telegram_format_id}")
                    except Exception as e2:
                        errors.append(f"-100 format ({telegram_format_id}): {e2}")
                        
                        # Method 3: Try with original raw_id as PeerChannel
                        if raw_id != actual_channel_id:
                            try:
                                entity = await client.get_entity(PeerChannel(raw_id))
                                logger.info(f"✅ Got entity using raw PeerChannel({raw_id})")
                            except Exception as e3:
                                errors.append(f"raw PeerChannel({raw_id}): {e3}")
                
                if not entity:
                    error_details = "; ".join(errors)
                    result.error_message = f"Channel not found. The MTProto client may not have access to this channel. Please ensure the channel is in your dialogs."
                    logger.warning(f"Could not find channel {channel_id}: {error_details}")
                    return result
                    
            except Exception as e:
                result.error_message = f"Failed to get channel entity: {str(e)}"
                logger.error(f"Failed to get channel entity {channel_id}: {e}")
                return result
            
            # Check if this is a broadcast channel or megagroup
            is_megagroup = getattr(entity, "megagroup", False)
            
            try:
                if is_megagroup:
                    # Get megagroup stats
                    from telethon.tl.functions.stats import GetMegagroupStatsRequest
                    stats = await client(GetMegagroupStatsRequest(
                        channel=entity,
                        dark=dark
                    ))
                else:
                    # Get broadcast channel stats
                    from telethon.tl.functions.stats import GetBroadcastStatsRequest
                    stats = await client(GetBroadcastStatsRequest(
                        channel=entity,
                        dark=dark
                    ))
                
                # Parse the stats response
                result = await self._parse_stats_response(stats, channel_id, is_megagroup)
                result.is_available = True
                
                logger.info(f"✅ Fetched Telegram stats for channel {channel_id}")
                
            except Exception as e:
                error_str = str(e).lower()
                
                if "broadcast_required" in error_str:
                    result.error_message = "Statistics require at least 500 subscribers"
                elif "admin" in error_str or "privileg" in error_str:
                    # Telegram returns admin error for channels with <500 subscribers too
                    result.error_message = "Statistics require at least 500 subscribers and admin access"
                elif "stat" in error_str:
                    result.error_message = "Statistics not available for this channel type"
                else:
                    result.error_message = f"Could not fetch statistics: {str(e)}"
                
                logger.warning(f"Could not fetch Telegram stats for channel {channel_id}: {e}")
                
        except Exception as e:
            result.error_message = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error fetching stats for channel {channel_id}: {e}")
        
        return result
    
    async def _parse_stats_response(
        self, 
        stats: Any, 
        channel_id: int,
        is_megagroup: bool
    ) -> TelegramChannelStats:
        """
        Parse the Telegram stats response into our data structure.
        
        Args:
            stats: Raw stats response from Telegram
            channel_id: Channel ID
            is_megagroup: Whether this is a megagroup
            
        Returns:
            Parsed TelegramChannelStats
        """
        result = TelegramChannelStats(channel_id=channel_id)
        
        try:
            # Extract period
            period = getattr(stats, "period", None)
            if period:
                result.period_start = getattr(period, "min_date", None)
                result.period_end = getattr(period, "max_date", None)
            
            # Extract follower count
            followers = getattr(stats, "followers", None)
            if followers:
                result.subscriber_count = getattr(followers, "current", 0)
                prev = getattr(followers, "previous", 0)
                if prev > 0:
                    result.followers_growth_rate = ((result.subscriber_count - prev) / prev) * 100
            
            # Extract mean view count
            views_per_post = getattr(stats, "views_per_post", None)
            if views_per_post:
                result.mean_view_count = int(getattr(views_per_post, "current", 0))
            
            # Extract mean share count
            shares_per_post = getattr(stats, "shares_per_post", None)
            if shares_per_post:
                result.mean_share_count = int(getattr(shares_per_post, "current", 0))
            
            # Extract mean reaction count
            reactions_per_post = getattr(stats, "reactions_per_post", None)
            if reactions_per_post:
                result.mean_reaction_count = int(getattr(reactions_per_post, "current", 0))
            
            # Parse language breakdown
            languages_graph = getattr(stats, "languages_graph", None)
            if languages_graph:
                result.languages = await self._parse_pie_chart(languages_graph, "language")
            
            # Parse growth graph for history
            growth_graph = getattr(stats, "growth_graph", None) or getattr(stats, "members_graph", None)
            if growth_graph:
                result.growth_history = await self._parse_growth_graph(growth_graph)
            
            # Parse interactions
            result.interactions = InteractionStats(
                views_per_post=float(result.mean_view_count),
                shares_per_post=float(result.mean_share_count),
                reactions_per_post=float(result.mean_reaction_count),
                comments_per_post=0.0,  # Not always available
            )
            
            # Try to get new followers by source
            new_followers_graph = getattr(stats, "new_followers_by_source_graph", None)
            if new_followers_graph:
                result.traffic_sources = await self._parse_traffic_sources(new_followers_graph)
            
        except Exception as e:
            logger.error(f"Error parsing stats response: {e}")
        
        return result
    
    async def _parse_pie_chart(
        self, 
        graph: Any, 
        chart_type: str
    ) -> list[LanguageStats] | list[CountryStats]:
        """Parse a pie chart (languages, countries, etc.)."""
        items = []
        
        try:
            # Handle StatsGraphAsync - need to load the data
            if hasattr(graph, "token"):
                # This is an async graph, we'd need to load it
                # For now, return empty - this requires additional API call
                logger.debug(f"Skipping async graph for {chart_type}")
                return items
            
            # Handle direct graph data
            json_data = getattr(graph, "json", None)
            if json_data:
                import json
                data = json.loads(json_data.data if hasattr(json_data, "data") else json_data)
                
                columns = data.get("columns", [])
                for col in columns:
                    if len(col) >= 2:
                        code = col[0]
                        values = col[1:]
                        
                        if chart_type == "language":
                            total = sum(values) if values else 1
                            percentage = (values[0] / total * 100) if values else 0
                            items.append(LanguageStats(
                                language_code=code,
                                language_name=LANGUAGE_NAMES.get(code, code),
                                percentage=round(percentage, 1),
                            ))
                        elif chart_type == "country":
                            total = sum(values) if values else 1
                            percentage = (values[0] / total * 100) if values else 0
                            items.append(CountryStats(
                                country_code=code,
                                country_name=COUNTRY_NAMES.get(code, code),
                                percentage=round(percentage, 1),
                            ))
                            
        except Exception as e:
            logger.debug(f"Could not parse pie chart for {chart_type}: {e}")
        
        return items
    
    async def _parse_growth_graph(self, graph: Any) -> list[GrowthPoint]:
        """Parse the growth/members graph."""
        points = []
        
        try:
            if hasattr(graph, "token"):
                # Async graph - skip for now
                return points
            
            json_data = getattr(graph, "json", None)
            if json_data:
                import json
                data = json.loads(json_data.data if hasattr(json_data, "data") else json_data)
                
                columns = data.get("columns", [])
                x_column = None
                y_columns = []
                
                for col in columns:
                    if col[0] == "x":
                        x_column = col[1:]
                    else:
                        y_columns.append(col)
                
                if x_column and y_columns:
                    for i, timestamp in enumerate(x_column):
                        date_str = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
                        subscribers = y_columns[0][i + 1] if len(y_columns) > 0 and i + 1 < len(y_columns[0]) else 0
                        joined = y_columns[1][i + 1] if len(y_columns) > 1 and i + 1 < len(y_columns[1]) else 0
                        left = y_columns[2][i + 1] if len(y_columns) > 2 and i + 1 < len(y_columns[2]) else 0
                        
                        points.append(GrowthPoint(
                            date=date_str,
                            subscribers=subscribers,
                            joined=joined,
                            left=left,
                        ))
                        
        except Exception as e:
            logger.debug(f"Could not parse growth graph: {e}")
        
        return points
    
    async def _parse_traffic_sources(self, graph: Any) -> list[TrafficSource]:
        """Parse traffic sources graph."""
        sources = []
        
        try:
            if hasattr(graph, "token"):
                # Async graph - skip for now
                return sources
            
            json_data = getattr(graph, "json", None)
            if json_data:
                import json
                data = json.loads(json_data.data if hasattr(json_data, "data") else json_data)
                
                # Parse source data
                columns = data.get("columns", [])
                total = 0
                source_data = []
                
                for col in columns:
                    if len(col) >= 2 and col[0] != "x":
                        source_name = col[0]
                        count = sum(col[1:]) if len(col) > 1 else 0
                        total += count
                        source_data.append((source_name, count))
                
                for source_name, count in source_data:
                    percentage = (count / total * 100) if total > 0 else 0
                    sources.append(TrafficSource(
                        source_type=self._classify_source(source_name),
                        source_name=source_name,
                        subscribers_count=count,
                        percentage=round(percentage, 1),
                    ))
                    
        except Exception as e:
            logger.debug(f"Could not parse traffic sources: {e}")
        
        return sources
    
    def _classify_source(self, source_name: str) -> str:
        """Classify a source name into a category."""
        name_lower = source_name.lower()
        
        if "search" in name_lower:
            return "search"
        elif "mention" in name_lower or "forward" in name_lower:
            return "mentions"
        elif "link" in name_lower or "url" in name_lower:
            return "links"
        elif "channel" in name_lower or "group" in name_lower:
            return "other_channels"
        else:
            return "direct"
