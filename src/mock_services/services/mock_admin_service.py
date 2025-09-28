"""
Mock Admin Service for centralized mock services
"""

import random
from datetime import datetime
from typing import Any

from .base_service import BaseMockService


class MockAdminService(BaseMockService):
    """Mock Admin Service for testing and development"""

    def get_service_name(self) -> str:
        return "MockAdminService"

    def get_system_stats(self) -> dict[str, Any]:
        """Get mock system statistics"""
        return {
            "total_users": random.randint(1000, 5000),
            "active_users": random.randint(500, 2000),
            "total_channels": random.randint(100, 500),
            "system_uptime": "99.5%",
            "last_updated": datetime.now().isoformat(),
        }

    def get_user_list(self, page: int = 1, limit: int = 20) -> dict[str, Any]:
        """Get mock user list"""
        users = []
        for i in range(limit):
            users.append(
                {
                    "id": i + ((page - 1) * limit),
                    "username": f"user_{i + ((page - 1) * limit)}",
                    "email": f"user{i}@example.com",
                    "status": random.choice(["active", "inactive", "suspended"]),
                    "created_at": datetime.now().isoformat(),
                }
            )

        return {
            "users": users,
            "page": page,
            "limit": limit,
            "total": random.randint(100, 1000),
        }

    def update_user_status(self, user_id: int, status: str) -> dict[str, Any]:
        """Mock user status update"""
        return {
            "user_id": user_id,
            "old_status": "active",
            "new_status": status,
            "updated_at": datetime.now().isoformat(),
            "success": True,
        }

    def get_audit_log(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get mock audit log"""
        logs = []
        actions = [
            "user_created",
            "user_updated",
            "user_deleted",
            "channel_added",
            "settings_changed",
        ]

        for i in range(limit):
            logs.append(
                {
                    "id": i,
                    "action": random.choice(actions),
                    "user_id": random.randint(1, 100),
                    "timestamp": datetime.now().isoformat(),
                    "details": {"mock": "audit_entry"},
                }
            )

        return logs

    def get_system_health(self) -> dict[str, Any]:
        """Get mock system health"""
        return {
            "status": "healthy",
            "services": {"database": "up", "redis": "up", "api": "up", "bot": "up"},
            "metrics": {
                "cpu_usage": random.uniform(0.1, 0.8),
                "memory_usage": random.uniform(0.3, 0.7),
                "disk_usage": random.uniform(0.2, 0.6),
            },
            "checked_at": datetime.now().isoformat(),
        }
