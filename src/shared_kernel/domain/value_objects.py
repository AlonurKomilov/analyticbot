"""
Value Objects - Immutable objects that represent concepts
"""

from abc import ABC
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValueObject(ABC):
    """
    Base class for value objects.
    
    Value objects are immutable objects that represent concepts
    and are compared by their values, not identity.
    """
    
    def __post_init__(self):
        """Override this method to add validation"""
        self.validate()
    
    def validate(self) -> None:
        """Override this method to add validation logic"""
        pass


@dataclass(frozen=True)
class UserId(ValueObject):
    """User ID value object"""
    value: int
    
    def validate(self) -> None:
        if self.value <= 0:
            raise ValueError("User ID must be positive")
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True)
class EmailAddress(ValueObject):
    """Email address value object with validation"""
    value: str
    
    def validate(self) -> None:
        if not self.value:
            raise ValueError("Email address cannot be empty")
        if "@" not in self.value:
            raise ValueError("Invalid email address format")
        if len(self.value) > 255:
            raise ValueError("Email address too long")
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def domain(self) -> str:
        """Get the domain part of the email"""
        return self.value.split("@")[1]
    
    @property
    def local_part(self) -> str:
        """Get the local part of the email"""
        return self.value.split("@")[0]


@dataclass(frozen=True)
class Username(ValueObject):
    """Username value object with validation"""
    value: str
    
    def validate(self) -> None:
        if not self.value:
            raise ValueError("Username cannot be empty")
        if len(self.value) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(self.value) > 50:
            raise ValueError("Username too long")
        if not self.value.replace("_", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, and underscores")
    
    def __str__(self) -> str:
        return self.value