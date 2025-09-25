"""
JWT Token Service - External service for token management
"""

import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os


class JWTTokenService:
    """
    JWT token service for creating and validating tokens.
    
    This is an infrastructure service that handles the technical
    details of JWT token creation and validation.
    """
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 30
    
    def create_access_token(self, user_id: int, email: str, role: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.JWTError:
            raise ValueError("Invalid token")
    
    def get_user_id_from_token(self, token: str) -> int:
        """Extract user ID from token"""
        payload = self.decode_token(token)
        return int(payload["sub"])
    
    def is_access_token(self, token: str) -> bool:
        """Check if token is an access token"""
        try:
            payload = self.decode_token(token)
            return payload.get("type") == "access"
        except ValueError:
            return False
    
    def is_refresh_token(self, token: str) -> bool:
        """Check if token is a refresh token"""
        try:
            payload = self.decode_token(token)
            return payload.get("type") == "refresh"
        except ValueError:
            return False
    
    def refresh_access_token(self, refresh_token: str, email: str, role: str) -> str:
        """Create new access token from refresh token"""
        if not self.is_refresh_token(refresh_token):
            raise ValueError("Invalid refresh token")
        
        user_id = self.get_user_id_from_token(refresh_token)
        return self.create_access_token(user_id, email, role)