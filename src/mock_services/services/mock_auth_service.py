"""
Mock Auth Service for centralized mock services
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import random
import hashlib

from .base_service import BaseMockService


class MockAuthService(BaseMockService):
    """Mock Auth Service for testing and development"""
    
    def __init__(self):
        super().__init__()
        self._users = {
            "admin@example.com": {
                "id": 1,
                "email": "admin@example.com",
                "username": "admin",
                "password_hash": "mock_hash_admin",
                "role": "admin",
                "is_active": True
            },
            "user@example.com": {
                "id": 2,
                "email": "user@example.com",
                "username": "user",
                "password_hash": "mock_hash_user", 
                "role": "user",
                "is_active": True
            }
        }
    
    def get_service_name(self) -> str:
        return "MockAuthService"
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Mock user authentication"""
        user = self._users.get(email)
        if user and user["is_active"]:
            return {
                "success": True,
                "user_id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "role": user["role"],
                "token": f"mock_token_{user['id']}",
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
        
        return {
            "success": False,
            "error": "Invalid credentials",
            "user_id": None,
            "token": None
        }
    
    def create_user(self, email: str, username: str, password: str, role: str = "user") -> Dict[str, Any]:
        """Mock user creation"""
        if email in self._users:
            return {
                "success": False,
                "error": "User already exists",
                "user_id": None
            }
        
        user_id = len(self._users) + 1
        self._users[email] = {
            "id": user_id,
            "email": email,
            "username": username,
            "password_hash": f"mock_hash_{user_id}",
            "role": role,
            "is_active": True
        }
        
        return {
            "success": True,
            "user_id": user_id,
            "email": email,
            "username": username,
            "role": role,
            "created_at": datetime.now().isoformat()
        }
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Mock token validation"""
        if token.startswith("mock_token_"):
            user_id = int(token.split("_")[-1])
            user = next((u for u in self._users.values() if u["id"] == user_id), None)
            
            if user:
                return {
                    "valid": True,
                    "user_id": user["id"],
                    "email": user["email"],
                    "username": user["username"],
                    "role": user["role"]
                }
        
        return {
            "valid": False,
            "error": "Invalid token",
            "user_id": None
        }
    
    def refresh_token(self, token: str) -> Dict[str, Any]:
        """Mock token refresh"""
        validation = self.validate_token(token)
        if validation["valid"]:
            return {
                "success": True,
                "new_token": f"mock_token_refreshed_{validation['user_id']}",
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
        
        return {
            "success": False,
            "error": "Invalid token",
            "new_token": None
        }
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """Mock user permissions"""
        user = next((u for u in self._users.values() if u["id"] == user_id), None)
        if not user:
            return []
        
        if user["role"] == "admin":
            return ["read", "write", "delete", "admin", "manage_users"]
        else:
            return ["read", "write"]
    
    def logout_user(self, token: str) -> Dict[str, Any]:
        """Mock user logout"""
        return {
            "success": True,
            "message": "User logged out successfully",
            "token_invalidated": True
        }