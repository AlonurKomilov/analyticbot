"""
Identity Domain Events
=====================

Domain events for the Identity bounded context.
These events represent important business moments in the user lifecycle.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.shared_kernel.domain.events import DomainEvent


@dataclass
class UserRegistered(DomainEvent):
    """Event raised when a new user registers"""
    user_id: str
    email: str
    username: str
    registration_time: datetime
    auth_provider: str = "local"
    event_id: str = None
    occurred_on: datetime = None
    
    @property
    def event_name(self) -> str:
        return "identity.user_registered"


@dataclass
class UserLoggedIn(DomainEvent):
    """Event raised when a user successfully logs in"""
    user_id: str
    email: str
    login_time: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    event_id: str = None
    occurred_on: datetime = None
    
    @property
    def event_name(self) -> str:
        return "identity.user_logged_in"


@dataclass
class UserPasswordChanged(DomainEvent):
    """Event raised when a user changes their password"""
    user_id: str
    email: str
    change_time: datetime
    event_id: str = None
    occurred_on: datetime = None
    
    @property
    def event_name(self) -> str:
        return "identity.user_password_changed"


@dataclass
class UserStatusChanged(DomainEvent):
    """Event raised when a user's status changes"""
    user_id: str
    email: str
    old_status: str
    new_status: str
    change_time: datetime
    reason: Optional[str] = None
    event_id: str = None
    occurred_on: datetime = None
    
    @property
    def event_name(self) -> str:
        return "identity.user_status_changed"


@dataclass
class UserEmailVerified(DomainEvent):
    """Event raised when a user verifies their email"""
    user_id: str
    email: str
    verification_time: datetime
    event_id: str = None
    occurred_on: datetime = None
    
    @property
    def event_name(self) -> str:
        return "identity.user_email_verified"


@dataclass
class UserAccountLocked(DomainEvent):
    """Event raised when a user account is locked"""
    user_id: str
    email: str
    lock_time: datetime
    reason: str
    failed_attempts: int
    event_id: str = None
    occurred_on: datetime = None
    
    @property
    def event_name(self) -> str:
        return "identity.user_account_locked"