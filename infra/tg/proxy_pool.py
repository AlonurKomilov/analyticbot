"""
Proxy Pool for MTProto with rotation and failure scoring.
Provides reliable proxy management with automatic failover.
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ProxyStatus(Enum):
    """Proxy health status."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    BANNED = "banned"


@dataclass
class ProxyState:
    """State tracking for a single proxy."""
    url: str
    status: ProxyStatus = ProxyStatus.HEALTHY
    fail_count: int = 0
    last_failure: Optional[float] = None
    last_success: Optional[float] = None
    last_used: float = field(default_factory=time.time)
    total_uses: int = 0
    consecutive_failures: int = 0
    ban_until: float = 0.0
    
    @property
    def is_available(self) -> bool:
        """Check if proxy is available for use."""
        if self.status == ProxyStatus.BANNED:
            return time.time() > self.ban_until
        return self.status == ProxyStatus.HEALTHY
    
    @property
    def health_score(self) -> float:
        """Calculate health score for selection (higher is better)."""
        base_score = 1.0
        
        # Penalty for failures
        if self.fail_count > 0:
            base_score -= min(0.8, self.fail_count * 0.1)
        
        # Bonus for recent success
        if self.last_success and (time.time() - self.last_success) < 300:  # 5 minutes
            base_score += 0.2
        
        # Penalty for consecutive failures
        base_score -= min(0.5, self.consecutive_failures * 0.1)
        
        # Add randomness for load balancing
        base_score += random.uniform(-0.05, 0.05)
        
        return max(0.0, base_score)
    
    def parse_proxy(self) -> Dict[str, Any]:
        """Parse proxy URL into components."""
        try:
            parsed = urlparse(self.url)
            return {
                "scheme": parsed.scheme,
                "hostname": parsed.hostname,
                "port": parsed.port,
                "username": parsed.username,
                "password": parsed.password,
            }
        except Exception as e:
            logger.error(f"Failed to parse proxy URL {self.url}: {e}")
            return {}


