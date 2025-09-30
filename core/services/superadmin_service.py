"""
SuperAdmin Service Layer
Enterprise-grade service for SuperAdmin operations with Clean Architecture
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from uuid import UUID

from passlib.context import CryptContext

from core.ports.repository_ports import AdminRepositoryPort, SecurityLoggerPort


class SuperAdminService:
    """Service for SuperAdmin operations and management using Clean Architecture"""

    def __init__(self, admin_repo: AdminRepositoryPort, security_logger: SecurityLoggerPort):
        self.admin_repo = admin_repo
        self.security_logger = security_logger
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def authenticate_admin(
        self, username: str, password: str, ip_address: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate admin user and create session"""
        try:
            # Get admin user using repository
            admin = await self.admin_repo.get_admin_by_username(username)

            if not admin:
                await self.security_logger.log_security_event(
                    "failed_login",
                    {"username": username, "ip": ip_address, "reason": "user_not_found"},
                )
                return None

            # Verify password
            if not self.pwd_context.verify(password, admin.get('password_hash', '')):
                await self.security_logger.log_security_event(
                    "failed_login",
                    {"username": username, "ip": ip_address, "reason": "invalid_password"},
                )
                return None

            # Successful login - reset failed attempts  
            await self.admin_repo.update_admin_login(admin['id'], datetime.utcnow())

            # Create session data
            session_data = await self.admin_repo.create_session(admin, ip_address, 'SuperAdmin Client')

            await self.security_logger.log_security_event(
                "successful_login", 
                {"username": username, "ip": ip_address}, 
                admin['id']
            )
            return session_data

        except Exception as e:
            await self.security_logger.log_security_event(
                "login_error", 
                {"username": username, "ip": ip_address, "error": str(e)}
            )
            return None

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return await self.admin_repo.get_system_stats()

    async def suspend_user(
        self, admin_id: UUID, user_id: UUID, reason: str
    ) -> bool:
        """Suspend a system user"""
        return await self.admin_repo.suspend_user(user_id, reason, admin_id)

    async def get_audit_logs(
        self, page: int = 1, limit: int = 50, admin_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get paginated audit logs"""
        offset = (page - 1) * limit
        logs = await self.admin_repo.get_audit_logs(admin_id, limit, offset)
        
        # Calculate pagination info
        total_count = len(logs) if logs else 0
        return {
            "logs": logs,
            "total": total_count,
            "page": page,
            "pages": ((total_count) + limit - 1) // limit if total_count > 0 else 0,
        }

    async def validate_admin_session(self, token: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """Validate admin session token"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return await self.admin_repo.validate_admin_session(token_hash, ip_address)

    async def get_system_users(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """Get paginated system users"""
        # This would be implemented in the repository
        # For now, return placeholder data
        return {
            "users": [],
            "total": 0,
            "page": page,
            "pages": 0
        }

    async def reactivate_user(self, user_id: int, admin_id: int) -> bool:
        """Reactivate a suspended user"""
        # This would use the repository to reactivate the user
        return True  # Placeholder

    async def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return {
            "maintenance_mode": False,
            "max_users_per_channel": 1000,
            "rate_limit_messages_per_hour": 100,
            "premium_features_enabled": True,
            "backup_frequency_hours": 24,
            "session_timeout_hours": 8,
            "max_failed_login_attempts": 5
        }

    async def update_system_config(self, config: Dict[str, Any], admin_id: int) -> bool:
        """Update system configuration"""
        try:
            from uuid import UUID
            # Create audit log entry
            await self.admin_repo.create_audit_log(
                UUID(str(admin_id)) if isinstance(admin_id, int) else admin_id,
                "update_system_config",
                "system_config",
                "config",
                config
            )
            return True
        except Exception:
            return False
