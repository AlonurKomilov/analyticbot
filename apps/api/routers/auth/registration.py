"""
User Registration Endpoint

Handles new user account creation.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from apps.api.middleware.auth import get_user_repository
from apps.api.middleware.rate_limiter import limiter, RateLimitConfig
from apps.api.routers.auth.models import RegisterRequest
from core.repositories.interfaces import UserRepository
from core.security_engine import ApplicationRole, AuthProvider, User, UserStatus

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(RateLimitConfig.AUTH_REGISTER)  # 3 registrations per hour per IP
async def register(
    request: Request,
    response: Response,
    register_data: RegisterRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Register new user account

    Creates a new user with email verification required.
    """
    logger.debug(f"Registration endpoint received: {register_data}")
    logger.debug(f"Email: {register_data.email}, Username: {register_data.username}")

    try:
        # Check if email already exists
        existing_user = await user_repo.get_user_by_email(register_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
            )

        # Check if username already exists
        existing_username = await user_repo.get_user_by_username(register_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        # Create User object
        logger.debug("Creating User object...")

        user = User(
            email=register_data.email,
            username=register_data.username,
            full_name=register_data.full_name,
            role=ApplicationRole.USER.value,  # Use new role system
            status=UserStatus.ACTIVE,  # Auto-activate users (no email verification required)
            auth_provider=AuthProvider.LOCAL,
        )

        # Set password
        user.set_password(register_data.password)

        # Save to database
        user_data = {
            "id": int(user.id) if user.id.isdigit() else hash(user.id) % (10**9),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "hashed_password": user.hashed_password,
            "role": user.role,  # role is now a string, no .value needed
            "status": user.status.value if isinstance(user.status, UserStatus) else user.status,
            "plan_id": 1,  # Default plan
        }

        created_user = await user_repo.create_user(user_data)

        logger.info(f"New user registered: {user.username}")

        return {
            "message": "Registration successful. Please check your email for verification.",
            "user_id": created_user["id"],
            "email": user.email,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed"
        )
