"""
FastAPI Exception Adapter

Converts framework-agnostic exceptions to FastAPI HTTPExceptions.
This allows core decorators to remain framework-independent while
maintaining FastAPI compatibility.
"""

from functools import wraps

from fastapi import HTTPException, status

from core.security_engine.decorators import AuthenticationError, PermissionError


def fastapi_exception_handler(func):
    """
    Decorator that converts core exceptions to FastAPI HTTPExceptions.

    This preserves all business logic in core while providing FastAPI integration.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AuthenticationError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
        except PermissionError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)

    return wrapper


# Create FastAPI-compatible versions of core decorators
def fastapi_require_permission(permission, allow_admin_override=True):
    """FastAPI version of require_permission decorator"""
    from core.security_engine.decorators import require_permission

    def decorator(func):
        # Apply core decorator first, then FastAPI exception handler
        core_decorated = require_permission(permission, allow_admin_override)(func)
        return fastapi_exception_handler(core_decorated)

    return decorator


def fastapi_require_role(min_role, allow_equal=True):
    """FastAPI version of require_role decorator"""
    from core.security_engine.decorators import require_role

    def decorator(func):
        core_decorated = require_role(min_role, allow_equal)(func)
        return fastapi_exception_handler(core_decorated)

    return decorator


def fastapi_require_admin(allow_moderator=True):
    """FastAPI version of require_admin decorator"""
    from core.security_engine.decorators import require_admin

    def decorator(func):
        core_decorated = require_admin(allow_moderator)(func)
        return fastapi_exception_handler(core_decorated)

    return decorator
