"""
Domain Exceptions - Common exceptions used across domains
"""

from typing import Any


class DomainException(Exception):
    """Base exception for domain-related errors"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(DomainException):
    """Raised when domain validation fails"""


class EntityNotFoundError(DomainException):
    """Raised when an entity cannot be found"""

    def __init__(self, entity_type: str, entity_id: Any):
        message = f"{entity_type} with ID {entity_id} not found"
        super().__init__(message, {"entity_type": entity_type, "entity_id": entity_id})


class EntityAlreadyExistsError(DomainException):
    """Raised when trying to create an entity that already exists"""

    def __init__(self, entity_type: str, identifier: str, value: Any):
        message = f"{entity_type} with {identifier} '{value}' already exists"
        super().__init__(
            message,
            {"entity_type": entity_type, "identifier": identifier, "value": value},
        )


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated"""


class UnauthorizedError(DomainException):
    """Raised when an unauthorized action is attempted"""


class ForbiddenError(DomainException):
    """Raised when a forbidden action is attempted"""