class ProxyPool:
    """Pool of proxies with rotation and failure management."""
    
    def __init__(
        self,
        proxy_urls: List[str],
        rotation_interval: int = 300,  # 5 minutes
        fail_score_limit: int = 3,
        ban_duration: float = 1800.0,  # 30 minutes
        health_check_interval: float = 60.0  # 1 minute
    ):
        self.proxy_urls = proxy_urls
        self.rotation_interval = rotation_interval
        self.fail_score_limit = fail_score_limit
        self.ban_duration = ban_duration
        self.health_check_interval = health_check_interval
        
        # Initialize proxy states
        self.proxies: List[ProxyState] = []
        for url in proxy_urls:
            if self._validate_proxy_url(url):
                self.proxies.append(ProxyState(url=url))
            else:
                logger.error(f"Invalid proxy URL: {url}")
        
        self.current_proxy: Optional[ProxyState] = None
        self.last_rotation: float = 0.0
        self._lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        self._started = False
        
        logger.info(f"Initialized proxy pool with {len(self.proxies)} proxies")
    
    def _validate_proxy_url(self, url: str) -> bool:
        """Validate proxy URL format."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.hostname or not parsed.port:
                return False
            if parsed.scheme not in ['http', 'https', 'socks4', 'socks5']:
                return False
            return True
        except:
            return False
    
    async def start(self) -> None:
        """Start the proxy pool and health checking."""
        if self._started:
            return
        
        if not self.proxies:
            logger.warning("No valid proxies available")
            self._started = True
            return
        
        # Select initial proxy
        await self._rotate_proxy()
        
        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        self._started = True
        logger.info(f"Proxy pool started with {len(self.proxies)} proxies")
    
    async def stop(self) -> None:
        """Stop the proxy pool."""
        if not self._started:
            return
        
        self._started = False
        
        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Proxy pool stopped")
    
    async def get_current_proxy(self) -> Optional[str]:
        """Get the current active proxy URL."""
        if not self._started or not self.proxies:
            return None
        
        async with self._lock:
            # Check if rotation is needed
            current_time = time.time()
            if (not self.current_proxy or 
                current_time - self.last_rotation > self.rotation_interval or
                not self.current_proxy.is_available):
                await self._rotate_proxy()
            
            return self.current_proxy.url if self.current_proxy else None
    
    async def report_success(self, proxy_url: str) -> None:
        """Report successful use of a proxy."""
        proxy = self._find_proxy(proxy_url)
        if proxy:
            proxy.last_success = time.time()
            proxy.consecutive_failures = 0
            if proxy.status != ProxyStatus.HEALTHY:
                proxy.status = ProxyStatus.HEALTHY
                logger.info(f"Proxy {proxy_url} recovered to healthy status")
    
    async def report_failure(self, proxy_url: str, error: Exception) -> None:
        """Report failure of a proxy."""
        proxy = self._find_proxy(proxy_url)
        if not proxy:
            return
        
        async with self._lock:
            proxy.fail_count += 1
            proxy.consecutive_failures += 1
            proxy.last_failure = time.time()
            
            error_str = str(error).lower()
            
            # Determine severity of error
            if any(word in error_str for word in ['timeout', 'connection', 'network']):
                # Network errors - mark unhealthy
                proxy.status = ProxyStatus.UNHEALTHY
                logger.warning(f"Proxy {proxy_url} marked unhealthy due to network error: {error}")
            
            elif any(word in error_str for word in ['banned', 'blocked', 'forbidden', '403']):
                # Ban-like errors - ban the proxy
                proxy.status = ProxyStatus.BANNED
                proxy.ban_until = time.time() + self.ban_duration
                logger.error(f"Proxy {proxy_url} banned for {self.ban_duration}s due to: {error}")
            
            else:
                # Generic error
                if proxy.fail_count >= self.fail_score_limit:
                    proxy.status = ProxyStatus.BANNED
                    proxy.ban_until = time.time() + self.ban_duration
                    logger.error(f"Proxy {proxy_url} banned after {proxy.fail_count} failures")
                else:
                    proxy.status = ProxyStatus.UNHEALTHY
                    logger.warning(f"Proxy {proxy_url} marked unhealthy "
                                 f"(failures: {proxy.fail_count}/{self.fail_score_limit})")
            
            # Force rotation if current proxy failed
            if self.current_proxy and self.current_proxy.url == proxy_url:
                await self._rotate_proxy()
    
    async def _rotate_proxy(self) -> None:
        """Rotate to the next best proxy."""
        available_proxies = [p for p in self.proxies if p.is_available]
        
        if not available_proxies:
            # Check for banned proxies that can be recovered
            self._recover_banned_proxies()
            available_proxies = [p for p in self.proxies if p.is_available]
        
        if not available_proxies:
            logger.error("No available proxies in pool")
            self.current_proxy = None
            return
        
        # Sort by health score (higher is better)
        available_proxies.sort(key=lambda p: p.health_score, reverse=True)
        
        old_proxy = self.current_proxy.url if self.current_proxy else "none"
        self.current_proxy = available_proxies[0]
        self.current_proxy.last_used = time.time()
        self.current_proxy.total_uses += 1
        self.last_rotation = time.time()
        
        logger.info(f"Rotated proxy from {old_proxy} to {self.current_proxy.url} "
                   f"(health_score: {self.current_proxy.health_score:.2f})")
    
    def _recover_banned_proxies(self) -> None:
        """Recover banned proxies that have completed their ban duration."""
        current_time = time.time()
        recovered = 0
        
        for proxy in self.proxies:
            if proxy.status == ProxyStatus.BANNED and current_time > proxy.ban_until:
                proxy.status = ProxyStatus.HEALTHY
                proxy.consecutive_failures = 0
                proxy.fail_count = max(0, proxy.fail_count - 1)  # Reduce fail count
                recovered += 1
                logger.info(f"Proxy {proxy.url} recovered from ban")
        
        if recovered > 0:
            logger.info(f"Recovered {recovered} proxies from ban")
    
    def _find_proxy(self, url: str) -> Optional[ProxyState]:
        """Find proxy state by URL."""
        return next((p for p in self.proxies if p.url == url), None)
    
    async def _health_check_loop(self) -> None:
        """Periodic health check loop."""
        while self._started:
            try:
                await asyncio.sleep(self.health_check_interval)
                if not self._started:
                    break
                
                # Recover banned proxies
                self._recover_banned_proxies()
                
                # Check if current proxy needs rotation
                if (self.current_proxy and 
                    not self.current_proxy.is_available and 
                    time.time() - self.last_rotation > 30):  # At least 30s between rotations
                    async with self._lock:
                        await self._rotate_proxy()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in proxy health check loop: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics."""
        status_counts = {}
        for status in ProxyStatus:
            status_counts[status.value] = len([p for p in self.proxies if p.status == status])
        
        total_uses = sum(p.total_uses for p in self.proxies)
        total_failures = sum(p.fail_count for p in self.proxies)
        
        proxy_details = []
        for proxy in self.proxies:
            proxy_details.append({
                "url": proxy.url,
                "status": proxy.status.value,
                "fail_count": proxy.fail_count,
                "consecutive_failures": proxy.consecutive_failures,
                "total_uses": proxy.total_uses,
                "health_score": proxy.health_score,
                "ban_remaining": max(0, proxy.ban_until - time.time()) if proxy.status == ProxyStatus.BANNED else 0,
                "last_used": proxy.last_used,
                "last_success": proxy.last_success,
                "last_failure": proxy.last_failure,
            })
        
        return {
            "total_proxies": len(self.proxies),
            "status_counts": status_counts,
            "current_proxy": self.current_proxy.url if self.current_proxy else None,
            "total_uses": total_uses,
            "total_failures": total_failures,
            "success_rate": (total_uses - total_failures) / max(1, total_uses),
            "last_rotation": self.last_rotation,
            "pool_started": self._started,
            "proxies": proxy_details,
            "config": {
                "rotation_interval": self.rotation_interval,
                "fail_score_limit": self.fail_score_limit,
                "ban_duration": self.ban_duration,
                "health_check_interval": self.health_check_interval
            }
        }
    
    @property
    def healthy_count(self) -> int:
        """Get count of healthy proxies."""
        return len([p for p in self.proxies if p.status == ProxyStatus.HEALTHY])
    
    @property
    def is_ready(self) -> bool:
        """Check if pool is ready (started and has available proxies)."""
        return self._started and any(p.is_available for p in self.proxies)