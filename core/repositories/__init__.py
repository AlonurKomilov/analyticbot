"""
Repository interfaces for data persistence
Framework-agnostic contracts for data access

All concrete implementations have been moved to infra/db/repositories/
This module now only contains imports of interface definitions
"""

# Import all repository interfaces
from .interfaces import (
    UserRepository,
    AdminRepository,
    ScheduleRepository,
    DeliveryRepository
)

__all__ = [
    "UserRepository",
    "AdminRepository", 
    "ScheduleRepository",
    "DeliveryRepository"
]
