"""
Identity Domain Events
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

from ...shared_kernel.domain.domain_events import DomainEvent


@dataclass
class UserRegistered(DomainEvent):
    """Event raised when a new user registers"""
    user_id: int
    email: str
    username: str
    auth_provider: str
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username,
            'auth_provider': self.auth_provider
        }


@dataclass 
class UserLoggedIn(DomainEvent):
    """Event raised when a user successfully logs in"""
    user_id: int
    login_time: datetime
    ip_address: Optional[str] = None
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'login_time': self.login_time.isoformat(),
            'ip_address': self.ip_address
        }


@dataclass
class UserPasswordChanged(DomainEvent):
    """Event raised when a user changes their password"""
    user_id: int
    changed_at: datetime
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'changed_at': self.changed_at.isoformat()
        }


@dataclass
class UserStatusChanged(DomainEvent):
    """Event raised when a user's status changes"""
    user_id: int
    old_status: str
    new_status: str
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'old_status': self.old_status,
            'new_status': self.new_status
        }


@dataclass
class UserEmailVerified(DomainEvent):
    """Event raised when a user's email is verified"""
    user_id: int
    email: str
    verified_at: datetime
    
    def _get_event_data(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'email': self.email,
            'verified_at': self.verified_at.isoformat()
        }