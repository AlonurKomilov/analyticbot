"""
Repository interfaces for data persistence
Framework-agnostic contracts for data access

All concrete implementations have been moved to infra/db/repositories/
This module now only contains imports of interface definitions
"""

# Import all repository interfaces
from .interfaces import AdminRepository, DeliveryRepository, ScheduleRepository, UserRepository

__all__ = [
    "UserRepository",
    "AdminRepository", 
    "ScheduleRepository",
    "DeliveryRepository"
]
