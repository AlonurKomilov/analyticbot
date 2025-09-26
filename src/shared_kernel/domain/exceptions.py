"""
Shared Domain Exceptions
"""


class DomainException(Exception):
    """Base domain exception"""
    pass


class ValidationError(DomainException):
    """Validation error in domain logic"""
    pass


class ResourceNotFoundError(DomainException):
    """Requested resource not found"""
    pass


class AuthenticationError(DomainException):
    """Authentication failed"""
    pass


class AuthorizationError(DomainException):
    """Authorization failed - user lacks permissions"""
    pass


class BusinessRuleViolation(DomainException):
    """Business rule violated"""
    pass
