"""
Repository interfaces for data persistence
Framework-agnostic contracts for data access

All concrete implementations have been moved to infra/db/repositories/
This module now imports interfaces from the migrated shared kernel
"""

# Create admin repository interface (simplified fallback)
from typing import Protocol

# Import user repository from identity domain
from src.identity.domain.repositories.user_repository import UserRepository

# Import all repository interfaces from migrated location
from src.shared_kernel.domain.repositories.interfaces import (
    DeliveryRepository,
    ScheduleRepository,
)


class AdminRepository(Protocol):
    """Admin repository interface - simplified for migration compatibility"""

    async def get_admin_by_id(self, admin_id: int): ...
    async def create_admin(self, admin_data: dict): ...
    async def update_admin(self, admin_id: int, admin_data: dict): ...


__all__ = [
    "UserRepository",
    "AdminRepository",
    "ScheduleRepository",
    "DeliveryRepository",
]
