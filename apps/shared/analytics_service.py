"""
Shared Analytics Service - Clean Architecture

Provides analytics data access for all apps (bot, jobs, frontend, api)
without creating circular dependencies between apps.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

try:
    import httpx
except ImportError:
    httpx = None

try:
    from pydantic import BaseModel as PydanticBaseModel
    BaseModel = PydanticBaseModel
except ImportError:
    # Fallback BaseModel if pydantic not available
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

logger = logging.getLogger(__name__)


class AnalyticsOverview(BaseModel):
    """Analytics overview response model"""
    total_users: int
    active_sessions: int
    total_events: int
    conversion_rate: float
    growth_rate: float


class AnalyticsMetric(BaseModel):
    """Analytics metric model"""
    metric_name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any]


class SharedAnalyticsService:
    """
    Shared Analytics Service - Framework Independent
    
    Provides analytics data access for all applications without
    creating dependencies between app layers.
    """

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        if httpx is None:
            raise ImportError("httpx is required for SharedAnalyticsService")
            
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries

        # Configure headers
        self.headers = {
            "Accept": "application/json", 
            "User-Agent": "AnalyticBot-SharedService/1.0"
        }

        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def get_overview(self) -> AnalyticsOverview:
        """Get analytics overview"""
        if httpx is None:
            raise RuntimeError("httpx library not available")
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = urljoin(self.base_url, "/api/analytics/overview")
            
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    data = response.json()
                    
                    return AnalyticsOverview(**data)
                    
                except Exception as e:
                    logger.warning(f"Analytics API attempt {attempt + 1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
        
        # This should never be reached due to raise in except block
        raise RuntimeError("Failed to get overview after all retries")

    async def get_metrics(
        self, 
        metric_names: List[str], 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AnalyticsMetric]:
        """Get specific metrics"""
        if httpx is None:
            raise RuntimeError("httpx library not available")
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = urljoin(self.base_url, "/api/analytics/metrics")
            
            params = {"metrics": ",".join(metric_names)}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
            
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(url, headers=self.headers, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    return [AnalyticsMetric(**item) for item in data.get("metrics", [])]
                    
                except Exception as e:
                    logger.warning(f"Metrics API attempt {attempt + 1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
        
        raise RuntimeError("Failed to get metrics after all retries")

    async def check_alert_conditions(
        self, 
        conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if alert conditions are met"""
        if httpx is None:
            raise RuntimeError("httpx library not available")
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = urljoin(self.base_url, "/api/analytics/alerts/check")
            
            for attempt in range(self.max_retries):
                try:
                    response = await client.post(
                        url, 
                        headers=self.headers, 
                        json=conditions
                    )
                    response.raise_for_status()
                    return response.json()
                    
                except Exception as e:
                    logger.warning(f"Alert check attempt {attempt + 1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
        
        raise RuntimeError("Failed to check alert conditions after all retries")

    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for specific user"""
        if httpx is None:
            raise RuntimeError("httpx library not available")
            
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = urljoin(self.base_url, f"/api/analytics/users/{user_id}")
            
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    return response.json()
                    
                except Exception as e:
                    logger.warning(f"User analytics attempt {attempt + 1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        raise
                    await asyncio.sleep(2 ** attempt)
        
        raise RuntimeError("Failed to get user analytics after all retries")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass