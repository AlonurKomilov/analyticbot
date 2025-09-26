"""
🔒 Centralized Authentication Utilities

Provides clean, unified access to authentication operations.
Eliminates redundant JWT token handling and auth logic duplication.
"""

from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .container import get_security_manager
from .models import User, UserRole
from core.repositories import UserRepository


# HTTP Bearer security scheme
security_scheme = HTTPBearer()


class AuthError(HTTPException):
    """Standardized authentication error"""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthUtils:
    """
    Centralized authentication utilities
    
    Provides clean, consistent access to auth operations without duplication.
    All methods use the unified SecurityManager from the container.
    """
    
    @staticmethod
    def verify_jwt_token(token: str) -> Dict[str, Any]:
        """
        Verify JWT token and return payload
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload dictionary
            
        Raises:
            AuthError: If token is invalid
        """
        try:
            security_manager = get_security_manager()
            return security_manager.verify_token(token)
        except Exception as e:
            raise AuthError(f"Invalid token: {str(e)}")
    
    @staticmethod
    def create_access_token(user: User, expires_minutes: Optional[int] = None) -> str:
        """
        Create access token for user
        
        Args:
            user: User object
            expires_minutes: Optional custom expiration time
            
        Returns:
            JWT access token string
        """
        security_manager = get_security_manager()
        return security_manager.create_access_token(user, expires_minutes)
    
    @staticmethod
    def create_refresh_token(user_id: int, session_token: str) -> str:
        """
        Create refresh token for user session
        
        Args:
            user_id: User ID
            session_token: Session token
            
        Returns:
            JWT refresh token string
        """
        security_manager = get_security_manager()
        return security_manager.create_refresh_token(user_id, session_token)
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """
        Create new access token from refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New JWT access token
            
        Raises:
            AuthError: If refresh token is invalid
        """
        try:
            security_manager = get_security_manager()
            return security_manager.refresh_access_token(refresh_token)
        except Exception as e:
            raise AuthError(f"Token refresh failed: {str(e)}")
    
    @staticmethod
    def revoke_user_sessions(user_id: str) -> None:
        """
        Revoke all user sessions
        
        Args:
            user_id: User ID to revoke sessions for
        """
        security_manager = get_security_manager()
        security_manager.revoke_user_sessions(user_id)
    
    @staticmethod
    async def get_user_from_token(
        credentials: HTTPAuthorizationCredentials,
        user_repo: UserRepository
    ) -> Dict[str, Any]:
        """
        Extract and validate user from JWT token with database lookup
        
        Args:
            credentials: HTTP Bearer credentials
            user_repo: User repository for database lookup
            
        Returns:
            User dictionary from database
            
        Raises:
            AuthError: If token is invalid or user not found
        """
        # Verify token
        payload = AuthUtils.verify_jwt_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if not user_id:
            raise AuthError("Invalid token: missing user ID")
        
        # Get user from database
        user = await user_repo.get_user_by_id(int(user_id))
        if not user:
            raise AuthError("User not found")
        
        return user
    
    @staticmethod 
    def check_user_role(user: Dict[str, Any], required_role: UserRole) -> bool:
        """
        Check if user has required role with hierarchy support
        
        Args:
            user: User dictionary
            required_role: Required role
            
        Returns:
            True if user has required role or higher
        """
        try:
            user_role = UserRole(user.get("role"))
            
            # Role hierarchy: SUPERADMIN > ADMIN > USER > GUEST
            role_hierarchy = {
                UserRole.GUEST: 0,
                UserRole.USER: 1, 
                UserRole.ADMIN: 2,
                UserRole.SUPERADMIN: 3
            }
            
            return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)
        except (ValueError, KeyError):
            return False


# Global auth utilities instance  
auth_utils = AuthUtils()