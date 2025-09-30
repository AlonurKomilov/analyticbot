"""
Mock Auth Service Implementation
Protocol-compliant authentication service for demo mode
"""

import asyncio
from typing import Dict, Any, List, Optional
from core.protocols import AuthServiceProtocol
from tests.mocks.constants import DEMO_API_DELAY_MS


class MockAuthService(AuthServiceProtocol):
    """Mock authentication service for demo mode"""
    
    def __init__(self):
        self.demo_users = {
            123: {"type": "premium", "email": "demo@example.com"},
            456: {"type": "free", "email": "free@example.com"},
            789: {"type": "admin", "email": "admin@example.com"}
        }
    
    def get_service_name(self) -> str:
        return "mock_auth_service"
    
    async def health_check(self) -> Dict[str, Any]:
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        return {
            "service": "auth",
            "status": "healthy",
            "demo_mode": True,
            "registered_demo_users": len(self.demo_users)
        }
    
    async def is_demo_user(self, user_id: int) -> bool:
        """Check if user is a demo user"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        return user_id in self.demo_users
    
    async def get_demo_user_type(self, user_id: int) -> Optional[str]:
        """Get demo user type"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        user_data = self.demo_users.get(user_id)
        return user_data.get("type") if user_data else None
    
    async def authenticate_user(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate user by token"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        # Mock token validation
        if token.startswith("demo_"):
            user_id = 123  # Default demo user
            return {
                "user_id": user_id,
                "email": self.demo_users[user_id]["email"],
                "type": self.demo_users[user_id]["type"],
                "authenticated": True,
                "demo_mode": True
            }
        return None
    
    async def get_user_permissions(self, user_id: int) -> List[str]:
        """Get user permissions"""
        await asyncio.sleep(DEMO_API_DELAY_MS / 1000)
        
        user_data = self.demo_users.get(user_id)
        if not user_data:
            return []
        
        user_type = user_data["type"]
        
        if user_type == "admin":
            return ["read", "write", "admin", "manage_users", "view_analytics"]
        elif user_type == "premium":
            return ["read", "write", "view_analytics"]
        else:  # free
            return ["read"]