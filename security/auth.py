"""
🔒 Core Authentication Manager - JWT, Sessions & Security

High-performance authentication system with comprehensive security features:
- JWT token management with refresh tokens
- Session management with Redis caching
- Account lockout protection
- Security event logging
- Device tracking
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import secrets
import redis
import json
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from .models import User, UserSession, UserRole, UserStatus, AuthProvider
from .config import SecurityConfig

# Configure logging
logger = logging.getLogger(__name__)

class SecurityManager:
    """
    🔐 Core Security Manager
    
    Handles all authentication operations with enterprise-grade security:
    - JWT token generation and validation
    - Session management with Redis
    - Multi-factor authentication
    - Account security policies
    - Audit logging
    """
    
    def __init__(self):
        self.config = SecurityConfig()
        self.redis_client = redis.Redis(
            host=self.config.REDIS_HOST,
            port=self.config.REDIS_PORT,
            db=self.config.REDIS_DB,
            decode_responses=True
        )
        self.security = HTTPBearer()
    
    def create_access_token(
        self, 
        user: User, 
        expires_delta: Optional[timedelta] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Create JWT access token with user claims
        
        Args:
            user: User object
            expires_delta: Token expiration time
            session_id: Associated session ID
            
        Returns:
            JWT access token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Token payload with comprehensive claims
        to_encode = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "status": user.status.value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(16),  # JWT ID for token tracking
            "session_id": session_id,
            "mfa_verified": user.is_mfa_enabled and session_id,
            "auth_provider": user.auth_provider.value
        }
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.config.SECRET_KEY, 
            algorithm=self.config.ALGORITHM
        )
        
        # Cache token in Redis for fast validation
        self._cache_token(encoded_jwt, to_encode, expire)
        
        logger.info(f"Access token created for user {user.username} (ID: {user.id})")
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str, session_id: str) -> str:
        """
        Create refresh token for token renewal
        
        Args:
            user_id: User ID
            session_id: Session ID
            
        Returns:
            Refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "sub": user_id,
            "session_id": session_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        refresh_token = jwt.encode(
            to_encode,
            self.config.REFRESH_SECRET_KEY,
            algorithm=self.config.ALGORITHM
        )
        
        # Store refresh token in Redis
        self.redis_client.setex(
            f"refresh_token:{refresh_token}",
            int(timedelta(days=self.config.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
            json.dumps({"user_id": user_id, "session_id": session_id})
        )
        
        return refresh_token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Token payload dictionary
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Check Redis cache first for performance
            cached_payload = self.redis_client.get(f"token:{token}")
            if cached_payload:
                payload = json.loads(cached_payload)
                
                # Verify expiration
                if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                    self._revoke_token(token)
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token expired"
                    )
                
                return payload
            
            # Decode JWT token
            payload = jwt.decode(
                token, 
                self.config.SECRET_KEY, 
                algorithms=[self.config.ALGORITHM]
            )
            
            # Additional security validations
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Check if token is revoked
            if self.redis_client.exists(f"revoked_token:{token}"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token revoked"
                )
            
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def create_user_session(
        self,
        user: User,
        request: Request,
        device_info: Optional[Dict[str, Any]] = None
    ) -> UserSession:
        """
        Create new user session with security tracking
        
        Args:
            user: User object
            request: FastAPI request object
            device_info: Device information dictionary
            
        Returns:
            UserSession object
        """
        # Create session
        session = UserSession(
            user_id=user.id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            device_info=device_info
        )
        
        # Store session in Redis
        session_data = session.dict()
        self.redis_client.setex(
            f"session:{session.id}",
            int(timedelta(hours=24).total_seconds()),
            json.dumps(session_data, default=str)
        )
        
        # Track active sessions for user
        self.redis_client.sadd(f"user_sessions:{user.id}", session.id)
        
        logger.info(f"Session created for user {user.username} from IP {session.ip_address}")
        return session
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """
        Retrieve user session from Redis
        
        Args:
            session_id: Session ID
            
        Returns:
            UserSession object or None
        """
        session_data = self.redis_client.get(f"session:{session_id}")
        if not session_data:
            return None
        
        try:
            data = json.loads(session_data)
            session = UserSession(**data)
            
            # Check if session is expired
            if session.is_expired():
                self.terminate_session(session_id)
                return None
            
            return session
        except (json.JSONDecodeError, ValueError):
            return None
    
    def extend_session(self, session_id: str, hours: int = 24) -> bool:
        """
        Extend session expiration time
        
        Args:
            session_id: Session ID
            hours: Hours to extend
            
        Returns:
            Success status
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.extend_session(hours)
        
        # Update in Redis
        self.redis_client.setex(
            f"session:{session_id}",
            int(timedelta(hours=hours).total_seconds()),
            json.dumps(session.dict(), default=str)
        )
        
        return True
    
    def terminate_session(self, session_id: str) -> bool:
        """
        Terminate user session
        
        Args:
            session_id: Session ID
            
        Returns:
            Success status
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Mark session as terminated
        session.terminate_session()
        
        # Remove from Redis
        self.redis_client.delete(f"session:{session_id}")
        
        # Remove from user's active sessions
        self.redis_client.srem(f"user_sessions:{session.user_id}", session_id)
        
        logger.info(f"Session {session_id} terminated for user {session.user_id}")
        return True
    
    def terminate_all_user_sessions(self, user_id: str) -> int:
        """
        Terminate all sessions for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Number of sessions terminated
        """
        session_ids = self.redis_client.smembers(f"user_sessions:{user_id}")
        terminated_count = 0
        
        for session_id in session_ids:
            if self.terminate_session(session_id):
                terminated_count += 1
        
        logger.info(f"Terminated {terminated_count} sessions for user {user_id}")
        return terminated_count
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke JWT token
        
        Args:
            token: JWT token to revoke
            
        Returns:
            Success status
        """
        try:
            # Decode to get expiration
            payload = jwt.decode(
                token,
                self.config.SECRET_KEY,
                algorithms=[self.config.ALGORITHM],
                options={"verify_exp": False}
            )
            
            # Add to revoked tokens with expiration
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                expire_time = datetime.fromtimestamp(exp_timestamp)
                seconds_until_exp = int((expire_time - datetime.utcnow()).total_seconds())
                
                if seconds_until_exp > 0:
                    self.redis_client.setex(
                        f"revoked_token:{token}",
                        seconds_until_exp,
                        "revoked"
                    )
            
            # Remove from token cache
            self._remove_cached_token(token)
            
            return True
            
        except JWTError:
            return False
    
    def _cache_token(self, token: str, payload: Dict[str, Any], expire: datetime) -> None:
        """Cache token in Redis for fast validation"""
        seconds_until_exp = int((expire - datetime.utcnow()).total_seconds())
        if seconds_until_exp > 0:
            self.redis_client.setex(
                f"token:{token}",
                seconds_until_exp,
                json.dumps(payload, default=str)
            )
    
    def _remove_cached_token(self, token: str) -> None:
        """Remove token from Redis cache"""
        self.redis_client.delete(f"token:{token}")
    
    def _revoke_token(self, token: str) -> None:
        """Internal method to revoke expired token"""
        self.redis_client.delete(f"token:{token}")
        self.redis_client.setex(f"revoked_token:{token}", 3600, "expired")

# Global security manager instance
security_manager = SecurityManager()

# FastAPI dependency functions
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user
    
    Returns:
        User payload from JWT token
    """
    token = credentials.credentials
    return security_manager.verify_token(token)

def require_role(required_role: UserRole):
    """
    FastAPI dependency to require specific user role
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function
    """
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = UserRole(current_user.get("role"))
        
        # Role hierarchy check
        role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.READONLY: 1,
            UserRole.USER: 2,
            UserRole.ANALYST: 3,
            UserRole.MODERATOR: 4,
            UserRole.ADMIN: 5
        }
        
        if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role.value}"
            )
        
        return current_user
    
    return role_checker

# Export convenience functions
create_access_token = security_manager.create_access_token
verify_token = security_manager.verify_token
