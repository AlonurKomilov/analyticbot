"""
Mock Admin Service Implementation
Protocol-compliant admin service for demo mode
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from core.protocols import AdminServiceProtocol
# Demo constants (moved from old apps.api.__mocks__.constants)
DEMO_API_DELAY_MS = 100
DEMO_SUCCESS_RATE = 0.95
DEFAULT_DEMO_CHANNEL_ID = "demo_channel_123"
DEMO_POSTS_COUNT = 50
DEMO_METRICS_DAYS = 30
class MockAdminService(AdminServiceProtocol):
    """Mock admin service for demo mode"""
    
    def get_service_name(self) -> str:
        return "mock_admin_service"
    
    async def health_check(self) -> Dict[str, Any]:
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        return {
            "service": "admin",
            "status": "healthy",
            "demo_mode": True,
            "operations_logged": random.randint(50, 200)
        }
    
    async def get_user_channels(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user channels for admin"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        # Generate mock channels
        channels = []
        for i in range(random.randint(2, 5)):
            channels.append({
                "id": f"channel_{user_id}_{i}",
                "name": f"Demo Channel {i+1}",
                "username": f"demo_channel_{i+1}",
                "members_count": random.randint(100, 10000),
                "type": random.choice(["public", "private"]),
                "created_date": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "is_active": random.choice([True, True, True, False]),  # Mostly active
                "category": random.choice(["Tech", "News", "Entertainment", "Education"])
            })
        
        return channels
    
    async def get_operations_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get admin operations log"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        operations = []
        operation_types = [
            "user_login", "user_logout", "channel_created", "channel_deleted",
            "payment_processed", "subscription_updated", "admin_action", "system_backup"
        ]
        
        for i in range(min(limit, random.randint(20, 50))):
            operations.append({
                "id": f"op_{i+1}",
                "type": random.choice(operation_types),
                "user_id": random.randint(100, 999),
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 1440))).isoformat(),
                "details": {
                    "ip_address": f"192.168.1.{random.randint(1, 254)}",
                    "user_agent": "Demo Browser 1.0",
                    "status": random.choice(["success", "success", "success", "failed"]),
                    "duration_ms": random.randint(10, 500)
                },
                "metadata": {
                    "demo_mode": True,
                    "severity": random.choice(["info", "info", "warning", "error"])
                }
            })
        
        return sorted(operations, key=lambda x: x["timestamp"], reverse=True)
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        return {
            "users": {
                "total": random.randint(1000, 5000),
                "active_today": random.randint(100, 500),
                "new_this_week": random.randint(10, 50),
                "demo_users": 3
            },
            "channels": {
                "total": random.randint(500, 2000),
                "active": random.randint(400, 1800),
                "created_today": random.randint(5, 20)
            },
            "system": {
                "uptime_hours": random.randint(100, 8760),
                "cpu_usage": round(random.uniform(20, 80), 1),
                "memory_usage": round(random.uniform(40, 90), 1),
                "disk_usage": round(random.uniform(30, 70), 1)
            },
            "api": {
                "requests_today": random.randint(10000, 50000),
                "avg_response_time_ms": random.randint(50, 200),
                "error_rate": round(random.uniform(0.1, 2.0), 2)
            },
            "demo_mode": True,
            "last_updated": datetime.now().isoformat()
        }