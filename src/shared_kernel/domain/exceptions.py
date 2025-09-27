"""
Shared Domain Exceptions
"""


class DomainException(Exception):
    """Base domain exception"""


class ValidationError(DomainException):
    """Validation error in domain logic"""


class ResourceNotFoundError(DomainException):
    """Requested resource not found"""


class AuthenticationError(DomainException):
    """Authentication failed"""


class AuthorizationError(DomainException):
    """Authorization failed - user lacks permissions"""


class BusinessRuleViolation(DomainException):
    """Business rule violated"""
