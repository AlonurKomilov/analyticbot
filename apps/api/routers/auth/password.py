"""
Password Management Endpoints

Handles password forgot/reset workflows.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from apps.api.middleware.auth import get_user_repository
from core.repositories.interfaces import UserRepository
from core.security_engine import SecurityManager, get_security_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# Password Reset Models
class ForgotPasswordRequest(BaseModel):
    """Forgot password request model"""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request model"""

    token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


# Helper functions
async def get_user_by_email(email: str, user_repository: UserRepository) -> dict | None:
    """Get user by email from the repository"""
    try:
        user = await user_repository.get_user_by_email(email)
        return user if user else None
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None


async def update_user_password(
    user_id: int, hashed_password: str, user_repository: UserRepository
) -> bool:
    """Update user password in the repository"""
    try:
        await user_repository.update_user(user_id, hashed_password=hashed_password)
        logger.info(f"Password updated for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error updating password: {e}")
        return False


@router.post("/password/forgot")
async def forgot_password(
    request: ForgotPasswordRequest,
    security_manager: SecurityManager = Depends(get_security_manager),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """
    Send password reset email

    This endpoint always returns success to prevent email enumeration attacks,
    but only sends reset emails to valid registered users.
    """
    try:
        # Check if user exists (but don't reveal this information)
        user = await get_user_by_email(request.email, user_repository)

        if user:
            # Generate reset token
            reset_token = get_security_manager().generate_password_reset_token(request.email)

            # In a production system, you would send an email here
            # For now, we'll just log the token (remove this in production!)
            logger.info(f"Password reset token for {request.email}: {reset_token}")

            # TODO: Send email with reset link
            # await send_password_reset_email(user.email, reset_token)

        return {
            "message": "If a user with that email exists, a password reset link has been sent.",
            "success": True,
        }

    except Exception as e:
        logger.error(f"Forgot password error: {str(e)}")
        # Always return success message to prevent information disclosure
        return {
            "message": "If a user with that email exists, a password reset link has been sent.",
            "success": True,
        }


@router.post("/password/reset")
async def reset_password(
    request: ResetPasswordRequest,
    security_manager: SecurityManager = Depends(get_security_manager),
    user_repository: UserRepository = Depends(get_user_repository),
):
    """
    Reset user password using reset token
    """
    try:
        # Verify reset token
        reset_data = get_security_manager().verify_password_reset_token(request.token)
        if not reset_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token"
            )

        user_email = reset_data["email"]

        # Get user by email
        user = await get_user_by_email(user_email, user_repository)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token"
            )

        # Hash new password
        from core.security_engine.models import pwd_context

        hashed_password = pwd_context.hash(request.new_password)

        # Update user password
        await update_user_password(user["id"], hashed_password, user_repository)

        # Consume the reset token (mark as used)
        get_security_manager().consume_password_reset_token(request.token)

        # Terminate all user sessions for security
        get_security_manager().terminate_all_user_sessions(str(user["id"]))
        logger.info(f"Password reset successful for user: {user_email}")

        return {
            "message": "Password reset successful. Please log in with your new password.",
            "success": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password reset failed"
        )
